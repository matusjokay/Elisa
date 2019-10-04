# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import isoweek
import collections

from django import forms as django_forms
from django.forms import widgets as django_widgets
from django.forms import models as django_forms_models

from mptt import forms as mptt_forms

from brutalform import models as brutalform_models
from tools import widgets as tools_widgets
from tools import constants

from .. import settings as options
from ..data import models as data_models

from . import models

import logging
logger = logging.getLogger(__name__)



class HourForm(brutalform_models.ModelForm):

	class Meta:
		widgets = {
			'from_time': tools_widgets.TimePickerFrom(), 
			'to_time': tools_widgets.TimePickerTo()
		}



class TimetableGridForm(brutalform_models.ModelForm):

	layout = 'horizontal'

	class Meta:
		model = models.TimetableGrid
		fields = ('name', 'period_prototype')
		widgets = {
			'period_prototype': django_widgets.RadioSelect(choices=options.PERIOD_PROTOTYPES),
		}

	class Forms:
		TimetableGridHourFormSet = django_forms_models.inlineformset_factory(models.TimetableGrid, models.Hour, form=HourForm, extra=1)
		inlines = collections.OrderedDict([
			('hours', TimetableGridHourFormSet),
		])
		legends = {
			'hours': 'Hours',
		}



class BaseCalendarFilterForm(django_forms.Form):
	room = django_forms.ModelChoiceField(required=False, empty_label=constants.SELECT_EMPTY_LABEL, queryset=data_models.Room.objects.all())
	group = mptt_forms.TreeNodeChoiceField(required=False, empty_label=constants.SELECT_EMPTY_LABEL, queryset=data_models.Group.objects.all())
	user = django_forms.ModelChoiceField(required=False, empty_label=constants.SELECT_EMPTY_LABEL, queryset=data_models.User.objects.all())
	subject = django_forms.ModelChoiceField(required=False, empty_label=constants.SELECT_EMPTY_LABEL, queryset=data_models.Subject.objects.all())
	month = django_forms.ChoiceField(required=False)
	week = django_forms.ChoiceField(required=False)
	day = django_forms.DateField(required=False, widget=tools_widgets.DatePicker())

	def __init__(self, *args, **kwargs):
		super(BaseCalendarFilterForm, self).__init__(*args, **kwargs)

		month_choices = [('', constants.SELECT_EMPTY_LABEL)]
		week_choices = [('', constants.SELECT_EMPTY_LABEL)]
		actual_day = options.CALENDAR_START_DATE
		actual_week = isoweek.Week.withdate(actual_day) - 1
		i_week = 0
		actual_month = 0
		while actual_day < options.CALENDAR_END_DATE:
			if actual_day.month != actual_month:
				actual_month = actual_day.month
				month_choices.append((datetime.date(actual_day.year, actual_day.month, 1).toordinal(), actual_day.strftime('%B %Y')))
			if actual_week != isoweek.Week.withdate(actual_day):
				actual_week = isoweek.Week.withdate(actual_day)
				i_week += 1
				week_choices.append((actual_week.monday().toordinal(), "{0:0=2}: {1} - {2}".format(i_week, actual_week.monday().strftime("%b %d, %Y"), actual_week.sunday().strftime("%b %d, %Y"))))
			actual_day = actual_day + datetime.timedelta(days=1)

		self.fields['month'].choices = month_choices
		self.fields['week'].choices = week_choices



class CalendarFilterForm(BaseCalendarFilterForm):
	grid = django_forms.ModelChoiceField(label='Hour set', empty_label=constants.SELECT_EMPTY_LABEL, queryset=models.TimetableGrid.objects.all())

	def __init__(self, *args, **kwargs):
		super(CalendarFilterForm, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['grid',] + self.fields.keyOrder[:-1]


	
class SemesterCalendarFilterForm(BaseCalendarFilterForm):
	pass



class ExaminationPeriodCalendarFilterForm(BaseCalendarFilterForm):
	pass



class ActivityFilterForm(django_forms.Form):
	layout = 'vertical'

	activitytype = django_forms.MultipleChoiceField(required=False)
	group = mptt_forms.TreeNodeMultipleChoiceField(required=False, queryset=data_models.Group.objects.exclude(name__in=('1', '2', '3')))
	year = django_forms.MultipleChoiceField(required=False, choices=options.STUDY_YEAR_CHOICES)
	# year = django_forms.MultipleChoiceField(required=False, choices=[('', constants.SELECT_EMPTY_LABEL)] + list(options.STUDY_YEAR_CHOICES))
	subject = django_forms.ChoiceField(required=False)
	department = django_forms.ChoiceField(required=False)

	def __init__(self, activity_prototypes, *args, **kwargs):
		logger.debug('Init ActivityFilterForm for prototypes %s', activity_prototypes)
		super(ActivityFilterForm, self).__init__(*args, **kwargs)
		
		self.fields['group'].help_text = ''
		self.fields['activitytype'].choices = [(activity_type.id, activity_type) for activity_type in data_models.ActivityType.objects.filter(prototype__in=activity_prototypes)]
		self.fields['activitytype'].initial = [choice_id for (choice_id, choice_name) in self.fields['activitytype'].choices]
		# self.fields['activitytype'].choices = [('', constants.SELECT_EMPTY_LABEL)] + [(activity_type.id, activity_type) for activity_type in data_models.ActivityType.objects.filter(prototype__in=activity_prototypes)]
		self.fields['year'].initial = [choice_id for (choice_id, choice_name) in self.fields['year'].choices]
		self.fields['subject'].choices = [('', constants.SELECT_EMPTY_LABEL)] + [(subject.id, subject) for subject in data_models.Subject.objects.exclude(parent__id__gt=0)]
		departments = [department for department in data_models.Department.objects.filter(level=1) if len(department.all_subjects) > 0]
		self.fields['department'].choices = [('', constants.SELECT_EMPTY_LABEL)] + [(department.id, department.name) for department in departments]