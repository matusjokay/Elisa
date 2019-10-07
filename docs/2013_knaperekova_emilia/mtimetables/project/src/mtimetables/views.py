# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mptt import models as mptt_models

from tools import views as tools_views

from . import mixins

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'mtimetables'



class TemplateView(mixins.RouterMixin, tools_views.BaseTemplateView):
	pass



class ListView(mixins.RouterMixin, tools_views.BaseListView):
	template_name = '%s/list.html' % PACKAGENAME

	def __init__(self, *args, **kwargs):
		logger.debug('ListView init')
		super(ListView, self).__init__(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(ListView, self).get_context_data(**kwargs)
		context['is_hierarchical'] = issubclass(self.model, mptt_models.MPTTModel)
		return context



class DetailView(mixins.RouterMixin, tools_views.BaseDetailView):
	template_name = '%s/detail.html' % PACKAGENAME



class FormView(mixins.RouterMixin, tools_views.BaseFormView):
	pass



class FormSetView(mixins.RouterMixin, tools_views.BaseFormSetView):
	pass



class CreateView(mixins.FormMixin, mixins.RouterMixin, tools_views.BaseCreateView):
	pass



class UpdateView(mixins.FormMixin, mixins.RouterMixin, tools_views.BaseUpdateView):
	pass



class DeleteView(mixins.RouterMixin, tools_views.BaseDeleteView):
	template_name = '%s/confirm_delete.html' % PACKAGENAME



class ViewSet(tools_views.BaseViewSet):

	packages = [PACKAGENAME, ]

	def __init__(self, *args, **kwargs):
		logger.debug('ViewSet init')
		super(ViewSet, self).__init__(*args, **kwargs)