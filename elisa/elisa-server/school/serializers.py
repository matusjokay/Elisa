from rest_framework import serializers

from . import models


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Group
        fields = ('id', 'name', 'abbr', 'parent')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Department
        fields = ('id', 'name', 'abbr', 'parent')


class CourseSerializer(serializers.ModelSerializer):
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
    category = serializers.SlugRelatedField(
        slug_field='name', queryset=models.RoomType.objects.all())
    equipment = RoomEquipmentSerializer(
        source='roomequipment_set', many=True, read_only=True)

    class Meta:
        model = models.Room
        fields = ('id', 'name', 'capacity', 'room_type', 'department',
                  'equipment')


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
        model = models.Period
        fields = '__all__'

# TODO: missing user group
# missing user subject role