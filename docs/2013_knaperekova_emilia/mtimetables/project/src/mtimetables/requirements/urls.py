# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django.conf.urls import url

from .. import misc as mtimetables_misc
from ..data import models as data_models

from . import views
from . import models



models = collections.OrderedDict([
	(models.RequirementPackage, {'viewset': views.RequirementPackageViewSet}),
	# (models.RequirementType, {'viewset': views.RequirementTypeViewSet}),

	(data_models.Group, {'viewset': views.GroupViewSet}),
	(data_models.User, {'viewset': views.UserViewSet}),
	(data_models.Subject, {'viewset': views.SubjectViewSet}),
	(data_models.ActivityType, {'viewset': views.ActivityTypeViewSet}),
	(data_models.ActivityDefinition, {'viewset': views.ActivityDefinitionViewSet}),
	(data_models.Room, {'viewset': views.RoomViewSet}),
	(data_models.RoomType, {'viewset': views.RoomTypeViewSet}),
])

urlpatterns = [

	url(r'^$', views.RequirementsIndex.as_view(), name='index'),

	# model RequirementType completion
	url(r'^requirementtype/install/$', views.RequirementTypesInstallView.as_view(), name='requirementtype_install'),
	
	# model Requirement
	url(r'^requirement/$', views.RequirementListView.as_view(), name='requirement_list'),
	url(r'^requirement/create/(?P<model_name>\w+)/$', views.RequirementCreateView.as_view(), name='requirement_create'),
	url(r'^requirement/create/(?P<model_name>\w+)/package/(?P<requirement_package>\d+)/$', views.RequirementCreateView.as_view(), name='requirement_create'),
	url(r'^requirement/(?P<pk>\d+)/$', views.RequirementDetailView.as_view(), name='requirement_detail'),
	url(r'^requirement/(?P<pk>\d+)/update/$', views.RequirementUpdateView.as_view(), name='requirement_update'),
	url(r'^requirement/(?P<pk>\d+)/delete/$', views.RequirementDeleteView.as_view(), name='requirement_delete'),

	url(r'^(?P<model_name>[group|user|subject|activitytype|activitydefinition|room|roomtype]+)/(?P<pk>\d+)/$', views.ObjectRequirementsView.as_view(), name='object_requirements'),
	# url(r'^(?P<model_name>[group|user|subject|activitytype|activitydefinition|room|roomtype]+)/(?P<pk>\d+)/requirements/$', views.ObjectRequirementsView.as_view(), name='object_requirements'),

]
urlpatterns += mtimetables_misc.package_views_factory('requirements', models)