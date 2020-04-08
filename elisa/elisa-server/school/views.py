import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from . import models, serializers
from fei import models as fei_models


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
    serializer_class = serializers.SubjectUserSerializer

    @action(detail=False)
    def filter_by_role(self, request):
        if request.query_params.get('role_id') is None:
            queryset = models.SubjectUser.objects.all()
        else:
            role_id = int(request.query_params.get('role_id'))
            queryset = models.SubjectUser.objects.filter(role=role_id)
        serializer = serializers.SubjectUserSerializer(queryset, many=True)
        return Response(serializer.data)
