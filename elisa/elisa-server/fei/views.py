import os
import json
from django.db import connection, utils

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core import serializers
from django.core.serializers.json import DjangoJSONEncoder
from django.http.response import JsonResponse
from django.db import transaction
from django.db.models import Q
from django.db.utils import IntegrityError
from django_fsm import TransitionNotAllowed
from django_tenants.utils import get_tenant_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, list_route
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination
)
from io import StringIO
from .models import AppUser, Version, Period
from .serializers import (
    VersionSerializer,
    UserSerializer,
    UserSerializerTable,
    UserSerializerShort,
    TeachersListSerializer,
    PeriodSerializer,
    AuthGroupSerializer
)
from authentication.permissions import (
    IsMainTimetableCreator,
    IsLocalTimetableCreator,
    IsTeacher
)
from school.models import ActivityCategory, SubjectUser
from authentication.views import LoginView


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })


def get_schema(schema_name):
    try:
        version = get_tenant_model().objects.get(name=schema_name)
    except utils.DatabaseError:
        raise ValueError("Database error.")
    except get_tenant_model().DoesNotExist:
        raise ValueError("Schema '%s' does not exists." % schema_name)
    return version


class VersionViewSet(viewsets.ModelViewSet):

    serializer_class = VersionSerializer
    permission_classes = (IsMainTimetableCreator,)

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'list':
            permission_classes = [IsAuthenticatedOrReadOnly]
        else:
            permission_classes = [IsMainTimetableCreator]
        return [permission() for permission in permission_classes]

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticatedOrReadOnly])
    def latest(self, request, pk=None):
        """
        API endpoint that returns latest version according to status
        """
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

    def get_queryset(self):
        """
        Returns list of versions without public
        """
        queryset = Version.objects.filter(~Q(schema_name='public'))

        return queryset

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
                return Response(
                    "Schema already exists.",
                    status=status.HTTP_400_BAD_REQUEST)
            schema_name = serializer.data['name']
            connection.set_tenant(get_schema(schema_name))
            # if setting exists and nothing is in database table, create
            # activity categories
            if hasattr(
                    settings,
                    'ACTIVITY_CATEGORIES'
                    ) and ActivityCategory.objects.count() == 0:
                for category in settings.ACTIVITY_CATEGORIES:
                    print('Creating category %s.' % category)
                    new_category = ActivityCategory.objects.get_or_create(
                        name_sk=category.get('name_sk'),
                        name_en=category.get('name_en'),
                        color=category.get('color'))

            if 'parent_schema' in request.data:
                tmpfile = serializer.data["name"] + '.json'

                with open(tmpfile, 'w', encoding="utf-8") as f:
                    call_command(
                        "dump_tenant",
                        "dump",
                        request.data['parent_schema'],
                        stdout=f)

                with open(tmpfile, 'r', encoding="utf-8") as f:
                    call_command(
                        "dump_tenant",
                        "load",
                        schema_name,
                        fixture=tmpfile)

                if os.path.exists(tmpfile):
                    print("Removing %s." % tmpfile)
                    os.remove(tmpfile)

            return Response("OK", status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def create_and_import(self, request):
        response = self.create(request)
        version_name = request.data.pop('name', None)
        out = StringIO()
        call_command('import', 'fei-data-new', version_name, stdout=out)
        result_command = out.getvalue()
        if "IMPORT DONE" in result_command:
            return Response("OK", status=status.HTTP_201_CREATED)
        else:
            return Response(
                "FAILED",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.action == 'set_main_timetable_maker':
            return UserSerializerShort
        return UserSerializer

    def create_full_names(self, results):
        response_data = list()
        for result in results:
            Dict = dict()
            title_before = result['title_before'] if result['title_before'] is not None else ''
            title_after = f" {result['title_after']}" if result['title_after'] is not None else ''
            full_name = f"{title_before}{result['first_name']} {result['last_name']}{title_after}"
            Dict['id'] = result['id']
            Dict['full_name'] = full_name
            response_data.append(Dict)
        return response_data

    @action(detail=False)
    def table_users(self, request):
        table_users = AppUser.objects.values(
            'id',
            'username',
            'title_before',
            'first_name',
            'last_name',
            'title_after',
            'groups')
        page = self.paginate_queryset(table_users)
        if page is not None:
            serializer = UserSerializerTable(page, many=True, read_only=True)
            return self.get_paginated_response(serializer.data)

    """
    Fetches list of users with desired specified fields 
    """
    @action(detail=False)
    def list_for_role(self, request):
        users_list = list(
            AppUser.objects.values(
                'id',
                'username',
                'title_before',
                'first_name',
                'last_name',
                'title_after'))
        return JsonResponse(users_list, safe=False)

    @action(
        detail=True,
        methods=['put'],
        permission_classes=[
            IsMainTimetableCreator,
            IsLocalTimetableCreator,
            IsTeacher]
        )
    def update_roles(self, request, pk=None):
        user = self.get_object()
        # clear previous roles
        user.groups.clear()
        # add the roles from payload
        for role in request.data:
            group = Group.objects.get(name=role["name"])
            user.groups.add(group)
        try:
            user.save()
            return Response("OK", status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                "Failed during updating",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response("data invalid ", status=status.HTTP_400_BAD_REQUEST)


    """
    Set user as main timetable maker
    """
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsMainTimetableCreator])
    def set_main_timetable_maker(self, request, pk=None):
        user = self.get_object()
        try:
            group = Group.objects.get(name='MAIN_TIMETABLE_CREATOR')
            if user is not None:
                user.groups.add(group)
                user.save()
                return Response({'status': 'group set'})
        except Group.DoesNotExist:
            return Response("error", status=status.HTTP_400_BAD_REQUEST)

        return Response("error2 ", status=status.HTTP_400_BAD_REQUEST)

    """
    After (ONLY) logging in this method will check
    whether user has some roles or if even is
    a superuser to begin with. If user has some roles
    already it will just return an 'empty' response.
    Otherwise it will set default roles accordingly:
    First logged user ever => will be set as the admin
    First time logged user when admin is present =>
    default role of STUDENT will be set.
    During this process a new JWT token pair 
    will be generated.
    """
    @action(
        detail=True,
        methods=['put'],
        permission_classes=[IsAuthenticated])
    def set_user_init_roles(self, request, pk=None):
        user = self.get_object()
        has_groups = list(user.groups.all())
        if len(has_groups) > 0:
            return Response(
                "OK",
                status=status.HTTP_200_OK
            )
        try:
            main_group = Group.objects.get(name='MAIN_TIMETABLE_CREATOR')
            main_group_users = list(main_group.user_set.all())
            has_superuser = list(AppUser.objects.filter(is_superuser=True))
            default = False
            if len(main_group_users) > 0 or len(has_superuser) > 0:
                default_group = Group.objects.get(
                    name='STUDENT'
                )
                user.groups.add(default_group)
                user.save()
                default = True
            else:
                all_groups = Group.objects.all()
                for group in all_groups:
                    user.groups.add(group)
                user.is_superuser = True
                user.save()
            login_view_response = LoginView.post(
                self,
                request=request
                )
            login_view_response.data['default'] = True if default is True else False
            return login_view_response
        except IntegrityError:
            return Response(
                "Failed to set init roles!",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['get'])
    def get_user_roles(self, request, pk=None):
        try:
            user = AppUser.objects.get(pk=pk)
            results = list(
                user.groups.values(
                    'id',
                    'name')
            )
            return JsonResponse(results, safe=False)
        except AppUser.DoesNotExist:
            return Response(
                "User with provided ID doesn't exist",
                status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def logout(self, request):
        current_user = request.user
        if current_user.access_id is not None:
            refresh = RefreshToken(current_user.access_id)
            # invalidate token
            refresh.blacklist()
            current_user.access_id = None
            current_user.save()
            request.COOKIES.pop('XSRF-TOKEN', None)
            return Response("OK", status=status.HTTP_200_OK)
        else:
            return Response(
                "Already logged out!",
                status=status.HTTP_204_NO_CONTENT)


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


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    serializer_class = PeriodSerializer
    # when read only just get requests are available in swagger
    permission_classes = (IsAuthenticatedOrReadOnly, )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticatedOrReadOnly])
    def current(self, request, pk=None):
        headers = request.headers['Timetable-Version']
        headers_array = headers.split('_')
        current_year = '/'.join(headers_array[1:])
        current_semester = headers_array[0] + ' ' + current_year
        print(
            f'current semester -> {current_semester} and current year -> {current_year}')
        current_year += ' - '
        periods = Period.objects.filter(
            Q(name__icontains=current_semester) | Q(name__icontains=current_year))
        serializer = PeriodSerializer(periods, many=True)
        return Response(serializer.data)
