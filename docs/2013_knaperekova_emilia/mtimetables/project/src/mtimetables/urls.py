# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include

from . import views

import logging
logger = logging.getLogger(__name__)



urlpatterns = [

	# home
	url(r'^$', views.TemplateView.as_view(template_name='mtimetables/index.html'), name='index'),

	# custom data app urls:
	url(r'^data/', include('mtimetables.data.urls', namespace='data')),

	# custom timetable app urls:
	url(r'^timetable/', include('mtimetables.timetable.urls', namespace='timetable')),

	# custom requirements app urls:
	url(r'^requirements/', include('mtimetables.requirements.urls', namespace='requirements')),
	
	# custom calendar app urls:
	url(r'^calendar/', include('mtimetables.calendar.urls', namespace='calendar')),
	
	# custom settings app urls:
	url(r'^settings/', include('mtimetables.settings.urls', namespace='settings')),

]