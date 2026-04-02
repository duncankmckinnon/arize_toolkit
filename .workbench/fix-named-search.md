# Fix Entity Search-by-Name Queries

## Context

The arize_toolkit uses GraphQL `search` parameters to find entities by name. The server returns fuzzy/partial matches, but several query classes blindly take `edges[0]` (the first result) instead of verifying an exact name match. This means searching for "model-v1" might return "model-v10" if it appears first in the search results.

A fix pattern has already been applied to `model_queries.py` and `space_queries.py` on the current branch. The pattern is:

1. Change `first: 1` to `first: 10` in GraphQL queries to get multiple candidates
1. Ensure the `name` field is requested in the GraphQL query if missing
1. Use `result.pop("__query_variables__", {})` to retrieve the original search term
1. Call `cls._find_exact_name_match(edges, search_name)` instead of `edges[0]["node"]`
1. Raise a specific error if no exact match found

The `_find_exact_name_match` method and `__query_variables__` injection are already in `basequery.py` on the current branch. All tasks should build on the current branch state (use `--local`).

## Conventions

- Python 3.9+, pydantic models, pytest for testing
- All query classes inherit from `BaseQuery` in `arize_toolkit/queries/basequery.py`
- `_find_exact_name_match(edges, search_name, name_field="name")` is available as a static method on `BaseQuery`
- `__query_variables__` is automatically injected into results by `_graphql_query` and `_graphql_mutation`
- Test files use `gql_client` fixture (a `MagicMock()`) from `tests/conftest.py`
- Tests call `QueryClass.run_graphql_query(gql_client, **kwargs)` or `QueryClass._graphql_query(gql_client, **kwargs)`
- Error cases use `pytest.raises(QueryClass.QueryException)`
- Test command: `pytest tests/test_queries/ -v`

## Task: Fix evaluator query

Files: arize_toolkit/queries/evaluator_queries.py, tests/test_queries/test_evaluator_queries.py

Apply the exact name match pattern to `GetEvaluatorByNameQuery` in `arize_toolkit/queries/evaluator_queries.py`.

### Changes to `arize_toolkit/queries/evaluator_queries.py`

In `GetEvaluatorByNameQuery` (line 87):

1. Change the GraphQL query's `evaluators(first: 1, name: $name)` to `evaluators(first: 10, name: $name)` to get multiple candidates
1. Update `_parse_graphql_result` to:
   - Extract the search name: `variables = result.pop("__query_variables__", {})` then `name = variables.get("name", "")`
   - After extracting edges, use `cls._find_exact_name_match(edges, name)` instead of `edges[0]["node"]`
   - Add a None check: if the result is None, raise exception with message `f"No evaluator found with the exact name '{name}'"`

The current implementation at lines 119-125 is:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    if "node" not in result or result["node"] is None:
        cls.raise_exception("Space not found")
    edges = result["node"].get("evaluators", {}).get("edges", [])
    if len(edges) == 0:
        cls.raise_exception("No evaluator found with the given name")
    return [cls.QueryResponse(**edges[0]["node"])], False, None
```

It should become:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    name = variables.get("name", "")
    if "node" not in result or result["node"] is None:
        cls.raise_exception("Space not found")
    edges = result["node"].get("evaluators", {}).get("edges", [])
    if len(edges) == 0:
        cls.raise_exception("No evaluator found with the given name")
    evaluator = cls._find_exact_name_match(edges, name)
    if evaluator is None:
        cls.raise_exception(f"No evaluator found with the exact name '{name}'")
    return [cls.QueryResponse(**evaluator)], False, None
```

### Changes to tests

In `tests/test_queries/test_evaluator_queries.py`, find the `TestGetEvaluatorByNameQuery` class. The existing tests use mock responses with `edges: [{"node": mock_evaluator}]`. These tests should still pass since the mock evaluator name "Hallucination Detector" will be matched.

Add a new test `test_get_evaluator_by_name_no_exact_match` that verifies a partial match is rejected:

```python
def test_get_evaluator_by_name_no_exact_match(self, gql_client, mock_evaluator):
    """Test that partial name matches are rejected."""
    mock_response = {
        "node": {
            "evaluators": {
                "edges": [{"node": mock_evaluator}],  # name is "Hallucination Detector"
            }
        }
    }
    gql_client.execute.return_value = mock_response
    with pytest.raises(
        GetEvaluatorByNameQuery.QueryException,
        match="No evaluator found with the exact name",
    ):
        GetEvaluatorByNameQuery.run_graphql_query(
            gql_client, space_id="space123", name="Hallucination"
        )
```

Also add a test `test_get_evaluator_by_name_multiple_results` verifying the correct one is picked from multiple results:

```python
def test_get_evaluator_by_name_multiple_results(self, gql_client, mock_evaluator):
    """Test exact match is found among multiple search results."""
    other_evaluator = {
        **mock_evaluator,
        "id": "eval456",
        "name": "Hallucination Detector v2",
    }
    mock_response = {
        "node": {
            "evaluators": {
                "edges": [
                    {"node": other_evaluator},
                    {
                        "node": mock_evaluator
                    },  # "Hallucination Detector" - the exact match
                ],
            }
        }
    }
    gql_client.execute.return_value = mock_response
    result = GetEvaluatorByNameQuery.run_graphql_query(
        gql_client, space_id="space123", name="Hallucination Detector"
    )
    assert result.id == "eval123"
    assert result.name == "Hallucination Detector"
```

### Test plan

Run: `pytest tests/test_queries/test_evaluator_queries.py -v`
All existing tests should pass. The two new tests should pass.

## Task: Fix dashboard query

Files: arize_toolkit/queries/dashboard_queries.py, tests/test_queries/test_dashboard_queries.py

Apply the exact name match pattern to `GetDashboardQuery` in `arize_toolkit/queries/dashboard_queries.py`.

### Changes to `arize_toolkit/queries/dashboard_queries.py`

In `GetDashboardQuery` (line 88):

1. Change the GraphQL query's `dashboards(search: $dashboardName, first: 1)` to `dashboards(search: $dashboardName, first: 10)`
1. The `DashboardBasis` model already has a `name` field, so no GraphQL field changes needed
1. Update `_parse_graphql_result` (lines 119-124):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    if not result["node"]["dashboards"]["edges"]:
        cls.raise_exception("No dashboard found with the given name")
    dashboard_node = result["node"]["dashboards"]["edges"][0]["node"]
    return [cls.QueryResponse(**dashboard_node)], False, None
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    dashboard_name = variables.get("dashboardName", "")
    if not result["node"]["dashboards"]["edges"]:
        cls.raise_exception("No dashboard found with the given name")
    edges = result["node"]["dashboards"]["edges"]
    dashboard = cls._find_exact_name_match(edges, dashboard_name)
    if dashboard is None:
        cls.raise_exception(
            f"No dashboard found with the exact name '{dashboard_name}'"
        )
    return [cls.QueryResponse(**dashboard)], False, None
```

### Changes to tests

In `tests/test_queries/test_dashboard_queries.py`, add a new `TestGetDashboardQuery` class with tests:

Import `GetDashboardQuery` at the top alongside existing imports.

The `DashboardBasis` model fields include at minimum: `id`, `name`. Check the model for other required fields by looking at `DashboardBasis.to_graphql_fields()` — but for tests, `id` and `name` are sufficient since `DashboardBasis` extends `BaseResponse` with optional fields.

```python
class TestGetDashboardQuery:
    def test_get_dashboard_by_name_success(self, gql_client):
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash1", "name": "My Dashboard"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        result = GetDashboardQuery.run_graphql_query(
            gql_client, spaceId="space1", dashboardName="My Dashboard"
        )
        assert result.id == "dash1"
        assert result.name == "My Dashboard"

    def test_get_dashboard_by_name_no_exact_match(self, gql_client):
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash1", "name": "My Dashboard Production"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        with pytest.raises(
            GetDashboardQuery.QueryException,
            match="No dashboard found with the exact name",
        ):
            GetDashboardQuery.run_graphql_query(
                gql_client, spaceId="space1", dashboardName="My Dashboard"
            )

    def test_get_dashboard_by_name_multiple_results(self, gql_client):
        mock_response = {
            "node": {
                "dashboards": {
                    "edges": [
                        {"node": {"id": "dash2", "name": "My Dashboard v2"}},
                        {"node": {"id": "dash1", "name": "My Dashboard"}},
                    ]
                }
            }
        }
        gql_client.execute.return_value = mock_response
        result = GetDashboardQuery.run_graphql_query(
            gql_client, spaceId="space1", dashboardName="My Dashboard"
        )
        assert result.id == "dash1"

    def test_get_dashboard_by_name_not_found(self, gql_client):
        mock_response = {"node": {"dashboards": {"edges": []}}}
        gql_client.execute.return_value = mock_response
        with pytest.raises(
            GetDashboardQuery.QueryException,
            match="No dashboard found with the given name",
        ):
            GetDashboardQuery.run_graphql_query(
                gql_client, spaceId="space1", dashboardName="Missing"
            )
```

### Test plan

Run: `pytest tests/test_queries/test_dashboard_queries.py -v`
All existing and new tests should pass.

## Task: Fix monitor queries

Files: arize_toolkit/queries/monitor_queries.py, tests/test_queries/test_monitor_queries.py

Apply the exact name match pattern to `GetMonitorQuery` and `GetModelMetricValueQuery` in `arize_toolkit/queries/monitor_queries.py`.

### Changes to `GetMonitorQuery` (line 52)

1. Change GraphQL: `monitors(first: 1, search: $monitor_name, modelName: $model_name)` to `monitors(first: 10, search: $monitor_name, modelName: $model_name)`
1. Update `_parse_graphql_result` (lines 84-93):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    edges = result["node"]["monitors"]["edges"]
    if len(edges) == 0:
        cls.raise_exception("No monitor found with the given name")
    node = edges[0]["node"]
    return (
        [cls.QueryResponse(**node)],
        False,
        None,
    )
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    monitor_name = variables.get("monitor_name", "")
    edges = result["node"]["monitors"]["edges"]
    if len(edges) == 0:
        cls.raise_exception("No monitor found with the given name")
    monitor = cls._find_exact_name_match(edges, monitor_name)
    if monitor is None:
        cls.raise_exception(f"No monitor found with the exact name '{monitor_name}'")
    return (
        [cls.QueryResponse(**monitor)],
        False,
        None,
    )
```

### Changes to `GetModelMetricValueQuery` (line 254)

1. Change GraphQL: `monitors(first: 1, search: $monitor_name)` to `monitors(first: 10, search: $monitor_name)`
1. Update `_parse_graphql_result` (lines 300-317):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    models_edges = result.get("node", {}).get("models", {}).get("edges", [])
    if not models_edges:
        cls.raise_exception("No model found with the given name")
    model_node = models_edges[0].get("node", {})
    monitors_edges = model_node.get("monitors", {}).get("edges", [])
    if not monitors_edges:
        cls.raise_exception("No monitor found with the given name")
    monitor_node = monitors_edges[0].get("node", {})
    metric_history = monitor_node.get("metricHistory")
    if not metric_history:
        cls.raise_exception(
            "No metric history data available for the specified time range"
        )
    return [cls.QueryResponse(**metric_history)], False, None
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    monitor_name = variables.get("monitor_name", "")
    models_edges = result.get("node", {}).get("models", {}).get("edges", [])
    if not models_edges:
        cls.raise_exception("No model found with the given name")
    model_node = models_edges[0].get("node", {})
    monitors_edges = model_node.get("monitors", {}).get("edges", [])
    if not monitors_edges:
        cls.raise_exception("No monitor found with the given name")
    monitor = cls._find_exact_name_match(monitors_edges, monitor_name)
    if monitor is None:
        cls.raise_exception(f"No monitor found with the exact name '{monitor_name}'")
    metric_history = monitor.get("metricHistory")
    if not metric_history:
        cls.raise_exception(
            "No metric history data available for the specified time range"
        )
    return [cls.QueryResponse(**metric_history)], False, None
```

Note: `GetModelMetricValueQuery` uses `useExactSearchMatch: true` for the model search, so only the monitor search needs the client-side fix. The model `edges[0]` is acceptable there since the server enforces exact match.

### Changes to tests

Read existing `tests/test_queries/test_monitor_queries.py` to see what's already tested. Add tests for both queries covering:

For `TestGetMonitorQuery`, add:

```python
def test_get_monitor_no_exact_match(self, gql_client):
    """Test that partial monitor name matches are rejected."""
    mock_response = {
        "node": {
            "monitors": {
                "edges": [{"node": {"id": "mon1", "name": "Latency Monitor Production", ...}}]
            }
        }
    }
    gql_client.execute.return_value = mock_response
    with pytest.raises(GetMonitorQuery.QueryException, match="No monitor found with the exact name"):
        GetMonitorQuery.run_graphql_query(gql_client, space_id="space1", model_name="model1", monitor_name="Latency Monitor")
```

Use the `Monitor` model's required fields for mock data. Check `Monitor.to_graphql_fields()` or existing test fixtures to determine the minimal required fields. At minimum, monitors have `id` and `name`.

For `TestGetModelMetricValueQuery`, add a test verifying exact match on monitor name within the nested structure.

### Test plan

Run: `pytest tests/test_queries/test_monitor_queries.py -v`

## Task: Fix prompt queries

Files: arize_toolkit/queries/llm_utils_queries.py, tests/test_queries/test_llm_utils_queries.py

Apply the exact name match pattern to `GetPromptQuery` and `GetAllPromptVersionsQuery` in `arize_toolkit/queries/llm_utils_queries.py`.

### Changes to `GetPromptQuery` (line 72)

1. Change GraphQL: `prompts(search: $prompt_name, first: 1)` to `prompts(search: $prompt_name, first: 10)`
1. Update `_parse_graphql_result` (lines 102-107):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    if (
        not result["node"]["prompts"]["edges"]
        or len(result["node"]["prompts"]["edges"]) == 0
    ):
        cls.raise_exception("No prompts found")
    prompt = result["node"]["prompts"]["edges"][0]["node"]
    return [cls.QueryResponse(**prompt)], False, None
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    prompt_name = variables.get("prompt_name", "")
    if (
        not result["node"]["prompts"]["edges"]
        or len(result["node"]["prompts"]["edges"]) == 0
    ):
        cls.raise_exception("No prompts found")
    edges = result["node"]["prompts"]["edges"]
    prompt = cls._find_exact_name_match(edges, prompt_name)
    if prompt is None:
        cls.raise_exception(f"No prompt found with the exact name '{prompt_name}'")
    return [cls.QueryResponse(**prompt)], False, None
```

### Changes to `GetAllPromptVersionsQuery` (line 134)

1. Change GraphQL: `prompts(search: $prompt_name, first: 1)` to `prompts(search: $prompt_name, first: 10)`
1. Update `_parse_graphql_result` (lines 174-184):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    if (
        not result["node"]["prompts"]["edges"]
        or len(result["node"]["prompts"]["edges"]) == 0
    ):
        cls.raise_exception("No prompts found")
    prompt = result["node"]["prompts"]["edges"][0]["node"]
    version_edges = prompt["versionHistory"]["edges"]
    ...
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    prompt_name = variables.get("prompt_name", "")
    if (
        not result["node"]["prompts"]["edges"]
        or len(result["node"]["prompts"]["edges"]) == 0
    ):
        cls.raise_exception("No prompts found")
    edges = result["node"]["prompts"]["edges"]
    prompt = cls._find_exact_name_match(edges, prompt_name)
    if prompt is None:
        cls.raise_exception(f"No prompt found with the exact name '{prompt_name}'")
    version_edges = prompt["versionHistory"]["edges"]
    if len(version_edges) == 0:
        cls.raise_exception("No versions found")
    has_next_page = prompt["versionHistory"]["pageInfo"]["hasNextPage"]
    end_cursor = prompt["versionHistory"]["pageInfo"]["endCursor"]
    versions = [cls.QueryResponse(**version["node"]) for version in version_edges]
    return versions, has_next_page, end_cursor
```

Note: In `GetAllPromptVersionsQuery`, `_find_exact_name_match` returns the node dict directly. But this query has nested data under the prompt node (`versionHistory`). The `_find_exact_name_match` method returns the `node` dict (not the edge), so `prompt["versionHistory"]` will work correctly since the `versionHistory` field is on the node.

### Changes to tests

Read existing `tests/test_queries/test_llm_utils_queries.py` to see what `mock_prompt` fixture contains. Add tests for exact match behavior:

For `GetPromptQuery`:

- `test_get_prompt_no_exact_match`: search for "test" but response has prompt named "test-v2" — should raise exception
- `test_get_prompt_multiple_results`: two prompts returned, verify the exact match is selected

For `GetAllPromptVersionsQuery`:

- `test_get_all_prompt_versions_no_exact_match`: similar pattern — partial name match rejected

Use the existing `mock_prompt` fixture pattern for mock data. The prompt node needs `name` field plus whatever `Prompt.to_graphql_fields()` requires.

### Test plan

Run: `pytest tests/test_queries/test_llm_utils_queries.py -v`

## Task: Fix custom metric query

Files: arize_toolkit/queries/custom_metric_queries.py, tests/test_queries/test_custom_metric_queries.py

Apply the exact name match pattern to `GetCustomMetricQuery` in `arize_toolkit/queries/custom_metric_queries.py`.

### Changes to `GetCustomMetricQuery` (line 107)

1. Change GraphQL: `customMetrics(searchTerm:$metric_name, first: 1)` to `customMetrics(searchTerm:$metric_name, first: 10)`
1. Note: The model search already uses `useExactSearchMatch:true`, so only the custom metric search needs the fix
1. Update `_parse_graphql_result` (lines 145-152):

Current:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    if not result["node"]["models"]["edges"]:
        cls.raise_exception("No model found with the given name")
    model_result = result["node"]["models"]["edges"][0]["node"]
    if not model_result["customMetrics"]["edges"]:
        cls.raise_exception("No custom metric found with the given name")
    custom_metric_result = model_result["customMetrics"]["edges"][0]["node"]
    return [cls.QueryResponse(**custom_metric_result)], False, None
```

New:

```python
@classmethod
def _parse_graphql_result(
    cls, result: dict
) -> Tuple[List[BaseResponse], bool, Optional[str]]:
    variables = result.pop("__query_variables__", {})
    metric_name = variables.get("metric_name", "")
    if not result["node"]["models"]["edges"]:
        cls.raise_exception("No model found with the given name")
    model_result = result["node"]["models"]["edges"][0]["node"]
    if not model_result["customMetrics"]["edges"]:
        cls.raise_exception("No custom metric found with the given name")
    edges = model_result["customMetrics"]["edges"]
    custom_metric = cls._find_exact_name_match(edges, metric_name)
    if custom_metric is None:
        cls.raise_exception(
            f"No custom metric found with the exact name '{metric_name}'"
        )
    return [cls.QueryResponse(**custom_metric)], False, None
```

### Changes to tests

Read `tests/test_queries/test_custom_metric_queries.py` for existing patterns. Add tests for `GetCustomMetricQuery`:

- `test_get_custom_metric_success`: exact name match works
- `test_get_custom_metric_no_exact_match`: partial match rejected
- `test_get_custom_metric_multiple_results`: correct metric selected from multiple

The `CustomMetric` model has at minimum `id` and `name` fields. Use minimal mock data:

```python
mock_metric = {"id": "cm1", "name": "My Metric", ...}  # check CustomMetric model for required fields
```

### Test plan

Run: `pytest tests/test_queries/test_custom_metric_queries.py -v`

## Task: Test base and existing

Files: tests/test_queries/test_basequery.py
Depends: fix-evaluator-query, fix-dashboard-query, fix-monitor-queries, fix-prompt-queries, fix-custom-metric-query

Create a new test file `tests/test_queries/test_basequery.py` that tests the `_find_exact_name_match` utility method directly, and run the full test suite to verify all changes work together.

### Tests for `_find_exact_name_match`

```python
import pytest
from arize_toolkit.queries.basequery import BaseQuery


class TestFindExactNameMatch:
    def test_exact_match_found(self):
        edges = [
            {"node": {"name": "alpha", "id": "1"}},
            {"node": {"name": "beta", "id": "2"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "beta")
        assert result == {"name": "beta", "id": "2"}

    def test_no_match(self):
        edges = [
            {"node": {"name": "alpha", "id": "1"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "gamma")
        assert result is None

    def test_partial_match_not_returned(self):
        edges = [
            {"node": {"name": "alpha-v2", "id": "1"}},
        ]
        result = BaseQuery._find_exact_name_match(edges, "alpha")
        assert result is None

    def test_empty_edges(self):
        result = BaseQuery._find_exact_name_match([], "anything")
        assert result is None

    def test_custom_name_field(self):
        edges = [
            {"node": {"email": "user@test.com", "id": "1"}},
            {"node": {"email": "other@test.com", "id": "2"}},
        ]
        result = BaseQuery._find_exact_name_match(
            edges, "user@test.com", name_field="email"
        )
        assert result == {"email": "user@test.com", "id": "1"}

    def test_missing_node_key(self):
        edges = [{"other": "data"}, {"node": {"name": "found", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "found")
        assert result == {"name": "found", "id": "1"}

    def test_none_node(self):
        edges = [{"node": None}, {"node": {"name": "found", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "found")
        assert result == {"name": "found", "id": "1"}

    def test_case_sensitive(self):
        edges = [{"node": {"name": "Alpha", "id": "1"}}]
        result = BaseQuery._find_exact_name_match(edges, "alpha")
        assert result is None
```

### Full suite verification

Run: `pytest tests/test_queries/ -v`
All tests across all query test files must pass.
