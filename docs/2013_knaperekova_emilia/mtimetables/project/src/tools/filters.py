# -*- coding: utf-8 -*-
from __future__ import unicode_literals


from django import forms as django_forms

from mptt import forms as mptt_forms

from . import constants

import logging
logger = logging.getLogger(__name__)



class ListFilter(object):

	title = None
	required = False
	multiple = False
	# template = 

	def __init__(self, request, params):
		self.request = request
		# self._matched_params_dict = {key: params[key] for key in set(params.keys()) & set(self.lookups.keys()) if params.get(key, False)}
		# self._matched_params_dict = {key: params[key] for key in set(params.keys()) & set(self.lookups.keys())}
		# self._matched_params_dict = {key: params.getlist(key) for key in set(params.keys()) & set(self.lookups.keys())}
		self._matched_params_dict = {}
		for key in set(params.keys()) & set(self.lookups.keys()):
			if self.multiple:
				self._matched_params_dict[key] = params.getlist(key) if params.get(key, False) else ()
				values = set()
				for value in self._matched_params_dict[key]:
					values.update(value.split('_'))
				self._matched_params_dict[key] = values
			else:
				self._matched_params_dict[key] = params[key] if params.get(key, False) else ''
		logger.debug('Filter %s matched_params_dict: %s', self.title, self._matched_params_dict)

	def queryset(self, request, queryset):
		"""
		Returns the filtered queryset.
		"""
		raise NotImplementedError('Subclasses of ListFilter must provide a queryset() method')

	@property
	def lookups(self):
		"""
		Must be overridden to return dictionary key: choices
		"""
		raise NotImplementedError('The SimpleListFilter.lookups() method must be overridden to return a list of tuples (value, verbose value)')

	@property
	def formfields(self):
		fields = {}
		field_class = django_forms.MultipleChoiceField if self.multiple else django_forms.ChoiceField
		for key, choices in self.lookups.items():
			fields[key] = field_class(
				required=self.required, 
				label=self.title.capitalize(), 
				choices=choices,
				help_text = ''
			)
		return fields

	@property
	def matched_params_dict(self):
		return self._matched_params_dict

	def get_values(self, param):
		if self.matched_params_dict[param] and type(self.matched_params_dict[param]) in (str, unicode):
			return (self.matched_params_dict[param],)
		return self.matched_params_dict[param] if self.matched_params_dict.get(param, False) else ()



# def list_filter_factory(title, keyword, model, lookup, multiple=False):
# 	name = str('%sFilter' % keyword.title())
# 	bases = (ListFilter,)
# 	filter_class = type(name, bases, {})
# 	filter_class.title = title
# 	filter_class.multiple = multiple
	
# 	def queryset(obj, request, queryset):
# 		for param in obj.matched_params_dict.keys():
# 			if param == keyword:
# 				value = request.GET[param]
# 				lookup_dict = {lookup: value,}
# 				queryset = queryset.filter(**lookup_dict)
# 		return queryset

# 	def lookups(obj):
# 		return {
# 			keyword: [('', 'all')] + [(obj.id, obj.name) for obj in model.objects.all()],
# 		}

# 	filter_class.queryset = queryset
# 	filter_class.lookups = property(lookups)

# 	return filter_class



class SingleParamListFilter(ListFilter):
	title = None
	key = None

	def __init__(self, *args, **kwargs):
		if not self.key:
			self.key = self.title.replace(' ', '').lower()
		super(SingleParamListFilter, self).__init__(*args, **kwargs)

	@property
	def choices(self):
		raise NotImplementedError('Subclasses of SingleParamListFilter must provide a choices property')

	@property
	def formfields(self):
		field_class = django_forms.ModelMultipleChoiceField if self.multiple else django_forms.ModelChoiceField
		field =  field_class(
			label=self.title.capitalize(), 
			required=self.required, 
			queryset=self.choices,
			# empty_label=constants.SELECT_EMPTY_LABEL
		)
		field.help_text = ''
		return {self.key: field}

	def process_values(self, values, queryset):
		raise NotImplementedError('Subclasses of SingleParamListFilter must provide a process_values() method')

	@property
	def lookups(self):
		return {self.key: self.choices}

	def queryset(self, request, queryset):
		if self.key in self.matched_params_dict.keys():
			values = self.get_values(self.key)
			logger.debug('values for %s is %s', self.key, values)
			if values:
				logger.debug('values for %s is %s', self.key, values)
				return self.process_values(values, queryset)
		return queryset



class HierarchicalParamListFilter(SingleParamListFilter):

	@property
	def formfields(self):
		field_class = mptt_forms.TreeNodeMultipleChoiceField if self.multiple else mptt_forms.TreeNodeChoiceField
		field = field_class(
			label=self.title.capitalize(), 
			required=self.required, 
			queryset=self.choices,
		)
		field.help_text = ''
		return {self.key: field}



def model_filter_factory(field_name, related_model, choices_filter=None, choices_queryset=None, multiple=False):
	name = str('%sFilter' % related_model._meta.model_name.title())

	if hasattr(related_model, 'hierarchical_str'):
		bases = (HierarchicalParamListFilter,)
	else:
		bases = (SingleParamListFilter,)

	filter_class = type(name, bases, {})
	filter_class.title = related_model._meta.verbose_name
	filter_class.key = related_model._meta.model_name
	filter_class.multiple = multiple
	
	def process_values(obj, values, queryset):
		lookup_dict = {
			'%s__in' % field_name: values,
		}
		return queryset.filter(**lookup_dict)

	def choices(obj):
		if choices_queryset:
			return choices_queryset
		if choices_filter:
			return related_model.objects.filter(**choices_filter)
		return related_model.objects.all()

	filter_class.process_values = process_values
	filter_class.choices = property(choices)

	return filter_class