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
    title_before = models.CharField(
        max_length=32, blank=True, null=True, default=None)
    title_after = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        default=None)
    access_id = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        default=None)
    objects = AppUserManager()

    """
    Return True if the user is in specified group by role
    """
    def has_role(self, role):
        return self.groups.filter(name=role).exists()

    """
    Creates the full name for user with all its academic 
    titles if he has them available
    """
    def construct_name(self):
        name = self.first_name + ' ' + self.last_name
        if self.title_before is not None:
            name = self.title_before + \
                self.first_name + ' ' + self.last_name
        if self.title_after is not None:
            name = self.first_name + ' ' + \
                self.last_name + ' ' + self.title_after
        if self.title_before is not None and self.title_after is not None:
            name = self.title_before + self.first_name + \
                ' ' + self.last_name + ' ' + self.title_after
        return name

    """
    Fetches id vales of users roles
    """
    def fetch_role_ids(self):
        groups_qs = self.groups.values_list(
            'id',
            flat=True)
        groups = list()
        for group in groups_qs:
            groups.append(group)
        return groups

    class Meta:
        db_table = u'"public\".\"fei_appuser"'
        ordering = ['id']


class Department(models.Model):
    name = models.CharField(max_length=300)
    abbr = models.CharField(max_length=30, blank=True, null=True)
    # parent should be a ForeignKey of its self BUT the data
    # from Oracle DB seems to have entries missing.
    # Uncomment when this issue will be resolved
    # parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    parent = models.IntegerField(null=True)

    class Meta:
        db_table = u'"public\".\"fei_department"'
        ordering = ['name']

    def __str__(self):
        return '{}'.format(self.name)


class UserDepartment(models.Model):
    # user = models.ForeignKey('fei.AppUser', on_delete=models.CASCADE)
    # department = models.ForeignKey('fei.Department', on_delete=models.CASCADE)
    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    employment = models.CharField(max_length=9, blank=True)


class Period(models.Model):
    # id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=300)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    # low value = oldest , higher = newest
    university_period = models.PositiveSmallIntegerField(null=True)
    # 1 is for WS , 2 is for SS
    academic_sequence = models.PositiveSmallIntegerField(null=True)
    previous_period = models.PositiveIntegerField(null=True)
    next_period = models.PositiveIntegerField(null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    active = models.BooleanField()

    class Meta:
        db_table = u'"public\".\"fei_period"'
        ordering = ['university_period']


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
    status = FSMField(
        max_length=6,
        choices=STATUSES,
        default=NEW,
        protected=True)
    auto_drop_schema = models.BooleanField(default=True)
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    last_updated = models.DateTimeField(
        default=None,
        null=True,
        blank=True)


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
