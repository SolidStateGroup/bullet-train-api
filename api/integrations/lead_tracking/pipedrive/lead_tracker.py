import logging

from django.conf import settings

from integrations.lead_tracking.lead_tracking import LeadTracker
from users.models import FFAdminUser

from .client import PipedriveAPIClient
from .exceptions import EntityNotFoundError, MultipleMatchingOrganizationsError
from .models import PipedriveLead, PipedriveOrganization

logger = logging.getLogger(__name__)


class PipedriveLeadTracker(LeadTracker):
    def create_lead(self, user: FFAdminUser) -> PipedriveLead:
        email_domain = user.email.split("@")[-1]

        try:
            organization = self._get_org_by_domain(email_domain)
        except EntityNotFoundError:
            organization = self.create_organization(email_domain)
        except MultipleMatchingOrganizationsError as e:
            logger.error(
                "Multiple organizations found in Pipedrive for domain %s", email_domain
            )
            raise e

        return self.client.create_lead(
            title=user.full_name, organization_id=organization.id
        )

    def create_organization(self, organization_domain: str) -> PipedriveOrganization:
        # grab the org name from the email domain, e.g. google.com -> google
        org_name = organization_domain.split(".")[-2]
        organization = self.client.create_organization(
            name=org_name,
            organization_fields={
                settings.PIPEDRIVE_DOMAIN_ORGANIZATION_FIELD_KEY: organization_domain
            },
        )
        return organization

    def _get_org_by_domain(self, domain: str) -> PipedriveOrganization:
        matching_organizations = self.client.search_organizations(domain)
        if not matching_organizations:
            raise EntityNotFoundError()
        elif len(matching_organizations) > 1:
            raise MultipleMatchingOrganizationsError()
        return matching_organizations[0]

    def _get_client(self) -> PipedriveAPIClient:
        return PipedriveAPIClient(
            api_token=settings.PIPEDRIVE_API_TOKEN,
            base_url=settings.PIPEDRIVE_BASE_API_URL,
        )
