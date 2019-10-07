# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import collections

from django.conf.urls import url

from .. import misc as mtimetables_misc
from ..data import models as data_models
from ..data import views as data_views
# from ..timetable import models as timetable_models
# from ..timetable import views as timetable_views
from ..requirements import models as requirements_models
from ..requirements import views as requirements_views
from ..calendar import models as calendar_models
# from ..calendar import views as calendar_views
from ..calendar import forms as calendar_forms

from . import views



viewsets = collections.OrderedDict([
	(calendar_models.TimetableGrid, {'form_class': calendar_forms.TimetableGridForm,}),
	(data_models.ActivityType, {'viewset': data_views.ActivityTypeViewSet}),
	(requirements_models.RequirementType, {'viewset': requirements_views.RequirementTypeViewSet}),
])

urlpatterns = [

	url(r'^$', views.SettingsIndex.as_view(), name='index'),

]
urlpatterns += mtimetables_misc.package_views_factory('settings', viewsets)