# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
	from .common import *
except ImportError:
	logger.error('Error while importing settings/common.py.')



DEBUG = False
TEMPLATE_DEBUG = DEBUG