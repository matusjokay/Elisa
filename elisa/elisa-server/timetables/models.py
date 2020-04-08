from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import IntegerRangeField
# from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from django_fsm import transition, FSMField

from school.models import Activity, Room, Group


class Timetable(models.Model):
    NEW = "NEW"
    WORK_IN_PROGRESS = "WIP"
    READY_FOR_MERGE = "RFM"
    MERGED = "MER"
    PUBLISHED_FOR_TEACHERS = "PFT"
    PUBLISH_PUBLIC = "PPV"
    STATUSES = (
        (NEW, 'New'),
        (WORK_IN_PROGRESS, 'Work in progress'),
        (READY_FOR_MERGE, 'Ready for merge'),
        (MERGED, 'Merged'),
        (PUBLISHED_FOR_TEACHERS, 'Published for teachers'),
        (PUBLISH_PUBLIC, 'Publish public version'),)

    name = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = FSMField(
        max_length=3,
        choices=STATUSES,
        default=NEW,
        protected=True)
    major_version = models.PositiveSmallIntegerField()
    minor_version = models.PositiveSmallIntegerField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    class Meta:
        ordering = ['-updated_at']

    @transition(field=status, source=NEW, target=WORK_IN_PROGRESS)
    def start_work(self):
        print("Starting work")

    @transition(field=status, source=WORK_IN_PROGRESS, target=READY_FOR_MERGE)
    def merge(self):
        print("Ready for merge")

    @transition(field=status, source=READY_FOR_MERGE, target=MERGED)
    def merge_done(self):
        print("Merged")

    @transition(
        field=status,
        source=WORK_IN_PROGRESS,
        target=PUBLISHED_FOR_TEACHERS)
    def publish_teachers(self):
        print("Publish working version for teachers")

    @transition(
        field=status,
        source=PUBLISHED_FOR_TEACHERS,
        target=PUBLISH_PUBLIC)
    def publish_public(self):
        print("Publish for everyone")


class Event(models.Model):
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
        (SUNDAY, 'Sunday'), )

    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    rooms = models.ManyToManyField(Room)
    # Interval of timetable periods (start, end).
    duration = IntegerRangeField()
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    # Comma separated list of week IDs, another option would be to
    # use bitfield.
    # -- not used now
    # weeks = models.CharField(
    #     max_length=127, validators=[validate_comma_separated_integer_list])
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Collision(models.Model):
    WARNING = 1
    ERROR = 2
    COLLISION_STATUSES = (
        (WARNING, 'Warning'),
        (ERROR, 'Error'),)
    TEACHER_COLLISION = 1
    ROOM_COLLISION = 2
    GROUP_COLLISION = 2
    COLLISION_TYPES = (
        (TEACHER_COLLISION, 'Collision between teachers'),
        (ROOM_COLLISION, 'Collision between rooms'),
        (GROUP_COLLISION, 'Collision between groups'),)

    status = models.PositiveSmallIntegerField(choices=COLLISION_STATUSES)
    type = models.PositiveSmallIntegerField(choices=COLLISION_TYPES)
    count = models.PositiveSmallIntegerField()
    events = models.ManyToManyField(to=Event)
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{}: status= {}, type={}'.format(
            self.id, self.status, self.type)


class Comment(models.Model):
    TEACHER = 1
    TIMETABLE_CREATOR = 2
    COMMENT_TYPE = (
        (TEACHER, 'Teacher comment'),
        (TIMETABLE_CREATOR, 'Timetable creator comment'),)

    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.PositiveSmallIntegerField(choices=COMMENT_TYPE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return '{}'.format(self.text)
