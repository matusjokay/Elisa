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

class PeriodResource(resources.ModelResource):
    department = fields.Field(
        attribute='department',
        column_name='department',
        widget=ForeignKeyWidgetWithCreation(models.Department))
    # previous_period = fields.Field(
    #     attribute='previous_period',
    #     column_name='previous_period',
    #     widget=ForeignKeyWidgetWithCreation(models.Period))
    # next_period = fields.Field(
    #     attribute='next_period',
    #     column_name='next_period',
    #     widget=ForeignKeyWidgetWithCreation(models.Period))

    class Meta:
        model = models.Period
        fields = ('id', 'name', 'department', 'university_period', 'academic_sequence', 'previous_period', 'next_period', 'start_date', 'end_date', 'active',)
        export_order = ('id', 'name', 'department', 'university_period', 'academic_sequence', 'previous_period', 'next_period', 'start_date', 'end_date', 'active',)

class CourseResource(resources.ModelResource):
    period = fields.Field(
        attribute='period',
        column_name='period',
        widget=ForeignKeyWidgetWithCreation(models.Period))
    teacher = fields.Field(
        attribute='teacher',
        column_name='teacher',
        widget=ForeignKeyWidgetWithCreation(AppUser))

    class Meta:
        model = models.Course
        skip_unchanged = True
        fields = ('id', 'period', 'department', 'teacher', 'code', 'name', 'completion', 'credits',)
        export_order = ('id', 'code', 'name', 'period', 'department', 'teacher', 'completion', 'credits')


class EquipmentResource(resources.ModelResource):
    class Meta:
        model = models.Equipment
        skip_unchanged = True
        export_order = ('id', 'name')


class RoomTypeResource(resources.ModelResource):
    class Meta:
        model = models.RoomType
        skip_unchanged = True
        export_order = ('id', 'name')


class RoomResource(resources.ModelResource):
    class Meta:
        model = models.Room
        skip_unchanged = True
        export_order = ('id', 'name', 'capacity', 'room_type', 'department')


class RoomEquipmentResource(resources.ModelResource):
    def skip_row(self, instance, original):
        #  Allow importing resources with empty id. We use ForeignKeys as
        #  import_id_fields to uniquely identify a model.
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    class Meta:
        model = models.RoomEquipment
        # idendification of id fields but this is a many to many join table
        import_id_fields = ('room', 'equipment')
        skip_unchanged = True
        fields = ('room', 'equipment', 'count')
        export_order = ('room', 'equipment', 'count')


class UserResource(resources.ModelResource):
    class Meta:
        # TODO: check if AppUser is a valid model 
        # otherwise just use a normal user 
        model = AppUser
        fields = ('id', 'username', 'first_name', 'last_name', 'title_before', 'title_after',)
        skip_unchanged = True
        export_order = ('id', 'username', 'first_name', 'last_name', 'title_before', 'title_after',)


class StudyTypeResource(resources.ModelResource):
    class Meta:
        model = models.StudyType
        skip_unchanged = True
        export_order = ('id', 'name')

class FormOfStudyResource(resources.ModelResource):
    class Meta:
        model = models.FormOfStudy
        skip_unchanged = True
        export_order = ('id', 'name')


# class SubjectStudyTypeResource(resources.ModelResource):
#     times = fields.Field()

#     class Meta:
#         model = models.SubjectStudyType
#         skip_unchanged = True
#         export_order = ('subject', 'type', 'times')

#     def skip_row(self, instance, original):
#         #  Allow importing resources with empty id. We use ForeignKeys as
#         #  import_id_fields to uniquely identify a model.
#         if not instance.id:
#             instance.id = original.id

#         super().skip_row(instance, original)

#     # delete unneeded columns from dataset in export
#     def after_export(self, queryset, data, *args, **kwargs):
#         del data['practice_hours']
#         del data['lecture_hours']
#         del data['id']
#         pass

#     # set times attribute for export
#     def dehydrate_times(self, subject_study_type):
#         return '%s/%s' % (subject_study_type.lecture_hours, subject_study_type.practice_hours)


# class FacultyResource(resources.ModelResource):
#     class Meta:
#         model = models.Faculty
#         skip_unchanged = True
#         export_order = ('id', 'name', 'abbr')


class SubjectUserResource(resources.ModelResource):
    subject = fields.Field(
        attribute='subject',
        column_name='subject',
        widget=ForeignKeyWidgetWithCreation(models.Course))
    def skip_row(self, instance, original):
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    class Meta:
        model = models.SubjectUser
        import_id_fields = ('subject', 'user')
        skip_unchanged = True
        export_order = ('subject', 'user', 'role')

class UserSubjectRoleResource(resources.ModelResource):
    class Meta:
        model = models.UserSubjectRole
        skip_unchanged = True
        export_order = ('id', 'name')


class UserDepartmentResource(resources.ModelResource):
    def skip_row(self, instance, original):
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    class Meta:
        model = models.UserDepartment
        import_id_fields = ('user', 'department')
        skip_unchanged = True
        export_order = ('user', 'department', 'employment')

# TODO: CHECK IF FOREIGN KEY CHECKING IS NEEDED
class UserGroupResource(resources.ModelResource):
    def skip_row(self, instance, original):
        if not instance.id:
            instance.id = original.id

        super().skip_row(instance, original)

    class Meta:
        model = models.UserGroup
        import_id_fields = ('user', 'group')
        skip_unchanged = True
        export_order = ('user', 'group', 'group_number', 'form_of_study', 'study_type')
