import os
import requests
import urllib3
import json
from django.core.management import call_command
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
    
"""
This command is for creating schema and trying to import all
the data based on schema.
Arguments provied are login and schema name based on format
in the following manner -> ZS/LS_YYYY/YYYY
Where ZS/LS is either Winter/Summer semester schema
TODO: Calls requests based on the provided login therefore
a new implementation on the client is preffered.
"""
class Command(BaseCommand):
    help = 'Create schemas based on semesters and their data'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for login to obtain token pair')
        parser.add_argument('pwd', type=str, help='Password')
        parser.add_argument('schema_name', type=str, help='Schema to create in the database')

    def handle(self, *args, **options):
        # to hide unsecure requests warning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        version_name = options['schema_name']
        # call request to server to obtain access token
        r = requests.post(URLlogin, data=dict({'username': options['username'], 'password': options['pwd']}), verify=False)
        if r.status_code == 200:
            response_data = json.loads(r.text)
        else:
            raise Exception("Fetching access token failed.")
        header_bearer = response_data['access']
        # create headers for request
        headers = { 'Authorization': 'Bearer ' + header_bearer }
        # create data with schema name
        Dict = {'name': version_name}
        # send request to create a new schema and check if it was successful
        r = requests.post(URLversions, headers=headers, data=Dict, verify=False)
        # TODO: Other status codes
        if r.status_code == 400:
            self.stdout.write(f"Schema -> {version_name} failed to be created. \nREASON: {r.text}")
        elif r.status_code == 200 or r.status_code == 201:                    
            if r.reason == 'Created':
                self.stdout.write(f"Schema -> {version_name} is successfully created!")
        self.stdout.write('Schemas init done.')
        # Try to import needed data from CSV for this specific created schema
        call_command('import', 'fei-data-new', version_name)