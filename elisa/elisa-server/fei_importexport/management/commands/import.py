import os

from django.core.management.base import BaseCommand
from django.db import connection, utils

from django_tenants.utils import get_tenant_model
from django_tenants.utils import schema_exists

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
        ('periods.csv', resources.PeriodResource()),
        ('subjects.csv', resources.CourseResource()),
        # ('studytypes.csv', resources.SubjectStudyTypeResource()),
        ('equipment.csv', resources.EquipmentResource()),
        ('roomtypes.csv', resources.RoomTypeResource()),
        ('rooms.csv', resources.RoomResource()),
        ('room_equipment.csv', resources.RoomEquipmentResource()),
        ('user_subject_role.csv', resources.UserSubjectRoleResource()),
        # ('users.csv', resources.UserResource()),
        ('subjects_users.csv', resources.SubjectUserResource()),
        ('users_departments.csv', resources.UserDepartmentResource()),
        ('form_of_study.csv', resources.FormOfStudyResource()),
        ('studytypes.csv', resources.StudyTypeResource()),
        ('users_groups.csv', resources.UserGroupResource()),
    ]

    role_map = {
        "student": 1,
        "garant": 2,
        "prednasajuci": 3,
        "cviciaci": 4,
        "skusajuci": 5,
        "administrator": 6,
        "tutor": 7
    }

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where import files are located')
        parser.add_argument('schema_name', type=str, help='Database schema name for import')

    def handle(self, *args, **options):
        connection.set_schema_to_public()
        schema_name = options['schema_name']
        if (schema_name == 'all'):
            versions = os.listdir(os.path.join(options['directory'] + '/SUBJECTS'))
            for schema in versions:
                if(schema_exists(schema)):
                    connection.set_tenant(get_schema(schema))
                    self.doImport(options, schema)
        else:                
            connection.set_tenant(get_schema(schema_name))
            self.doImport(options)

    def doImport(self, options, fromAllSchema=None):
        for csv, resource in self.resource_mapping:
            self.stdout.write(f"Opening {csv} for schema -> {options['schema_name']}") if fromAllSchema is None else self.stdout.write(f"Opening {csv} for schema -> {fromAllSchema}")
            # Nested folder for subjects of different periods
            if csv == 'subjects.csv':
                schema_filename = fromAllSchema if fromAllSchema is not None else options['schema_name']
                with open(os.path.join(options['directory'] + '/SUBJECTS/' + schema_filename, csv), encoding="utf-8") as infile:
                    data = infile.read()
                dataset = tablib.Dataset().load(data)
            else:
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
                
                if csv == 'subjects_users.csv' and options['directory'] == 'fei-data-new':
                    data = tablib.Dataset()
                    data.headers = ('id', 'subject', 'user', 'role')

                    for (id, subject, user, role) in dataset:
                        roles = role.split("/")
                        # remove empty roles from column
                        # roles = list(filter(None,roles))
                        role_id_from_text = self.role_map.get(roles[len(roles)-1])
                        data.append((id, subject, user, role_id_from_text))
                    
                    dataset = data

            self.stdout.write(f"Importing {csv} for schema -> {options['schema_name']}") if fromAllSchema is None else self.stdout.write(f"Importing {csv} for schema -> {fromAllSchema}")
            resource.import_data(dataset, raise_errors=True, use_transactions=True)
