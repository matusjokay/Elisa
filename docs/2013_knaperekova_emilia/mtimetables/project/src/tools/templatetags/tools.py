# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import template

import logging
logger = logging.getLogger(__name__)



register = template.Library()



@register.filter
def attr(value, arg):
	if hasattr(value, arg):
		if callable(getattr(value, arg)):
			return getattr(value, arg)()
		return getattr(value, arg)
	return ''
	

# for dictionary acces in templates and return '' if key does not exist
@register.filter
def key(dictionary_or_list, key):
	if isinstance(dictionary_or_list, dict):
		return dictionary_or_list.get(key, '')
	if isinstance(dictionary_or_list, list):
		return dictionary_or_list[key]
	if isinstance(dictionary_or_list, tuple):
		if len(dictionary_or_list) > int(key):
			return dictionary_or_list[key]
		return False


@register.simple_tag
def action_url(action, obj=None):
	return action.get_url(obj)