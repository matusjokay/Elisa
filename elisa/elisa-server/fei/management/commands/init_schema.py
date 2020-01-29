import os
import platform
import requests
import urllib3
import json
import getpass
import re
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

"""
This command is for creating schema and trying to import all
the data based on schema.
Arguments provied are login and schema name based on format
in the following manner -> ZS/LS_YYYY_YYYY
Where ZS/LS is either Winter/Summer semester schema
TODO: Calls requests based on the provided login therefore
a new implementation on the client is preffered.
"""
class Command(BaseCommand):
    help = 'Create schemas based on semesters and their data'
    URLlogin = 'https://localhost:8000/login/'
    URLversions = 'https://localhost:8000/versions/'
    schema_regex = r'^(ZS|LS)_\d{4}_\d{4}$'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username for login to obtain token pair')
        parser.add_argument('schema_name', type=str, help='Schema to create in the database')

    def handle(self, *args, **options):
        if re.match(self.schema_regex, options['schema_name']) == None:
            self.stdout.write('Invalid schema pattern! Pattern is ZS/LS_YYYY_YYYY')
            exit(1)
        pwd = getpass.getpass()
        # Try to clear the console, if getpass will still echo stdin
        if platform.system() == 'Windows':
            clear = lambda: os.system('cls')
            clear()
        elif platform.system() == 'Linux' or platform.system() == 'Darwin':
            clear = lambda: os.system('clear')
            clear()
        # to hide unsecure requests warning
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        version_name = options['schema_name']
        # call request to server to obtain access token
        r = requests.post(self.URLlogin, data=dict({'username': options['username'], 'password': pwd}), verify=False)
        if r.status_code == 200:
            self.stdout.write('Login successful! Token acquired.')
            response_data = json.loads(r.text)
        else:
            raise Exception("Fetching access token failed.")
            exit(1)
        header_bearer = response_data['access']
        # create headers for request
        headers = { 'Authorization': 'Bearer ' + header_bearer }
        # create data with schema name
        Dict = {'name': version_name}
        # send request to create a new schema and check if it was successful
        self.stdout.write('Trying to create schema...')
        r = requests.post(self.URLversions, headers=headers, data=Dict, verify=False)
        # TODO: Other status codes
        if r.status_code == 400:
            self.stdout.write(f"Schema -> {version_name} failed to be created. \nREASON: {r.text}")
        elif r.status_code == 200 or r.status_code == 201:                    
            if r.reason == 'Created':
                self.stdout.write(f"Schema -> {version_name} is successfully created!")
        self.stdout.write('Schemas init done.')
        # Try to import needed data from CSV for this specific created schema
        call_command('import', 'fei-data-new', version_name)