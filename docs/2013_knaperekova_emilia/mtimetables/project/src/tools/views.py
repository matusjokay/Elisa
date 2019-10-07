# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views import generic

from . import mixins

import logging
logger = logging.getLogger(__name__)



class BaseTemplateView(mixins.BaseViewMixin, generic.TemplateView):
	pass



class BaseListView(mixins.BaseViewMixin, mixins.PaginatorMixin, mixins.FilterMixin, mixins.SerializerMixin, generic.ListView):
	template_name = 'list.html'
	list_display = ('__unicode__',)
	list_display_labels = ('name',)
	current_action_type = 'list'

	@property
	def heading(self):
		return ('All %s' % self.model_verbose_name_plural)

	def __init__(self, *args, **kwargs):
		logger.debug('BaseListView init')
		super(BaseListView, self).__init__(*args, **kwargs)



class BaseDetailView(mixins.BaseViewMixin, mixins.SerializerMixin, generic.DetailView):
	template_name = 'detail.html'
	current_action_type = 'detail'

	@property
	def heading(self):
		return ('%s %s' % (self.model_verbose_name.capitalize(), self.object))

	def get_queryset(self):
		queryset = super(BaseDetailView, self).get_queryset()
		logger.debug('BaseDetailView get_queryset: %s', queryset.count())
		return queryset



class BaseFormView(mixins.BaseViewMixin, generic.edit.FormView):
	template_name = 'site-form.html'
	object_action_types = []
	model_action_types = []
	
	def get_success_url(self):
		if not self.success_url:
			return self.request.path
		else:
			return super(BaseTemplateView, self).get_success_url()



class ProcessFormSetView(generic.base.View):

	def get(self, request, *args, **kwargs):
		formset_class = self.get_formset_class()
		formset = self.get_formset(formset_class)
		return self.render_to_response(self.get_context_data(formset=formset))

	def post(self, request, *args, **kwargs):
		formset_class = self.get_formset_class()
		formset = self.get_formset(formset_class)
		if formset.is_valid():
			formset.save()
			return self.formset_valid(formset)
		else:
			return self.formset_invalid(formset)

	def put(self, *args, **kwargs):
		return self.post(*args, **kwargs)



class BaseFormSetView(mixins.BaseViewMixin, generic.base.TemplateResponseMixin, mixins.FormSetMixin, ProcessFormSetView):
	template_name = 'site-formset.html'



class BaseCreateView(mixins.BaseViewMixin, mixins.AjaxFormMixin, mixins.ModelFormMixin, generic.edit.CreateView):
	current_action_type = 'create'
	
	@property
	def heading(self):
		return ('Create %s' % self.model_verbose_name.lower())

	@property
	def success_url(self):
		return reverse(self.get_list_action().urlname)



class BaseUpdateView(mixins.BaseViewMixin, mixins.AjaxFormMixin, mixins.ModelFormMixin, generic.edit.UpdateView):
	current_action_type = 'update'

	@property
	def heading(self):
		return ('Update %s %s' % (self.model_verbose_name.lower(), self.object))
		
		

class BaseDeleteView(mixins.BaseViewMixin, generic.edit.DeleteView):
	current_action_type = 'delete'
	template_name = 'confirm_delete.html'
	heading = "Confirm deletion"

	def get_success_url(self):
		messages.success(self.request, '{0} {1} successfully deleted.'.format(self.object._meta.verbose_name.capitalize(), self.object))
		return reverse(self.get_list_action().urlname)



class BaseViewSet(object):

	view_types = 'CRUDL'
	model_action_types = ['list', 'create']
	object_action_types = ['detail', 'update', 'delete']

	def __init__(self, *args, **kwargs):
		logger.debug('BaseViewSet init with model %s', self.model)
		super(BaseViewSet, self).__init__(*args, **kwargs)