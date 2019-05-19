# from django.contrib import admin
from import_export import resources, fields, widgets

from school import models
from fei.models import AppUser


class ForeignKeyWidgetWithCreation(widgets.ForeignKeyWidget):
    # Workaround to import resources whose ForeignKey references models which
    # are not yet created.
    def clean(self, value, row=None, *args, **kwargs):
        if value:
            instance, new = self.model.objects.get_or_create(
                **{self.field: value})
            value = getattr(instance, self.field)
            return self.get_queryset(value, row, *args, **kwargs).get(
                **{self.field: value})
        else:
            return None

    def render(self, value, obj=None):
        return value.id


class GroupResource(resources.ModelResource):
    parent = fields.Field(
        attribute='parent',
        column_name='parent',
        widget=ForeignKeyWidgetWithCreation(models.Group))

    class Meta:
        model = models.Group
        fields = ('id', 'name', 'abbr', 'parent')
        export_order = ('id', 'name', 'abbr', 'parent')


class DepartmentResource(resources.ModelResource):
    parent = fields.Field(
        attribute='parent',
        column_name='parent',
        widget=ForeignKeyWidgetWithCreation(models.Department))

    class Meta:
        model = models.Department
        fields = ('id', 'abbr', 'name', 'parent')
        export_order = ('id', 'abbr', 'name', 'parent')


class CourseResource(resources.ModelResource):
    class Meta:
        model = models.Course
        skip_unchanged = True
        export_order = ('id', 'code', 'name', 'department', 'completion')


class EquipmentResource(resources.ModelResource):
    class Meta:
        model = models.Equipment
        skip_unchanged = True
        export_order = ('id', 'name')


class RoomCategoryResource(resources.ModelResource):
    class Meta:
        model = models.RoomCategory
        skip_unchanged = True
        export_order = ('id', 'name')


class RoomResource(resources.ModelResource):
    class Meta:
        model = models.Room
        skip_unchanged = True
        export_order = ('id', 'name', 'capacity', 'category', 'department')


class RoomEquipmentResource(resources.ModelResource):
    def skip_row(self, instance, original):
        #  Allow importing resources with empty id. We use ForeignKeys as
        #  import_id_fields to uniquely identify a model.
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    class Meta:
        model = models.RoomEquipment
        import_id_fields = ('room', 'equipment')
        skip_unchanged = True
        fields = ('room', 'equipment', 'count')
        export_order = ('room', 'equipment', 'count')


class UserResource(resources.ModelResource):
    class Meta:
        model = AppUser
        fields = ('id', 'username', 'first_name', 'last_name', 'title_before', 'title_after',)
        skip_unchanged = True
        export_order = ('id', 'username', 'first_name', 'last_name', 'title_before', 'title_after',)


class StudyTypeResource(resources.ModelResource):
    class Meta:
        model = models.StudyType
        skip_unchanged = True
        export_order = ('id', 'name')


class SubjectStudyTypeResource(resources.ModelResource):
    times = fields.Field()

    class Meta:
        model = models.SubjectStudyType
        skip_unchanged = True
        export_order = ('subject', 'type', 'times')

    def skip_row(self, instance, original):
        #  Allow importing resources with empty id. We use ForeignKeys as
        #  import_id_fields to uniquely identify a model.
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    # delete unneeded columns from dataset in export
    def after_export(self, queryset, data, *args, **kwargs):
        del data['practice_hours']
        del data['lecture_hours']
        del data['id']
        pass

    # set times attribute for export
    def dehydrate_times(self, subject_study_type):
        return '%s/%s' % (subject_study_type.lecture_hours, subject_study_type.practice_hours)


class FacultyResource(resources.ModelResource):
    class Meta:
        model = models.Faculty
        skip_unchanged = True
        export_order = ('id', 'name', 'abbr')


class SubjectUserResource(resources.ModelResource):
    class Meta:
        model = models.SubjectUser
        export_order = ('subject', 'user', 'role')


class UserDepartmentResource(resources.ModelResource):
    class Meta:
        model = models.UserDepartment
        skip_unchanged = True
        export_order = ('user', 'department', 'employment')


class UserGroupResource(resources.ModelResource):
    class Meta:
        model = models.UserGroup
        skip_unchanged = True
        export_order = ('user', 'group', 'group_number', 'study_type')
