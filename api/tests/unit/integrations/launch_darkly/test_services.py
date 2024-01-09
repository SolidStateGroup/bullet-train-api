from unittest.mock import MagicMock

import pytest
from django.core import signing
from flag_engine.segments import constants as segment_constants
from requests.exceptions import HTTPError, RequestException, Timeout

from environments.models import Environment
from features.models import Feature, FeatureState
from integrations.launch_darkly.models import LaunchDarklyImportRequest
from integrations.launch_darkly.services import (
    create_import_request,
    process_import_request,
)
from projects.models import Project
from projects.tags.models import Tag
from segments.models import Condition, Segment, SegmentRule
from users.models import FFAdminUser


def test_create_import_request__return_expected(
    ld_client_mock: MagicMock,
    ld_client_class_mock: MagicMock,
    project: Project,
    test_user: FFAdminUser,
) -> None:
    # Given
    ld_project_key = "test-project-key"
    ld_token = "test-token"

    expected_salt = f"ld_import_{test_user.id}"

    # When
    result = create_import_request(
        project=project,
        user=test_user,
        ld_project_key=ld_project_key,
        ld_token=ld_token,
    )

    # Then
    ld_client_class_mock.assert_called_once_with(ld_token)
    ld_client_mock.get_project.assert_called_once_with(project_key=ld_project_key)
    ld_client_mock.get_flag_count.assert_called_once_with(project_key=ld_project_key)

    assert result.status == {
        "requested_environment_count": 2,
        "requested_flag_count": 9,
    }
    assert signing.loads(result.ld_token, salt=expected_salt) == ld_token
    assert result.ld_project_key == ld_project_key
    assert result.created_by == test_user
    assert result.project == project


@pytest.mark.parametrize(
    "failing_ld_client_method_name", ["get_environments", "get_flags", "get_flag_tags"]
)
@pytest.mark.parametrize(
    "exception, expected_error_message",
    [
        (
            HTTPError(response=MagicMock(status_code=503)),
            "HTTPError 503 when requesting /expected_path",
        ),
        (Timeout(), "Timeout when requesting /expected_path"),
    ],
)
def test_process_import_request__api_error__expected_status(
    ld_client_mock: MagicMock,
    ld_client_class_mock: MagicMock,
    failing_ld_client_method_name: str,
    exception: RequestException,
    expected_error_message: str,
    import_request: LaunchDarklyImportRequest,
) -> None:
    # Given
    exception.request = MagicMock(path_url="/expected_path")
    getattr(ld_client_mock, failing_ld_client_method_name).side_effect = exception

    # When
    with pytest.raises(type(exception)):
        process_import_request(import_request)

    # Then
    assert import_request.completed_at
    assert import_request.ld_token == ""
    assert import_request.status["result"] == "failure"
    assert import_request.status["error_message"] == expected_error_message


def test_process_import_request__success__expected_status(
    project: Project,
    import_request: LaunchDarklyImportRequest,
):
    # When
    process_import_request(import_request)

    # Then
    # Import request is marked as completed successfully.
    assert import_request.completed_at
    assert import_request.ld_token == ""
    assert import_request.status["result"] == "success"

    # Environment names are correct.
    assert list(
        Environment.objects.filter(project=project).values_list("name", flat=True)
    ) == ["Test", "Production"]

    # Feature names are correct.
    assert list(
        Feature.objects.filter(project=project).values_list("name", flat=True)
    ) == [
        "flag1",
        "flag2_value",
        "flag3_multivalue",
        "flag4_multivalue",
        "flag5",
        "TEST_TARGETED_CONTEXT",
        "TEST_INDIVIDUAL_TARGET",
        "TEST_SEGMENT_TARGET",
        "TEST_COMBINED_TARGET",
    ]

    # Tags are created and set as expected.
    assert set(Tag.objects.filter(project=project).values_list("label", "color")) == {
        ("testtag", "#3d4db6"),
        ("testtag2", "#3d4db6"),
        ("Imported", "#3d4db6"),
    }
    assert set(
        Feature.objects.filter(project=project).values_list("name", "tags__label")
    ) == {
        ("flag1", "Imported"),
        ("flag2_value", "Imported"),
        ("flag3_multivalue", "Imported"),
        ("flag4_multivalue", "Imported"),
        ("flag5", "testtag"),
        ("flag5", "Imported"),
        ("flag5", "testtag2"),
        ("TEST_TARGETED_CONTEXT", "Imported"),
        ("TEST_INDIVIDUAL_TARGET", "Imported"),
        ("TEST_SEGMENT_TARGET", "Imported"),
        ("TEST_COMBINED_TARGET", "Imported"),
    }

    # Standard feature states have expected values.
    boolean_standard_feature = Feature.objects.get(project=project, name="flag1")
    boolean_standard_feature_states_by_env_name = {
        fs.environment.name: fs
        for fs in FeatureState.objects.filter(feature=boolean_standard_feature)
    }
    boolean_standard_feature_states_by_env_name["Test"].enabled is True
    boolean_standard_feature_states_by_env_name["Production"].enabled is False

    string_standard_feature = Feature.objects.get(project=project, name="flag2_value")
    string_standard_feature_states_by_env_name = {
        fs.environment.name: fs
        for fs in FeatureState.objects.filter(feature=string_standard_feature)
    }
    assert string_standard_feature_states_by_env_name["Test"].enabled is True
    assert (
        string_standard_feature_states_by_env_name["Test"].get_feature_state_value()
        == "123123"
    )
    assert (
        string_standard_feature_states_by_env_name["Test"].feature_state_value.type
        == "unicode"
    )
    assert (
        string_standard_feature_states_by_env_name[
            "Test"
        ].feature_state_value.string_value
        == "123123"
    )
    assert string_standard_feature_states_by_env_name["Production"].enabled is False
    assert (
        string_standard_feature_states_by_env_name[
            "Production"
        ].get_feature_state_value()
        == ""
    )
    assert (
        string_standard_feature_states_by_env_name[
            "Production"
        ].feature_state_value.type
        == "unicode"
    )
    assert (
        string_standard_feature_states_by_env_name[
            "Production"
        ].feature_state_value.string_value
        == ""
    )

    # Multivariate feature states with percentage rollout have expected values.
    percentage_mv_feature = Feature.objects.get(
        project=project, name="flag4_multivalue"
    )
    percentage_mv_feature_states_by_env_name = {
        fs.environment.name: fs
        for fs in FeatureState.objects.filter(feature=percentage_mv_feature)
    }

    assert percentage_mv_feature_states_by_env_name["Test"].enabled is False

    # The `off` variation from LD's environment is imported as the control value.
    assert (
        percentage_mv_feature_states_by_env_name["Test"].get_feature_state_value()
        == "variation2"
    )
    assert list(
        percentage_mv_feature_states_by_env_name[
            "Test"
        ].multivariate_feature_state_values.values_list(
            "multivariate_feature_option__string_value",
            "percentage_allocation",
        )
    ) == [("variation1", 100), ("variation2", 0), ("variation3", 0)]

    assert percentage_mv_feature_states_by_env_name["Production"].enabled is True

    # The `off` variation from LD's environment is imported as the control value.
    assert (
        percentage_mv_feature_states_by_env_name["Production"].get_feature_state_value()
        == "variation3"
    )
    assert list(
        percentage_mv_feature_states_by_env_name[
            "Production"
        ].multivariate_feature_state_values.values_list(
            "multivariate_feature_option__string_value",
            "percentage_allocation",
        )
    ) == [("variation1", 24), ("variation2", 25), ("variation3", 51)]

    # Tags are imported correctly.
    tagged_feature = Feature.objects.get(project=project, name="flag5")
    [tag.label for tag in tagged_feature.tags.all()] == ["testtag", "testtag2"]


def test_process_import_request__segments_imported(
    project: Project,
    import_request: LaunchDarklyImportRequest,
):
    # When
    process_import_request(import_request)

    # Then
    segments = Segment.objects.filter(project=project, feature_id=None)

    assert set(segments.values_list("name", flat=True)) == {
        # Segments
        "User List (Override for test)",
        "User List (Override for production)",
        "Dynamic List (Override for test)",
        "Dynamic List (Override for production)",
        "Dynamic List 2 (Override for test)",
        "Dynamic List 2 (Override for production)",
    }


def test_process_import_request__rules_imported(
    project: Project,
    import_request: LaunchDarklyImportRequest,
):
    # When
    process_import_request(import_request)

    # Then
    segments = Segment.objects.filter(project=project).exclude(feature_id=None)

    assert set(segments.values_list("name", flat=True)) == {
        # Feature Segments
        "Regular And",
        "Reverted And",
        "Just Not",
        # Feature Segments without descriptions
        "imported-56725db6-3d2a-4ed6-a2a1-60ef94ac62d5",
        "imported-a132f4aa-ad51-43c6-8d03-f18d6a5b205d",
        "imported-c034ec70-fcb3-4c15-9bea-b9fa0b341b4f",
        "imported-23b14914-3136-40f5-a64a-cdb3110a5277",
        "imported-d866a669-b439-4506-9ae6-83ea0e30ea38",
        "imported-dca5eadf-851e-4696-bb45-0fcce26944ba",
    }

    # Tests for "Regular And"

    and_rule = SegmentRule.objects.get(segment__name="Regular And")
    # Parents are always "ALL" rules.
    assert and_rule.type == SegmentRule.ALL_RULE

    and_subrules = SegmentRule.objects.filter(rule=and_rule)
    assert and_subrules.count() == 2
    # UI needs to have subrules as `ANY_RULE` to display properly.
    assert list(and_subrules)[0].type == SegmentRule.ANY_RULE
    assert list(and_subrules)[1].type == SegmentRule.ANY_RULE

    and_subconditions = Condition.objects.filter(rule__in=and_subrules)
    assert and_subconditions.count() == 2
    assert set(and_subconditions.values_list("property", "operator", "value")) == {
        ("p1", segment_constants.LESS_THAN_INCLUSIVE, "5"),
        ("p2", segment_constants.GREATER_THAN, "1"),
    }

    # Tests for "Reverted And"

    reverted_and_rule = SegmentRule.objects.get(segment__name="Reverted And")
    # Parents are always "ALL" rules.
    assert reverted_and_rule.type == SegmentRule.ALL_RULE

    reverted_and_subrules = SegmentRule.objects.filter(rule=reverted_and_rule).all()
    assert reverted_and_subrules.count() == 2
    assert list(reverted_and_subrules)[0].type == SegmentRule.ANY_RULE
    assert list(reverted_and_subrules)[1].type == SegmentRule.NONE_RULE

    reverted_and_any_subrule_conditions = Condition.objects.filter(
        rule=reverted_and_subrules[0]
    )
    assert reverted_and_any_subrule_conditions.count() == 1
    assert set(
        reverted_and_any_subrule_conditions.values_list("property", "operator", "value")
    ) == {
        ("p1", segment_constants.REGEX, ".*bar"),
    }

    reverted_and_none_subrule_conditions = Condition.objects.filter(
        rule=reverted_and_subrules[1]
    )
    assert reverted_and_none_subrule_conditions.count() == 2
    assert set(
        reverted_and_none_subrule_conditions.values_list(
            "property", "operator", "value"
        )
    ) == {
        ("p2", segment_constants.CONTAINS, "forbidden"),
        ("p2", segment_constants.CONTAINS, "words"),
    }

    # Tests for "Just Not
    just_not_rule = SegmentRule.objects.get(segment__name="Just Not")
    # Parents are always "ALL" rules.
    assert just_not_rule.type == SegmentRule.ALL_RULE

    just_not_subrules = SegmentRule.objects.filter(rule=just_not_rule).all()
    assert just_not_subrules.count() == 1
    assert list(just_not_subrules)[0].type == SegmentRule.NONE_RULE

    just_not_subrule_conditions = Condition.objects.filter(rule=just_not_subrules[0])
    assert just_not_subrule_conditions.count() == 1
    assert set(
        just_not_subrule_conditions.values_list("property", "operator", "value")
    ) == {
        ("p1", segment_constants.IN, "this,that"),
    }
