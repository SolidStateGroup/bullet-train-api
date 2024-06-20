from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in
from django.db.models import F
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import PermissionDenied

from organisations.invites.models import Invite
from users.auth_type import AuthType
from users.models import SignUpType

from ..constants import USER_REGISTRATION_WITHOUT_INVITE_ERROR_MESSAGE
from .github import GithubUser
from .google import get_user_info

GOOGLE_URL = "https://www.googleapis.com/oauth2/v1/userinfo?alt=json&"
UserModel = get_user_model()


class OAuthLoginSerializer(serializers.Serializer):
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

    auth_type: AuthType | None = None
    user_model_id_attribute: str = None

    class Meta:
        abstract = True

    def create(self, validated_data):
        user_info = self.get_user_info()
        if settings.AUTH_CONTROLLER_INSTALLED:
            from auth_controller.controller import (
                is_authentication_method_valid,
            )

            is_authentication_method_valid(
                self.context.get("request"),
                email=user_info.get("email"),
                raise_exception=True,
            )

        user = self._get_user(user_info)
        user_logged_in.send(
            sender=UserModel, request=self.context.get("request"), user=user
        )
        return Token.objects.get_or_create(user=user)[0]

    def _get_user(self, user_data: dict):
        email: str = user_data.pop("email")

        existing_user = (
            UserModel.objects.filter(email__iexact=email)
            .order_by(
                F("google_user_id").desc(nulls_last=True),
                F("github_user_id").desc(nulls_last=True),
            )
            .first()
        )

        if not existing_user:
            sign_up_type = self.validated_data.get("sign_up_type")
            if not (
                settings.ALLOW_REGISTRATION_WITHOUT_INVITE
                or sign_up_type == SignUpType.INVITE_LINK.value
                or Invite.objects.filter(email=email).exists()
            ):
                raise PermissionDenied(USER_REGISTRATION_WITHOUT_INVITE_ERROR_MESSAGE)

            return UserModel.objects.create(
                **user_data, email=email.lower(), sign_up_type=sign_up_type
            )
        elif existing_user.auth_type != self.get_auth_type().value:
            # In this scenario, we're seeing a user that had previously
            # authenticated with another authentication method and is now
            # authenticating with a new OAuth provider.
            user_model_id_attribute = self.get_user_model_id_attribute()
            setattr(
                existing_user,
                user_model_id_attribute,
                user_data[user_model_id_attribute],
            )
            existing_user.save()

        return existing_user

    def get_user_info(self):
        raise NotImplementedError("`get_user_info()` must be implemented.")

    def get_auth_type(self) -> AuthType:
        if not self.auth_type:
            raise NotImplementedError(
                "`auth_type` must be set, or `get_auth_type()` must be implemented."
            )
        return self.auth_type

    def get_user_model_id_attribute(self) -> str:
        if not self.user_model_id_attribute:
            raise NotImplementedError(
                "`user_model_id_attribute` must be set, "
                "or `get_user_model_id_attribute()` must be implemented."
            )
        return self.user_model_id_attribute


class GoogleLoginSerializer(OAuthLoginSerializer):
    auth_type = AuthType.GOOGLE
    user_model_id_attribute = "google_user_id"

    def get_user_info(self):
        return get_user_info(self.validated_data["access_token"])


class GithubLoginSerializer(OAuthLoginSerializer):
    auth_type = AuthType.GITHUB
    user_model_id_attribute = "github_user_id"

    def get_user_info(self):
        github_user = GithubUser(code=self.validated_data["access_token"])
        return github_user.get_user_info()
