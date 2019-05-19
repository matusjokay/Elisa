from django.core.validators import RegexValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from fei.models import AppUser

color_validator = RegexValidator(r'#[0-9a-fA-F]{6}', "Color has to be in hexadecimal format.")


class Group(MPTTModel):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=30, blank=True, null=True)
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
    abbr = models.CharField(max_length=30, blank=True, null=True)
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
    completion = models.CharField(max_length=16, null=True)

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
    name = models.CharField(max_length=300, unique=True)
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
    name_sk = models.CharField(max_length=300, unique=True)
    name_en = models.CharField(max_length=300, unique=True)
    color = models.CharField(max_length=7, null=True, validators=[color_validator])

    class Meta:
        ordering = ['id']


class Activity(models.Model):
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)


class Faculty(models.Model):
    name = models.CharField(max_length=128)
    abbr = models.CharField(max_length=16)


class StudyType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.name)


class UserGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    group_number = models.CharField(max_length=32, blank=True)
    study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE, null=True)


class UserDepartment(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    employment = models.PositiveSmallIntegerField(blank=True, null=True)


class SubjectUser(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Course, on_delete=models.CASCADE)
    role = models.PositiveSmallIntegerField()


class SubjectStudyType(models.Model):
    type = models.ForeignKey(StudyType, on_delete=models.CASCADE)
    subject = models.ForeignKey(Course, on_delete=models.CASCADE)
    lecture_hours = models.PositiveSmallIntegerField()
    practice_hours = models.PositiveSmallIntegerField()
