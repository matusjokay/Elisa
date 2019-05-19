import os

from django.core.management.base import BaseCommand
from django.db import connection, utils

import fei.admin as resources
from django_tenants.utils import get_tenant_model


def get_schema(schema_name):
    try:
        version = get_tenant_model().objects.get(name=schema_name)
    except utils.DatabaseError:
        raise ValueError("Database error.")
    except get_tenant_model().DoesNotExist:
        raise ValueError("Schema '%s' does not exists." % schema_name)
    return version


class Command(BaseCommand):
    help = 'Imports FEI data from specified directory'
    # Order sensitive because of foreign keys.

    resource_mapping = [
        ('groups', resources.GroupResource()),
        ('departments', resources.DepartmentResource()),
        ('studytypes', resources.StudyTypeResource()),
        ('subjects', resources.CourseResource()),
        ('subjects_studytypes', resources.SubjectStudyTypeResource()),
        ('equipment', resources.EquipmentResource()),
        ('faculties', resources.FacultyResource()),
        ('roomtypes', resources.RoomCategoryResource()),
        ('rooms', resources.RoomResource()),
        ('room_equipment', resources.RoomEquipmentResource()),
        ('users', resources.UserResource()),
        ('subjects_users', resources.SubjectUserResource()),
        ('users_departments', resources.UserDepartmentResource()),
        ('users_groups', resources.UserGroupResource()),
    ]

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where files will be exported')
        parser.add_argument('schema_name', type=str, help='Database schema name for export')

    def handle(self, *args, **options):
        connection.set_schema_to_public()
        schema_name = options['schema_name']
        connection.set_tenant(get_schema(schema_name))

        for name, resource in self.resource_mapping:
            filename = name + '_export.csv'
            with open(os.path.join(options['directory'], filename), encoding="utf-8", mode='w') as outfile:
                dataset = resource.export()
                print("Exporting %s" % name)
                outfile.write(dataset.export('csv'))
