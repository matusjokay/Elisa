from django.conf.urls import url
from .views import *

urlpatterns = [
    url('groups/import', GroupImportView.as_view(), name='import_groups'),
    url('departments/import', DepartmentImportView.as_view(), name='import_departments'),
    url('equipments/import', EquipmentImportView.as_view(), name='import_equipments'),
    url('users/import', UsersImportView.as_view(), name='import_users'),
    url('courses/import', CoursesImportView.as_view(), name='import_courses'),
    url('room-categories/import', RoomTypesImportView.as_view(), name='import_room_categories'),
    url('rooms/import', RoomsImportView.as_view(), name='import_rooms'),
]
