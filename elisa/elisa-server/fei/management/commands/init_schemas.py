import os
import requests
import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import connection, utils

from django_tenants.utils import get_tenant_model

import tablib
import fei.admin as resources
from fei.serializers import VersionSerializer
from fei.models import Version
from school.models import ActivityCategory

URLlogin = 'https://localhost:8000/login/'
URLversions = 'https://localhost:8000/versions/'

def get_schema(schema_name):
    try:
        version = get_tenant_model().objects.get(schema_name=schema_name)
    except utils.DatabaseError:
        raise ValueError("Database error.")
    except get_tenant_model().DoesNotExist:
        raise ValueError("Schema '%s' does not exists." % schema_name)
    return version

# trying to make a command that will create schemas and fill up 
# table (periods) in public schema
class Command(BaseCommand):
    help = 'Create schemas based on semesters and their data'

    def add_arguments(self, parser):
        parser.add_argument('directory', type=str, help='Directory where import files are located')
        parser.add_argument('username', type=str, help='Username for login to obtain token pair')
        parser.add_argument('pwd', type=str, help='Password')

    def handle(self, *args, **options):
        # returns the list of subjects for each version
        versions = os.listdir(os.path.join(options['directory'] + '/SUBJECTS'))
        r = requests.post(URLlogin, data=dict({'username': options['username'], 'password': options['pwd']}), verify=False)
        if r.status_code == 200:
            response_data = json.loads(r.text)
        else:
            raise Exception("Fetching access token failed.")
        header_bearer = response_data['access']
        for version_name in versions:
            headers = { 'Authorization': 'Bearer ' + header_bearer }
            Dict = {'name': version_name}
            r = requests.post(URLversions, headers=headers, data=Dict, verify=False)
            if r.status_code == 400:
                print(f"Schema -> {version_name} failed to be created. \nREASON: {r.text}")
            elif r.status_code == 200 or r.status_code == 201:                    
                if r.reason == 'Created':
                    print(f"Schema -> {version_name} is successfully created!")
        print('Created all schemas based on these versions')
        print(versions)