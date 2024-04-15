from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import APIException, PermissionDenied

from organisations.invites.models import Invite
from users.models import SignUpType

from ..constants import USER_REGISTRATION_WITHOUT_INVITE_ERROR_MESSAGE
from ..serializers import AuthControllerMixin
from .github import GithubUser
from .google import get_user_info

GOOGLE_URL = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&"
UserModel = get_user_model()


class OAuthLoginSerializer(AuthControllerMixin, serializers.Serializer):
    access_token = serializers.CharField(
        required=True,
        help_text="Code or access token returned from the FE interaction with the third party login provider.",
    )
    sign_up_type = serializers.ChoiceField(
        required=False,
        allow_null=True,
        allow_blank=True,
        choices=SignUpType.choices,
        help_text="Provide information about how the user signed up (i.e. via invite or not)",
        write_only=True,
    )

    class Meta:
        abstract = True

    def create(self, validated_data):
        user_data = self.get_user_info()

        # make pre-authentication checks and signal on failure
        email = user_data.get("email")
        self.check_auth_method(email)

        try:
            user = self._get_user(user_data)
        except APIException as e:
            # catch and signal non-django-authenticate login failure
            user_login_failed.send(
                sender=self.__module__,
                credentials={"username": email},
                request=self.context.get("request"),
                codes=e.get_codes(),
            )
            raise

        # create token
        token, _ = Token.objects.get_or_create(user=user)

        # signal successful login (django.contrib.auth will update last_login)
        user_logged_in.send(
            sender=UserModel, request=self.context.get("request"), user=user
        )

        # return token with latest user model
        token.user.refresh_from_db()

        return token

    def _get_user(self, user_data: dict):
        email = user_data.get("email")
        existing_user = UserModel.objects.filter(email=email).first()

        if not existing_user:
            sign_up_type = self.validated_data.get("sign_up_type")
            if not (
                settings.ALLOW_REGISTRATION_WITHOUT_INVITE
                or sign_up_type == SignUpType.INVITE_LINK.value
                or Invite.objects.filter(email=email).exists()
            ):
                raise PermissionDenied(USER_REGISTRATION_WITHOUT_INVITE_ERROR_MESSAGE)

            return UserModel.objects.create(**user_data, sign_up_type=sign_up_type)

        return existing_user

    def get_user_info(self):
        raise NotImplementedError("`get_user_info()` must be implemented.")


class GoogleLoginSerializer(OAuthLoginSerializer):
    def get_user_info(self):
        return get_user_info(self.validated_data["access_token"])


class GithubLoginSerializer(OAuthLoginSerializer):
    def get_user_info(self):
        github_user = GithubUser(code=self.validated_data["access_token"])
        return github_user.get_user_info()
