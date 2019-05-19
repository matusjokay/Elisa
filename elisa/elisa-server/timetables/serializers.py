from django.db import transaction
from django.db.models import Q
from psycopg2.extras import NumericRange
from rest_framework import serializers

from . import models
from school.models import Activity
from school.serializers import ActivitySerializer


def get_major_version(user, default):
    try:
        query = Q(owner=user) & Q(status=models.Timetable.WORK_IN_PROGRESS)
        return models.Timetable.objects.filter(query).latest('updated_at').major_version
    except models.Timetable.DoesNotExist:
        return default


def get_minor_version(user, default):
    try:
        query = Q(owner=user) & Q(status=models.Timetable.WORK_IN_PROGRESS)
        return models.Timetable.objects.filter(query).latest('updated_at').minor_version + 1
    except models.Timetable.DoesNotExist:
        return default


class TimetableSerializer(serializers.ModelSerializer):
    major_version = serializers.IntegerField(read_only=True)
    minor_version = serializers.IntegerField(read_only=True)
    owner = serializers.PrimaryKeyRelatedField(read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        major_version = get_major_version(user, 1)
        minor_version = get_minor_version(user, 0)

        timetable = models.Timetable(name=validated_data['name'], major_version=major_version,
                                     minor_version=minor_version, owner=user)
        timetable.save()
        return timetable

    class Meta:
        model = models.Timetable
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=True)

    def update(self, instance, validated_data):
        # TODO dohodnut s FE
        pass

    class Meta:
        model = models.Event
        fields = '__all__'


class EventSerializerPost(serializers.ModelSerializer):
    activity = ActivitySerializer(read_only=False)

    @transaction.atomic
    def create(self, validated_data):
        act = Activity(category=validated_data["activity"]["category"])
        act.save()
        act.courses.set(validated_data["activity"]["courses"])

        timetable = validated_data["timetable"]
        if timetable.status == models.Timetable.NEW:
            timetable.start_work()
            timetable.save()

        r = NumericRange(validated_data["duration"]["start"], validated_data["duration"]["end"])
        event = models.Event(day=validated_data["day"], duration=r, activity=act,
                             timetable=timetable, teacher=validated_data["teacher"])
        event.save()

        event.rooms.add(*validated_data["rooms"])
        event.groups.add(*validated_data["groups"])
        return event

    class Meta:
        model = models.Event
        fields = '__all__'


class CollisionSerializerPost(serializers.ModelSerializer):
    count = serializers.IntegerField(read_only=True)

    @transaction.atomic
    def create(self, validated_data):
        timetable = validated_data["timetable"]
        kwargs = {
            "status": validated_data["status"],
            "type": validated_data["type"],
            "timetable": timetable,
            "count": len(validated_data['events'])
        }

        collision = models.Collision(**kwargs)
        collision.save()

        collision.events.add(*validated_data["events"])
        return collision

    class Meta:
        model = models.Collision
        fields = '__all__'


class CollisionSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        # TODO dohodnut s FE
        pass

    class Meta:
        model = models.Collision
        fields = '__all__'

