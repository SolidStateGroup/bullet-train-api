from django.conf import settings
from github import Auth, Github


def generate_token(installation_id: str, app_id: int) -> str:  # pragma: no cover
    auth: Auth.AppInstallationAuth = Auth.AppAuth(
        app_id=int(app_id), private_key=settings.GITHUB_PEM
    ).get_installation_auth(
        installation_id=int(installation_id),
        token_permissions=None,
    )
    Github(auth=auth)
    token = auth.token
    return token


def generate_jwt_token(app_id: int) -> str:  # pragma: no cover
    github_auth: Auth.AppAuth = Auth.AppAuth(
        app_id=int(app_id),
        private_key=settings.GITHUB_PEM,
    )
    token = github_auth.create_jwt()
    return token
