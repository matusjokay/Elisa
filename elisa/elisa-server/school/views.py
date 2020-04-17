import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework import status
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import models, serializers
from fei import models as fei_models
from django.http.response import JsonResponse
import json
from django.db.utils import IntegrityError
from rest_framework.exceptions import ValidationError

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

# TODO: Missing view set for
# FORM OF STUDY


class GroupViewSet(ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('parent',)
    search_fields = ('name', 'abbr')


class DepartmentViewSet(ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = fei_models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('parent',)
    search_fields = ('name', 'abbr')


class CourseViewSet(ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializerFull
    pagination_class = StandardResultsSetPagination
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filterset_fields = ('department',)
    search_fields = ('name', 'code')
    ordering_fields = ('name', 'code')


class EquipmentViewSet(ModelViewSet):
    """
    API endpoint that allows equipment to be viewed or edited.
    """
    queryset = models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer


class RoomTypeViewSet(ModelViewSet):
    """
    API endpoint that allows room categories to be viewed or edited.
    """
    queryset = models.RoomType.objects.all()
    serializer_class = serializers.RoomCategorySerializer


class RoomFilter(FilterSet):
    min_capacity = django_filters.NumberFilter(
        field_name='capacity', lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(
        field_name='capacity', lookup_expr='lte')
    category = django_filters.CharFilter(field_name='category__name')

    class Meta:
        model = models.Room
        fields = ['category', 'department', 'min_capacity', 'max_capacity']


class RoomViewSet(ModelViewSet):
    """
    API endpoint that allows rooms to be viewed or edited.
    """
    queryset = models.Room.objects.all()
    serializer_class = serializers.RoomSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter, SearchFilter)
    filterset_class = RoomFilter
    ordering_fields = ('name', 'capacity', 'category')
    search_fields = ('name',)


class ActivityCategoryViewSet(ModelViewSet):
    """
    API endpoint that allows activity categories to be viewed or edited.
    """
    queryset = models.ActivityCategory.objects.all()
    serializer_class = serializers.ActivityCategorySerializer


class ActivityViewSet(ModelViewSet):
    """
    API endpoint that allows activities to be viewed or edited.
    """
    queryset = models.Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class SubjectUserViewSet(ModelViewSet):
    """
    API endpoint that allows managing of users (teachers, student etc)
    to adjust relationship between courses.
    """
    queryset = models.SubjectUser.objects.all()
    serializer_class = serializers.SubjectUserSerializerFull

    @action(detail=False, methods=['get'])
    def filter_by_role(self, request):
        if request.query_params.get('role') is None:
            queryset = models.SubjectUser.objects.all()
        else:
            role_id = int(request.query_params.get('role'))
            queryset = models.SubjectUser.objects.filter(role=role_id)
        serializer = serializers.SubjectUserSerializerFull(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_users(self, request):
        subject_id = request.query_params.get('subject')
        queryset = models.SubjectUser.objects.filter(subject_id=subject_id).distinct('user_id')
        result = list()
        for row in queryset:
            result.append({'userId': row.user.id,
            'userFullname': row.user.construct_name()})
        return JsonResponse(result, safe=False)

    @action(detail=False, methods=['get'])
    def get_entries_user(self, request):
        subject_id = request.query_params.get('subject')
        user_id = request.query_params.get('user')
        queryset = models.SubjectUser.objects.filter(
            subject_id=subject_id,
            user_id=user_id
        )
        result = list()
        for row in queryset:
            result.append({'idRow': row.id,
            # 'userId': row.user.id,
            # 'userFullname': row.user.construct_name(),
            'roleId': row.role.id,
            })
        return JsonResponse(result, safe=False)

    def destroy(self, request, pk=None):
        row = models.SubjectUser.objects.get(pk=pk)
        user_id_from_row = row.user_id
        rows = models.SubjectUser.objects.filter(user_id=user_id_from_row)
        try:
            if len(rows) <= 1:
                course_id_from_row = row.subject_id
                row.delete()
                course = models.Course.objects.get(pk=course_id_from_row)
                if course.teacher_id == user_id_from_row:
                    course.teacher_id = None
                    course.save()
                    return JsonResponse(
                        {'modified': True},
                        status=status.HTTP_200_OK)
                else:
                    return Response('OK!', status=status.HTTP_204_NO_CONTENT)
            else:
                row.delete()
                return Response('OK!', status=status.HTTP_204_NO_CONTENT)
        except IntegrityError:
            return Response(
                'Failed to remove role entry!',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create(self, request):
        subject_id = request.data['subject_id']
        user_id = request.data['user_id']
        role_id = request.data['role_id']
        subject = models.Course.objects.get(pk=subject_id)
        serializer = serializers.SubjectUserSerializerFull(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            if subject.teacher_id is None:
                subject.teacher_id = user_id
                subject.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(
                'Failed to add user for subject!',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValidationError:
            return Response(
                'Wrong data when adding user for subject!',
                status=status.HTTP_400_BAD_REQUEST)
        

    @action(detail=False, methods=['delete'])
    def remove_entries(self, request):
        subject_id = int(request.query_params.get('subject'))
        subject = models.Course.objects.get(pk=subject_id)
        user_id = int(request.query_params.get('user'))
        # delete all entries with user on the subject
        try:
            models.SubjectUser.objects.filter(
                subject_id=subject_id,
                user_id=user_id
            ).delete()
            if subject.teacher_id == user_id:
                subject.teacher_id = None
                subject.save()
                return JsonResponse(
                    {'modified': True},
                    status=status.HTTP_200_OK)
        except IntegrityError:
            return Response(
                'Failed to remove entries!',
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response('OK!', status=status.HTTP_204_NO_CONTENT)


class UserSubjectRoleViewSet(ModelViewSet):
    queryset = models.UserSubjectRole.objects.all()
    serializer_class = serializers.UserSubjectRoleSerializer