# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from tools import mixins as tools_mixins

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'mtimetables'



# class RouterMixin(object):
class RouterMixin(tools_mixins.AuthRequiredMixin):

	def __init__(self, *args, **kwargs):
		logger.debug('RouterMixin init')
		super(RouterMixin, self).__init__(*args, **kwargs)



class FormMixin(object):
	template_name = '%s/form.html' % PACKAGENAME

	def get_prefix(self):
		return self.model_name