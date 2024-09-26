import logging
import typing
import uuid
from decimal import Decimal
from typing import Dict, Tuple

from django.utils import timezone
from flag_engine.identities.traits.types import map_any_value_to_trait_value

from edge_api.identities.models import EdgeIdentity
from environments.identities.traits.models import Trait
from features.models import Feature, FeatureState
from features.multivariate.models import MultivariateFeatureOption

EXPORT_EDGE_IDENTITY_PAGINATION_LIMIT = 20000

logger = logging.getLogger()


def export_edge_identity_and_overrides(  # noqa: C901
    environment_api_key: str,
) -> Tuple[list, list, list]:
    kwargs = {
        "environment_api_key": environment_api_key,
        "limit": EXPORT_EDGE_IDENTITY_PAGINATION_LIMIT,
    }
    identity_export = []
    traits_export = []
    identity_override_export = []

    feature_id_to_uuid: Dict[int, str] = {}

    mv_feature_option_id_to_uuid: Dict[int, str] = {}
    while True:
        response = EdgeIdentity.dynamo_wrapper.get_all_items(**kwargs)
        for item in response["Items"]:
            identifier = item["identifier"]
            # export identity
            identity_export.append(
                export_edge_identity(
                    identifier, environment_api_key, item["created_date"]
                )
            )
            # export traits
            for trait in item["identity_traits"]:
                traits_export.append(
                    export_edge_trait(trait, identifier, environment_api_key)
                )
            for override in item["identity_features"]:
                featurestate_uuid = override["featurestate_uuid"]
                feature_id = override["feature"]["id"]
                if feature_id not in feature_id_to_uuid:
                    try:
                        feature_id_to_uuid[feature_id] = _get_feature_uuid(feature_id)
                    except Feature.DoesNotExist:
                        logging.warning("Feature with id %s does not exist", feature_id)
                        continue

                feature_uuid = feature_id_to_uuid[feature_id]

                # export feature state
                identity_override_export.append(
                    export_edge_feature_state(
                        identifier,
                        environment_api_key,
                        featurestate_uuid,
                        feature_uuid,
                        override["enabled"],
                    )
                )
                featurestate_value = override["feature_state_value"]
                if featurestate_value is not None:
                    # export feature state value
                    identity_override_export.append(
                        export_featurestate_value(featurestate_value, featurestate_uuid)
                    )
                if mvfsv := override["multivariate_feature_state_values"]:
                    # only one mvfs override can exists
                    mv_feature_option_id = mvfsv[0]["multivariate_feature_option"]["id"]
                    if mv_feature_option_id not in mv_feature_option_id_to_uuid:
                        try:
                            mv_feature_option_id_to_uuid[mv_feature_option_id] = (
                                _get_mv_feature_option_uuid(mv_feature_option_id)
                            )
                        except MultivariateFeatureOption.DoesNotExist:
                            logging.warning(
                                "MultivariateFeatureOption with id %s does not exist",
                                mv_feature_option_id,
                            )
                            continue

                    mv_feature_option_uuid = mv_feature_option_id_to_uuid[
                        mv_feature_option_id
                    ]

                    # export mv feature state value
                    identity_override_export.append(
                        export_mv_featurestate_value(
                            featurestate_uuid, mv_feature_option_uuid
                        )
                    )
        if "LastEvaluatedKey" not in response:
            break
        kwargs["start_key"] = response["LastEvaluatedKey"]
    return identity_export, traits_export, identity_override_export


def _get_feature_uuid(feature_id: int) -> str:
    return Feature.objects.get(id=feature_id).uuid


def _get_mv_feature_option_uuid(mv_feature_option_id: int) -> str:
    return MultivariateFeatureOption.objects.get(id=mv_feature_option_id).uuid


def export_edge_trait(trait: dict, identifier: str, environment_api_key: str) -> dict:
    trait_value = map_any_value_to_trait_value(trait["trait_value"])
    trait_value_data = Trait.generate_trait_value_data(trait_value)
    return {
        "model": "traits.trait",
        "fields": {
            "identity": [identifier, environment_api_key],
            "created_date": timezone.now().isoformat(),
            "trait_key": trait["trait_key"],
            **trait_value_data,
        },
    }


def export_edge_identity(
    identifier: str, environment_api_key: str, created_date: str
) -> dict:
    return {
        "model": "identities.identity",
        "fields": {
            "identifier": identifier,
            "created_date": created_date,
            "environment": [environment_api_key],
        },
    }


def export_edge_feature_state(
    identifier: str,
    environment_api_key: str,
    featurestate_uuid: str,
    feature_uuid: str,
    enabled: bool,
) -> dict:
    # NOTE: All of the datetime columns are not part of
    # dynamo but are part of the django model
    # hence we are setting them to current time
    return {
        "model": "features.featurestate",
        "fields": {
            "uuid": featurestate_uuid,
            "created_at": timezone.now().isoformat(),
            "updated_at": timezone.now().isoformat(),
            "live_from": timezone.now().isoformat(),
            "feature": [feature_uuid],
            "environment": [environment_api_key],
            "identity": [
                identifier,
                environment_api_key,
            ],
            "feature_segment": None,
            "enabled": enabled,
            "version": 1,
        },
    }


def export_featurestate_value(
    featurestate_value: typing.Any, featurestate_uuid: str
) -> dict:
    if isinstance(featurestate_value, Decimal):
        if featurestate_value.as_tuple().exponent == 0:
            featurestate_value = int(featurestate_value)

    fsv_data = FeatureState().generate_feature_state_value_data(featurestate_value)
    fsv_data.pop("feature_state")

    return {
        "model": "features.featurestatevalue",
        "fields": {
            "uuid": uuid.uuid4(),
            "feature_state": [featurestate_uuid],
            **fsv_data,
        },
    }


def export_mv_featurestate_value(
    featurestate_uuid: str, mv_feature_option_uuid: int
) -> dict:

    return {
        "model": "multivariate.multivariatefeaturestatevalue",
        "fields": {
            "uuid": uuid.uuid4(),
            "feature_state": [featurestate_uuid],
            "multivariate_feature_option": [mv_feature_option_uuid],
            "percentage_allocation": 100.0,
        },
    }
