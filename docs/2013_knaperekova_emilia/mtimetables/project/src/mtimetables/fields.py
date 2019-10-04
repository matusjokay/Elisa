# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets as django_widgets
from django.db import models as django_models

from tools import fields as tools_fields

from . import settings as options

import logging
logger = logging.getLogger(__name__)



class PriorityField(django_models.FloatField):
	choices = options.PRIORITIES_CHOICES

	def __init__(self, *args, **kwargs):
		super(PriorityField, self).__init__(*args, **kwargs)
		self.default = options.DEFAULT_PRIORITY

	def formfield(self, **kwargs):
		kwargs['widget'] = django_widgets.RadioSelect
		return super(PriorityField, self).formfield(**kwargs)



class EvaluationMethodField(tools_fields.ChoiceField):
	choices = options.EVALUATION_METHOD_CHOICES

	def get_default(self):
		return options.DEFAULT_EVALUATION_METHOD