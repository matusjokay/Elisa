from django.conf import settings
from django.db.models import Q

from django_filters import NumberFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet
from django_fsm import TransitionNotAllowed
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework_extensions.mixins import NestedViewSetMixin

from authentication.permissions import IsMainTimetableCreator, IsLocalTimetableCreator, IsTeacher
from . import models, serializers


class TimetableViewSet(NestedViewSetMixin, ModelViewSet):
    """
    API endpoint that allows timetables to be viewed or edited.
    """

    serializer_class = serializers.TimetableSerializer
    filter_backends = (OrderingFilter,)
    ordering_fields = ('name', 'updated_at')

    def get_queryset(self):
        timetables = []
        if self.request.user.is_anonymous:
            return timetables

        try:
            if self.request.user.has_role(settings.MAIN_TIMETABLE_CREATOR):
                # looking for timetables owned by user and timetables ready for
                # merge from local timetable creators
                timetables = models.Timetable.objects.filter(
                    Q(owner=self.request.user) | Q(status=models.Timetable.READY_FOR_MERGE))
            if self.request.user.has_role(settings.LOCAL_TIMETABLE_CREATOR):
                # looking for timetables owned by user
                timetables = models.Timetable.objects.filter(
                    owner=self.request.user)
            if self.request.user.has_role(settings.TEACHER):
                timetables = models.Timetable.objects.filter(
                    status=models.Timetable.PUBLISHED_FOR_TEACHERS) .latest('updated_at')
        except models.Timetable.DoesNotExist as e:
            print("No timetable found for users %s" % self.request.user.id)

        return timetables

    """
    API endpoint that returns latest timetable version owned by user and sorted by updated_at
    """
    @action(detail=False, methods=['get'])
    def latest(self, request):
        timetable = None
        if request.user.has_role(settings.MAIN_TIMETABLE_CREATOR) \
                or request.user.has_role(settings.LOCAL_TIMETABLE_CREATOR):
            timetable = models.Timetable.objects.filter(
                owner=request.user).latest('updated_at')
        elif request.user.has_role(settings.TEACHER):
            timetable = models.Timetable.objects.filter(
                status=models.Timetable.PUBLISHED_FOR_TEACHERS) .latest('updated_at')

        if timetable is not None:
            serializer = serializers.TimetableSerializer(timetable)
            return Response(serializer.data)

        return Response("No latest version", status=404)

    # TODO merge methods below to one, with changing method called on
    # timetable instance if possible
    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsMainTimetableCreator])
    def publish(self, request, pk=None):
        """
        Set timetable status to published for everyone
        """
        try:
            timetable = models.Timetable.objects.get(id=pk)
            timetable.publish_public()
            timetable.save()
        except models.Timetable.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsMainTimetableCreator])
    def publish_teachers(self, request, pk=None):
        """
        Set timetable status to published for teachers
        """
        try:
            timetable = models.Timetable.objects.get(id=pk)
            timetable.publish_teachers()
            timetable.save()
        except models.Timetable.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsLocalTimetableCreator])
    def merge(self, request, pk=None):
        """
        Set timetable status to ready for merge
        """
        try:
            timetable = models.Timetable.objects.get(id=pk)
            timetable.merge()
            timetable.save()
        except models.Timetable.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsMainTimetableCreator])
    def merge_done(self, request, pk=None):
        """
        Set timetable status as merged
        """
        try:
            timetable = models.Timetable.objects.get(id=pk)
            timetable.merge_done()
            timetable.save()
        except models.Timetable.DoesNotExist:
            return Response("Timetable not found", status=404)
        except TransitionNotAllowed:
            return Response("Transition is not allowed.", status=400)

        return Response(status=200)


class EventFilter(FilterSet):
    min_duration = NumberFilter(
        field_name='duration', lookup_expr='gte')
    max_duration = NumberFilter(
        field_name='duration', lookup_expr='lte')
    # week = django_filters.CharFilter(field_name='weeks', lookup_expr='contains')

    class Meta:
        model = models.Event
        fields = ['rooms', 'day', 'min_duration', 'max_duration']


class EventViewSet(NestedViewSetMixin, ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.update({'many': True})
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.EventSerializerPost
        return serializers.EventSerializer

    queryset = models.Event.objects.all()
    serializer_class = serializers.EventSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = EventFilter


class CollisionFilter(FilterSet):
    # min_duration = django_filters.NumberFilter(
    #     field_name='duration', lookup_expr='gte')
    # max_duration = django_filters.NumberFilter(
    #     field_name='duration', lookup_expr='lte')
    # week = django_filters.CharFilter(field_name='weeks', lookup_expr='contains')

    class Meta:
        model = models.Collision
        fields = ('type', 'status')


class CollisionViewSet(NestedViewSetMixin, ModelViewSet):
    """
    API endpoint that allows collisions to be viewed or edited.
    """

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.update({'many': True})
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CollisionSerializerPost
        return serializers.CollisionSerializer

    queryset = models.Collision.objects.all()
    serializer_class = serializers.CollisionSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = CollisionFilter
