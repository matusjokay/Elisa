import os
import csv
import time
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
        ('users.csv', resources.UserResource()),
        ('departments.csv', resources.DepartmentResource()),
        ('periods.csv', resources.PeriodResource())
    ]

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where to get csv data to initialize initial to the database.')

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
        # insert initial data
        self.insert_data(options['directory'])

    def insert_data(self, directory):
        # connection.set_schema_to_public()
        schema = get_tenant_model().objects.get(schema_name='public')
        connection.set_tenant(schema)
        for csvFile, resource in self.resource_mapping:
            self.stdout.write(f"Opening {csvFile}...")
            with open(os.path.join(directory, csvFile), newline='', encoding="utf-8") as infile:
                reader = csv.DictReader(infile, delimiter=',', quotechar='"')
                data = tablib.Dataset()
                data.headers = reader.fieldnames
                for row in reader:
                        data.append(row.values())
            infile.close()
            dataset = data
            self.stdout.write(f"Importing {csvFile}...")
            # resource.import_data(dataset, dry_run=True)
            start_time = time.time()
            resource.import_data(dataset, raise_errors=True, use_transactions=True)
            end_time = time.time() - start_time
            self.stdout.write(f"Done Importing {csvFile} and it took {end_time} seconds!")

