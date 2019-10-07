# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json

from django.core import serializers
from django.shortcuts import get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.conf import settings
from django.template.loader import render_to_string
from django.template import RequestContext
from django.contrib import messages

from tools import filters as tools_filters
from tools import misc as tools_misc
from tools import constants

from .. import views as mtimetables_views
from ..data import models as data_models

from . import models
from . import forms
from . import functions

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'timetable'



class TimetableIndex(mtimetables_views.TemplateView):
	template_name = 'mtimetables/timetable/index.html'



class CollisionView(mtimetables_views.TemplateView):
	heading = 'Collisions'
	template_name = 'mtimetables/timetable/collision_list.html'

	def get_context_data(self, **kwargs):
		context = super(CollisionView, self).get_context_data(**kwargs)
		context['object_list'] = functions.get_all_collisions()
		return context



class EventCollisionView(mtimetables_views.TemplateView):
	template_name = 'mtimetables/timetable/event_collision_list.html'

	def get_context_data(self, **kwargs):
		event_id = kwargs['pk']
		event_id = int(event_id)
		event = get_object_or_404(models.Event, pk=event_id)
		concrete_event = get_object_or_404(event.content_type.model_class(), pk=event_id)

		self.heading = 'Event %s collisions' % concrete_event

		context = super(EventCollisionView, self).get_context_data(**kwargs)
		context['event_collisions'] = functions.get_event_collisions(concrete_event)
		return context

	def render_to_response(self, context, **response_kwargs):
		if self.is_ajax():
			collisions = list(context['event_collisions'])
			collisions_json = serializers.serialize('myjson', collisions, fields=models.Event.serializer_fields)
			return HttpResponse(collisions_json, content_type="application/json")
		else:
			return super(EventCollisionView, self).render_to_response(context, **response_kwargs)

 

class EventViewSet(mtimetables_views.ViewSet):
	model = models.Event
	view_types = 'UDL'
	model_action_types = ('list',)
	object_action_types = ('update', 'delete')
	# try to serialize also event specific fields (onetimeevent and semesterevent)
	# TODO: remove event specific fields when events inheritance changed
	serializer_fields = ('auto_name', 'model_type', 'color', 'fixed', 'start', 'end', 'week_numbers', 'day_numbers', ('rooms', 'id', 'name', 'capacity'))
	list_display = ('__unicode__', 'model_type')
	list_display_labels = ('name', 'type')
	list_filter = (tools_filters.model_filter_factory('activities', data_models.ActivityDefinition),)



class EventUpdateView(mtimetables_views.UpdateView):
	model = models.Event
	model_action_types = []
	object_action_types = []

	# TODO: podla content typu vratit konkretny podla content typu
	def get_event_by_id(self, id):
		try:
			event = models.OneTimeEvent.objects.get(pk=id)
		except models.OneTimeEvent.DoesNotExist:
			try:
				event = models.SemesterEvent.objects.get(pk=id)
			except models.SemesterEvent.DoesNotExist:
				raise Http404
		return event

	def get(self, request, *args, **kwargs):  # redirecto to one time or semester event update page
		event = self.get_event_by_id(kwargs['pk'])
		return redirect('mtimetables:timetable:%s_update' % event._meta.model_name, pk=kwargs['pk'])

	def post(self, request, *args, **kwargs):  # get proper event instance and update date and time
		# TODO: mozno by sa dali pouzit F objects - urychlenie
		# https://docs.djangoproject.com/en/dev/ref/models/queries/#f-expressions

		logger.debug('Move existing event with POST data: %s', request.POST)
		
		event = self.get_event_by_id(kwargs['pk'])

		if event.model_type == 'semesterevent':
			event.start = datetime.datetime.strptime(request.POST.get('%s-start' % event.model_type), settings.TIME_INPUT_FORMATS[0]).time()
			event.end = datetime.datetime.strptime(request.POST.get('%s-end' % event.model_type), settings.TIME_INPUT_FORMATS[0]).time()
			event.days = 0
			event.weeks = 0
			for day in request.POST.getlist('%s-days' % event.model_type):
				event.days |= getattr(models.SemesterEvent.days, day)
			for week in request.POST.getlist('%s-weeks' % event.model_type):
				event.weeks |= getattr(models.SemesterEvent.weeks, week)
			logger.debug('Setting semesterevent days: %s and weeks: %s', event.days, event.weeks)
		else:
			date_from = datetime.datetime.strptime(request.POST.get('%s-start_0' % event.model_type), settings.DATE_INPUT_FORMATS[0]).date()
			time_from = datetime.datetime.strptime(request.POST.get('%s-start_1' % event.model_type), settings.TIME_INPUT_FORMATS[0]).time()
			date_to = datetime.datetime.strptime(request.POST.get('%s-end_0' % event.model_type), settings.DATE_INPUT_FORMATS[0]).date()
			time_to = datetime.datetime.strptime(request.POST.get('%s-end_1' % event.model_type), settings.TIME_INPUT_FORMATS[0]).time()
			event.start = datetime.datetime.combine(date_from, time_from)
			event.end = datetime.datetime.combine(date_to, time_to)

		rooms_ids = request.POST.getlist('%s-rooms' % event.model_type)
		if rooms_ids:
			event.rooms = []
		for room_id in rooms_ids:
			room = get_object_or_404(data_models.Room, pk=room_id)
			event.rooms.add(room)

		event.full_clean()
		event.save()

		# collisions = list(functions.get_event_collisions(event))
		# collisions_json = serializers.serialize('myjson', collisions, fields=event.serializer_fields)

		# if collisions:
		# 	messages.warning(self.request, 'Event update caused collision.')
		# else:
		messages.success(self.request, 'Event successfully updated.')

		response_data = {
			'msg': render_to_string('site_parts/messages.html', {}, RequestContext(self.request)),
		}
		response_data_json = json.dumps(response_data)
		# response_data_json = response_data_json[:-1] + ', \"collisions\": ' + collisions_json + response_data_json[-1]

		return HttpResponse(response_data_json, content_type="application/json")



class BaseEventViewSet(mtimetables_views.ViewSet):
	list_display = ('name', 'get_activities_str', 'get_rooms_str')
	list_display_labels = ('name', 'activities', 'rooms')
	list_filter = EventViewSet.list_filter
	
	@property
	def object_action_types(self):
		return ['collisions'] + super(BaseEventViewSet, self).object_action_types

	def get_collisions_action(self):
		return tools_misc.Action('mtimetables:timetable:event_collision_list', 'collisions', constants.ICON_COLLISIONS)


class SemesterEventViewSet(BaseEventViewSet):
	form_class = forms.SemesterEventForm


class OneTimeEventViewSet(BaseEventViewSet):
	form_class = forms.OneTimeEventForm