from django.core.validators import RegexValidator
from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from fei.models import AppUser

color_validator = RegexValidator(r'#[0-9a-fA-F]{6}', "Color has to be in hexadecimal format.")

# if primary_key = True then django wont autoincrement id
# by default if not specified then it will autoincrement

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

    def __str__(self):
        return '{}'.format(self.name)

# TODO: this class probably should be in public schema 
# as a reference for all other tenants
class Period(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    # low value = oldest , higher = newest
    university_period = models.PositiveSmallIntegerField()
    # 1 is for WS , 2 is for SS
    academic_sequence = models.PositiveSmallIntegerField()
    previous_period = models.ForeignKey('self', related_name='previous', on_delete=models.CASCADE)
    next_period = models.ForeignKey('self', related_name='next', on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField()

    class MPTTMeta:
        order_insertion_by = ['university_period']

# class User(models.Model):
#     id = models.BigAutoField(primary_key=True)
#     username = models.CharField(max_length=100)
#     first_name = models.CharField(max_length=100)
#     last_name = models.CharField(max_length=100)
#     title_before = models.CharField(max_length=50)
#     title_after = models.CharField(max_length=50)

#     class Meta:
#         ordering = ['username']


class Course(models.Model):
    id = models.BigAutoField(primary_key=True)
    period_id = models.ForeignKey(Period, on_delete=models.CASCADE)
    period = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    code = models.CharField(max_length=300)
    name = models.CharField(max_length=300)
    completion = models.CharField(max_length=16, null=True)
    credits = models.SmallIntegerField()

    class Meta:
        ordering = ['name']


class Equipment(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class RoomType(models.Model):
    name = models.CharField(max_length=300, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class Room(models.Model):
    name = models.CharField(max_length=300, unique=True)
    capacity = models.PositiveIntegerField(blank=True, null=True)
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE)
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


# class Faculty(models.Model):
#     name = models.CharField(max_length=128)
#     abbr = models.CharField(max_length=16)


class StudyType(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.name)

class FormOfStudy(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.name)


class UserGroup(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    group_number = models.CharField(max_length=32, blank=True)
    form_of_study = models.ForeignKey(FormOfStudy, on_delete=models.CASCADE)
    study_type = models.ForeignKey(StudyType, on_delete=models.CASCADE, null=True)
    # form_of_study = models.CharField(max_length=7)


class UserDepartment(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    employment = models.CharField(max_length=9, blank=True)
    # employment = models.PositiveSmallIntegerField(blank=True, null=True)


class UserSubjectRole(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return '{}'.format(self.name)

class SubjectUser(models.Model):
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    subject = models.ForeignKey(Course, on_delete=models.CASCADE)
    # role = models.PositiveSmallIntegerField()
    role = models.ForeignKey(UserSubjectRole, on_delete=models.CASCADE)


# class SubjectStudyType(models.Model):
#     type = models.ForeignKey(StudyType, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Course, on_delete=models.CASCADE)
#     lecture_hours = models.PositiveSmallIntegerField()
#     practice_hours = models.PositiveSmallIntegerField()
