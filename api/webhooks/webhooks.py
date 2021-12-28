import enum
import hashlib
import hmac
import json
import typing

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.serializers.json import DjangoJSONEncoder
from django.template.loader import get_template

from webhooks.sample_webhook_data import (
    environment_webhook_data,
    organisation_webhook_data,
)

from .constants import WEBHOOK_SIGNATURE_HEADER
from .serializers import WebhookSerializer


class WebhookEventType(enum.Enum):
    FLAG_UPDATED = "FLAG_UPDATED"
    AUDIT_LOG_CREATED = "AUDIT_LOG_CREATED"


class WebhookType(enum.Enum):
    ORGANISATION = "ORGANISATION"
    ENVIRONMENT = "ENVIRONMENT"


def generate_signature(payload: str, key: str) -> str:
    return hmac.new(
        key=key.encode(), msg=payload.encode(), digestmod=hashlib.sha256
    ).hexdigest()


def call_environment_webhooks(environment, data, event_type):
    _call_webhooks(
        environment.webhooks.filter(enabled=True),
        data,
        event_type,
        WebhookType.ENVIRONMENT,
    )


def call_organisation_webhooks(organisation, data, event_type):
    _call_webhooks(
        organisation.webhooks.filter(enabled=True),
        data,
        event_type,
        WebhookType.ORGANISATION,
    )


def trigger_sample_environment_webhook(
    webhook,
) -> typing.Optional[requests.models.Response]:
    data = environment_webhook_data
    serializer = WebhookSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return _call_webhook(webhook, serializer, WebhookType.ENVIRONMENT, False)


def trigger_sample_organisation_webhook(
    webhook,
) -> typing.Optional[requests.models.Response]:
    data = organisation_webhook_data
    serializer = WebhookSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return _call_webhook(webhook, serializer, WebhookType.ORGANISATION, False)


def _call_webhook(
    webhook, serializer, webhook_type, send_email_on_error=True
) -> typing.Optional[requests.models.Response]:
    try:
        headers = {"content-type": "application/json"}
        json_data = json.dumps(serializer.data, sort_keys=True, cls=DjangoJSONEncoder)
        if webhook.secret:
            signature = generate_signature(json_data, key=webhook.secret)
            headers.update({WEBHOOK_SIGNATURE_HEADER: signature})

        res = requests.post(str(webhook.url), data=json_data, headers=headers)
    except requests.exceptions.ConnectionError:
        if send_email_on_error:
            send_failure_email(webhook, serializer.data, webhook_type)
        return None

    if res.status_code != 200 and send_email_on_error:
        send_failure_email(webhook, serializer.data, webhook_type, res.status_code)
    return res


def _call_webhooks(webhooks, data, event_type, webhook_type):
    webhook_data = {"event_type": event_type.value, "data": data}
    serializer = WebhookSerializer(data=webhook_data)
    serializer.is_valid(raise_exception=False)
    for webhook in webhooks:
        _call_webhook(webhook, serializer, webhook_type)


def send_failure_email(webhook, data, webhook_type, status_code=None):
    template_data = _get_failure_email_template_data(
        webhook, data, webhook_type, status_code
    )
    organisation = (
        webhook.organisation
        if webhook_type == WebhookType.ORGANISATION
        else webhook.environment.project.organisation
    )

    text_template = get_template("features/webhook_failure.txt")
    text_content = text_template.render(template_data)
    subject = "Flagsmith Webhook Failure"
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_CONFIGURATION.get("INVITE_FROM_EMAIL"),
        [organisation.webhook_notification_email],
    )
    msg.content_subtype = "plain"
    msg.send()


def _get_failure_email_template_data(webhook, data, webhook_type, status_code=None):
    data = {
        "status_code": status_code,
        "data": json.dumps(data, sort_keys=True, indent=2, cls=DjangoJSONEncoder),
        "webhook_url": webhook.url,
    }

    if webhook_type == WebhookType.ENVIRONMENT:
        data["project_name"] = webhook.environment.project.name
        data["environment_name"] = webhook.environment.name

    return data
