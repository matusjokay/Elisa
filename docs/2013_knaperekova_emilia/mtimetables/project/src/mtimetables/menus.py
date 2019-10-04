# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse

import menu

import logging
logger = logging.getLogger(__name__)



settings_url = 'mtimetables:settings:%s_list'
settings_children = (
	menu.MenuItem('General', reverse('mtimetables:settings:index')),
	menu.MenuItem('Hours', reverse(settings_url % 'timetablegrid')),
	menu.MenuItem('Activity types', reverse(settings_url % 'activitytype')),
	menu.MenuItem('Requirement types', reverse(settings_url % 'requirementtype')),
)



data_url = 'mtimetables:data:%s_list'
data_children = (
	# menu.MenuItem('Activity types', reverse(data_url % 'activitytype')),
	menu.MenuItem('Departments', reverse(data_url % 'department')),
	menu.MenuItem('Groups', reverse(data_url % 'group')),
	menu.MenuItem('Users', reverse(data_url % 'user')),
	menu.MenuItem('Study types', reverse(data_url % 'studytype')),
	menu.MenuItem('Subjects', reverse(data_url % 'subject')),
	menu.MenuItem('Activity definitions', reverse(data_url % 'activitydefinition')),
	menu.MenuItem('Rooms', reverse(data_url % 'room')),
	menu.MenuItem('Room types', reverse(data_url % 'roomtype')),
	menu.MenuItem('Equipments', reverse(data_url % 'equipment')),
)



requirement_url = 'mtimetables:requirements:%s_list'
requirements_children = (
	menu.MenuItem('Requirement packages', reverse(requirement_url % 'requirementpackage')),
	# menu.MenuItem('Requirement types', reverse(requirement_url % 'requirementtype')),
	menu.MenuItem('Requirements', reverse(requirement_url % 'requirement')),
	menu.MenuItem('Groups', reverse(requirement_url % 'group'), separator=True),
	menu.MenuItem('Users', reverse(requirement_url % 'user')),
	menu.MenuItem('Subjects', reverse(requirement_url % 'subject')),
	menu.MenuItem('Activity types', reverse(requirement_url % 'activitytype')),
	menu.MenuItem('Activity definitions', reverse(requirement_url % 'activitydefinition')),
	menu.MenuItem('Rooms', reverse(requirement_url % 'room')),
	menu.MenuItem('Room types', reverse(requirement_url % 'roomtype')),
)



timetable_url = 'mtimetables:timetable:%s_list'
events_children = (
	menu.MenuItem('All events', reverse(timetable_url % 'event')),
	menu.MenuItem('One time events', reverse(timetable_url % 'onetimeevent')),
	menu.MenuItem('Semeter events', reverse(timetable_url % 'semesterevent')),
	menu.MenuItem('Collisions', reverse(timetable_url % 'collision')),
)



semester_calendar_children = (
)



examination_period_calendar_children = (
)



calendar_children = (
)



# menu.Menu.add_item('main', menu.MenuItem('Home', '/', icon='home'))
menu.Menu.add_item('main', menu.MenuItem('Data', reverse('mtimetables:data:index'), icon='hdd', children=data_children))
menu.Menu.add_item('main', menu.MenuItem('Requirements', reverse('mtimetables:requirements:index'), icon='filter', children=requirements_children))
menu.Menu.add_item('main', menu.MenuItem('Events', reverse('mtimetables:timetable:index'), icon='list-alt', children=events_children))
menu.Menu.add_item('main', menu.MenuItem('Semester timetable', reverse('mtimetables:calendar:semester'), icon='th', children=semester_calendar_children))
menu.Menu.add_item('main', menu.MenuItem('Examination period timetable', reverse('mtimetables:calendar:examinationperiod'), icon='th-list', children=examination_period_calendar_children))
menu.Menu.add_item('main', menu.MenuItem('Calendar', reverse('mtimetables:calendar:index'), icon='calendar', children=calendar_children))



menu.Menu.add_item('right', menu.MenuItem('Settings', reverse('mtimetables:settings:index'), icon_only=True, icon='wrench', children=settings_children))
menu.Menu.add_item('right', menu.MenuItem('Logout', reverse('logout'), icon_only=True, icon='log-out'))