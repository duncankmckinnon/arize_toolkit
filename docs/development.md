# Development Setup

To set up a development environment for this project, firstrun the bootstrap script to create a named virtual environment:

```bash
sh ./bin/bootstrap.sh
```

Then activate the virtual environment:

```bash
source .venv/bin/activate
```

You're ready to develop! The virtual environment will be created in the `.venv` directory with the name "arize-toolkit-venv".

# Development Patterns

## Base Classes Explained

### 1. BaseVariables

````python:sdk/python/api/arize_api/queries/basequery.py
class BaseVariables(BaseModel):
    """Base class for all query variables"""
    endCursor: Optional[str] = None
````

**Purpose:**
- Validates input parameters for GraphQL queries using Pydantic
- Ensures type safety for query variables
- Provides automatic validation and serialization
- Includes pagination support via `endCursor`

**Example Usage:**
````python
class GetModelQuery(BaseQuery):
    class Variables(BaseVariables):
        space_id: str
        model_name: str
````

### 2. BaseResponse

````python:sdk/python/api/arize_api/queries/basequery.py
class BaseResponse(BaseModel):
    """Base class for all query responses"""
    pass
````

**Purpose:**
- Defines the structure for query responses
- Provides type validation for API responses
- Ensures consistent response handling

**Example Usage:**
````python
class QueryResponse(BaseResponse):
    id: str  # Response will have an id field
    name: str  # And a name field
````

### 3. BaseAPIException

````python:sdk/python/api/arize_api/queries/basequery.py
class ArizeAPIException(Exception):
    """Base class for all API exceptions"""
    message: str = "An error occurred while running the query"
    details: Optional[str] = None
````

**Purpose:**
- Provides consistent error handling across all queries
- Allows for detailed error messages
- Enables custom exception types per query

**Example Usage:**
````python
class QueryException(ArizeAPIException):
    message: str = "Error getting the id of a named model in the space"
````

### 4. BaseQuery

````python:sdk/python/api/arize_api/queries/basequery.py
class BaseQuery:
    """Base class for all queries"""
    graphql_query: str
    query_description: str

    @classmethod
    def _graphql_query(cls, client: GraphQLClient, **kwargs) -> Tuple[BaseResponse, bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)
            result = client.execute(query, variable_values=cls.QueryVariables(**kwargs).model_dump())
            return cls._parse_graphql_result(result)
        except Exception as e:
            raise cls.QueryException(details=str(e))

    @classmethod
    def iterate_over_pages(cls, client: GraphQLClient, sleep_time: int = 0, **kwargs) -> List[BaseResponse]:
        # Handles pagination logic
````

**Purpose:**
1. **Query Execution:**
   - Handles GraphQL query execution
   - Manages variable validation
   - Provides error handling

2. **Pagination Support:**
   - Built-in pagination through `iterate_over_pages`
   - Handles cursor-based pagination
   - Supports rate limiting via sleep_time

3. **Response Parsing:**
   - Standardizes response parsing
   - Converts GraphQL responses to typed objects

## Benefits of This Architecture

### 1. **Type Safety:**
```python
# Variables are validated at runtime
def get_model(self, model_name: str):
    # This will fail if model_name is not a string
    results = GetModelQuery.run_graphql_query(
        self._graphql_client, 
        model_name=model_name
    )
```

### 2. **Consistent Error Handling:**
```python
try:
    result = GetModelQuery.run_graphql_query(...)
except GetModelQuery.QueryException as e:
    # Handle specific query errors
except ArizeAPIException as e:
    # Handle general API errors
```

### 3. **Easy to Extend:**
```python
class NewFeatureQuery(BaseQuery):
    graphql_query = """
        query newFeature($param: String!) {
            # New query definition
        }
    """
    # Just implement the required components
```

### 4. **Pagination Support:**
```python
# Automatically handles pagination
results = GetAllModelsQuery.iterate_over_pages(
    client, 
    space_id="123",
    sleep_time=1  # Rate limiting
)
```

This architecture provides a robust foundation for building GraphQL queries while maintaining type safety, error handling, and extensibility.


## Query Implementation Pattern

Each query follows this structure, as seen in `space_queries.py`:

```python
class GetModelQuery(BaseQuery):
    # 1. Define the GraphQL query string
    graphql_query = """
    query getModel($space_id: ID!, $model_name: String) {
        # ... GraphQL query definition ...
    }
    """
    query_description = "Get the id of a model in the space"

    # 2. Define expected variables
    class Variables(BaseVariables):
        space_id: str
        model_name: str

    # 3. Define possible exceptions
    class QueryException(ArizeAPIException):
        message: str = "Error getting the id of a named model in the space"
        
    # 4. Define response structure
    class QueryResponse(BaseResponse):
        id: str

    # 5. Implement response parsing
    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[BaseResponse, bool, Optional[str]]:
        # Parse and validate response
```

## Client Usage

The client provides a clean interface to run queries and retrieve data from the api:

```python:sdk/python/api/arize_api/client.py
class Client:
    def get_model(self, model_name: str):
        results = GetModelQuery.run_graphql_query(
            self._graphql_client, 
            model_name=model_name
        )
        return results.id
```

## Key Features

1. **Type Safety**: Uses Pydantic models for request/response validation
2. **Pagination**: Built-in support through `iterate_over_pages`
3. **Error Handling**: Structured exceptions for each query type
4. **Separation of Concerns**:
   - Query definition (GraphQL)
   - Parameter validation
   - Response parsing
   - Error handling

## Example Flow

1. Client makes a request:
```python
client.get_model("my_model")
```

2. Query execution:
   - Variables validated through `BaseVariables`
   - GraphQL query executed
   - Response parsed and validated
   - Typed response returned to client

3. Error handling:
   - Network errors caught
   - Invalid responses caught
   - Custom exceptions raised with context

This pattern makes it easy to:
- Add new queries
- Maintain type safety
- Handle errors consistently
- Support pagination where needed
- Test individual components
