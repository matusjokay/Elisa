from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now

from fei.models import AppUser
from timetables.models import Comment
from school.models import Course, Room


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
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    event_type = models.PositiveSmallIntegerField(choices=EVENT_TYPE)
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Requirement(models.Model):
    CREATED = 1
    EDITED = 2
    REJECTED = 3
    APPROVED = 4
    STATUS_TYPES = (
        (CREATED, 'Created'),
        (EDITED, 'Edited'),
        (REJECTED, 'Rejected'),
        (APPROVED, 'Approved'),)

    LECTURE = 1
    SEMINAR = 2
    REQUIREMENT_TYPES = (
        (LECTURE, 'Lecture'),
        (SEMINAR, 'Seminar'))
    created_by = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        related_name='created_by_requirement_set')
    teacher = models.ForeignKey(
        AppUser,
        on_delete=models.CASCADE,
        related_name='teacher_requirement_set')
    last_updated = models.DateTimeField(default=now, blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_TYPES)
    requirement_type = models.PositiveSmallIntegerField(
        choices=REQUIREMENT_TYPES)
    for_department = models.PositiveSmallIntegerField(null=True)
    teacher_type = models.PositiveSmallIntegerField(null=True)
    events = GenericRelation(RequirementEvent)
    comments = GenericRelation(Comment)
