from rest_framework import serializers

from . import models
from fei import models as fei_models
from fei import serializers as fei_serializers


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('id', 'name', 'abbr', 'parent')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = fei_models.Department
        fields = ('id', 'name', 'abbr', 'parent')


class DepartmentSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = fei_models.Department
        fields = ('id', 'name')


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = '__all__'


class CourseSerializerShort(serializers.ModelSerializer):
    class Meta:
        model = models.Course
        fields = ('id', 'name')


class CourseSerializerFull(serializers.ModelSerializer):
    teacher = fei_serializers.UserSerializerCourse()
    # period = fei_serializers.PeriodSerializerJustName(read_only=True)
    department = DepartmentSerializerShort()

    class Meta:
        model = models.Course
        fields = '__all__'


class EquipmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Equipment
        fields = '__all__'


class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Room
        fields = ('id', 'name', 'capacity', 'room_type', 'department')


class RoomEquipmentSerializer(serializers.ModelSerializer):
    equipment = EquipmentSerializer(read_only=True)
    room_id = serializers.IntegerField(source="room.id", read_only=True)

    class Meta:
        model = models.RoomEquipment
        fields = ('count', 'equipment', 'room_id')


class ActivityCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ActivityCategory
        fields = '__all__'


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Activity
        fields = '__all__'


class FormOfStudySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FormOfStudy
        fields = '__all__'

# TODO: foreign keys and self references keys


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = fei_models.Period
        fields = '__all__'


class UserSubjectRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.UserSubjectRole
        fields = '__all__'

# TODO: missing user group


class SubjectUserSerializerFull(serializers.ModelSerializer):
    subject = CourseSerializerShort(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Course.objects.all(),
        source='subject',
        write_only=True)
    user = fei_serializers.UserSerializerCourse(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=fei_models.AppUser.objects.all(),
        source='user',
        write_only=True)
    role = UserSubjectRoleSerializer(read_only=True)
    role_id = serializers.PrimaryKeyRelatedField(
        queryset=models.UserSubjectRole.objects.all(),
        source='role',
        write_only=True)

    class Meta:
        model = models.SubjectUser
        # fields = ('id', 'subject', 'user')
        fields = '__all__'


class SubjectUserSerializerRoleUser(serializers.ModelSerializer):
    user = fei_serializers.UserSerializerCourse(read_only=True)

    class Meta:
        model = models.SubjectUser
        fields = ('user',)
