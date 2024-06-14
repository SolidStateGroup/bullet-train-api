import logging

from django.db import models

from environments.models import Environment
from integrations.common.models import EnvironmentIntegrationModel

logger = logging.getLogger(__name__)


class GrafanaConfiguration(EnvironmentIntegrationModel):
    base_url = models.URLField(blank=False, null=True)
    environment = models.OneToOneField(
        Environment, related_name="grafana_config", on_delete=models.CASCADE
    )