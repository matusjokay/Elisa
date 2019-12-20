from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django_fsm import transition, FSMField
from django_tenants.models import TenantMixin, DomainMixin


class AppUserManager(UserManager):
    pass


class AppUser(AbstractUser):
    id = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title_before = models.CharField(max_length=32, blank=True, default='')
    title_after = models.CharField(max_length=32, blank=True, default='')
    objects = AppUserManager()

    def has_role(self, role):
        """
        Return True if the user is in specified group by role.
        """
        return self.groups.filter(name=role).exists()
    
    class Meta:
        db_table = u'"public\".\"fei_appuser"'
        ordering = ['id']

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
