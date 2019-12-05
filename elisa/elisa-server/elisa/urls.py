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
from django.urls import include, path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework_swagger.views import get_swagger_view

import school.views as school
import fei.views as fei
import requirements.views as requirements

# TODO: Add missing view sets
router = SimpleRouter()
router.register(r'groups', school.GroupViewSet)
router.register(r'departments', school.DepartmentViewSet)
router.register(r'courses', school.CourseViewSet)
router.register(r'equipments', school.EquipmentViewSet)
router.register(r'room-categories', school.RoomTypeViewSet)
router.register(r'rooms', school.RoomViewSet)
router.register(r'activity-categories', school.ActivityCategoryViewSet)
router.register(r'activities', school.ActivityViewSet)
router.register(r'versions', fei.VersionViewSet, basename='versions')
router.register(r'users', fei.UserViewSet)
router.register(r'requirements', requirements.RequirementsViewSet)
router.register(r'requirements-events', requirements.RequirementEventViewSet)

schema_view = get_swagger_view(title='Elisa API')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('fei_importexport.urls')),
    path('', include('timetables.urls')),
    path('', include('authentication.urls')),
    path('teachers/', fei.TeachersList.as_view()),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('docs/', schema_view),
]
