from django.urls import include, path
from rest_framework_extensions.routers import ExtendedSimpleRouter

import timetables.views as timetables


timetables_router = ExtendedSimpleRouter()
timetables_router.register(
    r'timetables', timetables.TimetableViewSet,
    base_name='timetable').register(
        r'events',
        timetables.EventViewSet,
        base_name='timetables-event',
        parents_query_lookups=['timetable'])
timetables_router.register(
    r'timetables', timetables.TimetableViewSet,
    base_name='timetable').register(
        r'collisions',
        timetables.CollisionViewSet,
        base_name='timetables-collision',
        parents_query_lookups=['events'])

urlpatterns = [
    path('', include(timetables_router.urls)),
    path('timetable-latest/', timetables.LatestTimetableViewSet.as_view()),
]
