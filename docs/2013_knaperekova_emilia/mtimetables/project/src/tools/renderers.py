# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms as django_forms

from bootstrap3 import renderers as bootstrap_renderers
from bootstrap3.bootstrap import get_bootstrap_setting



class FieldRenderer(bootstrap_renderers.FieldRenderer):

	def get_label(self):
		if isinstance(self.widget, django_forms.CheckboxInput):
			label = None
		else:
			label = self.field.label
		if self.layout == 'horizontal' and not label:
			return False
		return label

	def get_field_class(self):
		if not self.field.label:
			return ''
		field_class = self.field_class
		if not field_class and self.layout == 'horizontal':
			field_class = get_bootstrap_setting('horizontal_field_class')
		return field_class