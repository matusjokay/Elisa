from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django_fsm import transition, FSMField
from django_tenants.models import TenantMixin, DomainMixin


class AppUserManager(UserManager):
    pass


class AppUser(AbstractUser):
    # id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title_before = models.CharField(max_length=32, blank=True, null=True, default=None)
    title_after = models.CharField(max_length=32, blank=True, null=True, default=None)
    objects = AppUserManager()

    def has_role(self, role):
        """
        Return True if the user is in specified group by role.
        """
        return self.groups.filter(name=role).exists()
    
    class Meta:
        db_table = u'"public\".\"fei_appuser"'
        ordering = ['id']
        

class Department(models.Model):
    # id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=30, blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = u'"public\".\"fei_department"'
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)

class Period(models.Model):
    # id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    # low value = oldest , higher = newest
    university_period = models.PositiveSmallIntegerField(null=True)
    # 1 is for WS , 2 is for SS
    academic_sequence = models.PositiveSmallIntegerField(null=True)
    # previous_period = models.ForeignKey('self', related_name='previous', on_delete=models.CASCADE, null=True)
    # next_period = models.ForeignKey('self', related_name='next', on_delete=models.CASCADE, null=True)
    previous_period = models.PositiveIntegerField(null=True)
    next_period = models.PositiveIntegerField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField()

    class Meta:
        db_table = u'"public\".\"fei_period"'
        ordering = ['university_period']

# class FacultyCourse(models.Model):
#     # id = models.BigAutoField(primary_key=True)
#     period = models.ForeignKey(Period, on_delete=models.CASCADE, null=True)
#     # period = models.CharField(max_length=100)
#     department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)
#     teacher = models.ForeignKey(AppUser, on_delete=models.CASCADE, null=True)
#     code = models.CharField(max_length=300, null=True)
#     name = models.CharField(max_length=300, null=True)
#     completion = models.CharField(max_length=16, null=True)
#     credits = models.SmallIntegerField(null=True)

#     class Meta:
#         db_table = u'"public\".\"fei_faculty_course"'
#         ordering = ['period']

# class UserSubjectRole(models.Model):
#     name = models.CharField(max_length=32)

#     def __str__(self):
#         return '{}'.format(self.name)

#     class Meta:
#         db_table = u'"public\".\"fei_user_subject_role"'
#         ordering = ['name']

# class SubjectUser(models.Model):
#     user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
#     subject = models.ForeignKey(FacultyCourse, on_delete=models.CASCADE)
#     # role = models.PositiveSmallIntegerField()
#     role = models.ForeignKey(UserSubjectRole, on_delete=models.CASCADE)

#     class Meta:
#         db_table = u'"public\".\"fei_subject_user"'
#         ordering = ['user']

class Version(TenantMixin):
    NEW = "NEW"
    WORK_IN_PROGRESS = "WIP"
    PUBLIC = "PUBLIC"
    HIDDEN = "HIDDEN"
    STATUSES = (
        (NEW, 'New'),
        (WORK_IN_PROGRESS, 'Work in progress'),
        (PUBLIC, 'Published'),
        (HIDDEN, 'Hidden'),)
    name = models.CharField(max_length=100)
    status = FSMField(max_length=6, choices=STATUSES, default=NEW, protected=True)
    auto_drop_schema = models.BooleanField(default=True)

    @transition(field=status, source=NEW, target=WORK_IN_PROGRESS)
    def start_work(self):
        print("Starting work")

    @transition(field=status, source=WORK_IN_PROGRESS, target=PUBLIC)
    def publish(self):
        print("Published")

    @transition(field=status, source=PUBLIC, target=HIDDEN)
    def hide(self):
        print("Hidden")


class Domain(DomainMixin):
    pass
