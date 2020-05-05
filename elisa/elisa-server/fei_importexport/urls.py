from django.conf.urls import url
from .views import *

urlpatterns = [
    url('groups/import', GroupImportView.as_view(), name='import_groups'),
    url('departments/import', DepartmentImportView.as_view(), name='import_departments'),
    url('equipments/import', EquipmentImportView.as_view(), name='import_equipments'),
    url('users/import', UsersImportView.as_view(), name='import_users'),
    url('courses/import', CoursesImportView.as_view(), name='import_courses'),
    url('room-types/import', RoomTypesImportView.as_view(), name='import_room_types'),
    url('rooms/import', RoomsImportView.as_view(), name='import_rooms'),
    url('periods/import', PeriodImportView.as_view(), name='import_periods'),
    url('import/init', InitImportView.as_view(), name='init_import'),
    url('import/for-version', VersionDataImportView.as_view(), name='version_data_import')
]
