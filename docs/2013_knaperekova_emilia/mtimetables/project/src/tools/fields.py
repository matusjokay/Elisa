# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django import forms as django_forms
from django.forms import widgets as django_widgets

import bitfield

from . import widgets

import logging
logger = logging.getLogger(__name__)



class ChoiceField(models.PositiveIntegerField):
	
	def __init__(self, widget=None, *args, **kwargs):
		super(ChoiceField, self).__init__(*args, **kwargs)
		self.widget = widget
		if not self.has_default():
			self.default = None

	def formfield(self, **kwargs):
		kwargs['widget'] = self.widget or django_widgets.RadioSelect
		return super(ChoiceField, self).formfield(**kwargs)



class MultiSelectFormField(django_forms.MultipleChoiceField):
	pass



class MultiSelectField(models.CharField):

	def formfield(self, **kwargs):
		defaults = {
			'choices': self.choices, 
			'widget': django_forms.CheckboxSelectMultiple,
		}
		defaults.update(kwargs)
		return MultiSelectFormField(**defaults)

	def to_python(self, value):
		if isinstance(value, list):
			return value
		return value.split(",")

	def validate(self, value, model_instance):
		if not self.editable:
			# Skip validation for non-editable fields.
			return

		if self._choices and value not in self.empty_values:
			options = [key for key, val in self._choices]
			for value_part in value:
				if value_part not in options:
					raise exceptions.ValidationError(
						self.error_messages['invalid_choice'],
						code='invalid_choice',
						params={'value': value_part},
					)

		if value is None and not self.null:
			raise exceptions.ValidationError(self.error_messages['null'], code='null')

		if not self.blank and value in self.empty_values:
			raise exceptions.ValidationError(self.error_messages['blank'], code='blank')



class LinkField(django_forms.CharField):

	def __init__(self, url, name, *args, **kwargs):
		super(LinkField, self).__init__(*args, **kwargs)
		self.widget = widgets.LinkWidget(url, name)



class BitFormField(bitfield.forms.BitFormField):

	def prepare_value(self, value):
		if not value:
			return []
		try:
			return bitfield.types.BitHandler(value, [k for k, v in self.choices])
		except TypeError:
			return value



class BitField(bitfield.BitField):

	def formfield(self, form_class=BitFormField, **kwargs):
		return super(BitField, self).formfield(form_class, **kwargs)