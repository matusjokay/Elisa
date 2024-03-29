import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from . import models, serializers


class GroupViewSet(ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('parent',)
    search_fields = ('name', 'abbr')


class DepartmentViewSet(ModelViewSet):
    """
    API endpoint that allows departments to be viewed or edited.
    """
    queryset = models.Department.objects.all()
    serializer_class = serializers.DepartmentSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filter_fields = ('parent',)
    search_fields = ('name', 'abbr')


class CourseViewSet(ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    """
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    filter_backends = (DjangoFilterBackend, SearchFilter, OrderingFilter)
    filter_fields = ('department',)
    search_fields = ('name', 'code')
    ordering_fields = ('name', 'code')


class EquipmentViewSet(ModelViewSet):
    """
    API endpoint that allows equipment to be viewed or edited.
    """
    queryset = models.Equipment.objects.all()
    serializer_class = serializers.EquipmentSerializer


class RoomCategoryViewSet(ModelViewSet):
    """
    API endpoint that allows room categories to be viewed or edited.
    """
    queryset = models.RoomCategory.objects.all()
    serializer_class = serializers.RoomCategorySerializer


class RoomFilter(FilterSet):
    min_capacity = django_filters.NumberFilter(
        name='capacity', lookup_expr='gte')
    max_capacity = django_filters.NumberFilter(
        name='capacity', lookup_expr='lte')
    category = django_filters.CharFilter(name='category__name')

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
    filter_class = RoomFilter
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
