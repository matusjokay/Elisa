from django.contrib.contenttypes.models import ContentType
from django.db import connection
from django.http import Http404

from django_tenants.utils import get_public_schema_name, get_tenant_model
from django.db import utils
from django_tenants.middleware import TenantMainMiddleware


class VersionMiddleware(TenantMainMiddleware):
    """
        Determines tenant by the value of the ``HTTP_TIMETABLE_VERSION`` HTTP header.
    """

    def get_public_name(self):
        schema_name = None
        try:
            schema_name = get_tenant_model().objects.filter(status=get_tenant_model().PUBLIC).last()
        except get_tenant_model().DoesNotExist:
            print("No published schema.")

        if schema_name is None:
            schema_name = get_public_schema_name()
        return schema_name

    def process_request(self, request):
        connection.set_schema_to_public()
        schema_name = request.META.get('HTTP_TIMETABLE_VERSION', self.get_public_name())

        try:
            version = get_tenant_model().objects.get(name=schema_name)
            request.tenant = version
        except utils.DatabaseError:
            raise Http404
        except get_tenant_model().DoesNotExist:
            raise Http404

        connection.set_tenant(request.tenant)
        ContentType.objects.clear_cache()
