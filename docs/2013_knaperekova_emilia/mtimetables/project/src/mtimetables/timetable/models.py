# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.core.exceptions import ValidationError

from tools import fields as tools_fields

from .. import settings as options

import logging
logger = logging.getLogger(__name__)



# TODO: validacia, ze event musi mat nastavene aspon jedno z name a activities
class Event(models.Model):
	name = models.CharField(max_length=options.NAME_LENGTH, blank=True)
	description = models.TextField(blank=True)
	fixed = models.BooleanField(default=False)
	custom_color = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)
	content_type = models.ForeignKey(ContentType, editable=False)
	
	activities = models.ManyToManyField('data.ActivityDefinition', related_name='events', null=True, blank=True)
	groups = models.ManyToManyField('data.Group', related_name='events', null=True, blank=True)
	rooms = models.ManyToManyField('data.Room', related_name='events', blank=True, null=True)
	users = models.ManyToManyField('data.User', through='data.UserEventConnection', related_name='events', null=True, blank=True)

	serializer_fields = ('auto_name', 'model_type', 'color', 'fixed', 'start', 'end', 'week_numbers', 'day_numbers', ('rooms', 'id', 'name', 'capacity'))

	# @staticmethod
	# def __new__(cls, *args, **kwargs):
	# 	logger.debug('Event.__new__ for class %s', cls)
	# 	if cls == Event:
	# 		ct = ContentType.objects.get(pk=args[5])
	# 		logger.debug('content type %s', ct)
	# 		instance = ct.model_class().objects.get(pk=args[0])
	# 		logger.debug('created new instance %s', instance)
	# 		return instance
	# 	logger.debug('will call models.Model.__new__ on cls %s', cls)
	# 	return models.Model.__new__(cls)
		# return cls.__new__(cls)
		# return super(models.Model, cls).__new__(cls)
		# return super(Event, cls).__new__(cls)

	def __init__(self, *args, **kwargs):
		logger.debug('Event init %s %s', args, kwargs)
		super(Event, self).__init__(*args, **kwargs)

	@property
	def color(self):
		return self.custom_color or (self.activities.first().color if self.activities.all() else '')

	@property
	def auto_name(self):
		if self.name:
			return '%s' % self.name
		return self.get_activities_str()

	# @property
	# def capacity(self):
	# 	capacity = 0
	# 	for room in self.rooms.all():
	# 		capacity += room.capacity
	# 	return capacity

	@property
	def model_type(self):
		"""Return string representation of event type (onetimeevent or semesterevent)."""
		return self.content_type.model

	def __unicode__(self):
		return self.auto_name

	def get_activities_str(self):
		return ", ".join(['%s' % a for a in self.activities.all()])

	def get_rooms_str(self):
		return ", ".join(['%s' % r for r in self.rooms.all()])


	def get_info(self):
		raise NotImplementedError("Subclasses of Event should implement get_info()!")

	def get_occurences(self):
		raise NotImplementedError("Subclasses of Event should implement get_occurences()!")

	def clean(self):
		# additional validation
		# print('ACTIVITIES', self.activities.count(), self.activities.all())  # TODO many to many does not work
		# if not self.name and self.activities.count() < 1:
		# 	raise ValidationError('Event must have not empty name or activities.')
		if self.start >= self.end:
			raise ValidationError('Event start has to be before event end.')

	def save(self, *args, **kwargs):
		# set additional attributes
		if not hasattr(self, 'content_type') or not self.content_type:
			self.content_type = ContentType.objects.get_for_model(self)
		super(Event, self).save(*args, **kwargs)



class OneTimeEvent(Event):
	start = models.DateTimeField(verbose_name='from')
	end = models.DateTimeField(verbose_name='to')
	holiday = models.BooleanField(default=False)

	def __unicode__(self):
		return self.auto_name

	def get_occurences(self):
		return [(self.start, self.end),]

	def get_info(self):
		info = [
			('from', self.start),
			('to', self.end),
			('holiday', 'yes' if self.holiday else 'no'),
		]
		return info



class SemesterEvent(Event):
	start = models.TimeField(verbose_name='from')
	end = models.TimeField(verbose_name='to')
	days = tools_fields.BitField(flags=options.DAYS_CHOICES)
	weeks = tools_fields.BitField(flags=options.WEEKS_CHOICES, default=options.DEFAULT_WEEKS)

	@property
	def week_numbers(self):
		return tuple(i for i, (k, v) in enumerate(self.weeks.items()) if v)

	@property
	def day_numbers(self):
		return tuple(i for i, (k, v) in enumerate(self.days.items()) if v)

	def __init__(self, *args, **kwargs):
		logger.debug('SemesterEvent init')
		super(SemesterEvent, self).__init__(*args, **kwargs)

	def __unicode__(self):
		return self.auto_name

	def get_occurences(self):
		raise NotImplementedError("Not yet implemented: get_occurences() in SemesterEvent.")

	def get_info(self):
		info = [
			('from', self.start),
			('to', self.end),
			('days', ', '.join(list([unicode(self.days.get_label(i)) for i, item in enumerate(self.days.items()) if item[1]])) if self.days else 'undefined'),
			('weeks', ', '.join(list([unicode(self.weeks.get_label(i)) for i, item in enumerate(self.weeks.items()) if item[1]])) if self.weeks else 'undefined'),
		]
		return info



"""
class ConfigEvent(Event)
	date = models.DateField()
	substitution_date = models.DateField(null=True, blank=True)
	substitution_weekday = models.PositiveIntegerField(null=True, blank=True)
	fixed = models.BooleanField(default=True, editable=False)
	holiday = models.BooleanField(default=True)
	keyword (semester_start, semester_end...)

"""