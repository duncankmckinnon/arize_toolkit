import pytest
from unittest.mock import MagicMock


@pytest.fixture
def gql_client():
    """Mock GraphQL client"""
    return MagicMock()
