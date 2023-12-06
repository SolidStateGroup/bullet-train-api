import json

from django.db.models import QuerySet
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.request import Request
from rest_framework.response import Response

from environments.models import Environment

from .models import FeatureExport
from .permissions import (
    CreateFeatureExportPermissions,
    DownloadFeatureExportPermissions,
    FeatureExportListPermissions,
    FeatureImportPermissions,
)
from .serializers import (
    CreateFeatureExportSerializer,
    FeatureExportSerializer,
    FeatureImportSerializer,
    FeatureImportUploadSerializer,
)


@swagger_auto_schema(
    method="POST",
    request_body=CreateFeatureExportSerializer(),
    responses={201: CreateFeatureExportSerializer()},
)
@api_view(["POST"])
@permission_classes([CreateFeatureExportPermissions])
def create_feature_export(request: Request) -> Response:
    serializer = CreateFeatureExportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()

    return Response(serializer.validated_data, status=201)


@swagger_auto_schema(
    method="POST",
    request_body=FeatureImportUploadSerializer(),
    responses={201: FeatureImportSerializer()},
)
@api_view(["POST"])
@permission_classes([FeatureImportPermissions])
def feature_import(request: Request, environment_id: int) -> Response:
    upload_serializer = FeatureImportUploadSerializer(data=request.data)
    feature_import = upload_serializer.save(environment_id=environment_id)
    serializer = FeatureImportSerializer(feature_import)
    return Response(serializer.data, status=201)


@swagger_auto_schema(
    method="GET",
    responses={200: "File downloaded"},
    operation_description="This endpoint is to download a feature export file from a specific environment",
)
@api_view(["GET"])
@permission_classes([DownloadFeatureExportPermissions])
def download_feature_export(request: Request, feature_export_id: int) -> Response:
    feature_export = get_object_or_404(FeatureExport, id=feature_export_id)

    response = Response(
        json.loads(feature_export.data), content_type="application/json"
    )
    response.headers[
        "Content-Disposition"
    ] = f"attachment; filename=feature_export.{feature_export_id}.json"
    return response


class FeatureExportListView(ListAPIView):
    serializer_class = FeatureExportSerializer
    permission_classes = [FeatureExportListPermissions]

    def get_queryset(self) -> QuerySet[FeatureExport]:
        environment_ids = []
        user = self.request.user

        for environment in Environment.objects.filter(
            project_id=self.kwargs["project_id"],
        ):
            if user.is_environment_admin(environment):
                environment_ids.append(environment.id)

        # Order by environment name to match environment list order.
        return FeatureExport.objects.filter(environment__in=environment_ids).order_by(
            "environment__name"
        )
