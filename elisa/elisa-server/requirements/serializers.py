from django.db import transaction
from rest_framework import serializers
from fei.models import AppUser
from timetables.models import Comment
from . import models


class RequirementSerializerSimple(serializers.ModelSerializer):
    class Meta:
        model = models.Requirement
        fields = ('id', 'comments')


class RequirementEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.RequirementEvent
        fields = ('id', 'start', 'end', 'type', 'day')


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'type', 'text')


class RequirementSerializer(serializers.ModelSerializer):
    events = RequirementEventSerializer(many=True)
    comments = CommentSerializer(many=True)

    class Meta:
        model = models.Requirement
        fields = '__all__'


class RequirementSerializerPost(serializers.ModelSerializer):
    events = RequirementEventSerializer(many=True)
    created_by = None
    comments = CommentSerializer(many=True)

    @transaction.atomic
    def create(self, validated_data):
        created_by = AppUser.objects.get(id=self.context['request'].user.id)
        teacher = AppUser.objects.get(id=self.context['request'].data['teacher'])

        if 'course' in self.context['request'].data:
            req = models.Requirement(created_by=created_by, teacher=teacher,
                                 course_id=self.context['request'].data['course'])
        else:
            req = models.Requirement(created_by=created_by, teacher=teacher,
                                 course=None)

        req.save()

        events = validated_data.pop('events')
        for event in events:
            e = models.RequirementEvent(day=event['day'], start=event['start'], end=event['end'], type=event['type'],
                                        content_object=req)
            e.save()

        comments = validated_data.pop('comments')
        for comment in comments:
            c = Comment(text=comment['text'], type=comment['type'], content_object=req)
            c.save()

        return req

    class Meta:
        model = models.Requirement
        exclude = ('created_by',)
