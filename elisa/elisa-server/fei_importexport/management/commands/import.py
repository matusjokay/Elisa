import os
import csv
from django.core.management.base import BaseCommand
from django.db import connection, utils
from django.db.models import Q
from django_tenants.utils import get_tenant_model
from django_tenants.utils import schema_exists

import tablib
import fei.admin as resources
import fei.models as fei_models
from school.models import Course


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
        ('users_departments.csv', resources.UserDepartmentResource()),
        ('groups.csv', resources.GroupResource()),
        ('subjects.csv', resources.CourseResource()),
        ('user_subject_role.csv', resources.UserSubjectRoleResource()),
        ('subjects_users.csv', resources.SubjectUserResource()),
        ('form_of_study.csv', resources.FormOfStudyResource()),
        ('studytypes.csv', resources.StudyTypeResource()),
        ('users_groups.csv', resources.UserGroupResource()),
        ('equipment.csv', resources.EquipmentResource()),
        ('roomtypes.csv', resources.RoomTypeResource()),
        ('rooms.csv', resources.RoomResource()),
        ('room_equipment.csv', resources.RoomEquipmentResource())
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
        schema_name = options['schema_name'].lower()
        if (schema_name == 'all'):
            versions = os.listdir(os.path.join(options['directory'] + '/SUBJECTS'))
            for schema in versions:
                if(schema_exists(schema)):
                    connection.set_tenant(get_schema(schema))
                    self.doImport(options, schema)
        else:                
            connection.set_tenant(get_schema(schema_name))
            self.doImport(options)
    
    def parse_roles(self, row):
        if '/' in row['role']:
            roles = row['role'].split('/')
        elif ',' in row['role']:
            roles = row['role'].split(',')
        else:
            roles = [row['role']]
        role_id_from_text = self.role_map.get(roles[len(roles)-1])
        row['role'] = role_id_from_text
        return row

    def get_filter_periods(self, schema_name):
        schema_split = schema_name.split('_')
        matching_year = schema_split[1] + "/" + schema_split[2]
        schema_name = schema_split[0] + " " + matching_year
        # for PHD subjects
        matching_year = matching_year + " - "
        query_periods = Q(name__icontains=schema_name) | Q(name__icontains=matching_year)
        period_ids = fei_models.Period.objects.filter(query_periods).values_list('id', flat=True) 
        return list(period_ids)

    def get_filter_subjects(self, period_ids):
        query_subjects = Q(period_id__in=period_ids)
        subject_ids = Course.objects.filter(query_subjects).values_list('id', flat=True)
        return list(subject_ids)

    def doImport(self, options, fromAllSchema=None):
        list_periods_ids = self.get_filter_periods(options['schema_name'])
        for csvFile, resource in self.resource_mapping:
            self.stdout.write(f"Opening {csvFile} for schema -> {options['schema_name']}") if fromAllSchema is None else self.stdout.write(f"Opening {csvFile} for schema -> {fromAllSchema}")
            # Nested folder for subjects of different periods
            if csvFile == 'subjects.csv':
                with open(os.path.join(options['directory'], csvFile), newline='', encoding="utf-8") as infile:
                    reader = csv.DictReader(infile, delimiter=',', quotechar='"')
                    data = tablib.Dataset()
                    data.headers = reader.fieldnames
                    for row in reader:
                        if int(row['period']) in list_periods_ids:
                            data.append(row.values())
                infile.close()
                dataset = data
            elif csvFile == 'subjects_users.csv':
                list_subject_ids = self.get_filter_subjects(list_periods_ids)
                with open(os.path.join(options['directory'], csvFile), encoding="utf-8") as infile:
                    reader = csv.DictReader(infile, delimiter=',', quotechar='"')
                    data = tablib.Dataset()
                    data.headers = reader.fieldnames
                    for row in reader:
                        if int(row['subject']) in list_subject_ids:
                            row = self.parse_roles(row)
                            data.append(row.values())
                infile.close()
                dataset = data
            else:
                with open(os.path.join(options['directory'], csvFile), encoding="utf-8") as infile:
                    data = infile.read()
                dataset = tablib.Dataset().load(data)
            self.stdout.write(f"Importing {csvFile} for schema -> {options['schema_name']}") if fromAllSchema is None else self.stdout.write(f"Importing {csvFile} for schema -> {fromAllSchema}")
            resource.import_data(dataset, raise_errors=True, use_transactions=True)
