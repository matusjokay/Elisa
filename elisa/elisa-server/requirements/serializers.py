from django.db import transaction
from rest_framework import serializers
from fei.models import AppUser
from fei.serializers import UserSerializerCourse
from timetables.models import Comment
from . import models
import datetime


class RequirementSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = models.Requirement
        fields = ('id', 'comments')


class RequirementEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RequirementEvent
        fields = ('id', 'start', 'end', 'event_type', 'day', 'room', 'course')


class CommentSerializer(serializers.ModelSerializer):
    comment_by = UserSerializerCourse(read_only=True)
    comment_by_id = serializers.PrimaryKeyRelatedField(
        queryset=AppUser.objects.all(),
        source='comment_by',
        write_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'type', 'text',
                  'created_at', 'comment_by', 'comment_by_id')


class RequirementSerializer(serializers.ModelSerializer):
    events = RequirementEventSerializer(many=True)
    comments = CommentSerializer(many=True)
    teacher = UserSerializerCourse(read_only=True)
    created_by = UserSerializerCourse(read_only=True)

    class Meta:
        model = models.Requirement
        fields = '__all__'


class RequirementSerializerPost(serializers.ModelSerializer):
    events = RequirementEventSerializer(many=True)
    # created_by = None
    comments = CommentSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        created_by = validated_data.pop('created_by')
        teacher = validated_data.pop('teacher')
        requirement_type = validated_data.pop('requirement_type')
        status = validated_data.pop('status')
        for_department = validated_data.pop('for_department')
        teacher_type = validated_data.pop('teacher_type')

        kwargs = {
            'created_by': created_by,
            'teacher': teacher,
            'requirement_type': requirement_type,
            'for_department': for_department,
            'teacher_type': teacher_type,
            'status': status
        }

        req = models.Requirement.objects.create(**kwargs)

        events = validated_data.pop('events')
        for event in events:
            kwargs = {
                'day': event['day'],
                'start': event['start'],
                'end': event['end'],
                'event_type': event['event_type'],
                'room': event['room'],
                'course': event['course'],
                'content_object': req
            }
            obj = models.RequirementEvent.objects.create(**kwargs)

        comments = validated_data.pop('comments')
        for comment in comments:
            kwargs = {
                'text': comment['text'],
                'type': comment['type'],
                'comment_by': comment['comment_by'],
                'content_object': req
            }
            obj = models.Comment.objects.create(**kwargs)

        return req

    class Meta:
        model = models.Requirement
        fields = '__all__'


class RequirementSerializerPut(serializers.ModelSerializer):
    events = RequirementEventSerializer(many=True)
    # created_by = None
    comments = CommentSerializer(many=True)

    @transaction.atomic
    def update(self, instance, validated_data):
        instance.events.all().delete()
        instance.comments.all().delete()

        events = validated_data.pop('events')
        for event in events:
            kwargs = {
                'day': event['day'],
                'start': event['start'],
                'end': event['end'],
                'event_type': event['event_type'],
                'room': event['room'],
                'course': event['course'],
                'content_object': instance
            }
            obj = models.RequirementEvent.objects.create(**kwargs)

        comments = validated_data.pop('comments')
        for comment in comments:
            kwargs = {
                'text': comment['text'],
                'type': comment['type'],
                'comment_by': comment['comment_by'],
                'content_object': instance
            }
            obj = models.Comment.objects.create(**kwargs)
        instance.last_updated = datetime.datetime.utcnow()
        instance.save()
        return instance

    class Meta:
        model = models.Requirement
        fields = '__all__'
