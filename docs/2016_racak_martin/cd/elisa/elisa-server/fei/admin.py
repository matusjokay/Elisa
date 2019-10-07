# from django.contrib import admin
from import_export import resources, fields, widgets

from school import models


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


class GroupResource(resources.ModelResource):
    parent = fields.Field(
        attribute='parent',
        column_name='parent',
        widget=ForeignKeyWidgetWithCreation(models.Group))

    class Meta:
        model = models.Group


class DepartmentResource(resources.ModelResource):
    parent = fields.Field(
        attribute='parent',
        column_name='parent',
        widget=ForeignKeyWidgetWithCreation(models.Department))

    class Meta:
        model = models.Department


class CourseResource(resources.ModelResource):
    class Meta:
        model = models.Course


class EquipmentResource(resources.ModelResource):
    class Meta:
        model = models.Equipment


class RoomCategoryResource(resources.ModelResource):
    class Meta:
        model = models.RoomCategory


class RoomResource(resources.ModelResource):
    class Meta:
        model = models.Room


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
