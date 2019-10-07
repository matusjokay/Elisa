# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import unicodecsv as csv
from collections import OrderedDict
from exceptions import IOError, AttributeError
from django.db.utils import IntegrityError

from mtimetables.data import models as data_models
from mtimetables import settings as options

import logging
logger = logging.getLogger(__name__)


class FEI(object):
	column_separator = b";"
	import_order = [
		('equipments.csv', 'create_equipments'), 
		('roomtypes.csv', 'create_roomtypes'), 
		('departments.csv', 'create_departments'), 
		('rooms.csv', 'create_rooms'), 
		('rooms_equipments.csv', 'create_rooms_equipments'), 
		('groups.csv', 'create_groups'),
		('users.csv', 'create_users'),
		('users_groups.csv', 'create_users_groups'),
		('users_departments.csv', 'create_users_departments'),
		('studytypes.csv', 'create_studytypes'),
		('subjects.csv', 'create_subjects'),
		('subjects_studytypes.csv', 'create_subjects_studytypes'),
		('subjects_users.csv', 'create_subjects_users'),
	]

	def __init__(self, *args, **kwargs):
		self.omitted_subjects = []

	def csv_import(self, filepaths):
		filepaths = list(filepaths)
		filenames = list([fpath.split("/")[-1] for fpath in filepaths])
		for fname, import_function in self.import_order:
			try:
				i = filenames.index(fname)
			except ValueError:
				logger.warning('Cannot find data source file %s', fname)
			else:
				logger.info('Importing %s...', fname)
				try:
					with open(filepaths[i], 'rb') as csvfile:
						reader = csv.reader(csvfile, delimiter=self.column_separator)
						entries = [[attr.strip() for attr in line] for line in list(reader)]
						import_function = getattr(self, import_function)(entries)
				except IOError as e:
					logger.error('%s: %s', key, e)
				else:
					filenames.pop(i)
					filepaths.pop(i)
		if filenames:
			logger.warning('Unable to import files %s', ', '.join(filenames))

		logger.info('Creating default activity definitions for subjects.')
		self.create_activitydefinitions()
				
	def get_or_create_object(self, obj_class, ais_id):
		try:
			obj = obj_class.objects.get(uis_id=ais_id)
		except obj_class.DoesNotExist:
			obj = obj_class(uis_id=ais_id)
		return obj

	def get_existing_object(self, obj_class, ais_id):
		try:
			obj = obj_class.objects.get(uis_id=ais_id)
			return obj
		except obj_class.DoesNotExist as e:
			logger.error("%s: %s", ais_id, e)
			return None

	def save_object(self, obj):
		try:
			obj.full_clean()
			obj.save()
		except IntegrityError as e:
			logger.error("%s with FEI id=%s: %s", obj._meta.verbose_name.capitalize(), obj.uis_id, e)

	def create_equipments(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.Equipment, entry[0])
			obj.name = entry[1]
			self.save_object(obj)

	def create_roomtypes(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.RoomType, entry[0])
			obj.name = entry[1]
			self.save_object(obj)

	def create_rooms(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.Room, entry[0])
			obj.name = entry[1]
			obj.capacity = entry[2]
			obj.room_type = self.get_existing_object(data_models.RoomType, entry[3])
			if entry[4]:
				obj.department = self.get_existing_object(data_models.Department, entry[4])
			self.save_object(obj)

	def create_departments(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.Department, entry[0])
			obj.abbreviation = entry[1]
			obj.name = entry[2]
			self.save_object(obj)
		for existing_entry in entries:
			if existing_entry[3]:
				obj = self.get_existing_object(data_models.Department, existing_entry[0])
				obj.parent = self.get_existing_object(data_models.Department, existing_entry[3])
				self.save_object(obj)

	def create_rooms_equipments(self, entries):
		for entry in entries:
			r = self.get_existing_object(data_models.Room, entry[0])
			e = self.get_existing_object(data_models.Equipment, entry[1])
			if r and e:
				try:
					obj = data_models.RoomEquipmentConnection.objects.get(room=r, equipment=e)
				except data_models.RoomEquipmentConnection.DoesNotExist:
					obj = data_models.RoomEquipmentConnection(room=r, equipment=e)
				obj.count = entry[2]
				self.save_object(obj)

	def create_groups(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.Group, entry[0])
			obj.name = entry[1]
			obj.abbreviation = entry[2]
			self.save_object(obj)
		for existing_entry in entries:
			if existing_entry[3]:
				obj = self.get_existing_object(data_models.Group, existing_entry[0])
				obj.parent = self.get_existing_object(data_models.Group, existing_entry[3])
				self.save_object(obj)

	def create_users(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.User, entry[0])
			obj.login = entry[1]
			obj.name = entry[2]
			obj.surname = entry[3]
			obj.titles_before_name = entry[4] if len(entry) > 4 else ''
			obj.titles_after_name = entry[5] if len(entry) > 5 else ''
			self.save_object(obj)

	def create_users_departments(self, entries):
		for entry in entries:
			u = self.get_existing_object(data_models.User, entry[0])
			d = self.get_existing_object(data_models.Department, entry[1])
			if u and d:
				try:
					obj = data_models.UserDepartmentConnection.objects.get(user=u, department=d)
				except data_models.UserDepartmentConnection.DoesNotExist:
					obj = data_models.UserDepartmentConnection(user=u, department=d)
				obj.relation_type = entry[2]
				self.save_object(obj)			

	def create_subjects(self, entries):
		regexes = tuple(re.compile(r) for r in options.FEI_OMIT_SUBJECTS_REGEXES)
		for entry in entries:
			omit_entry = False
			for regex in regexes:
				if regex.match(entry[2].lower()):
					logger.info('...omitting subject %s - %s', entry[0], entry[2])
					omit_entry = True
					self.omitted_subjects.append(entry[0])
					continue
			if omit_entry:
				continue
			obj = self.get_or_create_object(data_models.Subject, entry[0])
			obj.code = entry[1]
			obj.name = entry[2]
			if len(entry) > 3:
				obj.department = self.get_existing_object(data_models.Department, entry[3])
			obj.completion_mode = entry[4] if len(entry) > 4 else ''
			self.save_object(obj)

	def create_subjects_users(self, entries):
		for entry in entries:
			if (entry[0] in self.omitted_subjects):
				continue
			s = self.get_existing_object(data_models.Subject, entry[0])
			u = self.get_existing_object(data_models.User, entry[1])
			if s and u:
				try:
					obj = data_models.UserSubjectConnection.objects.get(user=u, subject=s)
				except data_models.UserSubjectConnection.DoesNotExist:
					obj = data_models.UserSubjectConnection(user=u, subject=s)
				obj.relation_type = entry[2]
				self.save_object(obj)		

	def create_users_groups(self, entries):
		for entry in entries:
			u = self.get_existing_object(data_models.User, entry[0])
			g = self.get_existing_object(data_models.Group, entry[1])
			if u and g:
				try:
					obj = data_models.UserGroupConnection.objects.get(user=u, group=g)
				except data_models.UserGroupConnection.DoesNotExist:
					obj = data_models.UserGroupConnection(user=u, group=g)
				if entry[2]:
					obj.study_group = entry[2]
				if entry[3]:
					obj.study_method = entry[3]
				self.save_object(obj)

	def create_studytypes(self, entries):
		for entry in entries:
			obj = self.get_or_create_object(data_models.StudyType, entry[0])
			obj.name = entry[1]
			self.save_object(obj)

	def create_subjects_studytypes(self, entries):
		for entry in entries:
			if (entry[0] in self.omitted_subjects):
				continue
			s = self.get_existing_object(data_models.Subject, entry[0])
			st = self.get_existing_object(data_models.StudyType, entry[1])
			if s and st:
				try:
					obj = data_models.SubjectStudyTypeConnection.objects.get(subject=s, study_type=st)
				except data_models.SubjectStudyTypeConnection.DoesNotExist:
					obj = data_models.SubjectStudyTypeConnection(subject=s, study_type=st)
				obj.learning_plan = entry[2]
				self.save_object(obj)

	def create_activitydefinitions(self):
		data_models.ActivityDefinition.objects.all().delete()
		
		exam_activity_types = data_models.ActivityType.objects.filter(pk__in=options.DEFAULT_EXAM_ACTIVITY_TYPES)
		lecture_activity_types = data_models.ActivityType.objects.filter(pk__in=options.DEFAULT_LECTURE_ACTIVITY_TYPES)
		exercise_activity_types = data_models.ActivityType.objects.filter(pk__in=options.DEFAULT_EXERCISE_ACTIVITY_TYPES)
		
		for subject_studytype in data_models.SubjectStudyTypeConnection.objects.distinct('subject'):

			learning_plan = subject_studytype.learning_plan.split('/')
			if len(learning_plan) not in (2, 3):
				logger.error('Unsupported learning plan format: "%s". It should be "val/val[/val]", where val is one or more int numbers joined with "+".', learning_plan)
				continue

			lecture_plan = learning_plan[0].split('+')
			exercise_plan = learning_plan[1].split('+')
			if len(learning_plan) < 3:
				exam_plan = ['1', '1'] if subject_studytype.subject.completion_mode in options.SUBJECT_EXAM_COMPLETION_MODES else ['0']
				subject_studytype.learning_plan += '/%s' % '+'.join(exam_plan)
				subject_studytype.save()
			else:
				exam_plan = learning_plan[2].split('+')

			for i, lecture_plan_item in enumerate(lecture_plan):
				i_at = i % len(lecture_activity_types)
				hours_count = int(lecture_plan_item)
				if hours_count:
					settings = {
						'name': '%s - %s' % (subject_studytype.subject, lecture_activity_types[i_at]),
						'activity_type': lecture_activity_types[i_at],
						'hours_count': hours_count,
						'mandatory_instances_count': options.DEFAULT_LECTURE_MANDATORY_INSTANCES_COUNT,
						'room_capacity_rate': options.DEFAULT_ROOM_CAPACITY_RATE[options.AP_LECTURE]
					}
					lecture = data_models.ActivityDefinition.objects.create(**settings)
					lecture.subjects.add(subject_studytype.subject)

			for i, exercise_plan_item in enumerate(exercise_plan):
				i_at = i % len(exercise_activity_types)
				hours_count = int(exercise_plan_item)
				if hours_count:
					settings = {
						'name': '%s - %s' % (subject_studytype.subject, exercise_activity_types[i_at]),
						'activity_type': exercise_activity_types[i_at],
						'hours_count': hours_count,
						'mandatory_instances_count': options.DEFAULT_EXERCISE_MANDATORY_INSTANCES_COUNT,
						'room_capacity_rate': options.DEFAULT_ROOM_CAPACITY_RATE[options.AP_EXERCISE]
					}
					exercise = data_models.ActivityDefinition.objects.create(**settings)
					exercise.subjects.add(subject_studytype.subject)

			for i, exam_plan_item in enumerate(exam_plan):
				i_at = i % len(exam_activity_types)
				hours_count = int(exam_plan_item)
				if hours_count:
					settings = {
						'activity_type': exam_activity_types[i_at],
						'hours_count': hours_count,
						'mandatory_instances_count': options.DEFAULT_EXAM_MANDATORY_INSTANCES_COUNT,
						'room_capacity_rate': options.DEFAULT_ROOM_CAPACITY_RATE[options.AP_EXAM],
						'weeks': []
					}
					exam = data_models.ActivityDefinition.objects.create(name='%s - %s' % (subject_studytype.subject, exam_activity_types[i_at]), **settings)
					exam.subjects.add(subject_studytype.subject)