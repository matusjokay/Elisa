# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.serializers import json
from django.utils import six
from django.utils.encoding import smart_text
from django.conf import settings

import bitfield

import logging
logger = logging.getLogger(__name__)



class Serializer(json.Serializer):
	
	def __init__(self, *args, **kwargs):
		logger.debug('Using custom serializer class for json')
		super(Serializer, self).__init__(*args, **kwargs)
		self._date_format = settings.DATE_INPUT_FORMATS[0] if settings.DATE_INPUT_FORMATS else '%Y-%m-%d'
		self._time_format = settings.TIME_INPUT_FORMATS[0] if settings.TIME_INPUT_FORMATS else '%H:%M'
		self._datetime_format = self._date_format + ' ' + self._time_format

	def serialize(self, queryset, **options):
		"""
		Serialize a queryset.
		Inspired by https://github.com/django/django/blob/stable/1.6.x/django/core/serializers/base.py#L29
		"""
		self.options = options

		self.stream = options.pop("stream", six.StringIO())
		self.selected_fields = options.pop("fields", ())
		self.use_natural_keys = options.pop("use_natural_keys", False)

		self.start_serialization()
		self.first = True

		print(queryset)
		for obj in queryset:
			self.start_object(obj)

			obj = self.handle_object(obj)

			for attrname in self.selected_fields:
				self.handle_attr(obj, attrname)

			self.end_object(obj)
			if self.first:
				self.first = False
		self.end_serialization()
		return self.getvalue()

	def get_m2m_attr(self, obj, m2m_attr, attrs):
		m2m_value = []
		related_objs = getattr(obj, m2m_attr, [])
		for related_obj in related_objs.all():
			obj_values = dict()
			for attrname in attrs:
				if type(attrname) in (tuple, list):
					obj_values[attrname[0]] = self.get_m2m_attr(related_obj, attrname[0], attrname[1:])
				else:
					related_obj = self.handle_object(related_obj)
					value = getattr(related_obj, attrname, '')
					obj_values[attrname] = self.handle_value(value)
			m2m_value.append(obj_values)
		return m2m_value

	def handle_attr(self, obj, attrname):
		if type(attrname) in (tuple, list):
			self._current[attrname[0]] = self.get_m2m_attr(obj, attrname[0], attrname[1:])
		else:
			value = getattr(obj, attrname, '')
			# if callable(value):
			# 	value = value()
			self._current[attrname] = self.handle_value(value)

	def handle_value(self, value):
		if type(value) == datetime.date:
			value = value.strftime(self._date_format)
		elif type(value) == datetime.time:
			value = value.strftime(self._time_format)
		elif type(value) == datetime.datetime:
			value = value.strftime(self._datetime_format)
		elif type(value) == bitfield.types.BitHandler:
			# value = list(i+1 for i, (key, val) in enumerate(value.items()) if val)
			value = list(key for key, val in value.items() if val)
		return value

	def handle_object(self, obj):
		# TODO:
		# ATTENTION: this is only temporary solution for serialization of event objects!
		try:
			obj = getattr(obj, obj.content_type.model)
			logger.debug('...serializing obj with changed content type %s', obj)
		except AttributeError:
			logger.debug('...serializing obj %s', obj)
		return obj

	def get_dump_object(self, obj):
		base_dict = {
			"id": smart_text(obj._get_pk_val(), strings_only=True),
			# "model": smart_text(obj._meta),
			# "fields": self._current
		}
		base_dict.update(self._current)
		return base_dict


Deserializer = json.Deserializer
DjangoJSONEncoder = json.DjangoJSONEncoder
DateTimeAwareJSONEncoder = json.DateTimeAwareJSONEncoder