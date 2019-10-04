# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

import logging
logger = logging.getLogger(__name__)



PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))



# * * * * * OVERRIDE IN LOCAL * * * * * * * * * * * * * * * * * * * * */

DEBUG = False
TEMPLATE_DEBUG = DEBUG

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
DATABASES = {
	'default': {
		'ENGINE': '',
		'NAME': '',
		# The following settings are not used with sqlite3:
		'USER': '',
		'PASSWORD': '',
		'HOST': '',                      # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
		'PORT': '',                      # Set to empty string for default.
	}
}

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'my4jpdt)@d!cd6_5dv1t@y9ba+98$39dbupzkcagn56636*iwu'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''


ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'mtimetables.mwebair.info']
INTERNAL_IPS = ('127.0.0.1',)


# * * * * * GENERAL * * * * * * * * * * * * * * * * * * * * */

ADMINS = ()

MANAGERS = ADMINS

SITE_ID = 1

AUTH_USER_MODEL = 'auth.User'


# * * * * * URLS AND PATHS * * * * * * * * * * * * * * * * * * * * */

ROOT_URLCONF = 'mtimetables_project.urls'

WSGI_APPLICATION = 'mtimetables_project.wsgi.application'

LOGIN_REDIRECT_URL = 'mtimetables:index'
LOGIN_URL = 'login' # default 'accounts/login' 
LOGOUT_URL = 'logout' # default 'accounts/logout'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/
STATIC_URL = '/static/'

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
	'django.contrib.staticfiles.finders.FileSystemFinder',
	'django.contrib.staticfiles.finders.AppDirectoriesFinder',
	#'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Additional locations of static files
STATICFILES_DIRS = (
	# Put strings here, like "/home/html/static" or "C:/www/django/static".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	# os.path.join(PROJECT_PATH, 'static'),
)

TEMPLATE_DIRS = (
	# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
	# Always use forward slashes, even on Windows.
	# Don't forget to use absolute paths, not relative paths.
	# os.path.join(PROJECT_PATH, 'templates'),
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.JSONSerializer'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'


# * * * * * INTERNATIONALIZATION * * * * * * * * * * * * * * * * * * */
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Bratislava'

USE_I18N = False  # use traslations

USE_TZ = False  # use timezone

USE_L10N = False  # use localized formatting data (set to False to apply datetime input/output settings below)

DATETIME_FORMAT = 'N j, Y, H:i'

DATE_FORMAT = 'Y-m-d'
DATE_INPUT_FORMATS = ('%Y-%m-%d',)

TIME_FORMAT = 'H:i'
TIME_INPUT_FORMATS = ('%H:%M',)



# * * * * * INSTALLED APPS AND... * * * * * * * * * * * * * * * * * * * * * */

INSTALLED_APPS = [
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',

	'mptt', # tree foreign key support
	'bootstrap3',
	'menu', # django-simple-menu

	'tools',
	'brutalform',

	'mtimetables',
	'mtimetables.settings',
	'mtimetables.data',
	'mtimetables.timetable',
	'mtimetables.requirements',
	'mtimetables.requirementmodules',
	'mtimetables.calendar',

	'fei',
	'helloworld',
]


MIDDLEWARE_CLASSES = [
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


TEMPLATE_CONTEXT_PROCESSORS = [
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.core.context_processors.static',
	'django.contrib.messages.context_processors.messages',
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.tz',
	'django.core.context_processors.csrf',
	'django.core.context_processors.debug',
	'django.core.context_processors.request',
]


# * * * * * SERIALIZATION * * * * * * * * * * * * * * * * * * * * * */

SERIALIZATION_MODULES = {'myjson': 'tools.serializers.json'}



# * * * * * DJANGO-SIMPLE-MENU * * * * * * * * * * * * * * * * * * * */

MENU_SELECT_PARENTS = True



# * * * * * DJANGO-BOOTSTRAP3 * * * * * * * * * * * * * * * * * * * */

BOOTSTRAP3 = {
	'jquery_url': '//code.jquery.com/jquery.min.js',
	'base_url': '//netdna.bootstrapcdn.com/bootstrap/3.1.1/',
	'css_url': '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap.min.css',
	'theme_url': '//netdna.bootstrapcdn.com/bootstrap/3.1.1/css/bootstrap-theme.min.css',
	'javascript_url': '//netdna.bootstrapcdn.com/bootstrap/3.1.1/js/bootstrap.min.js',
	'horizontal_label_class': 'col-md-2',
	'horizontal_field_class': 'col-md-10',
	'field_renderers': {
		'default': 'tools.renderers.FieldRenderer'
	}
}



# * * * * * LOCAL SETTINGS * * * * * * * * * * * * * * * * * * * * */

try:
	from .local import *
except ImportError:
	logger.error('Error while importing settings/local.py.')



# * * * * * DEV/PROD SETTINGS * * * * * * * * * * * * * * * * * * * * */

if DEBUG:
	try:
		from .dev import *
	except ImportError:
		logger.error('Error while importing settings/dev.py.')
else:
	try:
		from .prod import *
	except ImportError:
		logger.error('Error while importing settings/prod.py.')