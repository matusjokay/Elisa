from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from django_tenants.management.commands import InteractiveTenantOption


class Command(BaseCommand, InteractiveTenantOption):
    help = 'Dump and load data'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)

        parser.add_argument('command', type=str, help='The command you want to call.')
        parser.add_argument('schema_name', type=str, help='The schema you want to dump.')
        parser.add_argument('fixture', nargs='?', default=None, help='The file you want to load.')

    def handle(self, *args, **options):
        tenant = self.get_tenant_from_options_or_interactive(**options)
        connection.set_tenant(tenant)
        schema_name = options['schema_name']
        del options['schema_name']

        if options['command'] == 'load':
            action = 'loaddata'
            filename = options['fixture']

            # delete arguments, which are not needed for loaddata
            del options['command']
            del options['fixture']

            options['exclude'] = ["contenttypes"]

            print("Loading data from %s to schema %s." % (filename, schema_name))
            call_command(action, filename, *args, **options)
            print("Load successful.")
        elif options['command'] == 'dump':
            action = 'dumpdata'

            # delete arguments, which are not needed for dumpdata
            del options['command']
            del options['fixture']

            options['exclude'] = ["contenttypes", "admin", "sessions", "auth", "timetables", "requirements", "fei"]

            print("Dumping data from schema %s." % schema_name)
            call_command(action, *args, **options)
            print("Dump successful.")
        else:
            raise CommandError("Invalid command %s." % options['command'])

