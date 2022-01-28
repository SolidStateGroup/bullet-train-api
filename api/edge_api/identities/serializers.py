from flag_engine.features.models import (
    FeatureStateModel as EngineFeatureStateModel,
)
from flag_engine.features.models import (
    MultivariateFeatureStateValueModel as EngineMultivariateFeatureStateValueModel,
)
from flag_engine.features.schemas import MultivariateFeatureStateValueSchema
from flag_engine.identities.builders import build_identity_dict
from flag_engine.utils.exceptions import (
    DuplicateFeatureState,
    InvalidPercentageAllocation,
)
from rest_framework import serializers

from environments.identities.models import Identity
from features.models import Feature, FeatureState, FeatureStateValue
from features.multivariate.models import (
    MultivariateFeatureOption,
    MultivariateFeatureStateValue,
)
from features.serializers import (
    FeatureStateSerializerFull,
    FeatureStateValueSerializer,
)

engine_multi_fs_value_schema = MultivariateFeatureStateValueSchema()


class EdgeMultivariateFeatureOptionField(serializers.Field):
    def to_internal_value(self, data):
        return MultivariateFeatureOption.objects.get(id=data)

    def to_representation(self, obj):
        return obj.id


class EdgeMultivariateFeatureStateValueSerializer(serializers.ModelSerializer):
    multivariate_feature_option = EdgeMultivariateFeatureOptionField()

    def to_internal_value(self, data):
        data = super().to_internal_value(data)
        return EngineMultivariateFeatureStateValueModel(**data)

    class Meta:
        model = MultivariateFeatureStateValue
        fields = (
            "multivariate_feature_option",
            "percentage_allocation",
        )


class FeatureStateValueEdgeIdentityField(serializers.Field):
    def to_representation(self, obj):
        identity_id = self.parent.get_identity_uuid()
        return obj.get_value(identity_id=identity_id)

    def get_attribute(self, instance):
        # We pass the object instance onto `to_representation`,
        # not just the field attribute.
        return instance

    def to_internal_value(self, data):
        feature_state_value_dict = FeatureState().generate_feature_state_value_data(
            data
        )

        data = {**feature_state_value_dict}
        fs_value_serializer = FeatureStateValueSerializer(data=data)
        fs_value_serializer.is_valid(raise_exception=True)
        return FeatureStateValue(**data).value


class EdgeFeatureField(serializers.Field):
    def to_representation(self, obj):
        return obj.id

    def to_internal_value(self, data):
        feature = Feature.objects.get(id=data)
        return feature


class EdgeIdentityFeatureStateSerializer(serializers.Serializer):
    feature_state_value = FeatureStateValueEdgeIdentityField()
    feature = EdgeFeatureField()
    multivariate_feature_state_values = EdgeMultivariateFeatureStateValueSerializer(
        many=True, required=False
    )
    enabled = serializers.BooleanField(required=False, default=False)
    identity_uuid = serializers.SerializerMethodField()

    featurestate_uuid = serializers.CharField(required=False, read_only=True)

    def get_identity_uuid(self, obj=None):
        return self.context["view"].kwargs["edge_identity_identity_uuid"]

    def save(self, **kwargs):
        identity = self.context["view"].identity
        feature_state_value = self.validated_data.pop("feature_state_value")

        if self.instance:
            if self.validated_data.get("multivariate_feature_state_values"):
                engine_multi_fs_value_models = engine_multi_fs_value_schema.load(
                    self.validated_data["multivariate_feature_state_values"], many=True
                )
                self.instance.multivariate_feature_state_values = (
                    engine_multi_fs_value_models
                )
            self.instance.set_value(feature_state_value)

        else:
            self.instance = EngineFeatureStateModel(**self.validated_data)
            try:
                identity.identity_features.append(self.instance)
            except DuplicateFeatureState as e:
                raise serializers.ValidationError(
                    "Feature state already exists."
                ) from e

        self.instance.set_value(feature_state_value)
        try:
            identity_dict = build_identity_dict(identity)
        except InvalidPercentageAllocation as e:
            raise serializers.ValidationError(
                {
                    "multivariate_feature_state_values": "Total percentage allocation"
                    "for feature must be less than 100 percent"
                }
            ) from e
        Identity.dynamo_wrapper.put_item(identity_dict)
        return self.instance


class FeatureStateSerializerFullWithIdentity(FeatureStateSerializerFull):
    identity_identifier = serializers.SerializerMethodField()

    def get_identity_identifier(self, instance):
        return instance.identity.identifier if instance.identity else None
