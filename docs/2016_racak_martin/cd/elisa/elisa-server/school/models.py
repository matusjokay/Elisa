from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Group(MPTTModel):
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=30)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']


class Department(MPTTModel):
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=30)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='children',
        db_index=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class Course(models.Model):
    name = models.CharField(max_length=300)
    code = models.CharField(max_length=300)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)

    class Meta:
        ordering = ['name']


class Equipment(models.Model):
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class RoomCategory(models.Model):
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class Room(models.Model):
    name = models.CharField(max_length=300)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    category = models.ForeignKey(RoomCategory, on_delete=models.CASCADE)
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, blank=True, null=True)
    equipment = models.ManyToManyField(Equipment, through='RoomEquipment')

    class Meta:
        ordering = ['name']


class RoomEquipment(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    # equipment count
    count = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('room', 'equipment')


class ActivityCategory(models.Model):
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        ordering = ['name']


class Activity(models.Model):
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
