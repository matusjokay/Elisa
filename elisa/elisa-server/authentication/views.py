from rest_framework_simplejwt.views import TokenViewBase
from . import serializers


class LoginView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = serializers.LoginSerializer


token_obtain_pair = LoginView.as_view()
