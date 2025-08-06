# Rules for Client Tests

When writing tests for the Arize Toolkit client (`tests/test_client.py`), follow these established patterns to ensure comprehensive test coverage and consistency.

## Test Structure

### 1. Test Organization

Group related tests into test classes:

```python
class TestResourceType:
    """Group all tests for a specific resource type"""

    def test_get_resource(self, client, mock_graphql_client):
        """Test getting a single resource"""
        pass

    def test_get_all_resources(self, client, mock_graphql_client):
        """Test getting all resources"""
        pass

    def test_create_resource(self, client, mock_graphql_client):
        """Test creating a resource"""
        pass

    def test_update_resource(self, client, mock_graphql_client):
        """Test updating a resource"""
        pass

    def test_delete_resource(self, client, mock_graphql_client):
        """Test deleting a resource"""
        pass
```

### 2. Fixture Usage

Always use the standard test fixtures:

```python
@pytest.fixture
def mock_graphql_client():
    """Create a mock GraphQL client"""
    with patch("arize_toolkit.client.GraphQLClient") as mock_client:
        # Mock the initial org/space lookup response
        mock_client.return_value.execute.return_value = {
            "account": {
                "organizations": {
                    "edges": [
                        {
                            "node": {
                                "id": "test_org_id",
                                "spaces": {
                                    "edges": [{"node": {"id": "test_space_id"}}]
                                },
                            }
                        }
                    ]
                }
            }
        }
        yield mock_client


@pytest.fixture
def client(mock_graphql_client):
    """Create a test client with mocked GraphQL client"""
    return Client(
        organization="test_org", space="test_space", arize_developer_key="test_token"
    )
```

### 3. Mock Response Pattern

Mock GraphQL responses to match the expected query structure:

```python
def test_get_resource(self, client, mock_graphql_client):
    """Test retrieving a resource by name"""
    # Reset mock to clear previous calls
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock the expected GraphQL response
    mock_graphql_client.return_value.execute.return_value = {
        "node": {
            "resources": {
                "edges": [
                    {
                        "node": {
                            "id": "resource_id",
                            "name": "resource_name",
                            "type": "resource_type",
                            "createdAt": "2024-01-01T00:00:00Z",
                        }
                    }
                ]
            }
        }
    }

    # Test the client method
    result = client.get_resource("resource_name")

    # Assert the expected results
    assert result["id"] == "resource_id"
    assert result["name"] == "resource_name"
    assert result["type"] == "resource_type"
    assert (
        result["createdAt"] == "2024-01-01T00:00:00.000000Z"
    )  # Note: Check datetime formatting
```

### 4. Pagination Testing

Test functions that handle pagination:

```python
def test_get_all_resources_with_pagination(self, client, mock_graphql_client):
    """Test getting all resources with pagination"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock multiple responses for pagination
    mock_responses = [
        {
            "node": {
                "resources": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [
                        {
                            "node": {
                                "id": "resource1",
                                "name": "Resource 1",
                            }
                        }
                    ],
                }
            }
        },
        {
            "node": {
                "resources": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [
                        {
                            "node": {
                                "id": "resource2",
                                "name": "Resource 2",
                            }
                        }
                    ],
                }
            }
        },
    ]

    mock_graphql_client.return_value.execute.side_effect = mock_responses

    results = client.get_all_resources()
    assert len(results) == 2
    assert results[0]["id"] == "resource1"
    assert results[1]["id"] == "resource2"
    assert mock_graphql_client.return_value.execute.call_count == 2
```

### 5. Error Handling Tests

Test both success and failure scenarios:

```python
def test_resource_not_found(self, client, mock_graphql_client):
    """Test handling when resource is not found"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock empty response
    mock_graphql_client.return_value.execute.return_value = {
        "node": {"resources": {"edges": []}}
    }

    with pytest.raises(ArizeAPIException) as exc_info:
        client.get_resource("non_existent_resource")
    assert "No resource found" in str(exc_info.value)


def test_api_error(self, client, mock_graphql_client):
    """Test handling API errors"""
    mock_graphql_client.return_value.execute.reset_mock()
    mock_graphql_client.return_value.execute.side_effect = Exception("API Error")

    with pytest.raises(Exception, match="API Error"):
        client.get_resource("resource_name")
```

### 6. Parametrized Tests

Use parametrization for testing multiple scenarios:

```python
@pytest.mark.parametrize(
    "input_params,expected_error",
    [
        (
            {
                "name": "test_resource",
                "type": "invalid_type",
                "setting": "value",
            },
            "Invalid resource type",
        ),
        (
            {
                "name": "",  # Empty name
                "type": "valid_type",
                "setting": "value",
            },
            "name is required",
        ),
    ],
)
def test_create_resource_validation(
    self, client, mock_graphql_client, input_params, expected_error
):
    """Test parameter validation for resource creation"""
    mock_graphql_client.return_value.execute.reset_mock()

    with pytest.raises(Exception) as exc_info:
        client.create_resource(**input_params)
    assert expected_error in str(exc_info.value)
```

### 7. Testing Creation Functions

Test functions that create resources and return URLs:

```python
def test_create_resource(self, client, mock_graphql_client):
    """Test creating a new resource"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock successful creation response
    mock_graphql_client.return_value.execute.return_value = {
        "createResource": {"resource": {"id": "new_resource_id"}}
    }

    # Test creation
    url = client.create_resource(
        name="new_resource",
        resource_type="type1",
        description="Test resource",
    )

    # Assert the URL is correctly generated
    assert url == client.resource_url("new_resource_id")

    # Verify the GraphQL call was made
    assert mock_graphql_client.return_value.execute.called
```

### 8. Testing Update Functions

Test update operations:

```python
def test_update_resource(self, client, mock_graphql_client):
    """Test updating a resource"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock getting the resource first (if needed for ID lookup)
    mock_graphql_client.return_value.execute.side_effect = [
        {
            "node": {
                "resources": {
                    "edges": [{"node": {"id": "resource_id", "name": "old_name"}}]
                }
            }
        },
        {
            "updateResource": {
                "resource": {
                    "id": "resource_id",
                    "name": "new_name",
                    "description": "Updated description",
                }
            }
        },
    ]

    result = client.update_resource(
        "old_name",
        name="new_name",
        description="Updated description",
    )

    assert result["name"] == "new_name"
    assert result["description"] == "Updated description"
```

### 9. Testing Delete Functions

Test deletion operations:

```python
def test_delete_resource(self, client, mock_graphql_client):
    """Test deleting a resource"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock getting resource ID, then successful deletion
    mock_graphql_client.return_value.execute.side_effect = [
        {"node": {"resources": {"edges": [{"node": {"id": "resource_id"}}]}}},
        {"deleteResource": {"clientMutationId": None}},
    ]

    result = client.delete_resource("resource_name")
    assert result is True
    assert mock_graphql_client.return_value.execute.call_count == 2
```

### 10. Testing Complex Operations

Test operations that involve multiple API calls:

```python
def test_copy_resource(self, client, mock_graphql_client):
    """Test copying a resource"""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock sequence: get source, get target model, create copy
    mock_graphql_client.return_value.execute.side_effect = [
        # Get source resource
        {
            "node": {
                "resources": {
                    "edges": [
                        {
                            "node": {
                                "id": "source_id",
                                "name": "source_resource",
                                "config": {"setting": "value"},
                            }
                        }
                    ]
                }
            }
        },
        # Get target parent
        {"node": {"parents": {"edges": [{"node": {"id": "target_parent_id"}}]}}},
        # Create copy
        {"createResource": {"resource": {"id": "copy_id"}}},
    ]

    url = client.copy_resource(
        current_resource_name="source_resource",
        current_parent_name="source_parent",
        new_parent_name="target_parent",
        new_resource_name="copied_resource",
    )

    assert url == client.resource_url("copy_id")
    assert mock_graphql_client.return_value.execute.call_count == 3
```

## Best Practices

### 1. Always Reset Mocks

```python
def test_something(self, client, mock_graphql_client):
    mock_graphql_client.return_value.execute.reset_mock()  # Always reset first
    # ... rest of test
```

### 2. Test Return Value Transformations

Verify that the client correctly transforms GraphQL responses:

```python
# GraphQL returns ISO format
mock_response = {"createdAt": "2024-01-01T00:00:00Z"}

# Client should format consistently
result = client.get_resource("name")
assert result["createdAt"] == "2024-01-01T00:00:00.000000Z"
```

### 3. Test Optional Parameters

Test functions with various combinations of optional parameters:

```python
# Test with minimal parameters
result1 = client.create_resource(name="resource", type="type1")

# Test with all parameters
result2 = client.create_resource(
    name="resource",
    type="type1",
    description="Description",
    tags=["tag1", "tag2"],
    environment="production",
)
```

### 4. Test Edge Cases

Include tests for edge cases:

```python
def test_empty_results(self, client, mock_graphql_client):
    """Test handling empty result sets"""
    mock_graphql_client.return_value.execute.return_value = {
        "node": {"resources": {"edges": []}}
    }

    results = client.get_all_resources()
    assert results == []


def test_null_values(self, client, mock_graphql_client):
    """Test handling null/None values in responses"""
    mock_graphql_client.return_value.execute.return_value = {
        "node": {"resource": {"id": "123", "description": None}}
    }

    result = client.get_resource_by_id("123")
    assert result["description"] is None
```

### 5. Test URL Generation

Always test that URL generation methods work correctly:

```python
def test_resource_url_generation(self, client):
    """Test URL generation for resources"""
    url = client.resource_url("resource_123")
    expected = f"{client.space_url}/resources/resource_123"
    assert url == expected
```

### 6. Use Descriptive Test Names

Test method names should clearly describe what is being tested:

```python
def test_get_resource_by_name_success(self, ...):
def test_get_resource_by_name_not_found(self, ...):
def test_create_resource_with_invalid_type(self, ...):
def test_update_resource_preserves_unchanged_fields(self, ...):
```

### 7. Document Complex Test Scenarios

Add docstrings to explain complex test scenarios:

```python
def test_resource_lifecycle(self, client, mock_graphql_client):
    """Test complete resource lifecycle: create, update, delete.

    This test simulates a complete workflow to ensure proper
    integration between different operations.
    """
    # ... test implementation
```

## Example: Complete Test for New Resource Type

```python
class TestDataSource:
    """Test data source operations"""

    def test_create_data_source(self, client, mock_graphql_client):
        """Test creating a new data source"""
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {"createDataSource": {"dataSource": {"id": "ds123"}}}
        mock_graphql_client.return_value.execute.return_value = mock_response

        url = client.create_data_source(
            name="production-db",
            source_type="database",
            connection_string="postgresql://localhost:5432/db",
            description="Production database",
        )

        assert url == client.data_source_url("ds123")
        assert mock_graphql_client.return_value.execute.called

    def test_get_data_source(self, client, mock_graphql_client):
        """Test retrieving a data source by name"""
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "node": {
                "dataSources": {
                    "edges": [
                        {
                            "node": {
                                "id": "ds123",
                                "name": "production-db",
                                "sourceType": "database",
                                "connectionString": "postgresql://...",
                                "refreshInterval": 3600,
                                "createdAt": "2024-01-01T00:00:00Z",
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        result = client.get_data_source("production-db")

        assert result["id"] == "ds123"
        assert result["sourceType"] == "database"
        assert result["refreshInterval"] == 3600

    def test_data_source_not_found(self, client, mock_graphql_client):
        """Test error when data source is not found"""
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.return_value = {
            "node": {"dataSources": {"edges": []}}
        }

        with pytest.raises(ArizeAPIException, match="not found"):
            client.get_data_source("non_existent")

    @pytest.mark.parametrize(
        "source_type,expected_error",
        [
            ("invalid_type", "Invalid source type"),
            ("", "source_type is required"),
        ],
    )
    def test_create_data_source_validation(
        self, client, mock_graphql_client, source_type, expected_error
    ):
        """Test parameter validation for data source creation"""
        with pytest.raises(ValueError, match=expected_error):
            client.create_data_source(
                name="test",
                source_type=source_type,
                connection_string="conn",
            )
```

## Key Testing Principles

1. **Test Coverage**: Ensure every client method has corresponding tests
1. **Mock Isolation**: Each test should be independent with proper mock setup
1. **Error Scenarios**: Test both success and failure paths
1. **Edge Cases**: Include tests for empty results, null values, and boundary conditions
1. **Clarity**: Test names and structure should be self-documenting
1. **Consistency**: Follow the established patterns from existing tests
1. **Assertions**: Make specific assertions about the expected behavior
