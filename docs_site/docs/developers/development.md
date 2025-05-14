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

BaseVariables is the base class for all query variables. It provides a structure for defining the variables for a query 
and ensures that the variables are validated and serialized correctly.

It inherits from `Dictable`, which is a utility class that wraps a Pydantic BaseModel. This interface allows for consistent type conversions between graphql friendly dictionaries and objects.

The `endCursor` field is used in pagination throughout Arize graphql, so it is included as an optional field by default.


````python:arize_toolkit/queries/basequery.py
class BaseVariables(Dictable):
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

The BaseVariables class is a convenient tool for validating the input to the query, but in situations where the input to the mutation is a model type, it may be more convenient to override the BaseVariables class in the BaseQuery with the model type definition instead.

**Example of a mutation using an existing model type:**
```python
class CreateThingMutation(BaseQuery):
    class Variables(Thing):
        pass
```

### 2. BaseResponse

BaseResponse is the base class for all query responses. It provides a structure for defining the response for a query,
and ensures that the response is validated and serialized correctly.

Like BaseVariables, it inherits from `Dictable`, which is a utility class that wraps a Pydantic BaseModel.

````python:arize_toolkit/queries/basequery.py
class BaseResponse(Dictable):
    """Base class for all query responses"""
    pass
````

**Purpose:**
- Defines the structure and type validation for query and mutation responses
- Ensures consistent response handling and error messages

**Example Usage:**
````python
class GetModelQuery(BaseQuery):
    class QueryResponse(BaseResponse):
        id: str
        name: str
````

As with BaseVariables, the BaseResponse class is a convenient tool for validating the response from the query, but in situations where the response is a model type, it may be more convenient to override the BaseResponse class in the BaseQuery with the model type definition instead.

**Example of a mutation using an existing model type:**
```python
class GetThingQuery(BaseQuery):
    class QueryResponse(Thing):
        pass
```

### 3. ArizeAPIException

All exceptions in the arize_toolkit are subclasses of ArizeAPIException. This allows for consistent error handling across all queries.
It also allows for custom exception types per query, and handling for common exceptions related to the API.

The keyword_exceptions class variable is used to define the exceptions that are common to all queries, but don't provide useful information about the error. The ArizeAPIException class uses a keyword search to determine if a raised exception is related to a common issue, and if so, it will use more specific and actionable error messages defined in the keyword exception classes.

````python:arize_toolkit/exceptions.py
class ArizeAPIException(Exception):
    """Base class for all API exceptions"""
    keyword_exceptions = [RateLimitException, RetryException]
    message: str = "An error occurred while running the query"
    details: Optional[str] = None
````

**Example Usage:**
````python
class GetModelQuery(BaseQuery):
    class QueryException(ArizeAPIException):
        message: str = "Error getting the id of a named model in the space"
````

### 4. BaseQuery

BaseQuery is the base class for all queries and mutations. It provides a structure for defining the query, variables, exception, parsing, and response.
All the base classes are inherited and used in the query logic, so the specific implementations only need to define:
- The GraphQL query
- The variables for the query
- The exception for the query
- The response for the query
- The logic for parsing the response

The base query handles logic around:
- Executing queries or mutations
- Validating the variables
- Handling the response
- Handling errors
- Iterating over pages
- Rate limiting

So you will rarely need to add any additional functionality in your query implementations outside of the setup and parsing logic.

````python:arize_toolkit/queries/basequery.py
class BaseQuery:
    """Base class for all queries"""
    graphql_query: str
    query_description: str

    class QueryVariables(BaseVariables):
        # Define the variables for the query
        pass

    class QueryException(ArizeAPIException):
        # Define the exception for the query
        pass

    class QueryResponse(BaseResponse):
        # Define the response for the query
        pass

    @classmethod
    def _graphql_query(cls, client: GraphQLClient, **kwargs) -> Tuple[BaseResponse, bool, Optional[str]]:
        try:
            query = gql(cls.graphql_query)

            # Relies on the QueryVariables class to validate the variables
            result = client.execute(query, variable_values=cls.QueryVariables(**kwargs).model_dump())

            # Relies on the QueryResponse class to parse the result
            return cls._parse_graphql_result(result)
        except Exception as e:
            # Relies on the QueryException class to handle the exception
            raise cls.QueryException(details=str(e))
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

4. **Error Handling:**
   - Handles common API errors
   - Allows for custom exception types per query
   - Provides detailed error messages

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
