# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import get_object_or_404
from django.forms import models as django_forms_models
from django.db.models import Q

from tools import filters as tools_filters
from tools import misc as tools_misc
from tools import constants

from .. import settings as options
from .. import views as mtimetables_views
from ..timetable import models as timetable_models
from ..timetable import forms as timetable_forms

from . import models
from . import forms

import logging
logger = logging.getLogger(__name__)



PACKAGENAME = 'data'



class DataIndex(mtimetables_views.TemplateView):
	template_name = 'mtimetables/data/index.html'



class RequireObjectViewSetMixin(object):

	@property
	def object_action_types(self):
		return ['requirements'] + super(RequireObjectViewSetMixin, self).object_action_types

	def get_requirements_action(self):
		return tools_misc.Action('mtimetables:requirements:object_requirements', 'requirements', constants.ICON_REQUIREMENTS, attrs=['_meta.model_name', 'id'])



class DepartmentViewSet(mtimetables_views.ViewSet):
	list_display = ('hierarchical_str',)
	paginate_by = None



class GroupViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	fields = ['name', 'abbreviation', 'priority', 'parent']
	list_display = ('hierarchical_str',)
	paginate_by = None



class UserViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	form_class = forms.UserForm
	list_display = ('__unicode__', 'login')
	serializer_fields = ('name', 'surname')

	def __init__(self, *args, **kwargs):
		logger.debug('UserViewSet init')
		super(UserViewSet, self).__init__(*args, **kwargs)

	class GroupFilter(tools_filters.HierarchicalParamListFilter):
		title = 'group'
		multiple = True

		@property
		def choices(self):
			return models.Group.objects.filter(level__lte=2)

		def process_values(self, values, queryset):
			users_ids = set()
			for group in models.Group.objects.filter(pk__in=values):
				users_ids.update(group.all_users.values_list('id', flat=True))
			return queryset.filter(id__in=users_ids)

	class DepartmentFilter(tools_filters.HierarchicalParamListFilter):
		title = 'department'

		@property
		def choices(self):
			departments = [department.id for department in models.Department.objects.filter(level=1) if len(department.all_users) > 0]
			return models.Department.objects.filter(id__in=departments)

		def process_values(self, values, queryset):
			users_ids = set()
			for department in models.Department.objects.filter(pk__in=values):
				users_ids.update(department.all_users.values_list('id', flat=True))
			return queryset.filter(id__in=users_ids)

	list_filter = (GroupFilter, DepartmentFilter)
	


class StudyTypeViewSet(mtimetables_views.ViewSet):
	pass



class SubjectViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	form_class = forms.SubjectForm
	list_display = ('hierarchical_str', 'hierarchical_code')
	list_display_labels = ('name', 'UIS code')
	serializer_fields = ('name', 'uis_id', 'department')

	@property
	def object_action_types(self):
		actions = ['students'] + super(SubjectViewSet, self).object_action_types
		return actions

	def get_students_action(self):
		return tools_misc.Action('%s_%s' % (self.model_url_name, 'students'), 'show students', 'user')

	class DepartmentFilter(tools_filters.HierarchicalParamListFilter):
		title = 'department'

		@property
		def choices(self):
			departments = [department.id for department in models.Department.objects.filter(level=1) if len(department.all_subjects) > 0]
			return models.Department.objects.filter(id__in=departments)

		def process_values(self, values, queryset):
			subjects = set()
			for	department in models.Department.objects.filter(pk__in=values):
				subjects.update(department.all_subjects.values_list('id', flat=True))
			return queryset.filter(id__in=subjects)

	list_filter = (DepartmentFilter, )



class SubjectStudents(SubjectViewSet, mtimetables_views.UpdateView):
	model = models.Subject
	packages = ['mtimetables', PACKAGENAME]
	form_class = forms.SubjectStudentsForm
	current_action_type = 'students'

	@property
	def heading(self):
		return 'Students of %s' % self.object.name



class RoomViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	form_class = forms.RoomForm
	list_display = ('hierarchical_str', 'capacity')
	list_filter = (tools_filters.model_filter_factory('room_type', models.RoomType),)
	serializer_fields = ('name', 'capacity')


class RoomTypeViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	fields = ['name', 'priority']



class EquipmentViewSet(mtimetables_views.ViewSet):
	pass



class ActivityTypeViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	form_class = forms.ActivityTypeForm
	list_display = ['__unicode__', 'priority']



class ActivityDefinitionViewSet(RequireObjectViewSetMixin, mtimetables_views.ViewSet):
	form_class = forms.ActivityDefinitionForm
	serializer_fields = ('name', 'hours_count', 'students_count', 'periodical', 'week_numbers', 'room_capacity_rate', 'color', ('events', 'id', 'model_type', 'start', 'end', 'week_numbers', 'day_numbers', 'auto_name', 'color', ('rooms', 'id', 'name', 'capacity')))

	class DepartmentFilter(tools_filters.SingleParamListFilter):
		title = 'department'

		@property
		def choices(self):
			departments = [department.id for department in models.Department.objects.filter(level=1) if len(department.all_subjects) > 0]
			return models.Department.objects.filter(id__in=departments)

		def process_values(self, values, queryset):
			subjects_ids = set()
			for department in models.Department.objects.filter(pk__in=values):
				subjects_ids.update(department.all_subjects.values_list('id', flat=True))
			return queryset.filter(subjects__id__in=subjects_ids)

	class GroupFilter(tools_filters.HierarchicalParamListFilter):
		title = 'group'
		multiple = True

		@property
		def choices(self):
			return models.Group.objects.exclude(name__in=('1', '2', '3'))

		def process_values(self, values, queryset):
			groups_ids = set()
			users_ids = set()
			for group in models.Group.objects.filter(pk__in=values):
				groups_ids.update(list(g.id for g in group.get_descendants(include_self=True)))
				users_ids.update(group.all_users.values_list('id', flat=True))
			subjects_ids = models.Subject.objects.filter(users__id__in=users_ids).values_list('id', flat=True)
			return queryset.filter(
				Q(groups__id__in=list(groups_ids)) | Q(subjects__id__in=list(subjects_ids))
			)

	class YearFilter(tools_filters.ListFilter):
		title = 'year'
		key = 'year'
		multiple = True

		@property
		def lookups(self):
			return {'year': options.STUDY_YEAR_CHOICES}

		def queryset(self, request, queryset):
			if self.key in self.matched_params_dict.keys():
				values = self.get_values(self.key)
				logger.debug('values for %s is %s', self.key, values)
				if values:
					groups_querysets = {
						options.STUDY_YEAR_1: models.Group.objects.get(pk=options.STUDY_YEAR_1_ROOT_GROUP_ID).get_leafnodes().filter(name='1').values_list('id', flat=True),
						options.STUDY_YEAR_2: models.Group.objects.get(pk=options.STUDY_YEAR_2_ROOT_GROUP_ID).get_leafnodes().filter(name='2').values_list('id', flat=True),
						options.STUDY_YEAR_3: models.Group.objects.get(pk=options.STUDY_YEAR_3_ROOT_GROUP_ID).get_leafnodes().filter(name='3').values_list('id', flat=True),
						options.STUDY_YEAR_4: models.Group.objects.get(pk=options.STUDY_YEAR_4_ROOT_GROUP_ID).get_leafnodes().filter(name='1').values_list('id', flat=True),
						options.STUDY_YEAR_5: models.Group.objects.get(pk=options.STUDY_YEAR_5_ROOT_GROUP_ID).get_leafnodes().filter(name='2').values_list('id', flat=True),
					}
					groups_ids = set()
					for year in values:
						groups_ids.update(groups_querysets[year])

					users_ids = set()
					for group in models.Group.objects.filter(pk__in=groups_ids):
						users_ids.update(group.all_users.values_list('id', flat=True))
					subjects_ids = models.Subject.objects.filter(users__id__in=users_ids).values_list('id', flat=True)
					queryset = queryset.filter(
						Q(groups__id__in=list(groups_ids)) | Q(subjects__id__in=list(subjects_ids))
					)

			return queryset

	list_filter = (
		tools_filters.model_filter_factory('activity_type', models.ActivityType, multiple=True),
		GroupFilter,
		YearFilter,
		tools_filters.model_filter_factory('subjects', models.Subject),
		DepartmentFilter,
	)

	@property
	def object_action_types(self):
		actions = ['events'] + super(ActivityDefinitionViewSet, self).object_action_types
		return actions

	def get_events_action(self):
		return tools_misc.Action('%s_%s' % (self.model_url_name, 'events'), 'events', 'th-list')



# TODO: success/error messages, dynamic formset
class ActivityDefinitionEventsView(ActivityDefinitionViewSet, mtimetables_views.FormSetView):
	template_name = 'mtimetables/data/activitydefinition_events.html'
	model = models.ActivityDefinition
	packages = ['mtimetables', PACKAGENAME]
	current_action_type = 'events'

	@property
	def heading(self):
		return 'Events of %s' % self.object

	def dispatch(self, request, *args, **kwargs):
		self.object = get_object_or_404(models.ActivityDefinition, pk=kwargs['pk'])
		return super(ActivityDefinitionEventsView, self).dispatch(request, *args, **kwargs)

	def get_formset_class(self):
		obj = self.object
		class decorated(timetable_forms.EventForm):
			def __init__(self, *args, **kwargs):
				kwargs.update({'initial': {'activities': [obj]}})
				super(timetable_forms.EventForm, self).__init__(*args, **kwargs)

		return django_forms_models.modelformset_factory(timetable_models.Event, form=decorated, extra=1, can_delete=True)

	def get_formset_queryset(self):
		qs = timetable_models.Event.objects.filter(activities__in=[self.object])
		logger.debug('ActivityDefinitionEventsView get_formset_queryset')
		return qs

	def get_context_data(self, **kwargs):
		context = super(ActivityDefinitionEventsView, self).get_context_data(**kwargs)
		context['object'] = self.object
		return context