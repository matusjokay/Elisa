# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django.forms import widgets as django_widgets
from django.forms import models as forms_models

from brutalform import models as brutalform_models
from tools import widgets as tools_widgets

from .. import settings as options
from ..timetable import models as timetable_models

from . import models

import logging
logger = logging.getLogger(__name__)



class DataBaseForm(brutalform_models.ModelForm):
	layout = 'horizontal'



class RoomForm(DataBaseForm):

	class Meta:
		model = models.Room
		fields = ['name', 'capacity', 'priority', 'parent', 'room_type', 'department']

	class Forms:
		RoomEquipmentFormSet = forms_models.inlineformset_factory(models.Room, models.RoomEquipmentConnection, extra=1)
		inlines = collections.OrderedDict([
			('equipments', RoomEquipmentFormSet),
		])
		legends = {
			'equipments': 'Equipments',
		}



class SubjectForm(DataBaseForm):

	class Meta:
		model = models.Subject
		fields = ['name', 'abbreviation', 'department', 'priority', 'parent', 'completion_mode']
		widgets = {
			'study_types': django_widgets.CheckboxSelectMultiple,
		}

	class Forms:
		class TeacherFormSet(forms_models.BaseInlineFormSet):
			def __init__(self, *args, **kwargs):
				super(SubjectForm.Forms.TeacherFormSet, self).__init__(*args, **kwargs)
				self.prefix = 'subject_teachers'
			def get_queryset(self):
				return super(SubjectForm.Forms.TeacherFormSet, self).get_queryset().exclude(relation_type=1).order_by('relation_type')
		SubjectTeacherFormSet = forms_models.inlineformset_factory(models.Subject, models.UserSubjectConnection, extra=1, formset=TeacherFormSet)
		SubjectStudyTypeFormSet = forms_models.inlineformset_factory(models.Subject, models.SubjectStudyTypeConnection, extra=1)
		inlines = collections.OrderedDict([
			('study_types', SubjectStudyTypeFormSet),
			('users', SubjectTeacherFormSet),
		])
		legends = {
			'study_types': 'Study types',
			'users': 'Teachers',
		}




class SubjectStudentsForm(DataBaseForm):

	class Meta:
		model = models.Subject
		fields = []

	class Forms:
		class StudentFormSet(forms_models.BaseInlineFormSet):
			def __init__(self, *args, **kwargs):
				super(SubjectStudentsForm.Forms.StudentFormSet, self).__init__(*args, **kwargs)
				self.prefix = 'subject_teachers'
			def get_queryset(self):
				return super(SubjectStudentsForm.Forms.StudentFormSet, self).get_queryset().filter(relation_type=1)
		SubjectStudentFormSet = forms_models.inlineformset_factory(models.Subject, models.UserSubjectConnection, extra=1, formset=StudentFormSet)
		inlines = collections.OrderedDict([
			('users', SubjectStudentFormSet),
		])
		legends = {
			'users': 'Students',
		}



class ActivityTypeForm(DataBaseForm):

	class Meta:
		model = models.ActivityType
		fields = ['name', 'prototype', 'priority', 'custom_color', 'mandatory',]
		widgets = {
			'prototype': django_widgets.RadioSelect(choices=options.ACTIVITY_PROTOTYPES),
			'custom_color': tools_widgets.ColorPicker()
		}



class ActivityDefinitionForm(DataBaseForm):

	class Meta:
		model = models.ActivityDefinition
		fields = ['name', 'activity_type', 'hours_count', 'mandatory_instances_count', 'room_capacity_rate', 'priority', 'custom_color', 'weeks', 'subjects', 'groups']
		widgets = {
			'custom_color': tools_widgets.ColorPicker()
		}

	# class Forms:
	# 	Exception: <class 'mtimetables.timetable.models.Event'> has no ForeignKey to <class 'mtimetables.data.models.ActivityDefinition'>
	#  	EventFormSet = forms_models.inlineformset_factory(models.ActivityDefinition, timetable_models.Event, extra=1)
	# 	inlines = collections.OrderedDict([
	# 		('events', EventFormSet),
	# 	])
	# 	legends = {
	# 		'events': 'Events',
	# 	}



class UserForm(DataBaseForm):

	class Meta:
		model = models.User
		fields = ['login', 'name', 'surname', 'titles_before_name', 'titles_after_name', 'priority']
		# exclude = ['requirement_packages', 'groups', 'departments']

	class Forms:
		UserGroupFormSet = forms_models.inlineformset_factory(models.User, models.UserGroupConnection, extra=1)
		UserDepartmentFormSet = forms_models.inlineformset_factory(models.User, models.UserDepartmentConnection, extra=1)
		inlines = collections.OrderedDict([
			('groups', UserGroupFormSet),
			('departments', UserDepartmentFormSet),
		])
		legends = {
			'groups': 'Groups',
			'departments': 'Departments',
		}



class ActivityDefinitionEventForm(brutalform_models.ModelForm):

	class Meta:
		model = timetable_models.Event
		fields = ['name', 'description', 'fixed', 'custom_color']