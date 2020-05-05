from django.db.models import Q
from django.contrib.auth.models import Group 
from rest_framework import serializers
from .models import (
    Version,
    AppUser,
    Period,
    Department,
    UserDepartment)
import re

from school.models import Course, SubjectUser


class UserMixin:
    def get_fullname(self, obj):
        """
        Return the full name with titles, with a space in between.
        """
        obj.title_before = '' if obj.title_before is None else obj.title_before
        obj.title_after = '' if obj.title_after is None else obj.title_after
        full_name = '%s%s %s' % (
            obj.title_before, obj.get_full_name(), obj.title_after)
        return full_name

    def get_fullname_table(self, obj):
        """
        Return the full name with titles, with a space in between for table.
        """
        obj['title_before'] = '' if obj['title_before'] is None else obj['title_before']
        obj['title_after'] = '' if obj['title_after'] is None else obj['title_after']
        full_name = '%s%s %s %s' % (
            obj['title_before'], obj['first_name'], obj['last_name'], obj['title_after'])
        return full_name


class VersionSerializer(serializers.ModelSerializer):
    parent_schema = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        name = str(validated_data['name']).lower()
        period_id = None
        if validated_data['period']:
            period_id = validated_data['period'].id

        # TODO: For now there can be multiple schemas that are work in progress

        # query = Q(status__in=[Version.WORK_IN_PROGRESS, Version.NEW]) & ~Q(schema_name='public')
        # if Version.objects.filter(query).exists():
        #     raise serializers.ValidationError("You have to publish version before creating a new one.")

        version = Version(
            schema_name=name,
            name=validated_data['name'],
            period_id=period_id
        )

        # TODO : move to creating timetables or remove
        version.start_work()
        version.save()

        return version

    class Meta:
        model = Version
        fields = ('id', 'name', 'status', 'parent_schema', 'last_updated', 'period')


class UserSerializer(UserMixin, serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')

    class Meta:
        model = AppUser
        fields = (
            'id',
            'username',
            'fullname',
            'title_before',
            'title_after',
            'first_name',
            'last_name',
            'groups')


class UserSerializerShort(UserMixin, serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'fullname', 'first_name', 'last_name')


class UserSerializerCourse(UserMixin, serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ('id', 'fullname')


class UserSerializerTable(UserMixin, serializers.ModelSerializer):
    fullname_table = serializers.SerializerMethodField()
    groups = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name')

    class Meta:
        model = AppUser
        fields = ('id', 'fullname_table', 'groups')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class UserDepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDepartment
        fields = '__all__'

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = '__all__'


class PeriodSerializerJustName(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ('id', 'name')


class AuthGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('id', 'name')


class TeachersListSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    user = UserSerializerShort()

    class Meta:
        model = SubjectUser
        fields = '__all__'
