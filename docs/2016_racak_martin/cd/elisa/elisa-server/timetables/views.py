import django_filters
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import models, serializers


class TimetableViewSet(NestedViewSetMixin, ModelViewSet):
    """
    API endpoint that allows timetables to be viewed or edited.
    """
    queryset = models.Timetable.objects.all()
    serializer_class = serializers.TimetableSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'date_start', 'date_end')


class EventFilter(FilterSet):
    min_duration = django_filters.NumberFilter(
        name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(
        name='duration', lookup_expr='lte')
    week = django_filters.CharFilter(name='weeks', lookup_expr='contains')

    class Meta:
        model = models.Event
        fields = ['room', 'day', 'week', 'min_duration', 'max_duration']


class EventViewSet(NestedViewSetMixin, ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """
    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = EventFilter
