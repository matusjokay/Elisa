import os

import tablib
from django.core.management.base import BaseCommand

import fei.admin as resources


class Command(BaseCommand):
    help = 'Imports FEI data from specified directory'
    # Order sensitive because of foreign keys.
    resource_mapping = [
        ('groups.csv', resources.GroupResource()),
        ('departments.csv', resources.DepartmentResource()),
        ('equipment.csv', resources.EquipmentResource()),
        ('roomtypes.csv', resources.RoomCategoryResource()),
        ('rooms.csv', resources.RoomResource()),
        ('room_equipment.csv', resources.RoomEquipmentResource()),
        ('subjects.csv', resources.CourseResource())
    ]

    def add_arguments(self, parser):
        parser.add_argument('directory')

    def handle(self, *args, **options):
        for csv, resource in self.resource_mapping:
            with open(os.path.join(options['directory'], csv)) as infile:
                data = infile.read()
            dataset = tablib.Dataset().load(data)
            resource.import_data(
                dataset, raise_errors=True, use_transactions=True)
