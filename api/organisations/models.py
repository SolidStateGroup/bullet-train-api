# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import AbstractBaseExportableModel
from django.conf import settings
from django.db import models
from django.utils import timezone
from django_lifecycle import (
    AFTER_CREATE,
    AFTER_SAVE,
    BEFORE_DELETE,
    LifecycleModelMixin,
    hook,
)

from organisations.chargebee import (
    get_customer_id_from_subscription_id,
    get_max_api_calls_for_plan,
    get_max_seats_for_plan,
    get_plan_meta_data,
    get_portal_url,
    get_subscription_metadata,
)
from organisations.chargebee.chargebee import (
    cancel_subscription as cancel_chargebee_subscription,
)
from organisations.subscriptions.constants import (
    CHARGEBEE,
    FREE_PLAN_SUBSCRIPTION_METADATA,
    MAX_SEATS_IN_FREE_PLAN,
    SUBSCRIPTION_PAYMENT_METHODS,
    XERO,
)
from organisations.subscriptions.metadata import BaseSubscriptionMetadata
from users.utils.mailer_lite import MailerLite
from webhooks.models import AbstractBaseWebhookModel


class OrganisationRole(models.TextChoices):
    ADMIN = ("ADMIN", "Admin")
    USER = ("USER", "User")


class Organisation(LifecycleModelMixin, AbstractBaseExportableModel):
    name = models.CharField(max_length=2000)
    has_requested_features = models.BooleanField(default=False)
    webhook_notification_email = models.EmailField(null=True, blank=True)
    created_date = models.DateTimeField("DateCreated", auto_now_add=True)
    alerted_over_plan_limit = models.BooleanField(default=False)
    stop_serving_flags = models.BooleanField(
        default=False,
        help_text="Enable this to cease serving flags for this organisation.",
    )
    restrict_project_create_to_admin = models.BooleanField(default=False)
    persist_trait_data = models.BooleanField(
        default=settings.DEFAULT_ORG_STORE_TRAITS_VALUE,
        help_text="Disable this if you don't want Flagsmith "
        "to store trait data for this org's identities.",
    )
    block_access_to_admin = models.BooleanField(
        default=False,
        help_text="Enable this to block all the access to admin "
        "interface for the organisation",
    )
    feature_analytics = models.BooleanField(
        default=False, help_text="Record feature analytics in InfluxDB"
    )

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return "Org %s (#%s)" % (self.name, self.id)

    # noinspection PyTypeChecker
    def get_unique_slug(self):
        return str(self.id) + "-" + self.name

    @property
    def num_seats(self):
        return self.users.count()

    def has_subscription(self):
        return (
            hasattr(self, "subscription")
            and self.subscription.subscription_id is not None
        )

    @property
    def is_paid(self):
        return self.has_subscription() and self.subscription.cancellation_date is None

    def over_plan_seats_limit(self):
        if self.has_subscription():
            return self.num_seats > self.subscription.max_seats

        return self.num_seats > MAX_SEATS_IN_FREE_PLAN

    def reset_alert_status(self):
        self.alerted_over_plan_limit = False
        self.save()

    @hook(BEFORE_DELETE)
    def cancel_subscription(self):
        if self.has_subscription():
            self.subscription.cancel()


class UserOrganisation(models.Model):
    user = models.ForeignKey("users.FFAdminUser", on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=50, choices=OrganisationRole.choices)

    class Meta:
        unique_together = (
            "user",
            "organisation",
        )


class Subscription(LifecycleModelMixin, AbstractBaseExportableModel):
    organisation = models.OneToOneField(
        Organisation, on_delete=models.CASCADE, related_name="subscription"
    )
    subscription_id = models.CharField(max_length=100, blank=True, null=True)
    subscription_date = models.DateTimeField(blank=True, null=True)
    plan = models.CharField(max_length=100, null=True, blank=True)
    max_seats = models.IntegerField(default=1)
    max_api_calls = models.BigIntegerField(default=50000)
    cancellation_date = models.DateTimeField(blank=True, null=True)
    customer_id = models.CharField(max_length=100, blank=True, null=True)

    payment_method = models.CharField(
        max_length=20,
        choices=SUBSCRIPTION_PAYMENT_METHODS,
        default=CHARGEBEE,
    )
    notes = models.CharField(max_length=500, blank=True, null=True)

    def update_plan(self, plan_id):
        plan_metadata = get_plan_meta_data(plan_id)
        self.cancellation_date = None
        self.plan = plan_id
        self.max_seats = get_max_seats_for_plan(plan_metadata)
        self.max_api_calls = get_max_api_calls_for_plan(plan_metadata)
        self.save()

    @hook(AFTER_CREATE)
    @hook(AFTER_SAVE, when="cancellation_date", has_changed=True)
    def update_mailer_lite_subscribers(self):
        if settings.MAILERLITE_API_KEY:
            mailer_lite = MailerLite()
            mailer_lite.update_organisation_users(self.organisation.id)

    def cancel(self, cancellation_date=timezone.now(), update_chargebee=True):
        self.cancellation_date = cancellation_date
        self.save()
        if self.payment_method == CHARGEBEE and update_chargebee:
            cancel_chargebee_subscription(self.subscription_id)

    def get_portal_url(self, redirect_url):
        if not self.subscription_id:
            return None

        if not self.customer_id:
            self.customer_id = get_customer_id_from_subscription_id(
                self.subscription_id
            )
            self.save()
        return get_portal_url(self.customer_id, redirect_url)

    def get_subscription_metadata(self) -> BaseSubscriptionMetadata:
        metadata = None

        if self.payment_method == CHARGEBEE and self.subscription_id:
            metadata = get_subscription_metadata(self.subscription_id)
        elif self.payment_method == XERO and self.subscription_id:
            metadata = BaseSubscriptionMetadata(
                seats=self.max_seats,
                api_calls=self.max_api_calls,
                projects=None,
                payment_source=XERO,
            )

        if not metadata:
            metadata = FREE_PLAN_SUBSCRIPTION_METADATA

        return metadata


class OrganisationWebhook(AbstractBaseWebhookModel):
    name = models.CharField(max_length=100)
    enabled = models.BooleanField(default=True)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="webhooks"
    )

    class Meta:
        ordering = ("id",)  # explicit ordering to prevent pagination warnings
