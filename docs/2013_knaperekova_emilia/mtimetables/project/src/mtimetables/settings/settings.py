# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
from tools import constants



# * * * * * DATABASE CONSTANTS * * * * *

ABBREVIATION_LENGTH = 50
NAME_LENGTH = 200
PASSWORD_LENGTH = 100
UIS_ID_LENGTH = 20



# * * * * * PERIODS AND DATERANGES * * * * *

WEEKDAYS = [5, 6]
SEMESTER_START_DATE = date(2014, 2, 17)
SEMESTER_END_DATE = date(2014, 5, 25)
SEMESTER_WEEKS_COUNT = 12
SEMESTER_WEEK_DAYS_COUNT = 5
WEEK_STARTS_AT = 1
EXAMINATION_PERIOD_START_DATE = date(2014, 5, 26)
EXAMINATION_PERIOD_END_DATE = date(2014, 7, 5)

CALENDAR_START_DATE = SEMESTER_START_DATE
CALENDAR_END_DATE = EXAMINATION_PERIOD_END_DATE

DAYS_CHOICES = tuple(('day_%s' % i, value) for i, value in enumerate(('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')))
WEEKS_CHOICES = tuple(('week_%s' % i, i+1) for i in range(SEMESTER_WEEKS_COUNT))
DEFAULT_WEEKS = tuple(k for k, v in WEEKS_CHOICES)  # unsupported in django-bitfield, but now using overriden BitField in tools.fields



# * * * * * MTIMETABLES GENERAL * * * * *

DEFAULT_PRIORITY = 0.75
PRIORITIES_CHOICES = (
	(0.25, '1'),
	(0.5, '2'),
	(0.75, '3'),
	(1.0, 'must be'),
)



# * * * * * DATA OPTIONS * * * * *

DEFAULT_USER_SUBJECT_RELATION_RATE = 1

STUDY_YEAR_1 = '1'
STUDY_YEAR_2 = '2'
STUDY_YEAR_3 = '3'
STUDY_YEAR_4 = '4'
STUDY_YEAR_5 = '5'
STUDY_YEAR_CHOICES = (
	(STUDY_YEAR_1, '1 bc'),
	(STUDY_YEAR_2, '2 bc'),
	(STUDY_YEAR_3, '3 bc'),
	(STUDY_YEAR_4, '1 ing'),
	(STUDY_YEAR_5, '2 ing'),
)
BACHELOR_ROOT_GROUP_ID = 236
ENGINEER_ROOT_GROUP_ID = 237
STUDY_YEAR_1_ROOT_GROUP_ID = BACHELOR_ROOT_GROUP_ID
STUDY_YEAR_2_ROOT_GROUP_ID = BACHELOR_ROOT_GROUP_ID
STUDY_YEAR_3_ROOT_GROUP_ID = BACHELOR_ROOT_GROUP_ID
STUDY_YEAR_4_ROOT_GROUP_ID = ENGINEER_ROOT_GROUP_ID
STUDY_YEAR_5_ROOT_GROUP_ID = ENGINEER_ROOT_GROUP_ID

USER_SUBJECT_RELATION_TYPES = (
	(1, 'student'),			# študent
	(2, 'supervisor'), 		# garant
	(3, 'lecturer'), 		# prednášajúci
	(4, 'instructor'),		# cvičiaci
	(5, 'examiner'),		# skúšajúci
	(6, 'administrator'),	# administrátor
	(7, 'tutor'),			# tútor
)
STUDENT_RELATION_TYPES = (1,)
TEACHER_RELATION_TYPES = (2,3,4,5,6,7)

USER_EVENT_RELATION_TYPES = USER_SUBJECT_RELATION_TYPES

USER_DEPARTMENT_RELATION_TYPES = (
	(1, 'interný'),
	(2, 'externý'),
	(3, 'doktorand'),
)

USER_GROUP_STUDY_METHODS = (
	(1, 'prezenčná'),
	(2, 'dištančná'),
	(3, 'kombinovaná'),
)

AP_LECTURE, AP_EXERCISE, AP_EXAM = (1, 2, 3)
ACTIVITY_PROTOTYPES = (
	(AP_LECTURE, 'lecture'),
	(AP_EXERCISE, 'exercise'),
	(AP_EXAM, 'exam')
)



# * * * * * TIMETABLE OPTIONS * * * * *

DEFAULT_COLORS = {
	AP_LECTURE: 'green',
	AP_EXERCISE: 'blue',
	AP_EXAM: 'red'
}



# * * * * * REQUIREMENTS OPTIONS * * * * *

REQUIRE_OBJECTS = ('group', 'user', 'subject', 'activitydefinition', 'activitytype', 'room', 'roomtype')

DEFAULT_ALLOWED_RT_COUNT = 0

EVAL_BOOL = 1
EVAL_FUZZY = 2
EVALUATION_METHODS = {
	EVAL_BOOL: 'Bool',
	EVAL_FUZZY: 'Fuzzy',
}
EVALUATION_METHOD_CHOICES = [(key, value) for key, value in EVALUATION_METHODS.items()]
DEFAULT_EVALUATION_METHOD = EVAL_BOOL

REQUIREMENT_PACKAGE_PERSONAL = 1
REQUIREMENT_PACKAGE_TYPES = (
	(REQUIREMENT_PACKAGE_PERSONAL, 'personal'),
	(2, 'group manual'),
	(3, 'group free'),
	(4, 'group protected'),
)



# * * * * * REQUIREMENT MODULES OPTIONS * * * * *

TIME_PRIORITIES_CHOICES = (
	(None, constants.SELECT_EMPTY_LABEL),
	(0.25, '1'),
	(0.5, '2'),
	(0.75, '3'),
	(1.0, 'must be'),
)



# * * * * * CALENDAR OPTIONS * * * * *

PP_SEMESTER, PP_EXAMINATION_PERIOD = (1, 2)
PERIOD_PROTOTYPES = (
	(PP_SEMESTER, 'semester'),
	(PP_EXAMINATION_PERIOD, 'examination period')
)

DEFAULT_SEMESTER_TIMETABLE_GRID = 1
DEFAULT_EXAMINATION_PERIOD_TIMETABLE_GRID = 2



# * * * * * FEI MODULE OPTIONS * * * * *

FEI_OMIT_SUBJECTS_REGEXES = ('^diplomov', '^bakal')

SUBJECT_EXAM_COMPLETION_MODES = ('s', 'kz')

DEFAULT_LECTURE_MANDATORY_INSTANCES_COUNT = 0
DEFAULT_EXERCISE_MANDATORY_INSTANCES_COUNT = 1
DEFAULT_EXAM_MANDATORY_INSTANCES_COUNT = 1

DEFAULT_LECTURE_ACTIVITY_TYPES = (7, )
DEFAULT_EXERCISE_ACTIVITY_TYPES = (4, )
DEFAULT_EXAM_ACTIVITY_TYPES = (1, 2)

DEFAULT_ROOM_CAPACITY_RATE = {
	AP_LECTURE: 1,
	AP_EXERCISE: 1,
	AP_EXAM: 3
}