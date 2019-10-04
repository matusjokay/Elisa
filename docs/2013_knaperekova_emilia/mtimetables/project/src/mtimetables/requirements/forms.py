# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django import forms
from django.forms import widgets as django_widgets
from django.forms import models as django_forms_models
from django.contrib.contenttypes.models import ContentType

from brutalform import models as brutalform_models

from .. import settings as options
from ..data import models as data_models

from . import models

import logging
logger = logging.getLogger(__name__)



class RequirementTypeInstallForm(forms.Form):
	layout = 'inline'
	requirement_types = forms.MultipleChoiceField(widget=django_widgets.CheckboxSelectMultiple)

	def __init__(self, available_requirement_types, installed_requirement_types=[], *args, **kwargs):
		super(RequirementTypeInstallForm, self).__init__(*args, **kwargs)
		logger.debug('RequirementTypeInstallForm choices: %s', available_requirement_types)
		self.fields['requirement_types'].choices = available_requirement_types
		self.fields['requirement_types'].initial = installed_requirement_types



class RequirementForm(forms.ModelForm):
	layout = 'horizontal'

	def __init__(self, object_class, requirement_package=None, *args, **kwargs):
		logger.debug('Requirement custom form for object of class %s, in requirement package %s with kwargs %s', object_class, requirement_package, kwargs)
		self._object_class = object_class
		self._requirement_package = requirement_package
		super(RequirementForm, self).__init__(*args, **kwargs)

		if hasattr(object_class, 'get_widget'):
			self.fields['values'].widget = object_class.get_widget()
			self.fields['values'].label = False

		if self._requirement_package:
			self.fields.pop('requirement_package')

	def save(self, commit=True):
		self.instance.requirement_type = self._object_class.get_requirement_type_instance()
		if self._requirement_package:
			self.instance.requirement_package = self._requirement_package
		return super(RequirementForm, self).save(commit)

	class Meta:
		model = models.Requirement
		exclude = ['requirement_type',]



class RequirementInlineForm(brutalform_models.ModelForm):

	class Meta:
		model = models.Requirement
		fields = ['requirement_type', 'priority']
		# exclude = ['requirement_type',]



class RequirementPackageForm(brutalform_models.ModelForm):
	layout = 'horizontal'

	class Meta:
		model = models.RequirementPackage
		fields = ['name', 'password', 'requirement_package_type', 'evaluation_method', 'evaluate_together']

	class Forms:
		RequirementPackageRequirementsFormSet = django_forms_models.inlineformset_factory(models.RequirementPackage, models.Requirement, form=RequirementInlineForm, extra=0)
		inlines = collections.OrderedDict([
			('requirements', RequirementPackageRequirementsFormSet)
		])
		legends = {
			'requirements': 'Requirements',
		}






# RequirementPackageFormSet = django_forms_models.inlineformset_factory(RequirementPackage, Requirement, extra=1)

class ObjectRequirementConnectionInlineForm(brutalform_models.ModelForm):

	def __init__(self, *args, **kwargs):
		super(ObjectRequirementConnectionInlineForm, self).__init__(*args, **kwargs)
		self.fields['requirement_package'].queryset = models.RequirementPackage.objects.filter(requirement_package_type__gt=options.REQUIREMENT_PACKAGE_PERSONAL)

	class Meta:
		model = models.ObjectRequirementConnection
		fields = ['requirement_package',]

	# class Forms:
	# 	inlines = collections.OrderedDict([
	# 		('requirements', RequirementPackageFormSet),
	# 	])
	# 	legends = {
	# 		'requirements': 'Requirements',
	# 	}


class ObjectRequirementConnectionFormSet(django_forms_models.BaseInlineFormSet):
	def get_queryset(self):
		return super(ObjectRequirementConnectionFormSet, self).get_queryset().filter(requirement_package__requirement_package_type__gt=options.REQUIREMENT_PACKAGE_PERSONAL)

ObjectRequirementConnectionInlineFormSet = django_forms_models.inlineformset_factory(data_models.RequireObject, models.ObjectRequirementConnection, formset=ObjectRequirementConnectionFormSet, form=ObjectRequirementConnectionInlineForm, can_order=True, extra=1)

class ObjectRequirementsForm(brutalform_models.ModelForm):
	layout = 'vertical'

	class Meta:
		model = data_models.RequireObject
		fields = ['priority', ]

	class Forms:
		inlines = collections.OrderedDict([
			('requirement_packages', ObjectRequirementConnectionInlineFormSet),
		])
		legends = {
			'requirement_packages': 'Requirement packages',
		}



class ObjectRequirementTypeConnectionForm(brutalform_models.ModelForm):

	class Meta:
		model = models.ObjectRequirementTypeConnection
		fields = ['content_type', 'object_id', 'allowed_count']

	def __init__(self, *args, **kwargs):
		super(ObjectRequirementTypeConnectionForm, self).__init__(*args, **kwargs)
		self.fields['content_type'].queryset = ContentType.objects.filter(app_label='data', model__in=options.REQUIRE_OBJECTS)



class RequirementTypeForm(brutalform_models.ModelForm):
	layout = 'horizontal'
	text = 'Caution: Unprofessional changes can make system inconsistent.'

	class Meta:
		model = models.RequirementType
		fields = ['priority', 'enabled']

	# def __init__(self, *args, **kwargs):
	# 	super(RequirementTypeForm, self).__init__(*args, **kwargs)

	# 	for require_object in options.REQUIRE_OBJECTS:
	# 		self.fields['%s count' % require_object] = forms.IntegerField(initial=0, required=True)

	class Forms:
		ObjectRequirementTypeConnectionFormSet = django_forms_models.inlineformset_factory(models.RequirementType, models.ObjectRequirementTypeConnection, form=ObjectRequirementTypeConnectionForm, extra=1)
		inlines = collections.OrderedDict([
			('object_requirementtype_connection', ObjectRequirementTypeConnectionFormSet),
		])
		legends = {
			'object_requirementtype_connection': 'Allowed objects',
		}