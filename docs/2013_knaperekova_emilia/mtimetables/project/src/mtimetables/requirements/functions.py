# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from . import models

import logging
logger = logging.getLogger(__name__)



def get_object_rt_info(obj):
	content_type = ContentType.objects.get_for_model(obj)
	# models.RequirementType.objects.filter(
	# 	Q(allowed_objects__content_type=content_type) & 
	# 	(Q(allowed_objects__object_id__isnull=True) | Q(allowed_objects__object_id=obj.id))
	# )

	obj_rt_connection = models.ObjectRequirementTypeConnection.objects.filter(
		Q(content_type=content_type) & 
		(Q(object_id__isnull=True) | Q(object_id=obj.id))
	)

	obj_rt_info = []

	for rt_conn in obj_rt_connection:
		count = models.ObjectRequirementConnection.objects.filter(
			require_object__id=obj.id, 
			requirement_package__requirements__requirement_type=rt_conn.requirement_type
		).count()

		obj_rt_info.append({
			'requirement_type': rt_conn.requirement_type,
			'allowed_count': rt_conn.allowed_count,
			'count': count,
		})

	return obj_rt_info


