from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings
from django.db import IntegrityError
import secrets


class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        # Customizing the payload with custom data for user
        token = super().get_token(user)
        token['roles'] = user.fetch_role_ids()
        token['name'] = user.construct_name()
        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)
        refresh_str = str(refresh)
        # Because of TokenPair inheritance it will automatically
        # create dict with access and refresh key value pairs.
        # We are removing refresh_token from dict as we don't
        # need this information inside the response.
        data.pop('refresh', None)
        try:
            self.user.access_id = refresh_str
            self.user.save()
        except IntegrityError as e:
            return Response(
                "Database error",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return data
