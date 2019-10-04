# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
	from .common import *
except ImportError:
	logger.error('Error while importing settings/common.py.')



DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': 'django.db.backends.postgresql_psycopg2',
		'NAME': 'mtimetables',
		'USER': 'mtimetables',
		'PASSWORD': '',
		'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT': '',                      # Set to empty string for default.
	}
}

SECRET_KEY = ''
MEDIA_ROOT = ''
STATIC_ROOT = ''