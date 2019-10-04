from rest_framework.serializers import ModelSerializer

from . import models


class TimetableSerializer(ModelSerializer):
    class Meta:
        model = models.Timetable
        fields = '__all__'


class EventSerializer(ModelSerializer):
    class Meta:
        model = models.Event
        fields = '__all__'
