import os
from django.db import connection, utils

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django_fsm import TransitionNotAllowed
from django_tenants.utils import get_tenant_model
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from .models import AppUser, Version
from .serializers import VersionSerializer, UserSerializer, UserSerializerShort, TeachersListSerializer
from authentication.permissions import IsMainTimetableCreator, IsLocalTimetableCreator, IsTeacher
from school.models import ActivityCategory, SubjectUser


def get_schema(schema_name):
    try:
        version = get_tenant_model().objects.get(name=schema_name)
    except utils.DatabaseError:
        raise ValueError("Database error.")
    except get_tenant_model().DoesNotExist:
        raise ValueError("Schema '%s' does not exists." % schema_name)
    return version


class LatestVersionView(RetrieveAPIView):
    """
    API endpoint that returns latest version according to status
    """
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            query = Q(status=Version.PUBLIC)
        else:
            # logged users can get work in progress and public versions
            query = Q(status__in=[Version.PUBLIC, Version.WORK_IN_PROGRESS])

        # without public
        query = query & ~Q(schema_name='public')

        try:
            version = Version.objects.filter(query).last()

            if version is None:
                return Response("No schema version found", status=404)
        except Version.DoesNotExist:
            return Response("No schema version found", status=404)

        serializer = VersionSerializer(version)
        return Response(serializer.data)


class VersionViewSet(viewsets.ModelViewSet):

    queryset = Version.objects.all()
    serializer_class = VersionSerializer
    permission_classes = (IsMainTimetableCreator,)

    """
    Create new version
    """
    @transaction.atomic
    def create(self, request):
        serializer = VersionSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
            except IntegrityError:
                return Response("Schema already exists.", status=status.HTTP_400_BAD_REQUEST)

            schema_name = serializer.data['name']
            connection.set_tenant(get_schema(schema_name))
            # if setting exists and nothing is in database table, create activity categories
            if hasattr(settings, 'ACTIVITY_CATEGORIES') and ActivityCategory.objects.count() == 0:
                for category in settings.ACTIVITY_CATEGORIES:
                    print('Creating category %s.' % category)
                    new_category = ActivityCategory.objects.get_or_create(name_sk=category.get('name_sk'),
                                                                          name_en=category.get('name_en'),
                                                                          color=category.get('color'))

            if 'parent_schema' in request.data:
                tmpfile = serializer.data["name"] + '.json'

                with open(tmpfile, 'w', encoding="utf-8") as f:
                    call_command("dump_tenant", "dump", request.data['parent_schema'], stdout=f)

                with open(tmpfile, 'r', encoding="utf-8") as f:
                    call_command("dump_tenant", "load", schema_name, fixture=tmpfile)

                if os.path.exists(tmpfile):
                    print("Removing %s." % tmpfile)
                    os.remove(tmpfile)

            return Response("OK", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """
        Publish current schema.
        """
        try:
            version = Version.objects.get(id=pk)
            version.publish()   # call transition
            version.save()
        except Version.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)

    @action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        """
        Hide published schema.
        """
        try:
            version = Version.objects.get(id=pk)
            version.hide()  # call transition
            version.save()
        except Version.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)


class UserViewSet(viewsets.ModelViewSet):

    queryset = AppUser.objects.all()

    def get_serializer_class(self):
        if self.action == 'set_main_timetable_maker':
            return UserSerializerShort
        return UserSerializer

    """
    Set user as main timetable maker
    """
    @action(detail=True, methods=['post'], permission_classes=[IsMainTimetableCreator])
    def set_main_timetable_maker(self, request, pk=None):
        user = self.get_object()
        try:
            group = Group.objects.get(name='main_timetable_maker')
            if user is not None:
                user.groups.add(group)
                user.save()
                return Response({'status': 'group set'})
        except Group.DoesNotExist:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

        return Response("error2 ", status=status.HTTP_400_BAD_REQUEST)


class TeachersList(generics.ListAPIView):

    serializer_class = TeachersListSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        """
        This view should return a list of all teachers
        that can add requirements
        """
        return SubjectUser.objects.filter(role=3)


    @classmethod
    def get_extra_actions(cls):
        return []

