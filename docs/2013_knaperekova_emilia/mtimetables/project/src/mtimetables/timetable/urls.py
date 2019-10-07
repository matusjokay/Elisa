# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django.conf.urls import url, include

from .. import misc as mtimetables_misc

from . import views
from . import models



viewsets = collections.OrderedDict([
	(models.Event, {'viewset': views.EventViewSet}),
	(models.OneTimeEvent, {'viewset': views.OneTimeEventViewSet}),
	(models.SemesterEvent, {'viewset': views.SemesterEventViewSet}),
])

urlpatterns = [

	url(r'^$', views.TimetableIndex.as_view(), name='index'),

	url(r'^collisions/$', views.CollisionView.as_view(), name='collision_list'),
	url(r'^event/(?P<pk>\d+)/collisions/$', views.EventCollisionView.as_view(), name='event_collision_list'),

	url(r'^event/(?P<pk>\d+)/update/$', views.EventUpdateView.as_view(), name='event_update'),

]
urlpatterns += mtimetables_misc.package_views_factory('timetable', viewsets)