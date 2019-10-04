# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from mptt import models as mptt_models
from tools import fields as tools_fields

from .. import settings as options
from .. import fields as mtimetables_fields

import logging
logger = logging.getLogger(__name__)



class RequireObject(models.Model):
	requirement_packages = models.ManyToManyField('requirements.RequirementPackage', blank=True, null=True, related_name='require_objects', through='requirements.ObjectRequirementConnection')
	priority = mtimetables_fields.PriorityField()

	@property
	def is_require_object(self):
		return True



class Department(mptt_models.MPTTModel):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)
	abbreviation = models.CharField(max_length=options.ABBREVIATION_LENGTH)
	parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)

	class MPTTMeta:
		order_insertion_by = ['name']

	@property
	def all_users(self):
		departments = self.get_descendants(include_self=True)
		return User.objects.filter(departments__in=departments)

	@property
	def all_rooms(self):
		departments = self.get_descendants(include_self=True)
		return Room.objects.filter(department__in=departments)

	@property
	def all_subjects(self):
		departments = self.get_descendants(include_self=True)
		return Subject.objects.filter(department__in=departments)

	@property
	def hierarchical_str(self):
		return "%s%s" % ("- - - - " * self.get_level(), self.name)

	def __unicode__(self):
		return '%s' % self.name



class Group(mptt_models.MPTTModel, RequireObject):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
	name = models.CharField(max_length=options.NAME_LENGTH)
	abbreviation = models.CharField(max_length=options.ABBREVIATION_LENGTH)

	class MPTTMeta:
		order_insertion_by = ['name']

	@property
	def all_users(self):
		groups = self.get_descendants(include_self=True)
		return User.objects.filter(groups__in=groups)

	@property
	def hierarchical_str(self):
		return "%s%s" % ("- - - - " * self.get_level(), self.name)

	def __unicode__(self):
		return '%s' % self.name



class User(RequireObject):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	login = models.CharField(max_length=options.NAME_LENGTH)
	name = models.CharField(max_length=options.NAME_LENGTH)
	surname = models.CharField(max_length=options.NAME_LENGTH)
	titles_before_name = models.CharField(max_length=options.NAME_LENGTH, blank=True)
	titles_after_name = models.CharField(max_length=options.NAME_LENGTH, blank=True)
	active = models.BooleanField(default=True)
	groups = models.ManyToManyField(Group, through='UserGroupConnection', blank=True, null=True, related_name='users')
	departments = models.ManyToManyField(Department, through='UserDepartmentConnection', blank=True, null=True, related_name='users')

	class Meta:
		ordering = ['surname', 'name']

	@property
	def all_groups(self):
		groups = []
		for group in self.groups.all():
			groups += group.get_ancestors(include_self=True)
		return list(set(groups))

	def __unicode__(self):
		return '%s%s %s%s' % (self.titles_before_name + " " if self.titles_before_name else "", self.name, self.surname, ", " + self.titles_after_name if self.titles_after_name else "")

	

class StudyType(models.Model):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)
	abbreviation = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)

	def __unicode__(self):
		return '%s' % self.name



class Subject(mptt_models.MPTTModel, RequireObject):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
	code = models.CharField(max_length=options.NAME_LENGTH, null=True, blank=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)
	abbreviation = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)
	completion_mode = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)
	study_types = models.ManyToManyField(StudyType, through='SubjectStudyTypeConnection', null=True, blank=True, related_name='subjects')
	department = models.ForeignKey(Department, null=True, blank=True, related_name='subjects')
	users = models.ManyToManyField(User, through='UserSubjectConnection', blank=True, null=True, related_name='subjects')

	class MPTTMeta:
		order_insertion_by = ['name']

	class Meta:
		ordering = ['name']

	@property
	def hierarchical_code(self):
		return self.code or ", ".join([child.code for child in self.children.all()])

	@property
	def hierarchical_str(self):
		return '%s%s' % ("- - - - " * self.get_level(), self.name)
	
	def __unicode__(self):
		return '%s' % self.name



class ActivityType(RequireObject):
	name = models.CharField(max_length=options.NAME_LENGTH)
	mandatory = models.BooleanField()
	prototype = models.PositiveIntegerField(blank=True, null=True)
	custom_color = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)

	@property
	def color(self):
		return self.custom_color or options.DEFAULT_COLORS.get(self.prototype, '')

	def __unicode__(self):
		return '%s' % self.name



class ActivityDefinition(RequireObject):
	name = models.CharField(max_length=options.NAME_LENGTH)
	activity_type = models.ForeignKey(ActivityType, related_name='activity_definitions')
	subjects = models.ManyToManyField(Subject, blank=True, null=True, related_name='activity_definitions')
	groups = models.ManyToManyField(Group, blank=True, null=True, related_name='activity_definitions')
	hours_count = models.PositiveIntegerField()
	mandatory_instances_count = models.PositiveIntegerField()
	room_capacity_rate = models.FloatField(default=1)
	custom_color = models.CharField(max_length=options.ABBREVIATION_LENGTH, blank=True)
	weeks = tools_fields.BitField(flags=options.WEEKS_CHOICES, default=options.DEFAULT_WEEKS, blank=True)

	@property
	def week_numbers(self):
		return tuple(i for i, (k, v) in enumerate(self.weeks.items()) if v)

	@property
	def periodical(self):
		return True if self.weeks else False

	@property
	def color(self):
		return self.custom_color or self.activity_type.color

	@property
	def users(self):
		return User.objects.filter(subjects__in=self.subjects.all())

	@property
	def students(self):
		users = self.users.filter(usersubjectconnection__relation_type__in=options.STUDENT_RELATION_TYPES, usersubjectconnection__subject__in=self.subjects.all())
		if self.groups.all():
			user_ids = []
			for group in self.groups.all():
				user_ids += group.all_users.values_list('id', flat=True)
			users = users.filter(id__in=set(user_ids))
		return users

	@property
	def students_count(self):
		return self.students.count()

	@property
	def teachers(self):
		return self.users.filter(usersubjectconnection__relation_type__in=options.TEACHER_RELATION_TYPES)

	def __unicode__(self):
		return '%s' % self.name



class Equipment(models.Model):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)

	class Meta:
		ordering = ['name']

	def __unicode__(self):
		return '%s' % self.name



class RoomType(RequireObject):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)

	class Meta:
		ordering = ['name']

	def __unicode__(self):
		return '%s' % self.name



class Room(mptt_models.MPTTModel, RequireObject):
	uis_id = models.CharField(max_length=options.UIS_ID_LENGTH, unique=True, blank=True, null=True, editable=False)
	name = models.CharField(max_length=options.NAME_LENGTH)
	capacity = models.PositiveIntegerField()
	parent = mptt_models.TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
	room_type = models.ForeignKey(RoomType, related_name='rooms')
	department = models.ForeignKey(Department, null=True, blank=True, related_name='rooms')
	equipments = models.ManyToManyField(Equipment, through='RoomEquipmentConnection', null=True, blank=True, related_name='rooms')

	class MPTTMeta:
		order_insertion_by = ['-capacity', 'name']

	class Meta:
		ordering = ['-capacity', 'name']

	@property
	def hierarchical_str(self):
		return "%s%s" % ("- - - - " * self.get_level(), self.name)

	def __unicode__(self):
		return '%s' % self.name



# class StudyMethod(models.Model):
# 	name = models.CharField(max_length=options.NAME_LENGTH)

# 	def __unicode__(self):
# 		return self.name


class UserGroupConnection(models.Model):
	user = models.ForeignKey(User)
	group = models.ForeignKey(Group)
	# study_method = models.ForeignKey(StudyMethod, related_name='users', blank=True, null=True)
	study_method = models.PositiveIntegerField(choices=options.USER_GROUP_STUDY_METHODS, blank=True, null=True)
	study_group = models.PositiveIntegerField(blank=True, null=True)

	def __unicode__(self):
		return '%s %s' % (self.user, self.group)



class UserEventConnection(models.Model):
	user = models.ForeignKey(User)
	event = models.ForeignKey('timetable.Event')
	relation_type = models.PositiveIntegerField(choices=options.USER_EVENT_RELATION_TYPES)

	def __unicode__(self):
		return '%s %s' % (self.user, self.event)



class UserSubjectConnection(models.Model):
	user = models.ForeignKey(User)
	subject = models.ForeignKey(Subject)
	relation_rate = models.FloatField(default=options.DEFAULT_USER_SUBJECT_RELATION_RATE)
	relation_type = models.PositiveIntegerField(choices=options.USER_SUBJECT_RELATION_TYPES)

	class Meta:
		unique_together = ('user', 'subject', 'relation_type')

	def __unicode__(self):
		return '%s %s' % (self.user, self.subject)
		


class UserDepartmentConnection(models.Model):
	user = models.ForeignKey(User)
	department = models.ForeignKey(Department)
	relation_type = models.PositiveIntegerField(choices=options.USER_DEPARTMENT_RELATION_TYPES)

	def __unicode__(self):
		return '%s %s' % (self.user, self.department)



class RoomEquipmentConnection(models.Model):
	room = models.ForeignKey(Room)
	equipment = models.ForeignKey(Equipment)
	count = models.PositiveIntegerField()

	def __unicode__(self):
		return '%s %s %s' % (self.room, self.equipment, self.count)



class SubjectStudyTypeConnection(models.Model):
	subject = models.ForeignKey(Subject)
	study_type = models.ForeignKey(StudyType)  # teaching_method
	learning_plan = models.CharField(max_length=options.ABBREVIATION_LENGTH)

	def __unicode__(self):
		return '%s %s %s' % (self.subject, self.study_type, self.learning_plan)