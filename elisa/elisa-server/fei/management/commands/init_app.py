from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from fei.models import Version


class Command(BaseCommand):
    help = 'Command to initialize app.'
    stealth_options = ('stdin',)

    def handle(self, *args, **options):
        for group in settings.GROUPS:
            self.stdout.write(self.style.SUCCESS('Creating group %s.' % group))
            new_group = Group.objects.get_or_create(name=group)

        self.stdout.write("Groups count: " + str(Group.objects.all().count()))

        self.stdout.write("Initializing tenant")

        tenant = Version(schema_name='public', name='public')
        tenant.save()
        self.stdout.write("Tenant initialized")


