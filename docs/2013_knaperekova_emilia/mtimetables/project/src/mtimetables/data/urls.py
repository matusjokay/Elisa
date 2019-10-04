# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django.conf.urls import url

from .. import misc as mtimetables_misc

from . import views
from . import models



viewsets = collections.OrderedDict([
	# (models.ActivityType, {'viewset': views.ActivityTypeViewSet}),
	(models.ActivityDefinition, {'viewset': views.ActivityDefinitionViewSet}),
	(models.Department, {'viewset': views.DepartmentViewSet}),
	(models.Group, {'viewset': views.GroupViewSet}),
	(models.User, {'viewset': views.UserViewSet}),
	(models.StudyType, {'viewset': views.StudyTypeViewSet}),
	(models.Subject, {'viewset': views.SubjectViewSet}),
	(models.Room, {'viewset': views.RoomViewSet}),
	(models.RoomType, {'viewset': views.RoomTypeViewSet}),
	(models.Equipment, {'viewset': views.EquipmentViewSet}),
])

urlpatterns = [

	url(r'^$', views.DataIndex.as_view(), name='index'),

	url(r'^activitydefinition/(?P<pk>\d+)/events/', views.ActivityDefinitionEventsView.as_view(), name='activitydefinition_events'),

	url(r'^subject/(?P<pk>\d+)/students/$', views.SubjectStudents.as_view(), name='subject_students'),

]
urlpatterns += mtimetables_misc.package_views_factory('data', viewsets)