# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from django.conf import settings

# from django.contrib import admin
# admin.autodiscover()



urlpatterns = [

	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'site-login.html'}, name='login'),
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),

	url(r'^', include('mtimetables.urls', namespace="mtimetables")),

	# url(r'^helloworld/', include('helloworld.urls', namespace='helloworld')),

	# url(r'^admin/', include(admin.site.urls)),

] + staticfiles_urlpatterns()