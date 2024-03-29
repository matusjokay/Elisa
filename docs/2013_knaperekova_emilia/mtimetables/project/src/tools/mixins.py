# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import datetime
import collections

from django.core import serializers
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.views import redirect_to_login
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.template import RequestContext
from django.views import generic
from django import forms as django_forms

from mptt import forms as mptt_forms

from . import constants
from . import misc

import logging
logger = logging.getLogger(__name__)



class BaseViewMixin(object):

	"""
	Every view should inherit from the BaseViewMixin as the first class if multiple inheritance is used.
	"""

	view_types = ''
	model = None
	packages = []

	model_action_types = []
	object_action_types = []

	@property
	def model_name(self):
		return self.model._meta.model_name if self.model else None

	@property
	def model_verbose_name(self):
		return self.model._meta.verbose_name if self.model else None
	
	@property
	def model_verbose_name_plural(self):
		return self.model._meta.verbose_name_plural if self.model else None

	@property
	def model_url_name(self):
		# logger.debug('model_url_name: %s', ':'.join(self.packages + [self.model_name or '',]))
		return ':'.join(self.packages + [self.model_name or '',])

	@property
	def model_actions(self):
		return self.get_actions(self.model_action_types)

	@property
	def object_actions(self):
		return self.get_actions(self.object_action_types)

	def __init__(self, *args, **kwargs):
		logger.debug('BaseViewMixin init')
		self.matched_params = set()
		super(BaseViewMixin, self).__init__(*args, **kwargs)

		logger.debug('View attributes (BaseViewMixin init):\n\tclass: %s\n\tmodel: %s\n\tmodel name: %s\n\tmodel verbose name: %s\n\tmodel verbose name plural: %s\n\tpackages: %s', 
						self, self.model, self.model_name, self.model_verbose_name, self.model_verbose_name_plural, self.packages)

	def get_actions(self, action_types):
		actions = []
		for action_slug in action_types:
			try:
				action = getattr(self, 'get_%s_action' % action_slug)()
				if action:
					actions.append((action_slug, action))
			except AttributeError as e:
				logger.error(e)
		return collections.OrderedDict(actions)

	def get_list_action(self):
		return misc.Action(self.get_action_url_name(constants.LIST_VIEW_NAME), 'show all %s' % self.model_verbose_name_plural, constants.ICON_LIST)

	def get_create_action(self):
		return misc.Action(self.get_action_url_name(constants.CREATE_VIEW_NAME), 'add new %s' % self.model_verbose_name, constants.ICON_CREATE)

	def get_detail_action(self):
		return misc.Action(self.get_action_url_name(constants.DETAIL_VIEW_NAME), 'view %s' % self.model_verbose_name, constants.ICON_DETAIL)

	def get_update_action(self):
		return misc.Action(self.get_action_url_name(constants.UPDATE_VIEW_NAME), 'edit %s' % self.model_verbose_name, constants.ICON_UPDATE)

	def get_delete_action(self):
		return misc.Action(self.get_action_url_name(constants.DELETE_VIEW_NAME), 'delete %s' % self.model_verbose_name, constants.ICON_DELETE)

	def get_action_url_name(self, action_key):
		return '%s_%s' % (self.model_url_name, action_key)

	def is_ajax(self):
		return self.request.is_ajax() or 'ajax' in self.matched_params

	def get(self, request, *args, **kwargs):
		logger.debug('BaseViewMixin get')
		response = super(BaseViewMixin, self).get(request, *args, **kwargs)
		self.check_params()
		return response

	def check_params(self):
		logger.debug('...CHECKING URL GET PARAMETERS...')
		logger.debug('\tmatched params: %s', self.matched_params)
		if self.request.GET:
			unmatched_params = list(set(self.request.GET.dict().keys()) - self.matched_params)
			if unmatched_params:
				logger.error('\tunmatched params: %s', unmatched_params)
				logger.debug('...ERROR...')
				raise Http404('Unrecognized url parameters: %s' % ", ".join(unmatched_params))
		logger.debug('...OK...')

	def get_template_names(self):
		templates = super(BaseViewMixin, self).get_template_names()
		logger.debug('Available template paths: %s', templates)
		suffix = self.template_name_suffix if hasattr(self, 'template_name_suffix') else ""
		if self.packages and self.model_name and not self.is_ajax():
			templates = ['%s%s.html' % (self.model_url_name.replace(':', '/'), suffix),] + templates
		logger.debug('Available template paths (with autogenerated): %s', templates)
		return templates
	
	def get_context_data(self, **kwargs):
		logger.debug('BaseViewMixin get_context_data')
		context = super(BaseViewMixin, self).get_context_data(**kwargs)
		context = self.update_context(context, ['heading', 'form_text'])
		return context
	
	def update_context(self, context, variables=[]):
		for variable in variables:
			if hasattr(self, variable):
				context[variable] = getattr(self, variable)
		return context



class AuthRequiredMixin(object):

	def dispatch(self, request, *args, **kwargs):
		if not request.user.is_authenticated():
			if not request.path == '/':
				messages.error(request, 'Login required to perform the requested operation.')
			return redirect_to_login(request.get_full_path())
		return super(AuthRequiredMixin, self).dispatch(request, *args, **kwargs)



class FilterMixin(object):

	list_filter = ()

	def __init__(self, *args, **kwargs):
		logger.debug('FilterMixin init')
		super(FilterMixin, self).__init__(*args, **kwargs)
		self.active_filters = dict()
		self.available_filters = []  # filter objects

	def dispatch(self, request, *args, **kwargs):
		logger.debug('FilterMixin dispatch')

		params = self.request.GET
		for filter_class in self.list_filter:
			self.available_filters.append(filter_class(self.request, params))
		return super(FilterMixin, self).dispatch(request, *args, **kwargs)

	def get_queryset(self):
		queryset = super(FilterMixin, self).get_queryset()
		for filter_object in self.available_filters:
			queryset = filter_object.queryset(self.request, queryset)
			self.active_filters.update(**filter_object.matched_params_dict)
			self.matched_params.update(filter_object.matched_params_dict.keys())
		return queryset

	def get_context_data(self, **kwargs):
		context = super(FilterMixin, self).get_context_data(**kwargs)
		logger.debug('FilterMixin get_context_data, initial: %s', self.active_filters)

		if self.available_filters:
			context['filters_available'] = django_forms.Form(initial=self.active_filters)
			context['filters_available'].layout = 'vertical'
			logger.debug('Available filters: %s', self.available_filters)
			for filter_object in self.available_filters:
				context['filters_available'].fields.update(filter_object.formfields)

			context['filters_active'] = "&".join(['%s=%s' % (key, value) for key, value in self.active_filters.items()])

		return context



class PaginatorMixin(object):
	paginator_class = Paginator
	paginate_by = constants.PAGINATE_BY
	paginate_length = constants.PAGINATE_LENGTH
	page_kwarg = 'page'
	limit_kwarg = 'limit'

	def __init__(self, *args, **kwargs):
		logger.debug('PaginatorMixin init')
		super(PaginatorMixin, self).__init__(*args, **kwargs)

	def dispatch(self, request, *args, **kwargs):
		self.paginate_by = request.GET.get(self.limit_kwarg, self.paginate_by)
		if self.page_kwarg in request.GET.keys():
			self.matched_params.update([self.page_kwarg, ])
		if self.limit_kwarg in request.GET.keys():
			self.matched_params.update([self.limit_kwarg, ])
		return super(PaginatorMixin, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(PaginatorMixin, self).get_context_data(**kwargs)
		if self.paginate_by:
			page_range = context['paginator'].page_range
			current_page = context['page_obj'].number
			start = current_page - self.paginate_length - 1 if current_page - self.paginate_length - 1 > page_range[0] else page_range[0]-1
			end = current_page + self.paginate_length if current_page + self.paginate_length < page_range[-1] else page_range[-1]
			context['paginator_range'] = page_range[start:end]
		return context



class SerializerMixin(object):

	serializer_fields = ()

	def __init__(self, *args, **kwargs):
		logger.debug('SerializerMixin init')
		super(SerializerMixin, self).__init__(*args, **kwargs)

	def get(self, request, *args, **kwargs):
		logger.debug('SerializerMixin get')
		if self.serializer_fields:
			if request.GET.get('format', None) == 'json':
				self.matched_params.update(['format',])
				if hasattr(self, 'get_object') and self.get_object():
					queryset = [self.get_object(),]
				else:
					queryset = self.get_queryset()
					if getattr(self, 'paginate_by', None):
						page_size = self.get_paginate_by(queryset)
						paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
				data = serializers.serialize('myjson', queryset, fields=self.serializer_fields)
				return HttpResponse(data, content_type='application/json')
		return super(SerializerMixin, self).get(request, *args, **kwargs)



class AjaxFormMixin(object):

	def __init__(self, *args, **kwargs):
		logger.debug('AjaxFormMixin init')
		super(AjaxFormMixin, self).__init__(*args, **kwargs)

	def dispatch(self, request, *args, **kwargs):
		logger.debug('AjaxFormMixin dispatch')
		if request.GET.get('ajax', None):
			self.matched_params.update(['ajax',])
			self.template_name = 'site_parts/form%s.html' % ('-modal' if request.GET['ajax'] == 'modal' else '')
		return super(AjaxFormMixin, self).dispatch(request, *args, **kwargs)

	def render_to_json_response(self, context, **response_kwargs):
		data = json.dumps(context)
		response_kwargs['content_type'] = 'application/json'
		return HttpResponse(data, **response_kwargs)

	def form_invalid(self, form):
		response = super(AjaxFormMixin, self).form_invalid(form)
		if self.is_ajax():
			data = {
				'msg': render_to_string('site_parts/messages.html', {}, RequestContext(self.request)),
				'errors': form.errors,
			}
			return self.render_to_json_response(data, status=400)
		else:
			return response

	def form_valid(self, form):
		logger.debug('AjaxFormMixin form_valid is_ajax')
		response = super(AjaxFormMixin, self).form_valid(form)
		if self.is_ajax():
			data = {
				'id': self.object.pk if self.object else None,
				'msg': render_to_string('site_parts/messages.html', {}, RequestContext(self.request)),
				'object_str': '%s' % self.object if self.object else None,
			}
			data_json = json.dumps(data)
			if self.object and hasattr(self.object, 'serializer_fields'):
				object_json = serializers.serialize('myjson', [self.object], fields=self.object.serializer_fields)
				data_json = data_json[:-1] + ', \"object_json\": ' + object_json[1:-1] + data_json[-1]
			return HttpResponse(data_json, content_type='application/json')
		else:
			return response



class ModelFormMixin(object):
	template_name = 'site-form.html'

	@property
	def success_message(self):
		if hasattr(self, 'object') and self.object:
			if isinstance(self.object, get_user_model()) and self.object == self.request.user:
				message = 'Profile successfully updated.'
			else:
				message = '{0} {1} successfully saved.'.format(self.object._meta.verbose_name.capitalize(), self.object)
		else:
			message = 'New {0} successfully created.'.format(self.model._meta.verbose_name.lower())
		return message
		
	@property
	def error_message(self):
		if hasattr(self, 'object') and self.object:
			if isinstance(self.object, get_user_model()) and self.object == self.request.user:
				message = 'Profile could not be updated.'
			else:
				message = '{0} {1} could not be saved.'.format(self.model._meta.verbose_name.capitalize(), self.object)
		else:
			message = '{0} could not be created.'.format(self.model._meta.verbose_name.capitalize())
		message += ' Check the field errors.'
		return message

	def __init__(self, *args, **kwargs):
		logger.debug('ModelFormMixin init')
		super(ModelFormMixin, self).__init__(*args, **kwargs)

	def form_valid(self, form):
		messages.success(self.request, self.success_message)
		return super(ModelFormMixin, self).form_valid(form)

	def form_invalid(self, form):
		messages.error(self.request, self.error_message)
		return super(ModelFormMixin, self).form_invalid(form)

	def get_success_url(self):
		if not self.success_url:
			return self.request.get_full_path()
		else:
			return super(ModelFormMixin, self).get_success_url()


class FormSetMixin(generic.base.ContextMixin):
	formset_class = None
	formset_queryset = None
	success_url = None
	prefix = None

	def get_prefix(self):
		return self.prefix

	def get_formset_class(self):
		return self.formset_class

	def get_formset(self, formset_class):
		return formset_class(**self.get_formset_kwargs())

	def get_formset_queryset(self):
		return self.formset_queryset

	def get_formset_kwargs(self):
		kwargs = {
			'prefix': self.get_prefix(),
			'queryset': self.get_formset_queryset(),
		}

		if self.request.method in ('POST', 'PUT'):
			kwargs.update({
				'data': self.request.POST,
				'files': self.request.FILES,
			})
		return kwargs

	def get_success_url(self):
		if self.success_url:
			return force_text(self.success_url)  # Forcing possible reverse_lazy evaluation
		else:
			return self.request.get_full_path()

	def formset_valid(self, formset):
		return HttpResponseRedirect(self.get_success_url())

	def formset_invalid(self, formset):
		return self.render_to_response(self.get_context_data(formset=formset))