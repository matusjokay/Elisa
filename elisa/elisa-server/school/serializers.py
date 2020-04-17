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


class RoomEquipmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='equipment.id')
    name = serializers.ReadOnlyField(source='equipment.name')

    class Meta:
        model = models.RoomEquipment
        fields = ('id', 'name', 'count')


class RoomCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    # category = RoomCategorySerializer()
    # category = serializers.SlugRelatedField(
    #     slug_field='name', queryset=models.RoomType.objects.all())
    # equipment = RoomEquipmentSerializer(
    #     source='roomequipment_set', many=True, read_only=True)
    department = DepartmentSerializer(
        source='department_set', many=True, read_only=True
    )

    class Meta:
        model = models.Room
        fields = ('id', 'name', 'capacity', 'room_type', 'department')


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
    # subject_id = serializers.PrimaryKeyRelatedField(queryset=models.Course.objects.all())
    # user_id = serializers.PrimaryKeyRelatedField(queryset=fei_models.AppUser.objects.all())

    class Meta:
        model = models.SubjectUser
        # fields = ('id', 'subject', 'user')
        fields = '__all__'

# class SubjectUserSerializerCreate(serializers.ModelSerializer):
    
    

#     def create(self, validated_data):
#         user_id = validated_data.pop('user')
#         subject_id = validated_data.pop('subject')
#         role_id = validated_data.pop('role')
#         row = models.SubjectUser.objects.create(
#             user=user_id,
#             subject=subject_id,
#             role=role_id)
#         return row

#     class Meta:
#         model = models.SubjectUser
#         fields = '__all__'