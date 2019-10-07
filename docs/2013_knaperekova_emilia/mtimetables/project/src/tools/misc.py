# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.core.urlresolvers import reverse

from . import constants

import logging
logger = logging.getLogger(__name__)



def daterange(date_from, date_to):
		for n in range((date_to - date_from).days + 1):
			yield date_from + datetime.timedelta(n)



class Action(object):

	def __init__(self, urlname, title, icon, button=constants.BTN_DEFAULT, attrs=['id',]):
		self.urlname = urlname
		self.title = title
		self.icon = icon
		self.button = button
		self.attrs = attrs

	def get_url(self, obj=None):
		if not obj:
			return reverse(self.urlname)
		args = []
		for attr in self.attrs:
			temp_obj = obj
			attr_parts = attr.split('.')
			for attr_part in attr_parts:
				temp_obj = getattr(temp_obj, attr_part)
			args.append(temp_obj)

		return reverse(self.urlname, args=args)