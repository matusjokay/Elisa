from django.db import IntegrityError, transaction, connection
from django.db.utils import ConnectionDoesNotExist, DatabaseError, DataError
from django.utils import timezone
from django_tenants.utils import schema_context, get_tenant_model
from django.db.models import Q

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from . import models
from authentication.permissions import IsMainTimetableCreator
import school.models as school
from fei.models import (
    AppUser,
    Department,
    Version,
    Period,
    UserDepartment
)
import time
from datetime import datetime

DATABASE_NAME = 'import'

def update_or_create(model, instance_id, default=None, **kwargs):
    return model.objects.update_or_create(id=instance_id, defaults=default)

def create(model, **kwargs):
    return model.objects.create(**kwargs)


def import_resource(import_method):
    try:
        import_method()
    except ConnectionDoesNotExist:
        print('No database with name %s.' % DATABASE_NAME)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except DatabaseError as e:
        print('Database error occured: %s.' % e)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response(status=status.HTTP_200_OK)


class GroupImportView(APIView):
    """
        API endpoint for import of groups from AIS
    """

    permission_classes = (IsMainTimetableCreator, )

    def import_groups(self):
        print('Inserting rows for Groups')
        groups = models.FeiGroups.objects.using(DATABASE_NAME).all()

        for group in groups:
            try:
                defaults = {}
                if not group.nadriadena_skupina:
                    defaults = {
                        "name": group.nazov,
                        "abbr": group.skratka,
                        "parent": None
                    }
                else:
                    parent, created = update_or_create(
                        model=school.Group,
                        instance_id=group.nadriadena_skupina)
                    defaults = {
                        "name": group.nazov,
                        "abbr": group.skratka,
                        "parent": parent
                    }
                obj, created = update_or_create(
                    model=school.Group,
                    instance_id=group.id,
                    default=defaults
                )
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for group %s.' % (e, group.id))
        print('Inserted')

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_groups)


class DepartmentImportView(APIView):
    """
        API endpoint for import of departments from AIS
    """

    permission_classes = (IsMainTimetableCreator, )

    def import_departments(self):
        print('Inserting rows for Department')
        departments = models.FeiDepartments.objects.using(DATABASE_NAME).all()

        for department in departments:
            try:
                nadriadene_prac = None if not department.nadriadene_prac else int(department.nadriadene_prac)
                defaults = {
                    "name": department.nazov,
                    "abbr": department.skratka,
                    "parent": nadriadene_prac
                    }
                obj, created = update_or_create(
                    model=Department,
                    instance_id=department.id,
                    default=defaults)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for department {department.name} ID -> {department.id}.')
        print('Inserted')
        self.import_users_departments()

    def import_users_departments(self):
        print('Inserting rows for UsersDepartment')
        rows = models.FeiUsersDepartments.objects.using(DATABASE_NAME).all()

        for row in rows:
            try:
                kwargs = {
                    "employment": row.typ_pracovneho_pomeru,
                    "department_id": row.pracovisko,
                    "user_id": row.ais_id
                    }

                obj = create(UserDepartment, **kwargs)
            except IntegrityError as e:
                print(f'Error {e} occured for row AISID {row.ais_id} department {row.pracovisko}.')
        print('Inserted')

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_departments)


class PeriodImportView(APIView):
    """
        API endpoint for import of Periods from AIS
    """

    permission_classes = (IsMainTimetableCreator, )

    def import_periods(self):
        # periods = models.AISObdobia.objects.using(DATABASE_NAME).all()
        # Only pracovisko 30 which is FEI faculty
        # Due to courses data being only from FEI
        print('Inserting rows for Period')
        periods = models.AISObdobia.objects.using(DATABASE_NAME).filter(
            pracovisko=30)

        for period in periods:
            try:
                defaults = {
                    "name": period.nazov_sk,
                    "department_id": period.pracovisko,
                    "active": period.aktivne,
                    "start_date": period.zaciatok,
                    "end_date": period.koniec,
                    "next_period": period.nasledujuce,
                    "previous_period": period.predchadzajuce,
                    "academic_sequence": period.por_ar,
                    "university_period": period.univ_obdobie
                    }
                obj, created = update_or_create(
                    model=Period,
                    instance_id=period.id,
                    default=defaults)
            except IntegrityError as e:
                print(f'Error {e} occured for Period {period.nazov_sk} id {period.id}.')
                pass
        print('Inserted')

    def post(self, request):
        return import_resource(self.import_periods)


class StudiesGroupsImportView(APIView):
    """
        API endpoint for import of FormOfStudy, StudyType
        and Users_Groups from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    studies = {
        "prezencna": 1,
        "distancna": 2
    }
    types = {
        "denna": 1,
        "externa": 2
    }

    def import_groups_users(self):
        print('Inserting rows for UserGroups')
        groups_users = models.FeiUsersGroups.objects.using(DATABASE_NAME).all()

        for group_user in groups_users:
            try:
                kwargs = {
                    "group_id": group_user.skupina,
                    "user_id": group_user.ais_id,
                    "group_number": None if not group_user.kruzok else int(group_user.kruzok),
                    "form_of_study_id": self.types[group_user.forma],
                    "study_type_id": self.studies[group_user.metoda]
                }
                obj = create(school.UserGroup, **kwargs)
            except IntegrityError as e:
                print(f'Error {e} occured for Group_user {group_user.ais_id}.')
        print('Inserted!')

    def import_form_and_types(self):
        print('Inserting rows for Form and Types studies')

        for name, value in self.studies.items():
            defaults = {
                "name": name
            }
            obj, created = update_or_create(
                model=school.FormOfStudy,
                instance_id=value,
                default=defaults)
        
        for name, value in self.types.items():
            kwargs = {
                "name": name
            }
            obj, created = update_or_create(
                model=school.StudyType,
                instance_id=value,
                default=defaults)
        print('Inserted!')
        self.import_groups_users()

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_form_and_types)


class EquipmentImportView(APIView):
    """
        API endpoint for import of equipments from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_equipments(self):
        print('Inserting rows for Equipment')
        equipments = models.FeiEquipments.objects.using(DATABASE_NAME).all()

        for equipment in equipments:
            try:
                defaults = {
                    "name": equipment.nazov
                    }
                obj, created = update_or_create(
                    model=school.Equipment,
                    instance_id=equipment.id,
                    default=defaults)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for equipment {equipment.id}.')
        print('Inserted!')

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_equipments)


class UsersImportView(APIView):
    """
        API endpoint for import of users from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_users(self):
        print('Inserting rows for Users')
        users = models.FeiUsers.objects.using(DATABASE_NAME).all()

        for user in users:
            try:
                defaults = {
                    "is_active": True,
                    "username": user.login,
                    "first_name": user.meno,
                    "last_name": user.priezvisko,
                    "title_before": user.tituly_pred,
                    "title_after": user.tituly_za
                }
                obj, created = update_or_create(
                    model=AppUser,
                    instance_id=user.ais_id,
                    defaults=defaults)
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for user %s.' % (e, user.ais_id))
                pass
        print('Inserted!')

    def post(self, request):
        return import_resource(self.import_users)


class CoursesImportView(APIView):
    """
        API endpoint for import of courses and users assigned to course from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    for_periods = []
    imported_ids = []

    role_map = {
        "student": 1,
        "garant": 2,
        "prednasajuci": 3,
        "cviciaci": 4,
        "skusajuci": 5,
        "administrator": 6,
        "tutor": 7
    }

    def import_course_users(self):
        print('Inserting rows for UserCourses')
        # TODO: Using __in causes performance hit when selecting specific
        # entries from this view. However right now there are just data for
        # the current active period. Later there may be other entries from 
        # different periods
        course_users = models.FeiSubjectsUsers.objects.using(DATABASE_NAME).filter(
            Q(predmet__in=self.imported_ids))
        for course_user in course_users:
            try:
                roles_strs = school.SubjectUser().parse_roles(                    
                    role_text=course_user.rola)
                for s in roles_strs:
                    kwargs = {
                        "user_id": course_user.ais_id,
                        "subject_id": course_user.predmet,
                        "role_id": self.role_map[s.strip()]
                    }
                    obj = create(school.SubjectUser, **kwargs)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for subject_user {course_user.ais_id}.')
        print('Inserted!')

    def import_user_course_role(self):
        print('Inserting rows for UserCourseRole')
        for role_name, role_value in self.role_map.items():
            try:
                defaults = {
                    "name": role_name
                }
                obj, created = update_or_create(
                    model=school.UserSubjectRole,
                    instance_id=role_value,
                    default=defaults)
            except IntegrityError as e:
                print(f'Error {e} occured for course_user_role {role_name}.')
        print('Inserted!')
        self.import_course_users()

    def import_courses(self):
        print('Inserting rows for Courses')
        period_map = {}
        if len(self.for_periods) == 1:
            courses = models.CPredmetyFei.objects.using(DATABASE_NAME).filter(Q(obdobie__icontains=self.for_periods[0]['name']))
            period_map = {
                self.for_periods[0]['name']: self.for_periods[0]['id']
            }
        elif len(self.for_periods) == 2:
            courses = models.CPredmetyFei.objects.using(DATABASE_NAME).filter(
                Q(obdobie__icontains=self.for_periods[0]['name']) |
                Q(obdobie__icontains=self.for_periods[1]['name']))
            period_map = {
                self.for_periods[0]['name']: self.for_periods[0]['id'],
                self.for_periods[1]['name']: self.for_periods[1]['id']
            }
        else:
            courses = models.CPredmetyFei.objects.using(DATABASE_NAME).all()

        for course in courses:
            try:
                # kw = {"id": course.garantujuce_pracovisko}
                defaults = {
                    "period_id": period_map[course.obdobie],
                    "department_id": course.garantujuce_pracovisko,
                    "teacher_id": course.garant,
                    "code": course.kod,
                    "name": course.nazov,
                    "completion": course.std_ukonc,
                    "credits": int(course.kredity)
                    }
                obj, created = update_or_create(
                    model=school.Course,
                    instance_id=course.id,
                    default=defaults)
                if created:
                    self.imported_ids.append(obj.id)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for course {course.id}.')
        print('Inserted!')
        self.import_user_course_role()

    def post(self, request):
        self.for_periods = request.data['periods']
        return import_resource(self.import_courses)


class RoomTypesImportView(APIView):
    """
        API endpoint for import of room types from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_room_types(self):
        print('Inserting rows for RoomTypes')
        room_types = models.FeiRoomtypes.objects.using(DATABASE_NAME).all()

        for room_type in room_types:
            try:
                # kwargs = {"id": room_type.id}
                defaults = {
                    "name": room_type.nazov
                }
                obj, created = update_or_create(
                    model=school.RoomType,
                    instance_id=room_type.id,
                    default=defaults)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for room_type {room_type.id}.')
        print('Inserted!')

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_room_types)


class RoomsImportView(APIView):
    """
        API endpoint for import of rooms and room equipment from AIS
    """
    permission_classes = (IsMainTimetableCreator, )


    def import_rooms(self):
        print('Inserting rows for Rooms')
        rooms = models.FeiRooms.objects.using(DATABASE_NAME).all()

        for room in rooms:
            try:
                defaults = {
                    "name": room.nazov,
                    "capacity": room.kapacita,
                    "room_type_id": room.typ,
                    "department_id": room.pracovisko
                }
                obj, created = update_or_create(
                    model=school.Room,
                    instance_id=room.id,
                    default=defaults)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for room {room.id}.')
        print('Inserted')
        self.import_rooms_equipment()
    
    def import_rooms_equipment(self):
        print('Inserting rows for RoomEquipment')
        rooms_equipments = models.FeiRoomsEquipments.objects.using(DATABASE_NAME).all()

        for room_equipment in rooms_equipments:
            try:
                kwargs = {
                    "room_id": room_equipment.miestnost,
                    "equipment_id": room_equipment.pomocka,
                    "count": int(room_equipment.pocet)
                }
                obj = create(school.RoomEquipment, **kwargs)
            except (DatabaseError, DataError) as e:
                print(f'Error {e} occured for room {room_equipment.miestnost} and equipment {room_equipment.pomocka}.')
        print('Inserted')

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_rooms)


class InitImportView(APIView):
    """
        API endpoint for importing initial data so user
        can continue creating schemas based on periods
    """
    permission_classes = (IsMainTimetableCreator, )

    views_dict = {
        "Users": UsersImportView(),
        "Departments": DepartmentImportView(),
        "Periods": PeriodImportView()
    }

    @transaction.atomic
    def post(self, request):
        start_time = time.time()
        for name, view in self.views_dict.items():
            print(f'Importing {name}...')
            response = view.post(request)
            if response.status_code == 500:
                return Response(
                    'Import Init data FAILED!',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(f'{name} done.')
        try:
            public_version = Version.objects.get(name='public')
            public_version.last_updated = datetime.now(tz=timezone.utc)
            public_version.save()
        except IntegrityError as e:
            print(f'Failed to set updated datetime reason: \n{e}')
        end_time = time.time() - start_time
        print(f"Done Importing data and it took {end_time} seconds!")
        return Response('Imported!', status=status.HTTP_200_OK)


class VersionDataImportView(APIView):
    """
        API endpoint for importing schema specific data so user
        can then access this version with the latest data
    """
    permission_classes = (IsMainTimetableCreator, )

    views_dict = {
        "Groups": GroupImportView(),
        "Courses": CoursesImportView(),
        "UserGroupsFormsAndStudies": StudiesGroupsImportView(),
        "Equipment": EquipmentImportView(),
        "RoomTypes": RoomTypesImportView(),
        "RoomsAndEquipment": RoomsImportView()
    }

    def post(self, request):
        version_name = request.headers['Timetable-Version']
        period_ids = request.data['periods']
        tenant_model = get_tenant_model().objects.get(schema_name=version_name.lower())
        periods = Period.objects.filter(id__in=period_ids).values('id', 'name')
        periods = list(periods)
        connection.set_tenant(tenant_model)
        start_time = time.time()
        for name, view in self.views_dict.items():
            if name == 'Courses':
                request.data['periods'] = periods
            response = view.post(request)
            if response.status_code == 500:
                return Response(
                    'Import Init data FAILED!',
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            print(f'{name} done.')
        try:
            tenant_model.last_updated = datetime.now(tz=timezone.utc)
            tenant_model.save()
        except IntegrityError as e:
            print(f'Failed to set updated datetime reason: \n{e}')
        end_time = time.time() - start_time
        print(f"Done Importing data and it took {end_time} seconds!")
        return Response('Imported!', status=status.HTTP_200_OK)
