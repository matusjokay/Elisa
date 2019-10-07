# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import collections

from django.conf import settings
from django.forms import models as django_forms_models

from brutalform import models as brutalform_models
from tools import widgets as tools_widgets

from .. import settings as options
from ..data import models as data_models

from . import models



class EventForm(brutalform_models.ModelForm):

	layout = 'horizontal'

	class Meta:
		model = models.Event
		exclude = ['users']

	class Forms:
		EventUserFormSet = django_forms_models.inlineformset_factory(models.Event, data_models.UserEventConnection, extra=1)
		inlines = collections.OrderedDict([
			('users', EventUserFormSet),
		])
		legends = {
			'users': 'Users',
		}



class OneTimeEventForm(EventForm):

	class Meta:
		model = models.OneTimeEvent
		# exclude = ['users',]
		fields = ['name', 'description', 'start', 'end', 'custom_color', 'fixed', 'holiday', 'activities', 'rooms', 'groups']
		widgets = {
			'start': tools_widgets.DatetimeWidgetFrom(),
			'end': tools_widgets.DatetimeWidgetTo(),
			'custom_color': tools_widgets.ColorPicker(),
		}



class SemesterEventForm(EventForm):

	class Meta:
		model = models.SemesterEvent
		# exclude = ['users']
		fields = ['name', 'description', 'start', 'end', 'days', 'weeks', 'custom_color', 'fixed', 'activities', 'rooms', 'groups']
		widgets = {
			'start': tools_widgets.TimePickerFrom(),
			'end': tools_widgets.TimePickerTo(),
			'custom_color': tools_widgets.ColorPicker(),
		}



class RoomEventForm(brutalform_models.ModelForm):

	layout = 'horizontal'

	class Meta:
		model = models.SemesterEvent
		exclude = ['users',]
		# fields = ['name', 'description', 'from_time', 'to_time', 'days', 'weeks', 'fixed']

	def __init__(self, room=None, *args, **kwargs):
		super(RoomEventForm, self).__init__(*args, **kwargs)
		self.room = room

	def save(self, commit=True):
		instance = super(RoomEventForm, self).save(commit)
		if self.room:
			instance.rooms = {self.room}
			instance.save()
		return instance