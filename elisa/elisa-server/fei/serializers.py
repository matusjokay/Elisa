from django.db.models import Q
from rest_framework import serializers
from .models import Version, AppUser

from school.models import Course, SubjectUser


class UserMixin:
    def get_fullname(self, obj):
        """
        Return the full name with titles, with a space in between.
        """
        full_name = '%s%s %s' % (obj.title_before, obj.get_full_name(), obj.title_after)
        return full_name


class VersionSerializer(serializers.ModelSerializer):
    parent_schema = serializers.CharField(write_only=True, required=False)

    def create(self, validated_data):
        name = str(validated_data['name']).lower()

        # TODO: For now there can be multiple schemas that are work in progress
        
        # query = Q(status__in=[Version.WORK_IN_PROGRESS, Version.NEW]) & ~Q(schema_name='public')
        # if Version.objects.filter(query).exists():
        #     raise serializers.ValidationError("You have to publish version before creating a new one.")

        version = Version(
            schema_name=name,
            name=validated_data['name']
        )

        # TODO : move to creating timetables or remove
        version.start_work()
        version.save()

        return version

    class Meta:
        model = Version
        fields = ('id', 'name', 'status', 'parent_schema')


class UserSerializer(UserMixin, serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()
    groups = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'fullname', 'first_name', 'last_name', 'groups')


class UserSerializerShort(UserMixin, serializers.ModelSerializer):
    fullname = serializers.SerializerMethodField()

    class Meta:
        model = AppUser
        fields = ('id', 'username', 'fullname', 'first_name', 'last_name')


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class TeachersListSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer()
    user = UserSerializerShort()

    class Meta:
        model = SubjectUser
        fields = '__all__'
