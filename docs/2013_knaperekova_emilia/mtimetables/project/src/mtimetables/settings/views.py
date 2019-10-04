# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import views as mtimetables_views



PACKAGENAME = 'settings'



class SettingsIndex(mtimetables_views.TemplateView):
	template_name = 'mtimetables/settings/index.html'