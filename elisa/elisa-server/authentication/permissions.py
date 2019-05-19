from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions


class IsMainTimetableCreator(permissions.BasePermission):
    """
    Permission check for main timetable creator
    """

    message = 'You are not main timetable creator.'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.has_role(settings.MAIN_TIMETABLE_CREATOR)


class IsLocalTimetableCreator(permissions.BasePermission):
    """
    Permission check for main timetable creator
    """

    message = 'You are not local timetable creator.'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.has_role(settings.LOCAL_TIMETABLE_CREATOR)


class IsTeacher(permissions.BasePermission):
    """
    Permission check for main timetable creator
    """

    message = 'You are not teacher.'

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.has_role(settings.TEACHER)
