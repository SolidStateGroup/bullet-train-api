from enum import Enum

from organisations.subscriptions.metadata import BaseSubscriptionMetadata

MAX_SEATS_IN_FREE_PLAN = 1
MAX_API_CALLS_IN_FREE_PLAN = 50000
MAX_PROJECTS_IN_FREE_PLAN = 1
SUBSCRIPTION_DEFAULT_LIMITS = (
    MAX_API_CALLS_IN_FREE_PLAN,
    MAX_SEATS_IN_FREE_PLAN,
    MAX_PROJECTS_IN_FREE_PLAN,
)

CHARGEBEE = "CHARGEBEE"
XERO = "XERO"
SUBSCRIPTION_PAYMENT_METHODS = [
    (CHARGEBEE, "Chargebee"),
    (XERO, "Xero"),
]

FREE_PLAN_SUBSCRIPTION_METADATA = BaseSubscriptionMetadata(
    seats=MAX_SEATS_IN_FREE_PLAN,
    api_calls=MAX_API_CALLS_IN_FREE_PLAN,
    projects=MAX_PROJECTS_IN_FREE_PLAN,
)
FREE_PLAN_ID = "free"


class SubscriptionCacheEntity(Enum):
    INFLUX = "INFLUX"
    CHARGEBEE = "CHARGEBEE"
