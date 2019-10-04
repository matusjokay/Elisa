# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import calendar
import isoweek

from django.core import serializers

from tools import misc

from .. import settings as options
from ..timetable import models as timetable_models
from ..timetable import views as timetable_views

import logging
logger = logging.getLogger(__name__)



class CalendarCell(object):

	HOUR = 0
	DAY = 1

	@property
	def date(self):
		return self.datetime_from.date()

	@property
	def time_from(self):
		return self.datetime_from.time()

	@property
	def time_to(self):
		return self.datetime_to.time()

	@property
	def weekday(self):
		return self.date.weekday()

	@property
	def grid_type(self):
		delta = self.datetime_to - self.datetime_from
		if delta.seconds < (23*60*60):
			return CalendarCell.HOUR
		return CalendarCell.DAY

	@property
	def events(self):
		# return []
		if self._events is not None:
			return self._events

		# TODO Django 1.7: use prefetch objects to reduce number of queries 
		# https://docs.djangoproject.com/en/dev/ref/models/queries/#prefetch-objects
		one_time_events_qs = timetable_models.OneTimeEvent.objects.all()
		semester_events_qs = timetable_models.SemesterEvent.objects.all()

		if self.room:
			one_time_events_qs = one_time_events_qs.filter(rooms__in=[self.room, ])
			semester_events_qs = semester_events_qs.filter(rooms__in=[self.room, ])
		if self.user:
			# TODO: include also not directly assigned users
			one_time_events_qs = one_time_events_qs.filter(users__in=[self.user, ])
			semester_events_qs = semester_events_qs.filter(users__in=[self.user,])
		if self.group:
			# TODO: include also not directly assigned groups
			one_time_events_qs = one_time_events_qs.filter(groups__in=[self.group, ])
			semester_events_qs = semester_events_qs.filter(groups__in=[self.group,])
		if self.subject:
			one_time_events_qs = one_time_events_qs.filter(activities__in=list(self.subject.activity_definitions.all()))
			semester_events_qs = semester_events_qs.filter(activities__in=list(self.subject.activity_definitions.all()))
		
		one_time_events_qs = one_time_events_qs.filter(start__lt=self.datetime_to, end__gt=self.datetime_from)

		events = list(one_time_events_qs)

		i_week = isoweek.Week.withdate(self.date) - isoweek.Week.withdate(options.SEMESTER_START_DATE)
		if 0 <= i_week < options.SEMESTER_WEEKS_COUNT:
			i_day = self.date.weekday()
			week_bit = getattr(timetable_models.SemesterEvent.weeks, 'week_%s' % i_week)
			day_bit = getattr(timetable_models.SemesterEvent.days, 'day_%s' % i_day)
			semester_events_qs = semester_events_qs.filter(weeks=week_bit, days=day_bit, start__lt=self.datetime_to.time(), end__gt=self.datetime_from.time())
			events += list(semester_events_qs)

		self._events = events
		return self._events

	def __init__(self, datetime_from, datetime_to, room=None, user=None, group=None, subject=None):
		self._events = None
		self.datetime_from = datetime_from
		self.datetime_to = datetime_to
		self.room = room
		self.user = user
		self.group = group
		self.subject = subject

		if self.grid_type == CalendarCell.DAY:
			self.label = self.date.day

	def is_holiday(self):
		for event in self.events:
			if getattr(event, 'holiday', False):
				return True
		return False

	def is_weekend(self):
		return self.weekday in options.WEEKDAYS

	def __unicode__(self):
		return '%s' % self.date


class Calendar(object):

	DAY = 1
	WEEK = 2
	MONTH = 3

	class _meta:
		verbose_name = 'calendar'
		verbose_name_plural = 'calendar'

	def __init__(self, date_from, date_to, hours, room=None, user=None, group=None, subject=None):
		
		logger.debug('Calendar init from %s to %s', date_from, date_to)

		self.firstweekday = calendar.firstweekday()
		self.date_from = date_from
		self.date_to = date_to
		self.hours = hours
		self.room = room
		self.user = user
		self.group = group
		self.subject = subject

		self._cells = []
		self._json_events = []

		# set view type
		delta = self.date_to - self.date_from
		if delta.days == 0:
			self.view_type = Calendar.DAY
		elif delta.days < 7:
			self.view_type = Calendar.WEEK
		else:
			self.view_type = Calendar.MONTH

	def row_labels(self):
		if not self.hours or self.view_type>Calendar.WEEK:
			return False
		return ["%s<br />(%s - %s)" % (hour.name, hour.from_time.strftime("%H:%M"), hour.to_time.strftime("%H:%M")) for hour in self.hours]

	def column_labels(self):
		if self.view_type == Calendar.DAY:
			return [self.date_from.strftime("%A, %b. %d"),]
		elif self.view_type == Calendar.WEEK:
			return [date.strftime("%A,<br />%b. %d") for date in misc.daterange(self.date_from, self.date_to)] # TODO: format v sablone
		return calendar.day_name

	def rows(self):
		logger.debug('Calendar: room: %s, user: %s, group: %s, subject: %s', self.room, self.user, self.group, self.subject)

		if self.view_type == Calendar.MONTH:
			month_calendar = calendar.Calendar(self.firstweekday).monthdatescalendar(self.date_from.year, self.date_from.month)
			month_cells = []
			for row in month_calendar:
				month_row_cells = []
				for date in row:
					datetime_from = datetime.datetime.combine(date, datetime.time(0,0))
					datetime_to = datetime.datetime.combine(date, datetime.time(23,59))
					month_row_cells.append(CalendarCell(datetime_from, datetime_to, room=self.room, user=self.user, group=self.group, subject=self.subject))
				self._cells += month_row_cells
				month_cells.append(month_row_cells)
			return month_cells

		elif self.view_type == Calendar.WEEK:
			week_cells = []
			for hour in self.hours:
				week_row_cells = []
				for date in misc.daterange(self.date_from, self.date_to):
					datetime_from = datetime.datetime.combine(date, hour.from_time)
					datetime_to = datetime.datetime.combine(date, hour.to_time)
					week_row_cells.append(CalendarCell(datetime_from, datetime_to, room=self.room, user=self.user, group=self.group, subject=self.subject))
				self._cells += week_row_cells
				week_cells.append(week_row_cells)
			return week_cells

		elif self.view_type == Calendar.DAY:
			day_cells = []
			for hour in self.hours:
				datetime_from = datetime.datetime.combine(self.date_from, hour.from_time)
				datetime_to = datetime.datetime.combine(self.date_from, hour.to_time)
				day_row_cells = [CalendarCell(datetime_from, datetime_to, room=self.room, user=self.user, group=self.group, subject=self.subject)]
				self._cells += day_row_cells
				day_cells.append(day_row_cells)
			return day_cells

	@property
	def json_events(self):
		""" Attention: use this after rows() call. """
		if not self._json_events:
			events = set()
			for cell in self._cells:
				events.update(cell.events)
			events = tuple(events)
			fields = list(timetable_views.EventViewSet.serializer_fields)
			self._json_events = serializers.serialize('myjson', events, fields=fields)
		return self._json_events