# Trace Tools

## Overview

In Arize, traces represent end-to-end executions of your LLM application, composed of individual spans. Each span captures a single operation (LLM call, retrieval, tool use, etc.) with its input, output, latency, and status.

In `arize_toolkit`, the `Client` exposes helpers for:

1. Discovering available span column names for a model
1. Listing recent traces (root spans) for a model in a time window
1. Retrieving all spans for a specific trace with full attributes
1. Exporting trace data as pandas DataFrames for analysis

| Operation | Helper |
|-----------|--------|
| Discover available columns | [`get_span_columns`](#get_span_columns) |
| List traces for a model | [`list_traces`](#list_traces) |
| Get all spans for a trace | [`get_trace`](#get_trace) |

## Trace Operations

______________________________________________________________________

### `get_span_columns`

```python
columns: list[str] = client.get_span_columns(
    model_name="my-agent",
    start_time="2025-01-01T00:00:00Z",
    end_time="2025-01-02T00:00:00Z",
)
```

Discovers all available span column names for a model by querying `tracingSchema.spanProperties`. Returns column names in `attributes.*` format ready to pass to `get_trace()`.

**Parameters**

- `model_name` (Optional[str]) — Name of the model. Either `model_name` or `model_id` is required.
- `model_id` (Optional[str]) — ID of the model (base64-encoded). Either `model_name` or `model_id` is required.
- `start_time` (Optional[datetime | str]) — Start of time window. Defaults to 7 days ago.
- `end_time` (Optional[datetime | str]) — End of time window. Defaults to now.

**Returns**

A list of column name strings, e.g. `["attributes.input.value", "attributes.output.value", "attributes.llm.model_name", ...]`.

**Example**

```python
columns = client.get_span_columns(model_name="business-intel-agent")
print(columns)
# ['attributes.input.value', 'attributes.output.value', 'attributes.llm.model_name', ...]
```

______________________________________________________________________

### `list_traces`

```python
traces: list[dict] = client.list_traces(
    model_name="my-agent",
    start_time="2025-01-01T00:00:00Z",
    end_time="2025-01-02T00:00:00Z",
    count=20,
    sort_direction="desc",
)
```

Lists root spans (one per trace) for a model within a time window. Use this to discover trace IDs for further inspection. By default, requests `attributes.input.value` and `attributes.output.value` as structured columns.

**Parameters**

- `model_name` (Optional[str]) — Name of the model. Either `model_name` or `model_id` is required.
- `model_id` (Optional[str]) — ID of the model (base64-encoded). Either `model_name` or `model_id` is required.
- `start_time` (Optional[datetime | str]) — Start of time window. Defaults to 7 days ago.
- `end_time` (Optional[datetime | str]) — End of time window. Defaults to now.
- `count` (int) — Number of traces per page. Default `20`.
- `sort_direction` (str) — Sort direction: `"desc"` or `"asc"`. Default `"desc"`.
- `to_dataframe` (bool) — If `True`, return a pandas DataFrame with flattened attributes as columns. Default `False`.

**Returns**

When `to_dataframe=False` (default), a list of dictionaries — one per trace — containing:

- `traceId` — Unique trace identifier
- `name` — Root span name
- `spanKind` — Span kind (e.g. `CHAIN`, `LLM`, `AGENT`)
- `statusCode` — Status (`OK`, `ERROR`, `UNSET`)
- `startTime` — When the trace started
- `latencyMs` — End-to-end latency in milliseconds
- `spanId` — Root span identifier
- `parentId` — Always `None` for root spans
- `attributes` — JSON string containing all span attributes
- `columns` — Structured column values for requested column names
- `traceTokenCounts` — Aggregate token counts (prompt, completion, total)

When `to_dataframe=True`, a pandas DataFrame with the above fields plus all attributes flattened as `attributes.<key>` columns.

**Example**

```python
from arize_toolkit import Client

client = Client(organization="my-org", space="my-space")

# List the 10 most recent traces
traces = client.list_traces(model_name="business-intel-agent", count=10)
for t in traces:
    print(f"[{t['statusCode']}] {t['name']} — {t['latencyMs']:.0f}ms — {t['traceId']}")

# Get traces as a DataFrame for analysis
df = client.list_traces(model_name="business-intel-agent", count=50, to_dataframe=True)
print(df[["traceId", "name", "latencyMs", "attributes.input.value"]].head())
```

______________________________________________________________________

### `get_trace`

```python
spans: list[dict] = client.get_trace(
    trace_id="abc123-def456",
    model_name="my-agent",
)
```

Retrieves all spans for a specific trace with full attributes and structured column data. When `column_names` is not specified, all available columns are auto-discovered via `get_span_columns()`.

**Parameters**

- `trace_id` (str) — The trace ID to look up.
- `model_name` (Optional[str]) — Name of the model. Either `model_name` or `model_id` is required.
- `model_id` (Optional[str]) — ID of the model (base64-encoded). Either `model_name` or `model_id` is required.
- `start_time` (Optional[datetime | str]) — Start of time window. Defaults to 7 days ago.
- `end_time` (Optional[datetime | str]) — End of time window. Defaults to now.
- `column_names` (Optional\[list[str]\]) — Column names to include (e.g. `["attributes.input.value"]`). If `None` (default), all available columns are auto-discovered.
- `count` (int) — Number of spans per page. Default `20`.
- `to_dataframe` (bool) — If `True`, return a pandas DataFrame with flattened attributes as columns. Default `False`.

**Returns**

When `to_dataframe=False` (default), a list of dictionaries — one per span — containing:

- `spanId` — Span identifier
- `traceId` — Parent trace identifier
- `name` — Span name
- `spanKind` — Span kind (e.g. `LLM`, `RETRIEVER`, `TOOL`)
- `statusCode` — Status (`OK`, `ERROR`, `UNSET`)
- `parentId` — Parent span ID (`None` for root)
- `startTime` — When the span started
- `latencyMs` — Span latency in milliseconds
- `attributes` — JSON string of all span attributes
- `columns` — Structured column values for requested column names
- `traceTokenCounts` — Aggregate token counts (prompt, completion, total)

When `to_dataframe=True`, a pandas DataFrame with span fields plus attributes flattened as `attributes.<key>` columns. Structured column values take precedence over parsed attributes.

**Column Names**

Column names use the `attributes.*` prefix format. Use `get_span_columns()` to discover available columns, or refer to common ones below:

| Category | Column Names |
|----------|-------------|
| Core | `attributes.input.value`, `attributes.output.value` |
| LLM Messages | `attributes.llm.input_messages`, `attributes.llm.output_messages` |
| Token Counts | `attributes.llm.token_count.prompt`, `attributes.llm.token_count.completion`, `attributes.llm.token_count.total` |
| Metadata | `attributes.llm.model_name`, `attributes.llm.provider` |

**Example**

```python
# Get all spans with all available columns (auto-discovered)
spans = client.get_trace(
    trace_id="abc123-def456",
    model_name="business-intel-agent",
)
for s in spans:
    indent = "  " if s["parentId"] else ""
    print(f"{indent}{s['name']} ({s['spanKind']}) — {s['latencyMs']:.0f}ms")

# Get a DataFrame with specific columns
df = client.get_trace(
    trace_id="abc123-def456",
    model_name="business-intel-agent",
    column_names=[
        "attributes.input.value",
        "attributes.output.value",
        "attributes.llm.token_count.total",
    ],
    to_dataframe=True,
)
print(df[["name", "spanKind", "latencyMs", "attributes.input.value"]].to_string())

# Discover all available columns first
columns = client.get_span_columns(model_name="business-intel-agent")
print(f"Available columns: {columns}")
```
