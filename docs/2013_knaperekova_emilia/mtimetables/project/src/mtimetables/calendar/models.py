# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

from tools import fields as tools_fields

from .. import settings as options

import logging
logger = logging.getLogger(__name__)



class TimetableGrid(models.Model):
	name = models.CharField(max_length=options.NAME_LENGTH)
	period_prototype = models.PositiveIntegerField(verbose_name='period', blank=True, null=True)

	def __unicode__(self):
		return '%s' % self.name



# TODO: validacia, ze from time musi byt mensie ako to time
class Hour(models.Model):
	timetable_grid = models.ForeignKey(TimetableGrid, related_name='hours')
	name = models.CharField(max_length=options.ABBREVIATION_LENGTH)
	from_time = models.TimeField()
	to_time = models.TimeField()

	def __unicode__(self):
		return '%s' % self.name

	def clean(self):
		if self.from_time >= self.to_time:
			raise ValidationError('Hour start has to be before hour end.')