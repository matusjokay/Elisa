# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from . import views



urlpatterns = [

	url(r'^$', views.CalendarView.as_view(), name='index'),
	url(r'^semester/$', views.SemesterTimetableView.as_view(), name='semester'),
	url(r'^examinationperiod/$', views.ExaminationPeriodTimetableView.as_view(), name='examinationperiod'),
	
]