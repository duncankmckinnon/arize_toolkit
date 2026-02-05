______________________________________________________________________

## name: new-query-workflow description: Complete workflow for adding new GraphQL queries or mutations to the Arize Toolkit, including models, types, tests, client methods, and documentation. Use when (1) adding a new GraphQL query or mutation to arize_toolkit, (2) implementing new API functionality that requires queries, (3) user requests to add Arize API capabilities, or (4) user invokes /new-query-workflow. Triggers on phrases like "add a query", "create a mutation", "implement API for", "add support for [feature]", or explicit workflow invocation.

# New Query Workflow

Complete workflow for adding GraphQL queries/mutations to the Arize Toolkit with all supporting components.

## Workflow Overview

```
Phase 1: GraphQL Development → Phase 2: Component Discovery → Phase 3: Gap Analysis
                                           ↓
Phase 6: Documentation ← Phase 5: Testing ← Phase 4: Implementation
```

Execute phases in order. Pause for user validation after Phases 1, 3, and 4.

## Phase 1: GraphQL Query Development

**Goal**: Develop and validate the GraphQL query using the `arize-graphql-analytics` skill.

1. **Invoke arize-graphql-analytics** to explore schema and develop query
1. **Document the query specification**:
   - Query/mutation name and type
   - Complete GraphQL string
   - Variables with types and requirements
   - Response structure and field paths
   - Pagination pattern (if applicable)
   - Error conditions to handle

**Pause**: Present query specification to user for validation before proceeding.

## Phase 2: Component Discovery

**Goal**: Identify all components needed and their locations.

### 2.1 Identify Query Elements

From the GraphQL analysis, catalog:

- **Enum types** used in query (check `arize_toolkit/types.py`)
- **Input types** for mutations (check `arize_toolkit/models/`)
- **Response types** for query results (check `arize_toolkit/models/`)

### 2.2 Determine File Locations

| Domain | Query File | Model File |
|--------|-----------|------------|
| Models/Datasets | `model_queries.py` | `base_models.py` |
| Monitors/Alerts | `monitor_queries.py` | `monitor_models.py` |
| Dashboards | `dashboard_queries.py` | `dashboard_models.py` |
| LLM/Prompts | `llm_utils_queries.py` | `llm_utils_models.py` |
| Data Import | `data_import_queries.py` | `data_import_models.py` |
| Spaces/Orgs | `space_queries.py` | `space_models.py` |
| Custom Metrics | `custom_metric_queries.py` | `custom_metrics_models.py` |

### 2.3 Identify Related Queries

Check if the new functionality depends on existing queries (e.g., need model ID before creating monitor).

## Phase 3: Gap Analysis

**Goal**: Identify what needs to be created vs. reused.

### 3.1 Missing Types

For each enum in the query not in `types.py`:

- Use arize-graphql-analytics to get exact enum values from schema
- Document canonical values and aliases needed

### 3.2 Missing Models

For each input/response type not in `models/`:

- Define all fields with types
- Determine base class (`GraphQLModel`, `BaseNode`, etc.)
- Identify validators needed

### 3.3 Client Integration

Determine:

- Method name(s) following CRUD pattern: `get_`, `get_all_`, `create_`, `update_`, `delete_`, `copy_`
- Name-to-ID resolution needs
- Dependencies on other client methods
- URL generation pattern (if UI link exists)

**Pause**: Present gap analysis to user. Confirm implementation plan.

## Phase 4: Implementation

Execute in order to manage dependencies. See [references/implementation-patterns.md](references/implementation-patterns.md) for detailed patterns.

### 4.1 Create Enum Types (if needed)

**File**: `arize_toolkit/types.py`

```python
class NewEnumType(InputValidationEnum):
    """Description. Values verified from GraphQL schema."""

    value_one = "apiValue", "User Friendly", "alias"
```

### 4.2 Create Models (if needed)

**File**: `arize_toolkit/models/{domain}_models.py`

```python
class NewModel(GraphQLModel):
    id: str = Field(description="Unique identifier")
    name: str = Field(description="Name")
    optional_field: Optional[str] = Field(default=None, description="Optional")
```

### 4.3 Create Query/Mutation

**File**: `arize_toolkit/queries/{domain}_queries.py`

```python
class NewOperationQuery(BaseQuery):
    graphql_query: str = """..."""
    query_description: str = "What this does"

    class Variables(BaseVariables):
        param: str

    class QueryException(ArizeAPIException):
        message: str = "Error message"

    class QueryResponse(NewModel):
        pass

    @classmethod
    def _parse_graphql_result(cls, result):
        # Parse and return (results, has_next, cursor)
```

### 4.4 Add Client Methods

**File**: `arize_toolkit/client.py`

```python
def get_new_resource(self, name: str) -> dict:
    """Retrieves resource by name.

    Args:
        name (str): Resource name

    Returns:
        dict: Resource data with id, name, etc.

    Raises:
        ValueError: If name is empty
        ArizeAPIException: If not found
    """
    result = NewOperationQuery.run_graphql_query(
        self._graphql_client, space_id=self.space_id, name=name
    )
    return result.to_dict()
```

**Pause**: Present generated code for validation before adding tests.

## Phase 5: Testing

See [references/test-patterns.md](references/test-patterns.md) for detailed patterns.

### 5.1 Type Tests (if new types)

**File**: `tests/test_types.py`

Test enum values, aliases, and invalid input handling.

### 5.2 Model Tests (if new models)

**File**: `tests/test_models/test_{domain}_models.py`

Test initialization, defaults, validation, and serialization.

### 5.3 Query Tests

**File**: `tests/test_queries/test_{domain}_queries.py`

Test query structure, success cases, error handling, and pagination.

### 5.4 Client Tests

**File**: `tests/test_client.py`

Test client methods with mocked GraphQL responses.

## Phase 6: Documentation

See [references/doc-patterns.md](references/doc-patterns.md) for detailed patterns.

### 6.1 Update Tool Documentation

**File**: `docs_site/docs/{domain}_tools.md`

Add method documentation with signature, parameters, returns, and example.

### 6.2 Update Overview Table

Add entry to the Overview table at top of documentation file.

### 6.3 Update Index (if new page)

- Add link to `docs_site/docs/index.md`
- Add entry to `mkdocs.yml` under 'Tools'

## Validation Checklist

Before completing, verify:

**Types**: [ ] Defined in types.py [ ] Schema-verified values [ ] Aliases provided [ ] Tests added

**Models**: [ ] In correct models/ file [ ] Correct base class [ ] Field descriptions [ ] Tests added

**Queries**: [ ] In correct queries/ file [ ] Variables class complete [ ] Exception defined [ ] Response uses model [ ] Parser handles all cases [ ] Tests added

**Client**: [ ] CRUD naming convention [ ] Docstring complete [ ] Validation implemented [ ] Tests added

**Docs**: [ ] Tool page updated [ ] Overview table updated [ ] Examples provided

## Resources

- [references/implementation-patterns.md](references/implementation-patterns.md) - Detailed code patterns for types, models, queries, client
- [references/test-patterns.md](references/test-patterns.md) - Test patterns for all components
- [references/doc-patterns.md](references/doc-patterns.md) - Documentation formatting patterns
