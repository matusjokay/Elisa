from django.contrib.postgres.fields import IntegerRangeField
from django.core.validators import validate_comma_separated_integer_list
from django.db import models

from school.models import Activity, Room, Group


class Timetable(models.Model):
    name = models.CharField(max_length=300)
    date_start = models.DateField()
    date_end = models.DateField()
    # TODO timetable settings (period length, weeks, ...)

    class Meta:
        ordering = ['-date_start']


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

    activity = models.ForeignKey(Activity)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    # Interval of timetable periods (start, end).
    duration = IntegerRangeField()
    day = models.PositiveSmallIntegerField(choices=DAYS_OF_WEEK)
    # Comma separated list of week IDs, another option would be to
    # use bitfield.
    weeks = models.CharField(
        max_length=127, validators=[validate_comma_separated_integer_list])
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)
