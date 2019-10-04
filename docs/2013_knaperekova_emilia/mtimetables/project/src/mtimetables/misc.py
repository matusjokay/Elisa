# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from collections import namedtuple

from django.conf.urls import patterns, url

from tools import constants

from . import views

import logging
logger = logging.getLogger(__name__)



ViewUrl = namedtuple('ViewUrl', ['regex', 'view', 'name'])
def model_views_factory(model, package_name, viewset=views.ViewSet, **kwargs):
	model_name = model._meta.model_name
	view_mapping = {
		'C': ViewUrl(r'^%screate/$', views.CreateView, constants.CREATE_VIEW_NAME),
		'R': ViewUrl(r'^%s(?P<pk>\d+)/$', views.DetailView, constants.DETAIL_VIEW_NAME),
		'U': ViewUrl(r'^%s(?P<pk>\d+)/update/$', views.UpdateView, constants.UPDATE_VIEW_NAME),
		'D': ViewUrl(r'^%s(?P<pk>\d+)/delete/$', views.DeleteView, constants.DELETE_VIEW_NAME),
		'L': ViewUrl(r'^%s$', views.ListView, constants.LIST_VIEW_NAME),
	}
	url_patterns = ['',]
	for view_type in viewset.view_types:
		bases = (viewset, view_mapping[view_type].view)
		name = package_name.title() + model.__name__ + view_mapping[view_type].view.__name__
		view_regex = view_mapping[view_type].regex % (model_name + "/")
		view_class = type(str(name), bases, kwargs)
		view_class.model = model
		view_class.packages = ['mtimetables', package_name,]
		view_name = model_name + "_" + view_mapping[view_type].name
		url_patterns.append(url(view_regex, view_class.as_view(), name=view_name))
	return patterns(*url_patterns)



def package_views_factory(package_key, package_models):
	package_patterns = ['',]
	for model, model_dict in package_models.items():
		package_patterns += model_views_factory(model, package_name=package_key, **model_dict)
	package_patterns = patterns(*package_patterns)
	return package_patterns