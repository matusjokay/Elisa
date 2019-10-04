# -*- coding: utf-8 -*-
from __future__ import unicode_literals

try:
	from .common import *
except ImportError:
	logger.error('Error while importing settings/common.py.')



# * * * * * OVERRIDES * * * * * * * * * * * * * * * * * * * * * */

MIDDLEWARE_CLASSES += [
	'debug_toolbar.middleware.DebugToolbarMiddleware',
]

INSTALLED_APPS += [
	'debug_toolbar',
	'django_extensions',
]



# * * * * * DEBUG TOOLBAR  * * * * * * * * * * * * * * * * * * */

DEBUG_TOOLBAR_CONFIG = {
	# 'DISABLE_PANELS': ('debug_toolbar.panels.redirects.RedirectsPanel',)
}

DEBUG_TOOLBAR_PANELS = [
	# 'debug_toolbar.panels.versions.VersionsPanel',
	'debug_toolbar.panels.timer.TimerPanel',
	'debug_toolbar.panels.settings.SettingsPanel',
	'debug_toolbar.panels.headers.HeadersPanel',
	'debug_toolbar.panels.request.RequestPanel',
	'debug_toolbar.panels.sql.SQLPanel',
	# 'debug_toolbar.panels.staticfiles.StaticFilesPanel',
	'debug_toolbar.panels.templates.TemplatesPanel',
	# 'debug_toolbar.panels.cache.CachePanel',
	# 'debug_toolbar.panels.signals.SignalsPanel',
	'debug_toolbar.panels.logging.LoggingPanel',
	'debug_toolbar.panels.redirects.RedirectsPanel',
]



# * * * * * LOGGING * * * * * * * * * * * * * * * * * * * * * */

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
	'version': 1,
	'disable_existing_loggers': False,
	'formatters': {
		'verbose': {
			'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
		},
		'simple': {
			'format': '%(levelname)s: %(message)s'
		},
	},
	'filters': {
		'require_debug_false': {
			'()': 'django.utils.log.RequireDebugFalse'
		}
	},
	'handlers': {
		'mail_admins': {
			'level': 'ERROR',
			'filters': ['require_debug_false'],
			'class': 'django.utils.log.AdminEmailHandler'
		},
		'console':{
			'level': 'DEBUG',
			'class': 'logging.StreamHandler',
			# 'formatter': 'verbose'
			'formatter': 'simple'
		},
	},
	'loggers': {
		# 'django.request': {
		# 	'handlers': ['mail_admins'],
		# 	'level': 'ERROR',
		# 	'propagate': True,
		# },
		'mtimetables': {
			'handlers': ['console', 'mail_admins'],
			'level': 'DEBUG',
		},
		'fei': {
			'handlers': ['console', 'mail_admins'],
			'level': 'DEBUG',
		},
		'brutalform': {
			'handlers': ['console', 'mail_admins'],
			'level': 'DEBUG',
		},
		'tools': {
			'handlers': ['console', 'mail_admins'],
			'level': 'DEBUG',
		},
		'bootstrap3': {
			'handlers': ['console', 'mail_admins'],
			'level': 'DEBUG',
		},
	}
}