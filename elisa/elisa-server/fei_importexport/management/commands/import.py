import os

from django.core.management.base import BaseCommand
from django.db import connection, utils

from django_tenants.utils import get_tenant_model

import tablib
import fei.admin as resources


def get_schema(schema_name):
    try:
        version = get_tenant_model().objects.get(schema_name=schema_name)
    except utils.DatabaseError:
        raise ValueError("Database error.")
    except get_tenant_model().DoesNotExist:
        raise ValueError("Schema '%s' does not exists." % schema_name)
    return version


class Command(BaseCommand):
    help = 'Imports FEI data from specified directory and schema'
    # Order sensitive because of foreign keys.

    resource_mapping = [
        ('groups.csv', resources.GroupResource()),
        ('departments.csv', resources.DepartmentResource()),
        ('studytypes.csv', resources.StudyTypeResource()),
        ('subjects.csv', resources.CourseResource()),
        ('subjects_studytypes.csv', resources.SubjectStudyTypeResource()),
        ('equipment.csv', resources.EquipmentResource()),
        ('faculties.csv', resources.FacultyResource()),
        ('roomtypes.csv', resources.RoomCategoryResource()),
        ('rooms.csv', resources.RoomResource()),
        ('room_equipment.csv', resources.RoomEquipmentResource()),
        ('users.csv', resources.UserResource()),
        ('subjects_users.csv', resources.SubjectUserResource()),
        ('users_departments.csv', resources.UserDepartmentResource()),
        ('users_groups.csv', resources.UserGroupResource()),
    ]

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where import files are located')
        parser.add_argument('schema_name', type=str, help='Database schema name for import')

    def handle(self, *args, **options):
        connection.set_schema_to_public()
        schema_name = options['schema_name']
        connection.set_tenant(get_schema(schema_name))

        for csv, resource in self.resource_mapping:
            with open(os.path.join(options['directory'], csv), encoding="utf-8") as infile:
                data = infile.read()
            dataset = tablib.Dataset().load(data)

            # In case of subject study types we parse subject hours from 3/1 into two separate columns
            if csv == 'subjects_studytypes.csv':
                data = tablib.Dataset()
                data.headers = ('id', 'subject', 'type', 'lecture_hours', 'practice_hours')

                for (stid, subject, study_type, times) in dataset:
                    hrs = times.split("/")
                    data.append((stid, subject, study_type, hrs[0], hrs[1]))

                dataset = data

            print("Importing %s" % csv)
            resource.import_data(dataset, raise_errors=True, use_transactions=True)
