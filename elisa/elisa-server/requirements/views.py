from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from . import models, serializers


class RequirementsViewSet(ModelViewSet):
    """
    API endpoint that allows requirements to be viewed or edited.
    """
    serializer_class = serializers.RequirementSerializer
    queryset = models.Requirement.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.RequirementSerializerPost
        elif self.action == 'update':
            return serializers.RequirementSerializerPut
        return serializers.RequirementSerializer


class RequirementEventViewSet(ModelViewSet):
    """
    API endpoint that allows requirement events to be viewed or edited.
    """
    queryset = models.RequirementEvent.objects.all()
    serializer_class = serializers.RequirementEventSerializer
