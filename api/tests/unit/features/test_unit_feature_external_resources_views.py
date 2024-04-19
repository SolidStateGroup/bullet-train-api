import datetime

import pytest
import simplejson as json
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from django.urls import reverse
from freezegun import freeze_time
from pytest_lazyfixture import lazy_fixture
from rest_framework import status
from rest_framework.test import APIClient

from environments.models import Environment
from features.feature_external_resources.models import FeatureExternalResource
from features.models import Feature
from integrations.github.models import GithubConfiguration, GithubRepository

_django_json_encoder_default = DjangoJSONEncoder().default


def mocked_requests_post(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def raise_for_status(self) -> None:
            pass

        def json(self):
            return self.json_data

    return MockResponse(json_data={"data": "data"}, status_code=200)


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
@freeze_time("2024-01-01")
def test_create_feature_external_resource(
    # mock_generate_token,
    client: APIClient,
    feature: Feature,
    environment: Environment,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
    mocker,
) -> None:
    # Given
    mock_generate_token = mocker.patch(
        "integrations.github.github.generate_token",
    )
    mock_generate_token.return_value = "mocked_token"
    github_request_mock = mocker.patch(
        "requests.post", side_effect=mocked_requests_post
    )
    datetime_now = datetime.datetime.now()

    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://github.com/repoowner/repo-name/issues/35",
        "feature": feature.id,
        "metadata": {"status": "open"},
        "environment": environment.id,
    }

    url = reverse("api-v1:features:external-resources-list", args=[feature.id])

    # When
    response = client.post(url, data=feature_external_resource_data, format="json")

    github_request_mock.assert_called_with(
        "https://api.github.com/repos/repoowner/repo-name/issues/35/comments",
        json={
            "body": f"### This pull request is linked to a Flagsmith Feature (Test Feature1):\n**Test Environment**\n- [ ] Disabled\n\n```No value.```\n\nLast Updated {datetime_now.strftime('%dth %b %Y %I:%M%p')}"  # noqa E501
        },
        headers={
            "Accept": "application/vnd.github.v3+json",
            "Authorization": "Bearer mocked_token",
        },
        timeout=10,
    )
    # Then
    assert response.status_code == status.HTTP_201_CREATED
    # assert that the payload has been save to the database
    db_record = FeatureExternalResource.objects.filter(
        feature=feature,
        type=feature_external_resource_data["type"],
        url=feature_external_resource_data["url"],
    ).all()

    assert len(db_record) == 1
    assert db_record[0].metadata == json.dumps(
        feature_external_resource_data["metadata"], default=_django_json_encoder_default
    )
    assert db_record[0].feature == feature
    assert db_record[0].type == feature_external_resource_data["type"]
    assert db_record[0].url == feature_external_resource_data["url"]

    # And When
    data = {"environment": environment.id}
    url = reverse(
        "api-v1:features:external-resources-list",
        kwargs={"feature_pk": feature.id},
    )

    response = client.get(url, data=data)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["count"] == 1
    assert (
        response.json()["results"][0]["type"] == feature_external_resource_data["type"]
    )
    assert response.json()["results"][0]["url"] == feature_external_resource_data["url"]
    assert (
        response.json()["results"][0]["metadata"]
        == feature_external_resource_data["metadata"]
    )


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_cannot_create_feature_external_resource_when_doesnt_have_a_valid_gitHub_integration(
    client: APIClient,
    feature: Feature,
    environment: Environment,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://example.com?item=create",
        "feature": feature.id,
        "metadata": {"status": "open"},
        "environment": environment.id,
    }
    url = reverse("api-v1:features:external-resources-list", args=[feature.id])

    # When
    response = client.post(url, data=feature_external_resource_data, format="json")

    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_cannot_create_feature_external_resource_when_doesnt_have_permissions(
    client: APIClient,
    feature: Feature,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://example.com?item=create",
        "feature": feature.id,
        "metadata": {"status": "open"},
        "environment": 3,
    }
    url = reverse("api-v1:features:external-resources-list", args=[feature.id])

    # When
    response = client.post(url, data=feature_external_resource_data, format="json")

    # Then
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_cannot_create_feature_external_resource_when_the_type_is_incorrect(
    client: APIClient,
    feature: Feature,
    environment: Environment,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "UNKNOWN_TYPE",
        "url": "https://example.com",
        "feature": feature.id,
        "environment": environment.id,
    }
    url = reverse("api-v1:features:external-resources-list", args=[feature.id])

    # When
    response = client.post(url, data=feature_external_resource_data)
    # Then
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_cannot_create_feature_external_resource_due_to_unique_constraint(
    client: APIClient,
    feature: Feature,
    feature_external_resource: FeatureExternalResource,
    environment: Environment,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    feature_external_resource_data = {
        "type": "GITHUB_ISSUE",
        "url": "https://github.com/userexample/example-project-repo/issues/11",
        "feature": feature.id,
        "environment": environment.id,
    }
    url = reverse("api-v1:features:external-resources-list", args=[feature.id])

    # When
    with pytest.raises(IntegrityError) as exc_info:
        response = client.post(url, data=feature_external_resource_data)

        # Then
        assert "duplicate key value violates unique constraint" in str(exc_info.value)
        assert (
            "Key (feature_id, url)=(1, https://github.com/userexample/example-project-repo/issues/11) already exists."
            in str(exc_info.value)
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_delete_feature_external_resource(
    client: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    environment: Environment,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
    mocker,
) -> None:
    # Given
    data = {"environment": environment.id}
    mock_generate_token = mocker.patch(
        "integrations.github.github.generate_token",
    )
    mock_generate_token.return_value = "mocked_token"
    url = reverse(
        "api-v1:features:external-resources-detail",
        args=[feature.id, feature_external_resource.id],
    )

    # When
    response = client.delete(url, data=data)

    # Then
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not FeatureExternalResource.objects.filter(
        id=feature_external_resource.id
    ).exists()


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_get_feature_external_resources(
    client: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    environment: Environment,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    data = {"environment": environment.id}
    url = reverse(
        "api-v1:features:external-resources-list",
        kwargs={"feature_pk": feature.id},
    )

    # When
    response = client.get(url, data=data)

    # Then
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize(
    "client",
    [lazy_fixture("admin_master_api_key_client"), lazy_fixture("admin_client")],
)
def test_get_feature_external_resource(
    client: APIClient,
    feature_external_resource: FeatureExternalResource,
    feature: Feature,
    environment: Environment,
    github_configuration: GithubConfiguration,
    github_repository: GithubRepository,
) -> None:
    # Given
    data = {"environment": environment.id}
    url = reverse(
        "api-v1:features:external-resources-detail",
        args=[feature.id, feature_external_resource.id],
    )

    # When
    response = client.get(url, data=data)

    # Then
    assert response.status_code == status.HTTP_200_OK
    assert response.data["id"] == feature_external_resource.id
    assert response.data["type"] == feature_external_resource.type
    assert response.data["url"] == feature_external_resource.url
