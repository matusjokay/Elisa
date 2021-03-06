"""elisa URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.routers import SimpleRouter
from rest_framework_extensions.routers import ExtendedSimpleRouter
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework_swagger.views import get_swagger_view

import school.views as school
import timetables.views as timetables

router = SimpleRouter()
router.register(r'groups', school.GroupViewSet)
router.register(r'departments', school.DepartmentViewSet)
router.register(r'courses', school.CourseViewSet)
router.register(r'equipment', school.EquipmentViewSet)
router.register(r'room-categories', school.RoomCategoryViewSet)
router.register(r'rooms', school.RoomViewSet)
router.register(r'activity-categories', school.ActivityCategoryViewSet)
router.register(r'activities', school.ActivityViewSet)

timetables_router = ExtendedSimpleRouter()
timetables_router.register(
    r'timetables', timetables.TimetableViewSet,
    base_name='timetable').register(
        r'events',
        timetables.EventViewSet,
        base_name='timetables-event',
        parents_query_lookups=['timetable'])

schema_view = get_swagger_view(title='Elisa API')

urlpatterns = [
    url(r'^$', schema_view),
    url(r'^', include(router.urls)),
    url(r'^', include(timetables_router.urls)),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^api-token-refresh/', refresh_jwt_token),
    url(r'^admin/', admin.site.urls),
]
