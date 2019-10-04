# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import patterns, url
from django.views.generic import TemplateView

urlpatterns = [

	# index
    url(r'^$', TemplateView.as_view(template_name='helloworld/index.html'), name='index'),

]