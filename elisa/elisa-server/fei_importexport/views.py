from django.db import transaction
from django.db.utils import ConnectionDoesNotExist, DatabaseError, DataError

from rest_framework.response import Response
from rest_framework.views import APIView

from . import models
from authentication.permissions import IsMainTimetableCreator
import school.models as school
from fei.models import AppUser

DATABASE_NAME = 'import'


def get_or_create3(model, obj_id, **kwargs):
    try:
        new_model = model.objects.get(id=obj_id)
    except model.DoesNotExist:
        new_model = model.objects.create(**kwargs)
    return new_model


def get_or_create(model, **kwargs):
    try:
        new_model = model.objects.get(**kwargs)
    except model.DoesNotExist:
        new_model = model.objects.create(**kwargs)
    return new_model


def import_resource(import_method):
    try:
        import_method()
    except ConnectionDoesNotExist:
        print('No database with name %s.' % DATABASE_NAME)
        return Response(status=500)
    except DatabaseError as e:
        print('Database error occured: %s.' % e)
        return Response(status=500)
    return Response(status=200)


class GroupImportView(APIView):
    """
        API endpoint for import of groups from AIS
    """

    permission_classes = (IsMainTimetableCreator, )

    def import_groups(self):
        groups = models.FeiGroups.objects.using(DATABASE_NAME).all()

        for group in groups:
            try:
                kwargs = {"id": group.id}
                new_group = get_or_create(school.Group, **kwargs)

                if group.nadriadena_skupina is not None:
                    kwargs = {"id": group.nadriadena_skupina}
                    new_group.parent = get_or_create(school.Group, **kwargs)

                new_group.name = group.nazov
                new_group.abbr = group.skratka
                new_group.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for group %s.' % (e, group.id))
                pass

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_groups)


class DepartmentImportView(APIView):
    """
        API endpoint for import of departments from AIS
    """

    permission_classes = (IsMainTimetableCreator, )

    def import_departments(self):
        departments = models.FeiDepartments.objects.using(DATABASE_NAME).all()

        for department in departments:
            try:
                kwargs = {"id": department.id}
                new_department = get_or_create(school.Department, **kwargs)

                if department.nadriadene_prac:
                    kwargs = {"id": int(department.nadriadene_prac)}
                    new_department.parent = get_or_create(school.Department, **kwargs)

                new_department.name = department.nazov
                new_department.abbr = department.skratka
                new_department.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for department %s.' % (e, department.id))
                pass

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_departments)


class EquipmentImportView(APIView):
    """
        API endpoint for import of equipments from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_equipments(self):
        equipments = models.FeiEquipments.objects.using(DATABASE_NAME).all()

        for equipment in equipments:
            try:
                kwargs = {"id": equipment.id}
                new_equipment = get_or_create(school.Equipment, **kwargs)
                new_equipment.name = equipment.nazov
                new_equipment.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for equipment %s.' % (e, equipment.id))
                pass

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_equipments)


class UsersImportView(APIView):
    """
        API endpoint for import of users from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_users(self):
        users = models.FeiUsers.objects.using(DATABASE_NAME).all()

        for user in users:
            try:
                kwargs = {"id": user.ais_id, "is_active": True, "username": user.login}
                new_user = get_or_create3(AppUser, user.ais_id, **kwargs)

                new_user.first_name = user.meno
                new_user.last_name = user.priezvisko
                new_user.title_before = user.tituly_pred
                new_user.title_after = user.tituly_za

                new_user.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for user %s.' % (e, user.ais_id))
                pass
            except:
                print('Other error occured for user %s.' % user.ais_id)
                pass

        # TODO doriesit este user_group, aktualne nepresne premapovanie na studyType

    def post(self, request):
        return import_resource(self.import_users)


class CoursesImportView(APIView):
    """
        API endpoint for import of courses and users assigned to course from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    role_map = {
        "student": 1,
        "garant": 2,
        "prednasajuci": 3,
        "cviciaci": 4,
        "skusajuci": 5,
        "administrator": 6,
        "tutor": 7
    }

    def import_subject_users(self):
        subject_users = models.FeiSubjectsUsers.objects.using(DATABASE_NAME).all()

        for subject_user in subject_users:
            try:
                with transaction.atomic():
                    new_subject_user = school.SubjectUser()
                    kw = {"id": subject_user.predmet}
                    new_subject_user.subject = get_or_create(school.Course, **kw)

                    kw = {"id": subject_user.ais_id}
                    new_subject_user.user = get_or_create(AppUser, **kw)
                    new_subject_user.role = self.role_map.get(subject_user.rola)

                    new_subject_user.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for subject_user %s.' % (e, subject_user.ais_id))
                pass

    def import_courses(self):
        courses = models.CPredmetyFei.objects.using(DATABASE_NAME).all()

        for course in courses:
            try:

                kw = {"id": course.garantujuce_pracovisko}
                department = get_or_create(school.Department, **kw)
                kwargs = {"department": department, "id": course.id}
                new_course = get_or_create3(school.Course, course.id, **kwargs)
                new_course.name = course.nazov
                new_course.code = course.kod
                new_course.completion = course.std_ukonc

                new_course.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for course %s.' % (e, course.id))
                pass

        self.import_subject_users()

    def post(self, request):
        return import_resource(self.import_courses)


class RoomTypesImportView(APIView):
    """
        API endpoint for import of room types from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_room_types(self):
        room_types = models.FeiRoomtypes.objects.using(DATABASE_NAME).all()

        for room_type in room_types:
            try:
                kwargs = {"id": room_type.id}
                new_room_type = get_or_create(school.RoomCategory, **kwargs)
                new_room_type.name = room_type.nazov
                new_room_type.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for room_type %s.' % (e, room_type.id))
                pass

    @transaction.atomic
    def post(self, request):
        return import_resource(self.import_room_types)


class RoomsImportView(APIView):
    """
        API endpoint for import of rooms and room equipment from AIS
    """
    permission_classes = (IsMainTimetableCreator, )

    def import_rooms(self):
        rooms = models.FeiRooms.objects.using(DATABASE_NAME).all()

        for room in rooms:
            try:
                kwargs = {"id": room.typ}
                category = get_or_create(school.RoomCategory, **kwargs)
                kwargs = {"id": room.pracovisko}
                department = get_or_create(school.Department, **kwargs)

                kwargs = {"department": department, "id": room.id, "category": category}
                new_room = get_or_create3(school.Room, room.id, **kwargs)
                new_room.name = room.nazov
                new_room.capacity = room.kapacita

                new_room.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for room %s.' % (e, room.id))
                pass

        self.import_rooms_equipment()

    def import_rooms_equipment(self):
        rooms_equipments = models.FeiRoomsEquipments.objects.using(DATABASE_NAME).all()

        for room_equipment in rooms_equipments:
            try:
                new_equipment = school.RoomEquipment()
                new_equipment.count = int(room_equipment.pocet)
                kwargs = {"id": room_equipment.miestnost}
                new_equipment.room = get_or_create(school.Room, **kwargs)
                kwargs = {"id": room_equipment.pomocka}
                new_equipment.equipment = get_or_create(school.Equipment, **kwargs)

                new_equipment.save()
            except (DatabaseError, DataError) as e:
                print('Error {%s} occured for room %s and equipment %s.' % (e, room_equipment.miestnost, room_equipment.pomocka))
                pass

    def post(self, request):
        return import_resource(self.import_rooms)

