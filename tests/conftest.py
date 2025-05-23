from unittest.mock import MagicMock

import pytest


@pytest.fixture
def gql_client():
    """Mock GraphQL client"""
    return MagicMock()
