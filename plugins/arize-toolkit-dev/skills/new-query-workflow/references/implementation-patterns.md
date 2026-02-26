# Implementation Patterns

Detailed patterns for implementing types, models, queries, and client methods in the Arize Toolkit.

## Table of Contents

1. [Type Creation Patterns](#type-creation-patterns)
1. [Model Creation Patterns](#model-creation-patterns)
1. [Query Creation Patterns](#query-creation-patterns)
1. [Client Method Patterns](#client-method-patterns)

---

## Type Creation Patterns

### Base Class Usage

All enum types inherit from `InputValidationEnum`:

```python
from enum import Enum


class InputValidationEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        for member in cls:
            if isinstance(member.value, tuple) and value in member.value:
                return member
        return None

    @classmethod
    def from_input(cls, user_input):
        for operator in cls:
            if user_input in operator.value:
                return operator.name
        raise ValueError(f"{user_input} is not a valid {cls.__name__}")
```

### Value Definition Pattern

Use tuples for multiple aliases. **First value MUST be exact API value**:

```python
class ExampleType(InputValidationEnum):
    """Description. Values verified from GraphQL schema on [date]."""

    # PRIMARY VALUE MUST MATCH API/SCHEMA EXACTLY
    primary_value = "primary_value", "Primary Value", "primaryValue"

    # Include common variations
    secondary_value = (
        "secondary_value",  # ← Exact API value FIRST
        "secondaryValue",
        "Secondary Value",
        "SECONDARY_VALUE",
        "secondary",
    )
```

### Naming Conventions

- **Enum class names**: PascalCase (`PerformanceMetric`, `DriftMetric`)
- **Enum value names**: snake_case matching API (`f_1`, `euclidean_distance`)
- **Aliases**: Include snake_case, PascalCase, UPPER_CASE, human-readable, abbreviations

### Domain-Specific Patterns

**Metrics and Measurements**:

```python
class NewMetricType(InputValidationEnum):
    mean_squared_error = "mse", "Mean Squared Error", "MSE", "mean_squared_error"
    area_under_curve = "auc", "Area Under Curve", "AUC", "roc_auc", "AUROC"
```

**Operators**:

```python
class NewOperatorType(InputValidationEnum):
    greater_than = "greaterThan", "Greater Than", ">", "gt"
    less_than = "lessThan", "Less Than", "<", "lt"
```

---

## Model Creation Patterns

### Model Structure

```python
from typing import Optional, List, Literal, Dict, Any
from datetime import datetime
from pydantic import Field, model_validator
from arize_toolkit.utils import GraphQLModel


class NewModel(GraphQLModel):
    """Model description."""

    # Required fields (no default)
    id: str = Field(description="The unique identifier")
    name: str = Field(description="The name")

    # Optional fields (with defaults)
    description: Optional[str] = Field(default=None, description="Optional description")

    # Enums and Literals
    status: Literal["active", "inactive"] = Field(
        default="active", description="Status"
    )

    # Complex fields
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata")
    created_at: Optional[datetime] = Field(default=None, description="Creation time")

    # Lists of other models
    items: Optional[List[OtherModel]] = Field(default=None, description="Related items")

    # Optional validator
    @model_validator(mode="after")
    def validate_model(self):
        # Validation logic
        return self
```

### Inheritance Hierarchy

```
GraphQLModel (base utility class)
├── Dictable (provides to_dict())
└── All models inherit from GraphQLModel
    ├── BaseNode (with id, name fields)
    │   ├── User, Model, Monitor types
    │   └── Organization, Space
    └── Schema/Input Models
        ├── BaseModelSchema
        └── Various Input/Config models
```

### Input vs Response Models

```python
# Response model - comprehensive fields
class UserModel(GraphQLModel):
    id: str = Field(description="User ID")
    name: str = Field(description="Display name")
    email: Optional[str] = Field(default=None)
    created_at: Optional[datetime] = Field(default=None)


# Input model - only necessary fields, use Input suffix
class UserInput(GraphQLModel):
    name: str = Field(description="Display name")
    email: Optional[str] = Field(default=None)
```

### Using to_graphql_fields()

Models automatically generate GraphQL field selection:

```python
# In query definition
graphql_query = (
    """query GetItems($spaceId: ID!) {
        node(id: $spaceId) {
            ... on Space {
                items {
                    edges {
                        node {"""
    + ItemModel.to_graphql_fields()
    + """}
                    }
                }
            }
        }
    }"""
)
```

---

## Query Creation Patterns

### Basic Query Structure

```python
from typing import Optional, List, Tuple
from arize_toolkit.queries.basequery import BaseQuery, BaseVariables, BaseResponse
from arize_toolkit.exceptions import ArizeAPIException
from arize_toolkit.models.{domain}_models import ResponseModel


class GetItemQuery(BaseQuery):
    graphql_query: str = """
    query GetItem($id: ID!) {
        node(id: $id) {
            ... on Item {
                id
                name
            }
        }
    }
    """
    query_description: str = "Get an item by ID"

    class Variables(BaseVariables):
        id: str  # Required - no default
        optional_param: Optional[str] = None  # Optional - with default

    class QueryException(ArizeAPIException):
        message: str = "Error getting item"

    class QueryResponse(BaseResponse):
        id: str
        name: str
```

### Query with Model Response

```python
class GetCustomItemQuery(BaseQuery):
    graphql_query = (
        """query GetCustomItem($spaceId: ID!, $itemName: String) {
            node(id: $spaceId) {
                ... on Space {
                    customItems(search: $itemName, first: 1) {
                        edges {
                            node {"""
        + CustomItem.to_graphql_fields()
        + """}
                        }
                    }
                }
            }
        }"""
    )
    query_description = "Get a custom item by name"

    class Variables(BaseVariables):
        spaceId: str
        itemName: str

    class QueryException(ArizeAPIException):
        message: str = "Error finding custom item"

    class QueryResponse(CustomItem):
        pass

    @classmethod
    def _parse_graphql_result(
        cls, result: dict
    ) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if not result["node"]["customItems"]["edges"]:
            cls.raise_exception("No customItems found with given name")
        node = result["node"]["customItems"]["edges"][0]["node"]
        return [cls.QueryResponse(**node)], False, None
```

### Mutation Pattern

```python
class CreateItemMutation(BaseQuery):
    graphql_query = """
    mutation CreateItem($input: ItemInput!) {
        createItem(input: $input) {
            item {
                id
            }
        }
    }
    """
    query_description = "Create a new item"

    class Variables(ItemInput):  # Inherit from input model
        pass

    class QueryException(ArizeAPIException):
        message: str = "Error creating item"

    class QueryResponse(BaseResponse):
        item_id: str

    @classmethod
    def _parse_graphql_result(
        cls, result: dict
    ) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        if "createItem" not in result:
            cls.raise_exception("Item creation failed")
        return (
            [cls.QueryResponse(item_id=result["createItem"]["item"]["id"])],
            False,
            None,
        )
```

### Pagination Pattern

```python
class GetAllItemsQuery(BaseQuery):
    graphql_query = """
    query GetAllItems($spaceId: ID!, $endCursor: String) {
        node(id: $spaceId) {
            ... on Space {
                items(first: 100, after: $endCursor) {
                    pageInfo {
                        hasNextPage
                        endCursor
                    }
                    edges {
                        node {
                            id
                            name
                        }
                    }
                }
            }
        }
    }
    """
    query_description = "Get all items in a space"

    class Variables(BaseVariables):
        spaceId: str

    # ... Exception and Response classes ...

    @classmethod
    def _parse_graphql_result(
        cls, result: dict
    ) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        items = result["node"]["items"]
        page_info = items.get("pageInfo", {})
        edges = items.get("edges", [])

        return (
            [cls.QueryResponse(**edge["node"]) for edge in edges],
            page_info.get("hasNextPage", False),
            page_info.get("endCursor"),
        )
```

---

## Client Method Patterns

### Naming Conventions

- `create_X` - Create resource
- `get_X` - Get single resource by name
- `get_X_by_id` - Get single resource by ID
- `get_all_X` - Get all resources (with optional filtering)
- `update_X` - Update existing resource
- `delete_X` - Delete by name
- `delete_X_by_id` - Delete by ID
- `copy_X` - Copy resource
- `X_url()` - Generate UI URL

### Standard Method Pattern

```python
def get_resource(self, resource_name: str) -> dict:
    """Retrieves a resource by name.

    Args:
        resource_name (str): Name of the resource to retrieve

    Returns:
        dict: A dictionary containing resource information:
        - id (str): Unique identifier
        - name (str): Resource name
        - type (str): Resource type
        - createdAt (datetime): Creation timestamp

    Raises:
        ValueError: If resource_name is empty or None
        ArizeAPIException: If resource not found or API error

    Example:
        >>> resource = client.get_resource("my-resource")
        >>> print(f"Resource ID: {resource['id']}")
    """
    if not resource_name:
        raise ValueError("resource_name is required")

    result = GetResourceQuery.run_graphql_query(
        self._graphql_client,
        resource_name=resource_name,
        space_id=self.space_id,
    )
    sleep(self.sleep_time)
    return result.to_dict()
```

### ID Resolution Pattern

When function accepts name but query needs ID:

```python
def delete_resource(self, resource_name: str, parent_name: str) -> bool:
    """Delete resource by name."""
    # Get parent ID first
    parent = GetParentQuery.run_graphql_query(
        self._graphql_client,
        parent_name=parent_name,
        space_id=self.space_id,
    )
    # Get resource ID
    resource = GetResourceQuery.run_graphql_query(
        self._graphql_client,
        resource_name=resource_name,
        parent_id=parent.id,
    )
    # Delete by ID
    return self.delete_resource_by_id(resource.id)
```

### Pagination Pattern

```python
def get_all_resources(self, filter_param: Optional[str] = None) -> List[dict]:
    """Retrieves all resources with automatic pagination.

    Args:
        filter_param (Optional[str]): Optional filter

    Returns:
        List[dict]: List of resource dictionaries
    """
    results = GetAllResourcesQuery.iterate_over_pages(
        self._graphql_client,
        space_id=self.space_id,
        filter_param=filter_param,
        sleep_time=self.sleep_time,
    )
    return [result.to_dict() for result in results]
```

### URL Generation Pattern

```python
def resource_url(self, resource_id: str) -> str:
    """Generate the URL for a resource in the Arize UI.

    Args:
        resource_id (str): The unique identifier

    Returns:
        str: Full URL to the resource
    """
    return f"{self.space_url}/resources/{resource_id}"
```

### Creation Method Pattern

```python
def create_resource(
    self,
    name: str,
    resource_type: str,
    description: Optional[str] = None,
) -> str:
    """Creates a new resource.

    Args:
        name (str): Resource name
        resource_type (str): Type of resource
        description (Optional[str]): Description

    Returns:
        str: URL to the newly created resource

    Raises:
        ValueError: If required parameters missing
        ArizeAPIException: If creation fails
    """
    result = CreateResourceMutation.run_graphql_mutation(
        self._graphql_client,
        space_id=self.space_id,
        name=name,
        resourceType=resource_type,
        description=description,
    )
    return self.resource_url(result.resource_id)
```
