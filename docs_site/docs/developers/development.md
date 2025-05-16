# Development

## Setup

The following instructions are for setting up a development environment for the arize_toolkit.
Before you begin, make sure to clone the repository and navigate to the `arize_toolkit` directory:

```bash
git clone https://github.com/duncankmckinnon/arize_toolkit.git
cd arize_toolkit
```

To set up a development environment for this project, firstrun the bootstrap script to create a named virtual environment and install the dependencies using poetry:

```bash
sh ./bin/bootstrap.sh
```

Then activate the virtual environment:

```bash
source .venv/bin/activate
```

You're ready to develop! The virtual environment will be created in the `.venv` directory with the name "arize-toolkit-venv".

## Base Classes Explained

### 1. BaseVariables

BaseVariables is the base class for all query variables. It provides a structure for defining the variables for a query 
and ensures that the variables are validated and serialized correctly.

It inherits from `Dictable`, which is a utility class that wraps a Pydantic BaseModel. This interface allows for consistent type conversions between graphql friendly dictionaries and objects. All the model types in the arize_toolkit eventually inherit from `Dictable` so that they can be used in the same way.

The `endCursor` field is used in pagination throughout Arize graphql, so it is included as an optional field by default.

```python
class BaseVariables(Dictable):
    """Base class for all query variables"""
    endCursor: Optional[str] = None
```

**Purpose:**

- Validates input parameters for GraphQL queries using Pydantic
- Ensures type safety for query variables
- Provides automatic validation and serialization
- Includes pagination support via `endCursor`

#### Implementation in BaseQuery

The `BaseQuery` class requires a `Variables` class that often inherits from `BaseVariables`. This allows for the variables to be validated and serialized correctly. When defining the `Variables` class you simply need to define the fields and types of variables used as input to the query.

**Example Usage:**

```python
class GetModelQuery(BaseQuery):
    class Variables(BaseVariables):
        space_id: str
        model_name: str
```

The BaseVariables class is a convenient tool for validating the input to the query, but in situations where the input to the mutation is already represented by a model type, it may be more convenient to override the BaseVariables class in the BaseQuery with the model type definition instead.

**Example of a mutation using an existing model type:**

```python
class Thing(GraphQLModel):
    id: str
    name: str

class CreateThingMutation(BaseQuery):
    class Variables(Thing):
        pass
```

### 2. BaseResponse

BaseResponse is the base class for all query responses. It provides a structure for defining the response for a query,
and ensures that the response is validated and serialized correctly.

Like BaseVariables, it inherits from `Dictable`, which is a utility class that wraps a Pydantic BaseModel.

```python
class BaseResponse(Dictable):
    """Base class for all query responses"""
    pass
```

**Purpose:**

- Defines the structure and type validation for query and mutation responses
- Ensures consistent response handling and error messages

**Example Usage:**

```python
class GetModelQuery(BaseQuery):
    class QueryResponse(BaseResponse):
        id: str
        name: str
```

As with BaseVariables, the BaseResponse class is a convenient tool for validating the response from the query, but in situations where the response is a model type, it may be more convenient to override the BaseResponse class in the BaseQuery with the model type definition instead.

**Example of a mutation using an existing model type:**

```python
class Thing(GraphQLModel):
    id: str
    name: str

class GetThingQuery(BaseQuery):
    class QueryResponse(Thing):
        pass
```

### 3. ArizeAPIException

All exceptions in the arize_toolkit are subclasses of ArizeAPIException. This allows for consistent error handling across all queries.
It also allows for custom exception types per query, and handling for common exceptions related to the API.

The keyword_exceptions class variable is used to define the exceptions that are common to all queries, but don't provide useful information about the error. The ArizeAPIException class uses a keyword search to determine if a raised exception is related to a common issue, and if so, it will use more specific and actionable error messages defined in the keyword exception classes.

```python
class ArizeAPIException(Exception):
    """Base class for all API exceptions"""
    keyword_exceptions = [RateLimitException, RetryException]
    message: str = "An error occurred while running the query"
    details: Optional[str] = None
```

**Example Usage:**

```python
class GetModelQuery(BaseQuery):
    class QueryException(ArizeAPIException):
        message: str = "Error getting the id of a named model in the space"
```

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

```python
class BaseQuery:
    """Base class for all queries"""
    graphql_query: str
    query_description: str

    class Variables(BaseVariables):
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
            result = client.execute(query, variable_values=cls.QueryVariables(**kwargs).to_dict(exclude_none=False))

            # Relies on the QueryResponse class to parse the result
            return cls._parse_graphql_result(result)
        except Exception as e:
            # Relies on the QueryException class to handle the exception
            raise cls.QueryException(details=str(e))
```

## Implementing Patterns for Queries and Mutations

### GraphQL Model Types



### Parsing

The base query handles parsing of the response from the API. This is done by the `_parse_graphql_result` method.
For queries that retrieve a single item by its id, the base query will handle the parsing of the response into the model type.
For other queries and mutations, you will need to implement the `_parse_graphql_result` method in your query implementation.

The `_parse_graphql_result` method takes in the graphql query result as a dictionary and returns a tuple containing a list of the parsed response(s), a boolean indicating if there are more pages, and an optional endCursor to be used for pagination. For queries that retrieve a single item by its id, the base query will handle the parsing of the response into the model type.

#### Base Implementation for Queries of Objects by Id

For any query that retrieves a single item by its id, the base query will handle the parsing of the response into the model type. This is the base implementation because regardless of the object type, the response is always the same format:

```json
{
    "node": {
        "id": "123",
        "name": "Thing",
        ...
    }
}
```

```python
class GetThingQuery(BaseQuery):
    ...
    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        # Default behavior for queries of objects by id
        if "node" in result and result["node"] is not None:
            result_node = result["node"]
            return [cls.QueryResponse(**result_node)], False, None
        else:
            cls.raise_exception("Object not found")
```

#### Parsing Queries that Retrieve a List of Items

For queries that retrieve a list of items, the base query will handle the parsing of the response into a list of model types.
The form of these queries is often the same in Arize GraphQL, with an `endCursor` marker for pagination and a flag indicating if there are more pages to retrieve.

**Example of a query that retrieves a list of items:**

```python
class GetThingsQuery(BaseQuery):
    # Typical form of a query that retrieves a list of items - the node is the object type that is being retrieved
    graphql_query = """
        query getAllThings($space_id: ID!, $endCursor: String) {
            node(id: $space_id) {
                ... on Space {
                    things (first: 10, after: $endCursor) {
                        edges {
                            node {""" + Thing.to_graphql_fields() + """ }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
    """
    ...
    @classmethod
    def _parse_graphql_result(cls, result: dict) -> Tuple[List[BaseResponse], bool, Optional[str]]:
        # Default behavior for queries of objects by id
        if "edges" in result["node"]["things"] and result["node"]["things"]["edges"] is not None:
            edges = result["node"]["things"]["edges"]
            things = [cls.QueryResponse(**edge["node"]) for edge in edges]
            
            # Check if there are more pages to retrieve
            page_info = result["node"]["things"]["pageInfo"]
            hasNextPage = page_info["hasNextPage"]
            endCursor = page_info["endCursor"]
            return things, hasNextPage, endCursor
        else:
            cls.raise_exception("No things found")
```

## Adding Functions to the Client

The client provides a clean interface to run queries and retrieve data from the api. It is the main interface for the arize_toolkit. Under the hood, each function exposed by the client uses base query classes to interact with the API and handle the response parsing and error handling.

**Example of a client function:**

```python
class Client:
    def get_model(self, model_name: str) -> Dict:
        results, _, _ = GetModelQuery.run_graphql_query(
            self._graphql_client,
            space_id=self._space_id,
            model_name=model_name
        )
        # The results are a list of the model type defined in the QueryResponse class
        return results[0].to_dict()
```

While there is flexibility in how client functions are defined, there are some conventions that are used throughout the arize_toolkit



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
