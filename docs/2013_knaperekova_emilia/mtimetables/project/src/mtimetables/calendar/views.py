# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import isoweek
import calendar as python_calendar

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.conf import settings

from .. import settings as options
from .. import views as mtimetables_views
from ..data import models as data_models
from ..timetable import forms as timetable_forms

from . import core
from . import forms
from . import models

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'calendar'



class BaseCalendarView(mtimetables_views.FormView):
	template_name = 'mtimetables/calendar/site-calendar.html'
	heading = 'Calendar'
	form_class = forms.CalendarFilterForm
	packages = ['mtimetables', PACKAGENAME]
	view_types = ''
	activity_prototypes = ()

	def __init__(self, *args, **kwargs):
		logger.debug('BaseCalendarView init')
		super(BaseCalendarView, self).__init__(*args, **kwargs)
		self.grid = None
		self.week = None
		self.month = None
		self.day = None
		self.subject = None
		self.user = None
		self.room = None
		self.group = None

		self._render_calendar = False

	def form_valid(self, form):
		if self.is_ajax():
			self.template_name = 'mtimetables/calendar/calendar.html'
			return self.render_to_response(self.get_context_data())
		return super(BaseCalendarView, self).form_valid(form)
		
	def dispatch(self, request, *args, **kwargs):

		logger.debug('BaseCalendarView dispatch')

		R = request.GET
		if request.POST:
			R = request.POST

		matched_filter_params = set(R.keys()) & set(['next', 'previous', 'grid', 'week', 'month', 'day', 'room', 'user', 'group', 'subject'])

		if matched_filter_params:

			self.matched_params.update(matched_filter_params)

			if R.get('month'):
				self.month = int(R.get('month'))
				self.week = None
				self.day = None
			elif R.get('week'):
				self.week = int(R.get('week'))
				self.month = None
				self.day = None
			elif R.get('day'):
				self.day = datetime.datetime.strptime(R.get('day'), settings.DATE_INPUT_FORMATS[0]).date().toordinal()
				self.week = None
				self.month = None

			if 'calendar-next' in R.keys():
				if self.month:
					day = datetime.date.fromordinal(self.month)
					new_day = datetime.date(day.year if day.month<12 else day.year+1, day.month+1 if day.month<12 else 1, 1)
					self.month = datetime.date(new_day.year, new_day.month, 1).toordinal()
				elif self.week:
					self.week += 7
				elif self.day:
					self.day += 1
			elif 'calendar-previous' in R.keys():
				if self.month:
					day = datetime.date.fromordinal(int(R.get('month')))
					new_day = datetime.date(day.year if day.month>1 else day.year-1, day.month-1 if day.month>1 else 12, 1)
					self.month = datetime.date(new_day.year, new_day.month, 1).toordinal()
				elif self.week:
					self.week -= 7
				elif self.day:
					self.day -= 1

			if self.grid and (self.month or self.week or self.day):
				self._render_calendar = True
				self.room = get_object_or_404(data_models.Room, pk=R.get('room')) if R.get('room') else None
				self.user = get_object_or_404(data_models.User, pk=R.get('user')) if R.get('user') else None
				self.group = get_object_or_404(data_models.Group, pk=R.get('group')) if R.get('group') else None
				self.subject = get_object_or_404(data_models.Subject, pk=R.get('subject')) if R.get('subject') else None

		return super(BaseCalendarView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(BaseCalendarView, self).get_context_data(**kwargs)

		from_date = False
		to_date = False
		if self.month:
			day = datetime.date.fromordinal(self.month)
			monthrange = python_calendar.monthrange(day.year, day.month)
			from_date = datetime.date(day.year, day.month, 1)
			to_date = datetime.date(day.year, day.month, monthrange[1])
		elif self.week:
			day = datetime.date.fromordinal(self.week)
			week = isoweek.Week.withdate(day)
			from_date = week.monday()
			to_date = week.sunday()
		elif self.day:
			from_date = to_date = datetime.date.fromordinal(self.day)

		if self._render_calendar:
			hours = self.grid.hours.all()
			context['calendar'] = core.Calendar(from_date, to_date, hours=hours, room=self.room, user=self.user, group=self.group, subject=self.subject)
			context['success_url'] = self.get_success_url()

		context['render_toolbar'] = False

		if not self.is_ajax():
			context['form_id'] = 'calendar-view-form'

			if self.activity_prototypes:
				context['render_toolbar'] = True
				context['onetimeevent_form'] = timetable_forms.OneTimeEventForm(prefix='onetimeevent')
				context['semesterevent_form'] = timetable_forms.SemesterEventForm(prefix='semesterevent')
				context['activity_filter_form'] = forms.ActivityFilterForm(activity_prototypes=self.activity_prototypes)

		return context

	def get_initial(self):
		initial = super(BaseCalendarView, self).get_initial()
		logger.debug('BaseCalendarView get_initial')
		if self.room:
			initial['room'] = self.room.id
		if self.user:
			initial['user'] = self.user.id
		if self.group:
			initial['group'] = self.group.id
		if self.subject:
			initial['subject'] = self.subject.id
		if self.month:
			initial['month'] = self.month
		if self.week:
			initial['week'] = self.week
		if self.day:
			initial['day'] = datetime.date.fromordinal(self.day).strftime(settings.DATE_INPUT_FORMATS[0])
		return initial

	def get_success_url(self):
		logger.debug('BaseCalendarView get_success_url')
		request_part = []
		if self.grid and 'grid' in self.matched_params:
			request_part += ["grid=%s" % self.grid.id]
		if self.month:
			request_part += ["month=%s" % self.month]
		if self.week:
			request_part += ["week=%s" % self.week]
		if self.day:
			request_part += ["day=%s" % datetime.date.fromordinal(self.day).strftime(settings.DATE_INPUT_FORMATS[0])]
		if self.room:
			request_part += ["room=%s" % self.room.id]
		if self.user:
			request_part += ["user=%s" % self.user.id]
		if self.group:
			request_part += ["group=%s" % self.group.id]
		if self.subject:
			request_part += ["subject=%s" % self.subject.id]
		return "%s%s%s" % (self.request.path, "?" if request_part else "", "&".join(request_part))



class CalendarView(BaseCalendarView):

	def __init__(self, *args, **kwargs):
		logger.debug('CalendarView init')
		super(CalendarView, self).__init__(*args, **kwargs)

	def dispatch(self, request, *args, **kwargs):
		grid_id = request.POST.get('grid') or request.GET.get('grid') or None
		self.grid = get_object_or_404(models.TimetableGrid, pk=grid_id) if grid_id else None
		return super(CalendarView, self).dispatch(request, *args, **kwargs)

	def get_initial(self):
		initial = super(CalendarView, self).get_initial()
		if self.grid:
			initial['grid'] = self.grid.id
		return initial



class SemesterTimetableView(BaseCalendarView):
	heading = 'Semester timetable'
	form_class = forms.SemesterCalendarFilterForm
	activity_prototypes = (options.AP_LECTURE, options.AP_EXERCISE)

	def __init__(self, *args, **kwargs):
		logger.debug('SemesterTimetableView init')
		super(SemesterTimetableView, self).__init__(*args, **kwargs)
		self.grid = get_object_or_404(models.TimetableGrid, pk=options.DEFAULT_SEMESTER_TIMETABLE_GRID)
		if not (self.month or self.week or self.day):
			week =  isoweek.Week.withdate(options.SEMESTER_START_DATE)
			self.week = week.monday().toordinal()



class ExaminationPeriodTimetableView(BaseCalendarView):
	heading = 'Examination period timetable'
	form_class = forms.ExaminationPeriodCalendarFilterForm
	activity_prototypes = (options.AP_EXAM, )

	def __init__(self, *args, **kwargs):
		logger.debug('ExaminationPeriodTimetableView init')
		super(ExaminationPeriodTimetableView, self).__init__(*args, **kwargs)
		self.grid = get_object_or_404(models.TimetableGrid, pk=options.DEFAULT_EXAMINATION_PERIOD_TIMETABLE_GRID)
		if not (self.month or self.week or self.day):
			week =  isoweek.Week.withdate(options.EXAMINATION_PERIOD_START_DATE)
			self.week = week.monday().toordinal()