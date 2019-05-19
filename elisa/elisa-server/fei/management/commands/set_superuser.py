from django.contrib.auth.models import Group
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import DatabaseError

from fei.models import AppUser


class Command(BaseCommand):
    help = 'Manage app data'
    stealth_options = ('stdin',)

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Main timetable creator username.')
        parser.add_argument('user_id', type=str, help='Main timetable creator id.')

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Checking groups...'))

        try:
            group = Group.objects.get(name=settings.MAIN_TIMETABLE_CREATOR)

            self.stdout.write(self.style.SUCCESS('Creating superuser with username: %s' % options['username']))

            try:
                user = AppUser.objects.get(username=options['username'])
            except AppUser.DoesNotExist as e:
                if settings.DEBUG:
                    self.stderr.write(str(e))

                # if user does not exists, we create one
                user = AppUser.objects.create(id=int(options['user_id']), username=options['username'])
                user.is_active = True

            # add this user to main timetable creator group
            user.groups.add(group)
            user.save()
            self.stdout.write(self.style.SUCCESS('User created successfully.'))
        except Group.DoesNotExist as e:
            if settings.DEBUG:
                self.stderr.write(str(e))
            self.stderr.write(self.style.ERROR('ERROR: Initialize groups first.'))
        except (DatabaseError, TypeError) as e:
            if settings.DEBUG:
                self.stderr.write(str(e))
            self.stderr.write(self.style.ERROR('ERROR: Unable to create superuser.'))