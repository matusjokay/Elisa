from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from fei.models import AppUser
from timetables.models import Comment
from school.models import Course


class RequirementEvent(models.Model):
    SUITABLE = 1
    UNSUITABLE = 2
    UNAVAILABLE = 3
    EVENT_TYPE = (
        (SUITABLE, 'Suitable'),
        (UNSUITABLE, 'Unsuitable'),
        (UNAVAILABLE, 'Unavailable'),)

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7
    DAYS_OF_WEEK = (
        (MONDAY, 'Monday'),
        (TUESDAY, 'Tuesday'),
        (WEDNESDAY, 'Wednesday'),
        (THURSDAY, 'Thursday'),
        (FRIDAY, 'Friday'),
        (SATURDAY, 'Saturday'),
        (SUNDAY, 'Sunday'),)

    start = models.CharField(max_length=8)
    end = models.CharField(max_length=8)
    type = models.PositiveSmallIntegerField(choices=EVENT_TYPE)
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Requirement(models.Model):
    created_by = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='created_by_requirement_set')
    teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE, related_name='teacher_requirement_set')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    events = GenericRelation(RequirementEvent)
    comments = GenericRelation(Comment)




