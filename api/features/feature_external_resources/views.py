import re

from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.response import Response

from features.models import Feature
from features.permissions import FeatureExternalResourcePermissions
from integrations.github.client import (
    get_github_issue_pr_title_and_state,
    label_github_issue_pr,
)
from organisations.models import Organisation

from .models import FeatureExternalResource
from .serializers import FeatureExternalResourceSerializer


class FeatureExternalResourceViewSet(viewsets.ModelViewSet):
    serializer_class = FeatureExternalResourceSerializer
    permission_classes = [FeatureExternalResourcePermissions]

    def get_queryset(self):
        if "pk" in self.kwargs:
            return FeatureExternalResource.objects.filter(id=self.kwargs["pk"])
        else:
            features_pk = self.kwargs["feature_pk"]
            return FeatureExternalResource.objects.filter(feature=features_pk)

    # Override get list view to add github issue/pr name to each linked external resource
    def list(self, request, *args, **kwargs) -> Response:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # get organisation id from feature and get feature from validated data
        organisation_id = get_object_or_404(
            Feature.objects.filter(id=self.kwargs["feature_pk"]),
        ).project.organisation_id

        for resource in data if isinstance(data, list) else []:
            if resource_url := resource.get("url"):
                resource["metadata"] = get_github_issue_pr_title_and_state(
                    organisation_id=organisation_id, resource_url=resource_url
                )

        return Response(data={"results": data})

    def create(self, request, *args, **kwargs):
        feature = get_object_or_404(
            Feature.objects.filter(
                id=self.kwargs["feature_pk"],
            ),
        )

        github_configuration = (
            Organisation.objects.prefetch_related("github_config")
            .get(id=feature.project.organisation_id)
            .github_config.first()
        )

        if not github_configuration or not hasattr(feature.project, "github_project"):
            return Response(
                data={
                    "detail": "This Project doesn't have a valid GitHub integration configuration"
                },
                content_type="application/json",
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Get repository owner and name, and issue/PR number from the external resource URL
            url = request.data.get("url")
            if request.data.get("type") == "GITHUB_PR":
                pattern = r"github.com/([^/]+)/([^/]+)/pull/(\d+)$"
            elif request.data.get("type") == "GITHUB_ISSUE":
                pattern = r"github.com/([^/]+)/([^/]+)/issues/(\d+)$"
            else:
                return Response(
                    data={"detail": "Incorrect GitHub type"},
                    content_type="application/json",
                    status=status.HTTP_400_BAD_REQUEST,
                )

            match = re.search(pattern, url)
            if match:
                owner, repo, issue = match.groups()

                label_github_issue_pr(
                    installation_id=github_configuration.installation_id,
                    owner=owner,
                    repo=repo,
                    issue=issue,
                )
                response = super().create(request, *args, **kwargs)
                return response
            else:
                return Response(
                    data={"detail": "Invalid GitHub Issue/PR URL"},
                    content_type="application/json",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except IntegrityError as e:
            if re.search(r"Key \(feature_id, url\)", str(e)) and re.search(
                r"already exists.$", str(e)
            ):
                return Response(
                    data={
                        "detail": "Duplication error. The feature already has this resource URI"
                    },
                    content_type="application/json",
                    status=status.HTTP_400_BAD_REQUEST,
                )

    def perform_update(self, serializer):
        external_resource_id = int(self.kwargs["pk"])
        serializer.save(id=external_resource_id)
