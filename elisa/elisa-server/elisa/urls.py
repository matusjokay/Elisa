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
from django.urls import include, path, re_path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


import school.views as school
import fei.views as fei
import requirements.views as requirements

# TODO: Add missing view sets
router = SimpleRouter()
router.register(r'groups', school.GroupViewSet)
router.register(r'departments', fei.DepartmentViewSet)
router.register(r'user-department', fei.UserDepartmentViewSet)
router.register(r'courses', school.CourseViewSet)
router.register(r'equipments', school.EquipmentViewSet)
router.register(r'room-types', school.RoomTypeViewSet)
router.register(r'rooms', school.RoomViewSet)
router.register(r'room-equipment', school.RoomEquipmentViewSet)
router.register(r'activity-categories', school.ActivityCategoryViewSet)
router.register(r'activities', school.ActivityViewSet)
router.register(r'subject-users', school.SubjectUserViewSet)
router.register(r'user-subject-roles', school.UserSubjectRoleViewSet)
router.register(r'versions', fei.VersionViewSet, basename='versions')
router.register(r'users', fei.UserViewSet)
router.register(r'requirements', requirements.RequirementsViewSet)
router.register(r'requirements-events', requirements.RequirementEventViewSet)
router.register(r'periods', fei.PeriodViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="Elisa API",
        default_version='v1',
        description="All the available api endpoints",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="xjokay@stuba.sk"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path(
        '',
        include(
            router.urls)),
    path(
        '',
        include('fei_importexport.urls')),
    path(
        '',
        include('timetables.urls')),
    path(
        '',
        include('authentication.urls')),
    path(
        'api-auth/',
        include(
            'rest_framework.urls',
            namespace='rest_framework')),
    re_path(
        r'^swagger(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(
            cache_timeout=0),
        name='schema-json'),
    re_path(
        r'^swagger/$',
        schema_view.with_ui(
            'swagger',
            cache_timeout=0),
        name='schema-swagger-ui'),
    re_path(
        r'^redoc/$',
        schema_view.with_ui(
            'redoc',
            cache_timeout=0),
        name='schema-redoc'),
]
