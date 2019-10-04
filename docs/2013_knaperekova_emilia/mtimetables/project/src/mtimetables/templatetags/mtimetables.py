# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

from .. import settings as options

import logging
logger = logging.getLogger(__name__)



register = template.Library()



@register.simple_tag
def mtimetables_option(*args):
	logger.debug('mtimetables_option get %s', args)
	new_val = options
	for value in args:
		new_val = getattr(new_val, value)
	return new_val