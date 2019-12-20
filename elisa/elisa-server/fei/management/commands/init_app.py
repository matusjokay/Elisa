import os
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django_tenants.utils import get_tenant_model
from django.db import connection, utils, IntegrityError
import tablib
from fei.models import Version
import fei.admin as resources


class Command(BaseCommand):
    help = 'Command to initialize app.'
    stealth_options = ('stdin',)

    resource_mapping = [
        ('users.csv', resources.UserResource())
    ]

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where import files are located')

    def handle(self, *args, **options):
        error = None
        for group in settings.GROUPS:
            self.stdout.write(self.style.SUCCESS('Creating group %s.' % group))
            new_group = Group.objects.get_or_create(name=group)

        self.stdout.write("Groups count: " + str(Group.objects.all().count()))

        self.stdout.write("ng tenant")

        tenant = Version(schema_name='public', name='public')
        try:
            tenant.save()
        except IntegrityError as e:
            error = True
            self.stdout.write("Schema probably exists")
        if error is None:
            self.stdout.write("Tenant initialized")
        self.insert_users(options['directory'])

    def insert_users(self, directory):
        connection.set_schema_to_public()
        schema = get_tenant_model().objects.get(schema_name='public')
        connection.set_tenant(schema)
        for csv, resource in self.resource_mapping:
            self.stdout.write(f"Opening {csv}...")
            with open(os.path.join(directory, csv), encoding="utf-8") as infile:
                data = infile.read()
            dataset = tablib.Dataset().load(data)
            self.stdout.write(f"Importing {csv}...")
            resource.import_data(dataset, raise_errors=True, use_transactions=True)
            self.stdout.write(f"Done Importing {csv}")

