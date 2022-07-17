import pytest

from organisations.chargebee.types import ChargebeeObjMetadata


@pytest.fixture
def chargebee_object_metadata():
    return ChargebeeObjMetadata(seats=10, api_calls=100, projects=10)
