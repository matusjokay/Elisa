# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.test import TestCase

from .. import settings as options
from ..data import models as data_models

from . import models
from . import functions

import logging
logger = logging.getLogger(__name__)



class CollisionTestCase(TestCase):
	"""
	Test case for function mtimetables.timetable.function.get_event_collisions.
	"""

	fixtures = ['test_data.json']

	def setUp(self):
		logger.debug('Running CollisionTestCase')

	def create_events(self, prefix, periodical=False, days=None, weeks=None, **kwargs):
		# creates events distributed in time like this:
		# 07    08    09    10    11    12    13    14    15    16    17    18    19
		#                          |A---------------------------|
		#  |B---|      |C---------||D---||E---------|      |F---||G---|      |H---|
		#                    |X---------|                    |Y----|
		if days or weeks:
			periodical = True

		if periodical:
			dt = lambda h, m=0: datetime.time(h, m)
			model = models.SemesterEvent
		else:
			date = options.SEMESTER_START_DATE
			self.assertEqual(date.weekday(), 0, 'Semester start day is not Monday.')
			dt = lambda h, m=0: datetime.datetime.combine(date, datetime.time(h, m))
			model = models.OneTimeEvent

		events = {
			'a': model(start=dt(11), end=dt(16)),
			'b': model(start=dt(7), end=dt(8)),
			'c': model(start=dt(9), end=dt(11)),
			'd': model(start=dt(11), end=dt(12)),
			'e': model(start=dt(12), end=dt(14)),
			'f': model(start=dt(15), end=dt(16)),
			'g': model(start=dt(16), end=dt(17)),
			'h': model(start=dt(18), end=dt(19)),
			'x': model(start=dt(10), end=dt(12)),
			'y': model(start=dt(15, 30), end=dt(16, 30)),
		}
		for key, event in events.items():
			event.name = '%s %s %s' % ('semesterevent' if periodical else 'onetimeevent', prefix, key)
			if periodical:
				event.days = model.days.day_0
				if days:
					event.days = 0
					keys = model.days.keys()
					for i_day in days:
						self.assertGreater(len(keys), i_day, 'Mistake in test input parameters.')
						event.days |= getattr(model.days, keys[i_day])
				if weeks:
					event.weeks = 0
					keys = model.weeks.keys()
					for i_week in weeks:
						self.assertGreater(len(keys), i_week, 'Mistake in test input parameters.')
						event.weeks |= getattr(model.weeks, keys[i_week])
			event.full_clean()
			event.save()
			for key, value in kwargs.items():
				if hasattr(event, key):
					setattr(event, key, value)

		return events

	def assert_events(self, events):

		if type(events) is dict:
			events = (events,)

		for i_events_dict in events:
			result_a = set()
			result_b = set()
			result_c = set()
			result_d = set()
			result_e = set()
			result_f = set()
			result_g = set()
			result_h = set()
			result_x = set()
			result_y = set()
			for j_events_dict in events:
				result_a.update([j_events_dict['d'], j_events_dict['e'], j_events_dict['f'], j_events_dict['x'], j_events_dict['y']])
				result_c.update([j_events_dict['x']])
				result_d.update([j_events_dict['a'], j_events_dict['x']])
				result_e.update([j_events_dict['a']])
				result_f.update([j_events_dict['a'], j_events_dict['y']])
				result_g.update([j_events_dict['y']])
				result_x.update([j_events_dict['a'], j_events_dict['c'], j_events_dict['d']])
				result_y.update([j_events_dict['a'], j_events_dict['f'], j_events_dict['g']])
				if j_events_dict != i_events_dict:
					result_a.update([j_events_dict['a']])
					result_b.update([j_events_dict['b']])
					result_c.update([j_events_dict['c']])
					result_d.update([j_events_dict['d']])
					result_e.update([j_events_dict['e']])
					result_f.update([j_events_dict['f']])
					result_g.update([j_events_dict['g']])
					result_h.update([j_events_dict['h']])
					result_x.update([j_events_dict['x']])
					result_y.update([j_events_dict['y']])

			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['a'])), result_a)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['b'])), result_b)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['c'])), result_c)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['d'])), result_d)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['e'])), result_e)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['f'])), result_f)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['g'])), result_g)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['h'])), result_h)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['x'])), result_x)
			self.assertSetEqual(set(functions.get_event_collisions(i_events_dict['y'])), result_y)

	def test_onetimeevents_room(self):
		room = data_models.Room.objects.first()
		events = self.create_events('room', rooms=[room])
		self.assert_events(events)

	def test_onetimeevents_user(self):
		user = data_models.User.objects.first()
		events = self.create_events('user')
		for key, event in events.items():
			data_models.UserEventConnection.objects.create(user=user, event=event, relation_type=options.USER_EVENT_RELATION_TYPES[0][0])
		self.assert_events(events)

	def test_onetimeevents_group(self):
		group = data_models.Group.objects.get(abbreviation='B-API-BIS')
		events = self.create_events('group', groups=[group])
		self.assert_events(events)

	def test_onetimeevents_activity(self):
		activity = data_models.ActivityDefinition.objects.first()
		events = self.create_events('activity', activities=[activity])
		self.assert_events(events)

	def test_semesterevents_room(self):
		room = data_models.Room.objects.first()
		events = self.create_events('room', periodical=True, rooms=[room])
		self.assert_events(events)

	def test_semesterevents_user(self):
		user = data_models.User.objects.first()
		events = self.create_events('user', periodical=True)
		for key, event in events.items():
			data_models.UserEventConnection.objects.create(user=user, event=event, relation_type=options.USER_EVENT_RELATION_TYPES[0][0])
		self.assert_events(events)

	def test_semesterevents_group(self):
		group = data_models.Group.objects.get(abbreviation='B-API-BIS')
		events = self.create_events('group', periodical=True, groups=[group])
		self.assert_events(events)

	def test_semesterevents_activity(self):
		activity = data_models.ActivityDefinition.objects.first()
		events = self.create_events('activity', periodical=True, activities=[activity])
		self.assert_events(events)

	def test_bothevents_room(self):
		room = data_models.Room.objects.first()
		events0 = self.create_events('room', rooms=[room])
		events1 = self.create_events('room periodical day_0', periodical=True, rooms=[room])
		events2 = self.create_events('room periodical day_1', days=[1,], rooms=[room])
		self.assert_events((events0, events1))
		self.assert_events(events2)

	def test_bothevents_user(self):
		user = data_models.User.objects.first()
		events0 = self.create_events('user')
		events1 = self.create_events('user periodical day_0', periodical=True)
		events2 = self.create_events('user periodical day_1', days=[1,])
		for key, event in events0.items():
			data_models.UserEventConnection.objects.create(user=user, event=event, relation_type=options.USER_EVENT_RELATION_TYPES[0][0])
		for key, event in events1.items():
			data_models.UserEventConnection.objects.create(user=user, event=event, relation_type=options.USER_EVENT_RELATION_TYPES[0][0])
		for key, event in events2.items():
			data_models.UserEventConnection.objects.create(user=user, event=event, relation_type=options.USER_EVENT_RELATION_TYPES[0][0])
		self.assert_events((events0, events1))
		self.assert_events(events2)

	def test_bothevents_group(self):
		group = data_models.Group.objects.get(abbreviation='B-API-BIS')
		events0 = self.create_events('group', groups=[group])
		events1 = self.create_events('group periodical day_0', periodical=True, groups=[group])
		events2 = self.create_events('group periodical day_1', days=[1,], groups=[group])
		self.assert_events((events0, events1))
		self.assert_events(events2)

	def test_bothevents_activity(self):
		activity = data_models.ActivityDefinition.objects.first()
		events0 = self.create_events('activity', activities=[activity])
		events1 = self.create_events('activity periodical day_0', periodical=True, activities=[activity])
		events2 = self.create_events('activity periodical day_1', days=[1,], activities=[activity])
		self.assert_events((events0, events1))
		self.assert_events(events2)