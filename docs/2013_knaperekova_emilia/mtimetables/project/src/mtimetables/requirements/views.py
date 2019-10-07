# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import inspect

from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType

from tools import filters as tools_filters
from tools import misc as tools_misc
from tools import constants

from .. import settings as options
from .. import views as mtimetables_views
from .. import requirementmodules  # this import is because of install requirement types
from ..data import views as data_views
from ..data import models as data_models

from . import functions
from . import forms
from . import models

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'requirements'



class RequirementsIndex(mtimetables_views.TemplateView):
	template_name = 'mtimetables/requirements/index.html'



class RequirementPackageViewSet(mtimetables_views.ViewSet):
	form_class = forms.RequirementPackageForm

	class PackageTypeFilter(tools_filters.ListFilter):
		title = 'package type'

		def queryset(self, request, queryset):
			for param in self.matched_params_dict.keys():
				if param == 'type':
					value = request.GET[param]
					queryset = queryset.filter(requirement_package_type=value)
			return queryset

		@property
		def lookups(self):
			return {
				'type': [('', constants.SELECT_EMPTY_LABEL)] + list(options.REQUIREMENT_PACKAGE_TYPES),
			}

	list_filter = (PackageTypeFilter,)



class ObjectRequirementsView(mtimetables_views.ViewSet, mtimetables_views.UpdateView):
	form_class = forms.ObjectRequirementsForm
	template_name = 'mtimetables/requirements/requireobject_form.html'
	packages = ['mtimetables', 'data']
	current_action_type = 'requirements'
	# model_name = 'requireobject'

	def __init__(self, *args, **kwargs):
		logger.debug('ObjectRequirementsView init')
		super(ObjectRequirementsView, self).__init__(*args, **kwargs)

	@property
	def heading(self):
		return 'Requirements of %s' % self.object

	def dispatch(self, request, *args, **kwargs):
		content_type = get_object_or_404(ContentType, app_label='data', model=kwargs['model_name'])
		self.model = content_type.model_class()
		if self.model == data_models.ActivityType:
			self.packages = ['mtimetables', 'settings']
		return super(ObjectRequirementsView, self).dispatch(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		kwargs = super(ObjectRequirementsView, self).get_context_data(**kwargs)
		kwargs['requirement_packages'] = models.RequirementPackage.objects.filter(require_objects=self.object)
		kwargs['rt_info'] = functions.get_object_rt_info(self.object)
		try:
			rp = models.RequirementPackage.objects.get(require_objects=self.object, requirement_package_type=options.REQUIREMENT_PACKAGE_PERSONAL)
			logger.debug('requirement package for object %s already exists: %s', self.object, rp)
		except models.RequirementPackage.DoesNotExist:
			rp = models.RequirementPackage(evaluation_method=1, requirement_package_type=options.REQUIREMENT_PACKAGE_PERSONAL, name='%s %s' % (self.object._meta.verbose_name, self.object))
			rp.full_clean()
			rp.save()
			rorp = models.ObjectRequirementConnection(require_object=self.object, requirement_package=rp, order=0)
			rorp.full_clean()
			rorp.save()
			logger.debug('for object %s created requirement package %s', self.object, rp)
		kwargs['personal_requirement_package'] = rp
		return kwargs



class RequirementTypeViewSet(mtimetables_views.ViewSet):
	model = models.RequirementType
	form_class = forms.RequirementTypeForm
	packages = ['mtimetables', PACKAGENAME]
	view_types = 'RUDL'
	list_display = ['__unicode__', 'priority', 'enabled']

	model_action_types = ['list', 'install']

	def get_install_action(self):
		return tools_misc.Action('mtimetables:requirements:requirementtype_install', 'install %s' % self.model_verbose_name_plural, 'search')



class RequirementTypesInstallView(mtimetables_views.FormView):
	heading = 'Install requirement types'
	model_name = 'requirementtype'
	packages = ['mtimetables', 'settings']
	form_class = forms.RequirementTypeInstallForm
	prefix = 'requirementtype_install'

	def get_requirement_modules(self):
		available_modules = []
		installed_indexes = []
		i = 0
		for name, module_class in inspect.getmembers(requirementmodules):
			if hasattr(module_class, "__bases__") and models.RequirementModuleBase in module_class.__bases__:
				available_modules.append(module_class)
				if module_class.get_requirement_type_instance():
					installed_indexes.append(i)
				i += 1
		return available_modules, installed_indexes
	
	def post(self, *args, **kwargs):
		installed_modules = []
		uninstalled_modules = []
		available_modules, installed_indexes = self.get_requirement_modules()
		new_indexes = list([int(index) for index in self.request.POST.getlist('%s-requirement_types' % self.prefix, [])])

		# logger.debug('POST: %s', self.request.POST)
		logger.debug('Available modules: %s', available_modules)
		logger.debug('Installed indexes: %s', installed_indexes)
		logger.debug('New indexes: %s', new_indexes)

		for i, module in enumerate(available_modules):
			logger.debug('i: %s, module: %s', i, module)
			if i in installed_indexes and i not in new_indexes:
				module.uninstall()
				uninstalled_modules.append(module.get_name())
			elif i not in installed_indexes and i in new_indexes:
				module.install()
				installed_modules.append(module.get_name())

		success_message = []
		if installed_modules:
			success_message.append('Installed requirement types: %s.' % ', '.join(installed_modules))
		if uninstalled_modules:
			success_message.append('Uninstalled requirement types: %s.' % ', '.join(uninstalled_modules))
		if success_message:
			messages.success(self.request, ' '.join(success_message))
		else:
			messages.info(self.request, 'No requirement types installed or uninstalled.')
		return redirect(self.get_list_action().get_url())

	def get_form_kwargs(self):
		available_modules, installed_indexes = self.get_requirement_modules()
		choices = ((i, rt.get_name()) for i, rt in enumerate(available_modules))
		kwargs = super(RequirementTypesInstallView, self).get_form_kwargs()
		kwargs['available_requirement_types'] = list(choices)
		kwargs['installed_requirement_types'] = list(installed_indexes)
		return kwargs



class RequirementViewSet(mtimetables_views.ViewSet):
	view_types = 'CUDL'
	packages = ['mtimetables', PACKAGENAME]
	model = models.Requirement
	model_name = 'requirement'  # should be explicitly defined because of reverse urls for requirement subclasses
	model_action_types = ['list',]



class RequirementListView(RequirementViewSet, mtimetables_views.ListView):

	list_display = ('__unicode__', 'requirement_package')
	list_filter = (tools_filters.model_filter_factory('requirement_type', models.RequirementType),)

	def get_context_data(self, **kwargs):
		logger.debug('RequirementListView get_context_data for model %s', self.model)
		kw = super(RequirementListView, self).get_context_data(**kwargs)
		kw['requirement_types'] = models.RequirementType.objects.all()
		return kw



class RequirementDetailView(RequirementViewSet, mtimetables_views.DetailView):
	pass
	


class RequirementFormMixin(object):
	form_class = forms.RequirementForm

	@property
	def form_text(self):
		return self.model.description

	@property
	def success_message(self):
		return 'Requirement %s successfully %s.' % (self.model.get_name(), 'saved' if getattr(self, 'object', False) else 'created')
		
	@property
	def error_message(self):
		return 'Requirement %s could not be %s. Check the field errors.' % (self.model.get_name(), 'saved' if getattr(self, 'object', False) else 'created')

	def dispatch(self, request, *args, **kwargs):
		if 'model_name' in kwargs.keys():  # RequirementCreateView
			content_type = ContentType.objects.get(app_label='requirementmodules', model=kwargs['model_name'])
			self.model = content_type.model_class()
			logger.debug('Correcting view model attribute from Requirement to %s, model name is %s, model verbose name is %s', self.model, self.model_name, self.model_verbose_name)
			if 'requirement_package' in kwargs.keys():
				self.requirement_package = get_object_or_404(models.RequirementPackage, pk=kwargs['requirement_package'])
		elif 'pk' in kwargs.keys():  # RequirementUpdateView
			obj = get_object_or_404(models.Requirement, pk=kwargs['pk'])
			self.model = obj.requirement_type.class_object
			logger.debug('Correcting view model attribute from Requirement to %s, model name is %s, model verbose name is %s', self.model, self.model_name, self.model_verbose_name)
		return super(RequirementFormMixin, self).dispatch(request, *args, **kwargs)

	def get_prefix(self):
		prefix = "_".join(self.packages + [self.model_name,])
		logger.debug('Requirement form prefix: %s', prefix)
		return prefix

	def get_form_kwargs(self):
		kwargs = super(RequirementFormMixin, self).get_form_kwargs()
		if issubclass(self.model, models.Requirement): # should be True
			kwargs['object_class'] = self.model
		if hasattr(self, 'requirement_package'):
			kwargs['requirement_package'] = self.requirement_package
		return kwargs



class RequirementCreateView(RequirementViewSet, RequirementFormMixin, mtimetables_views.CreateView):

	@property
	def heading(self):
		return ('Create requirement %s' % self.model.get_name())



class RequirementUpdateView(RequirementViewSet, RequirementFormMixin, mtimetables_views.UpdateView):

	@property
	def heading(self):
		return ('Update requirement %s' % self.model.get_name())



class RequirementDeleteView(RequirementViewSet, mtimetables_views.DeleteView):
	pass




# * * * * * * * * * * * REQUIRE OBJECTS VIEWSETS * * * * * * * * * * * * * *

class RequireObjectViewSet(mtimetables_views.ViewSet):
	view_types = 'L'
	model_action_types = ['list']
	object_action_types = ['requirements']
	current_action_type = 'requirements'
	template_name = 'mtimetables/requirements/requireobject_list.html'



class GroupViewSet(data_views.GroupViewSet, RequireObjectViewSet):
	pass



class UserViewSet(data_views.UserViewSet, RequireObjectViewSet):
	pass



class SubjectViewSet(data_views.SubjectViewSet, RequireObjectViewSet):
	pass


class RoomViewSet(data_views.RoomViewSet, RequireObjectViewSet):
	pass



class RoomTypeViewSet(data_views.RoomTypeViewSet, RequireObjectViewSet):
	pass



class ActivityTypeViewSet(data_views.ActivityTypeViewSet, RequireObjectViewSet):
	packages = ['mtimetables', 'settings']



class ActivityDefinitionViewSet(data_views.ActivityDefinitionViewSet, RequireObjectViewSet):
	pass