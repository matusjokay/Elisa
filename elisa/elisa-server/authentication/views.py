from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework.request import Request
from django_python3_ldap.auth import LDAPBackend
from rest_framework import status
from fei.models import AppUser
from . import serializers, backend
from django.db import IntegrityError
from django.conf import settings
import jwt
import datetime


class LoginView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access JWT and other
    user information. A refresh token is attached as a cookie that is
    httpOnly which means it cannot be accessed via client but is being sent
    when needed for access JWT renewal.
    """
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = serializers.LoginSerializer(data=request.data)

        if serializer.is_valid():
            user = AppUser.objects.get(username=request.data['username'])
            session_id = user.access_id
            expiration = (datetime.datetime.now() +
                          settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])

            response = Response(
                data=serializer.validated_data,
                status=status.HTTP_200_OK)
            # TODO: add secure when client will be https
            response.set_cookie(
                'XSRF-TOKEN',
                value=session_id,
                expires=expiration,
                httponly=True)
            return response


token_obtain_pair = LoginView.as_view()


class RefreshView(TokenViewBase):
    """
    Takes refresh_token from cookie to retrieve valid access
    token. If refresh_token is not valid then it removes access_id
    and returns 401 status code.
    """
    serializer_class = TokenRefreshSerializer

    def post(self, request, *args, **kwargs):
        # refresh_token_raw = request.data.get("refresh")
        if ('XSRF-TOKEN' not in request.COOKIES):
            response_data = {
                    'detail': InvalidToken.default_detail,
                    'code': InvalidToken.default_code}
            return Response(
                    data=response_data,
                    status=status.HTTP_401_UNAUTHORIZED)
        refresh_token_raw = request.COOKIES['XSRF-TOKEN']
        # extract the payload from refresh jwt
        user_id_from_refresh = jwt.decode(
            refresh_token_raw,
            settings.SECRET_KEY,
            options={'verify_exp': False}
            )
        user_id = int(user_id_from_refresh['user_id'])
        # fetch the user that wants to refresh access
        user = AppUser.objects.get(pk=user_id)
        request.data["refresh"] = refresh_token_raw
        serializer = TokenRefreshSerializer(data=request.data)
        # check if the token is still valid
        # if so then return access otherwise
        # remove session id and return unauthorized
        try:
            if serializer.is_valid() is True:
                return Response(serializer.validated_data)
        except TokenError as e:
            print('is not valid remove session id')
            if user.access_id is not None:
                try:
                    user.access_id = None
                    user.save()
                    request.COOKIES.pop('XSRF-TOKEN', None)
                except IntegrityError as e:
                    return Response(
                        data={"message": e.message},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            response_data = {
                    'detail': InvalidToken.default_detail,
                    'code': InvalidToken.default_code}
            return Response(
                    data=response_data,
                    status=status.HTTP_401_UNAUTHORIZED)


token_refresh = RefreshView.as_view()
