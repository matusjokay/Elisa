from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class LoginSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        return RefreshToken.for_user(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        data['name'] = self.user.first_name + ' ' + self.user.last_name
        if self.user.title_before is not None:
            data['name'] = self.user.title_before + self.user.first_name + ' ' + self.user.last_name
        if self.user.title_after is not None:
            data['name'] = self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.title_after
        if self.user.title_before is not None and self.user.title_after is not None:
            data['name'] = self.user.title_before + self.user.first_name + ' ' + self.user.last_name + ' ' + self.user.title_after
        # data['title_before'] = self.user.title_before
        # data['title_after'] = self.user.title_after if self.user.title_after is not None else ''
        data['role'] = self.user.groups.values_list('name', flat=True)

        return data
