# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from exceptions import NotImplementedError

from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericForeignKey
from django.db import models

from tools import fields as tools_fields

from .. import settings as options
from .. import fields as mtimetables_fields

import logging
logger = logging.getLogger(__name__)



class RequirementParameter(object):
	keyword = ''
	datatype = ''
	datarange = ''
	widget = ''



class RequirementModuleInterface(object):
	"""
	Abstract base class. Please implement in subclasses:
	- Meta.verbose_name (name of the requirement)
	- description
	- text
	- evaluation_methods
	- getter and setter for values, which will compress and decompress values string to specific requirement attributes
	"""

	@property
	def description(self):
		raise NotImplementedError("Subclasses should implement this!")

	# @property
	# def text(self):
	# 	raise NotImplementedError("Subclasses should implement this!")

	@property
	def evaluation_methods(self):
		raise NotImplementedError("Subclasses should implement this!")

	@classmethod
	def install(self):
		""" 
		Returns True, if module has been successfully installed, otherwise False (module already exists). 
		"""
		
		content_type = ContentType.objects.get(app_label='requirementmodules', model=self._meta.model_name)
		try:
			obj = RequirementType.objects.get(content_type=content_type)
		except RequirementType.DoesNotExist:
			obj = RequirementType.objects.create(content_type=content_type)
			logger.info('%s successfully installed.', self._meta.object_name)
			return True  # installed
		return False  # module already exists

	@classmethod
	def uninstall(self):
		content_type = ContentType.objects.get(app_label='requirementmodules', model=self._meta.model_name)
		try:
			obj = RequirementType.objects.get(content_type=content_type)
			obj.delete()
			logger.info('%s module uninstalled.', self._meta.object_name)
		except RequirementType.DoesNotExist:
			pass


class ObjectRequirementConnection(models.Model):
	requirement_package = models.ForeignKey('RequirementPackage')
	require_object = models.ForeignKey('data.RequireObject')
	order = models.PositiveIntegerField() # order of requirement package for require object

	def __unicode__(self):
		return '%s' % self.order

	class Meta:
		ordering = ['order',]
		# order_with_respect_to = 'require_object'



class RequirementPackage(models.Model):
	requirement_package_type = tools_fields.ChoiceField(choices=options.REQUIREMENT_PACKAGE_TYPES)
	name = models.CharField(max_length=options.NAME_LENGTH, blank=True)
	password = models.CharField(max_length=options.PASSWORD_LENGTH, blank=True)
	evaluate_together = models.BooleanField(default=False)
	evaluation_method = mtimetables_fields.EvaluationMethodField()

	@property
	def personal(self):
		return True if not self.name else False

	def __unicode__(self):
		return '%s' % self.name

	def evaluate(self):
		for r in self.requirements.all():
			r.evaluate()



class RequirementType(models.Model):
	priority = mtimetables_fields.PriorityField() # priority by requirement type
	enabled = models.BooleanField(default=True)
	content_type = models.ForeignKey(ContentType, editable=False)

	@property
	def slug(self):
		return self.content_type.model

	@property
	def class_object(self):
		return self.content_type.model_class()

	@property
	def name(self):
		return self.class_object.get_name()

	@property
	def description(self):
		return self.class_object.description

	@property
	def text(self):
		return self.class_object.text

	@property
	def evaluation_methods(self):
		return self.class_object.evaluation_methods

	def __unicode__(self):
		return '%s' % self.name



class Requirement(models.Model):
	requirement_package = models.ForeignKey(RequirementPackage, related_name='requirements')
	requirement_type = models.ForeignKey(RequirementType, related_name='requirements')
	priority = mtimetables_fields.PriorityField() # priority by requirement instance
	evaluation_method = mtimetables_fields.EvaluationMethodField()
	actual_compliance_rate = models.FloatField(blank=True, default=0, editable=False)
	min_compliance_rate = models.FloatField(blank=True, default=0)
	description = models.TextField(blank=True) # arguments
	values = models.TextField()

	@staticmethod
	def __new__(cls, *args, **kwargs):
		if cls == Requirement and len(args) > 2:
			requirement_type = get_object_or_404(RequirementType, pk=args[2])
			cls = requirement_type.class_object
			logger.debug('Instantiating requirement specific object of class %s', cls)
		return super(Requirement, cls).__new__(cls)

	def __unicode__(self):
		return '%s' % self.requirement_type

	def save(self, *args, **kwargs):
		if not self.requirement_type.content_type:
			self.requirement_type.content_type = ContentType.objects.get_for_model(self)
		super(Requirement, self).save(*args, **kwargs)



class RequirementModuleBase(RequirementModuleInterface, Requirement):

	@classmethod
	def get_requirement_type_instance(self):
		content_type = ContentType.objects.get(app_label='requirementmodules', model=self._meta.model_name)
		try:
			return RequirementType.objects.get(content_type=content_type)
		except RequirementType.DoesNotExist as e:
			logger.warning('Trying to get unsupported requirement type %s: %s', content_type, e)
			return None

	@classmethod
	def get_name(self):
		return self._meta.verbose_name

	class Meta:
		"""
		All classes should implement Meta.proxy = True (this attribute cannot be inherited)!
		"""
		proxy = True
		# default_permissions = []  # TODO Django 1.7



class ObjectRequirementTypeConnection(models.Model):
	requirement_type = models.ForeignKey(RequirementType, related_name='allowed_objects')
	content_type = models.ForeignKey(ContentType)
	object_id = models.PositiveIntegerField(blank=True, null=True)
	allowed_count = models.PositiveIntegerField(default=options.DEFAULT_ALLOWED_RT_COUNT)
	content_object = GenericForeignKey('content_type', 'object_id')

	def __unicode__(self):
		return '%s %s' % (self.content_type, self.object_id if self.object_id else '')