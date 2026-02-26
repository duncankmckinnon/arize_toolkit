# Test Patterns

Comprehensive test patterns for all Arize Toolkit components.

## Table of Contents

1. [Type Tests](#type-tests)
1. [Model Tests](#model-tests)
1. [Query Tests](#query-tests)
1. [Client Tests](#client-tests)

---

## Type Tests

**File**: `tests/test_types.py`

### Test All Enum Values

```python
class TestNewEnumType:
    def test_enum_values(self):
        """Test that all enum values are accessible."""
        assert NewEnumType.value_one.value[0] == "apiValue"
        assert NewEnumType.value_two.value[0] == "apiValue2"

    def test_from_input_primary_value(self):
        """Test primary API value resolution."""
        assert NewEnumType.from_input("apiValue") == "value_one"

    def test_from_input_aliases(self):
        """Test that all aliases resolve correctly."""
        assert NewEnumType.from_input("apiValue") == "value_one"
        assert NewEnumType.from_input("User Friendly") == "value_one"
        assert NewEnumType.from_input("alias1") == "value_one"

    def test_invalid_input(self):
        """Test that invalid input raises appropriate error."""
        with pytest.raises(ValueError, match="not a valid NewEnumType"):
            NewEnumType.from_input("invalid_value")
```

---

## Model Tests

**File**: `tests/test_models/test_{domain}_models.py`

### Test Class Structure

```python
class TestNewModel:
    """Test suite for NewModel."""

    def test_init(self):
        """Test model initialization with valid parameters."""
        model = NewModel(
            id="123",
            name="Test",
            optional_field="value",
        )
        assert model.id == "123"
        assert model.name == "Test"
        assert model.optional_field == "value"

    def test_default_values(self):
        """Test optional fields have correct defaults."""
        model = NewModel(id="123", name="Test")
        assert model.optional_field is None
        assert model.list_field == []

    def test_validation_required_fields(self):
        """Test that required fields must be provided."""
        with pytest.raises(ValidationError) as exc_info:
            NewModel()
        assert "id" in str(exc_info.value)
        assert "name" in str(exc_info.value)

    def test_validation_enum_fields(self):
        """Test enum field validation."""
        with pytest.raises(ValidationError):
            NewModel(id="123", name="Test", enum_field="invalid")

    def test_to_graphql_fields(self):
        """Test GraphQL field generation."""
        fields = NewModel.to_graphql_fields()
        assert "id" in fields
        assert "name" in fields

    def test_to_dict(self):
        """Test dictionary serialization."""
        model = NewModel(id="123", name="Test")
        data = model.to_dict()
        assert data["id"] == "123"
        assert data["name"] == "Test"
```

### Model Validator Tests

```python
def test_model_validator(self):
    """Test custom model validation logic."""
    # Valid case
    valid = ModelWithValidator(field1="value1", field2="value2")
    assert valid.field1 == "value1"

    # Invalid case
    with pytest.raises(ValueError, match="Expected error"):
        ModelWithValidator(field1="value1", field2="invalid")
```

### Nested Model Tests

```python
def test_nested_model(self):
    """Test nested model handling."""
    nested = NestedModel(data="test")
    parent = ParentModel(id="123", nested=nested)
    assert parent.nested.data == "test"


def test_list_of_models(self):
    """Test list of nested models."""
    items = [ItemModel(name="item1"), ItemModel(name="item2")]
    parent = ParentModel(id="123", items=items)
    assert len(parent.items) == 2
```

### Fixtures

```python
@pytest.fixture
def sample_model():
    return NewModel(id="123", name="Test")


@pytest.fixture
def sample_nested_config():
    return NestedConfig(setting1="value1", setting2=42)
```

---

## Query Tests

**File**: `tests/test_queries/test_{domain}_queries.py`

### Test Class Structure

```python
class TestNewOperationQuery:
    def test_query_structure(self):
        """Test query string structure."""
        query = NewOperationQuery.graphql_query
        assert "query NewOperation" in query  # or "mutation"
        assert "id" in query
        assert "name" in query

    def test_success(self, gql_client):
        """Test successful query execution."""
        mock_response = {
            "node": {
                "items": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": {"id": "123", "name": "Test"}}],
                }
            }
        }
        gql_client.execute.return_value = mock_response

        result = NewOperationQuery.run_graphql_query(gql_client, spaceId="space_id")

        assert result.id == "123"
        assert result.name == "Test"
        gql_client.execute.assert_called_once()

    def test_not_found(self, gql_client):
        """Test error when resource not found."""
        mock_response = {"node": {"items": {"edges": []}}}
        gql_client.execute.return_value = mock_response

        with pytest.raises(NewOperationQuery.QueryException):
            NewOperationQuery.run_graphql_query(gql_client, spaceId="id")

    def test_api_error(self, gql_client):
        """Test API error handling."""
        mock_response = {"errors": [{"message": "API Error"}]}
        gql_client.execute.return_value = mock_response

        with pytest.raises(NewOperationQuery.QueryException):
            NewOperationQuery.run_graphql_query(gql_client, spaceId="id")
```

### Pagination Tests

```python
def test_pagination(self, gql_client):
    """Test pagination handling."""
    responses = [
        {
            "node": {
                "items": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [{"node": {"id": "1", "name": "First"}}],
                }
            }
        },
        {
            "node": {
                "items": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": {"id": "2", "name": "Second"}}],
                }
            }
        },
    ]
    gql_client.execute.side_effect = responses

    results = NewOperationQuery.iterate_over_pages(gql_client, spaceId="id")

    assert len(results) == 2
    assert results[0].id == "1"
    assert results[1].id == "2"
    assert gql_client.execute.call_count == 2
```

### Mutation Tests

```python
def test_mutation_success(self, gql_client):
    """Test successful mutation execution."""
    mock_response = {"createItem": {"item": {"id": "new_123"}}}
    gql_client.execute.return_value = mock_response

    result = CreateItemMutation.run_graphql_mutation(gql_client, name="New Item")

    assert result.item_id == "new_123"
```

### Input Validation Tests

```python
@pytest.mark.parametrize(
    "input_data,expected_error",
    [
        ({"invalid_field": "value"}, "field_name"),
        ({}, "required_field"),
    ],
)
def test_input_validation(self, input_data, expected_error):
    """Test input validation."""
    with pytest.raises(ValidationError) as exc:
        NewOperationQuery.Variables(**input_data)
    assert expected_error in str(exc.value)
```

### Fixture

```python
@pytest.fixture
def gql_client():
    """Create mock GraphQL client."""
    return MagicMock()
```

---

## Client Tests

**File**: `tests/test_client.py`

### Test Class Structure

```python
class TestNewResource:
    """Test new resource operations."""

    def test_get_resource(self, client, mock_graphql_client):
        """Test retrieving a resource by name."""
        mock_graphql_client.return_value.execute.reset_mock()

        mock_response = {
            "node": {
                "resources": {
                    "edges": [
                        {
                            "node": {
                                "id": "res_123",
                                "name": "TestResource",
                                "type": "example",
                            }
                        }
                    ]
                }
            }
        }
        mock_graphql_client.return_value.execute.return_value = mock_response

        result = client.get_resource("TestResource")

        assert result["id"] == "res_123"
        assert result["name"] == "TestResource"
        mock_graphql_client.return_value.execute.assert_called()

    def test_get_resource_not_found(self, client, mock_graphql_client):
        """Test error when resource not found."""
        mock_graphql_client.return_value.execute.reset_mock()
        mock_graphql_client.return_value.execute.return_value = {
            "node": {"resources": {"edges": []}}
        }

        with pytest.raises(ArizeAPIException, match="not found"):
            client.get_resource("NonExistent")

    def test_resource_url(self, client):
        """Test URL generation."""
        url = client.resource_url("res_123")
        assert "resources/res_123" in url
```

### Pagination Tests

```python
def test_get_all_resources_pagination(self, client, mock_graphql_client):
    """Test getting all resources with pagination."""
    mock_graphql_client.return_value.execute.reset_mock()

    mock_responses = [
        {
            "node": {
                "resources": {
                    "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    "edges": [{"node": {"id": "1", "name": "First"}}],
                }
            }
        },
        {
            "node": {
                "resources": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "edges": [{"node": {"id": "2", "name": "Second"}}],
                }
            }
        },
    ]
    mock_graphql_client.return_value.execute.side_effect = mock_responses

    results = client.get_all_resources()

    assert len(results) == 2
    assert mock_graphql_client.return_value.execute.call_count == 2
```

### Creation Tests

```python
def test_create_resource(self, client, mock_graphql_client):
    """Test creating a new resource."""
    mock_graphql_client.return_value.execute.reset_mock()

    mock_response = {"createResource": {"resource": {"id": "new_123"}}}
    mock_graphql_client.return_value.execute.return_value = mock_response

    url = client.create_resource(
        name="new-resource",
        resource_type="example",
        description="Test resource",
    )

    assert url == client.resource_url("new_123")
    mock_graphql_client.return_value.execute.assert_called()
```

### Delete Tests

```python
def test_delete_resource(self, client, mock_graphql_client):
    """Test deleting a resource."""
    mock_graphql_client.return_value.execute.reset_mock()

    # Mock: get resource ID, then delete
    mock_graphql_client.return_value.execute.side_effect = [
        {"node": {"resources": {"edges": [{"node": {"id": "res_123"}}]}}},
        {"deleteResource": {"clientMutationId": None}},
    ]

    result = client.delete_resource("resource-name")

    assert result is True
    assert mock_graphql_client.return_value.execute.call_count == 2
```

### Parametrized Validation Tests

```python
@pytest.mark.parametrize(
    "params,expected_error",
    [
        ({"name": "", "type": "valid"}, "name is required"),
        ({"name": "test", "type": "invalid"}, "Invalid type"),
    ],
)
def test_create_resource_validation(
    self, client, mock_graphql_client, params, expected_error
):
    """Test parameter validation."""
    with pytest.raises(ValueError, match=expected_error):
        client.create_resource(**params)
```

### Fixtures

```python
@pytest.fixture
def mock_graphql_client():
    """Create mock GraphQL client."""
    with patch("arize_toolkit.client.GraphQLClient") as mock:
        # Mock initial org/space lookup
        mock.return_value.execute.return_value = {
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
        yield mock


@pytest.fixture
def client(mock_graphql_client):
    """Create test client."""
    return Client(
        organization="test_org", space="test_space", arize_developer_key="test_token"
    )
```

### Best Practices

1. **Always reset mocks** at start of each test
1. **Test return value transformations** (datetime formatting, etc.)
1. **Test optional parameters** with various combinations
1. **Test edge cases** (empty results, null values)
1. **Use descriptive test names** that indicate the scenario
1. **Document complex scenarios** with docstrings
