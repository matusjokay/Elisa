# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.forms import widgets as django_widgets

from tools import widgets as tools_widgets

from .. import settings as options
from ..requirements import models as requirements_models

from . import widgets

import logging
logger = logging.getLogger(__name__)



class SemesterCalendar(requirements_models.RequirementModuleBase):
	description = "Calendar with time preferences."
	# text = ""
	evaluation_methods = ""

	class Meta:
		proxy = True
		verbose_name = "semester calendar"

	@classmethod
	def get_widget(self):
		return widgets.TableInput(django_widgets.Select(choices=options.TIME_PRIORITIES_CHOICES), 5, 12, 
			row_labels=[i+1 for i in range(5)], 
			col_labels=[i+1 for i in range(12)], 
			label='Time priorities'
		)


class ExaminationPeriodCalendar(requirements_models.RequirementModuleBase):
	description = "Calendar with time preferences during examination period."
	# text = ""
	evaluation_methods = ""

	class Meta:
		proxy = True
		verbose_name = "examination period calendar"

	@classmethod
	def get_widget(self):
		daterange = lambda d1, d2: (d1 + datetime.timedelta(days=i) for i in range((d2 - d1).days + 1))
		n_days = (options.EXAMINATION_PERIOD_END_DATE - options.EXAMINATION_PERIOD_START_DATE).days
		return widgets.TableInput(django_widgets.Select(choices=options.TIME_PRIORITIES_CHOICES), n_days, 4, 
			row_labels=[d.strftime("%a, %b %d") for d in daterange(options.EXAMINATION_PERIOD_START_DATE, options.EXAMINATION_PERIOD_END_DATE)], 
			col_labels=[i+1 for i in range(4)], 
			label='Time priorities'
		)


class MaxTransfersBetweenBulildings(requirements_models.RequirementModuleBase):
	description = "The maximum number of transfers between buildings per day/week."
	# text = ""
	evaluation_methods = ""	

	_count = ""
	_type = "" # D - for per day, W - form per week

	@property
	def values(self):
		return self._count + "," + self._type
	@values.setter
	def values(self, value):
		s = value.split(",")
		self._count = s[0] or 0
		self._type = s[1] or ''

	class Meta:
		proxy = True
		verbose_name = "max transfers between buildings"

	@classmethod
	def get_widget(self): 
		return tools_widgets.BaseMultiWidget(
			widgets = [django_widgets.NumberInput, django_widgets.RadioSelect(choices=(('day', 'per day'), ('week', 'per weeek')))], 
			labels = ['Count', 'Type'],
		)


class LunchBreak(requirements_models.RequirementModuleBase):
	description = "Any break (with defined length) in selected time interval. Ideal for lunch break."
	# text = ""
	evaluation_methods = ""

	class Meta:
		proxy = True
		verbose_name = "lunch break"

	@classmethod
	def get_widget(self):
		return tools_widgets.BaseMultiWidget(
			widgets = [django_widgets.NumberInput, tools_widgets.TimePickerFrom(), tools_widgets.TimePickerTo()], 
			labels = ['Minimal length [minutes]', 'Time from', 'Time to'],
		)
