# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import isoweek

from django.db.models import Q, F

import bitfield

from tools import misc as tools_misc

from .. import settings as options

from . import models

import logging
logger = logging.getLogger(__name__)



def get_conflict_semesterevents_queryset(event, day_nums, week_nums):

	logger.debug('get_conflict_semesterevents_queryset for event %s with days %s, weeks %s', event, day_nums, week_nums)

	day_bits = (getattr(models.SemesterEvent.days, 'day_%s' % i_day) for i_day in day_nums)
	week_bits = (getattr(models.SemesterEvent.weeks, 'week_%s' % i_week) for i_week in week_nums)

	days_q = Q()
	for bit in day_bits:
		days_q |= Q(days=bit)

	weeks_q = Q()
	for bit in week_bits:
		weeks_q |= Q(weeks=bit)

	start = event.start if event.model_type == 'semesterevent' else event.start.time()
	end = event.end if event.model_type == 'semesterevent' else event.end.time()

	result = models.SemesterEvent.objects.exclude(pk=event.pk).filter(
		start__lt=end,
		end__gt=start,
	).filter(days_q).filter(weeks_q)

	return result



def get_event_collisions(event):

	# TODO: groups urobit ako hierarchicke!
	# filter for onetimeevent and semesterevent common attributes
	generic_event_filter = lambda event_qs: event_qs.filter(
		Q(rooms__in=event.rooms.all()) | 
		Q(users__in=event.users.all()) | 
		Q(groups__in=event.groups.all()) | 
		Q(activities=event.activities.all())
	).distinct()

	qs_onetimeevents = False
	qs_semesterevents = False

	semester_start_week = isoweek.Week.withdate(options.SEMESTER_START_DATE)
	
	if event.model_type == 'onetimeevent':

		# build onetimeevent queryset
		qs_onetimeevents = models.OneTimeEvent.objects.exclude(pk=event.pk).filter(
			start__lt=event.end,
			end__gt=event.start
		)		

		# if event influences semester (not out of semester range), build semesterevent queryset
		if event.start.date() <= options.SEMESTER_END_DATE and event.end.date() >= options.SEMESTER_START_DATE:

			# bound event start/end by semester daterange
			start_date = event.start.date() if event.start.date() >= options.SEMESTER_START_DATE else options.SEMESTER_START_DATE
			end_date = event.end.date() if event.end.date() <= options.SEMESTER_END_DATE else options.SEMESTER_END_DATE

			# calculate days and weeks
			end_week = isoweek.Week.withdate(end_date)
			temp_week = isoweek.Week.withdate(start_date)
			day_nums = tuple(set([date.weekday() for date in tools_misc.daterange(start_date, end_date)]))
			week_nums = []
			while temp_week <= end_week:
				num = temp_week - semester_start_week
				if num >= options.SEMESTER_WEEKS_COUNT:
					break
				week_nums.append(num)
				temp_week = temp_week + 1

			if week_nums and day_nums:
				qs_semesterevents = get_conflict_semesterevents_queryset(event, day_nums, week_nums)

	elif event.model_type == 'semesterevent':

		# build semesterevents queryset
		day_nums = tuple(i for i, (key, value) in enumerate(event.days.items()) if value)
		week_nums = tuple(i for i, (key, value) in enumerate(event.weeks.items()) if value)
		qs_semesterevents = get_conflict_semesterevents_queryset(event, day_nums, week_nums)

		# build onetimeevents queryset
		dates = []
		for i_week in week_nums:
			week = semester_start_week + i_week
			for i_day in day_nums:
				dates.append(week.day(i_day))  # append i_day of week as datetime.date object, 0 is monday
		q = Q()
		for date in dates:
			start = datetime.datetime.combine(date, event.start)
			end = datetime.datetime.combine(date, event.end)
			q |= (Q(start__lt=end) & Q(end__gt=start))
		qs_onetimeevents = models.OneTimeEvent.objects.exclude(pk=event.pk).filter(q)
	
	qs_onetimeevents = list(generic_event_filter(qs_onetimeevents)) if qs_onetimeevents else []
	qs_semesterevents = list(generic_event_filter(qs_semesterevents)) if qs_semesterevents else []

	collisions = qs_onetimeevents + qs_semesterevents

	logger.debug('Event %s collisions: %s', event, ", ".join(['%s' % e for e in collisions]))

	return collisions



def get_all_collisions():
	conflict_events = dict()
	for event in list(models.OneTimeEvent.objects.all()) + list(models.SemesterEvent.objects.all()):
		collisions = get_event_collisions(event)
		if collisions:
			conflict_events[event] = collisions
	return conflict_events



def get_room_collisions(room):
	return list([get_event_collisions(event) for event in room.events])



def get_user_collisions(user):
	return list([get_event_collisions(event) for event in user.events])



def get_group_collisions(group):
	return list([get_event_collisions(event) for event in group.events])