# Traces

## Overview

The `traces` command group queries and inspects trace and span data from Arize models with tracing enabled.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`traces list`](#traces-list) | List recent traces for a model | `list_traces` |
| [`traces get`](#traces-get) | Get all spans for a specific trace | `get_trace` |
| [`traces columns`](#traces-columns) | List available span column names | `get_span_columns` |

______________________________________________________________________

### `traces list`

```bash
arize_toolkit traces list --model-name NAME [OPTIONS]
```

Lists recent traces (root spans) for a model. Returns trace IDs, names, status, latency, and attribute columns (`attributes.input.value`, `attributes.output.value` by default).

**Options**

- `--model-name` — Model name (either `--model-name` or `--model-id` required).
- `--model-id` — Model ID (base64-encoded).
- `--start-time` — Start of time window (ISO format). Defaults to 7 days ago.
- `--end-time` — End of time window (ISO format). Defaults to now.
- `--count` — Number of traces per page. Default `20`.
- `--sort` — Sort direction: `desc` or `asc`. Default `desc`.
- `--csv PATH` — Export results to a CSV file with flattened attributes as columns.

**Example**

```bash
$ arize_toolkit traces list --model-name business-intel-agent
                              Traces
┌──────────────┬─────────────┬──────────┬────────────┬─────────────────────┬───────────┬──────────────────────┬──────────────────────┐
│ traceId      │ name        │ spanKind │ statusCode │ startTime           │ latencyMs │ attributes.input.val │ attributes.output.va │
├──────────────┼─────────────┼──────────┼────────────┼─────────────────────┼───────────┼──────────────────────┼──────────────────────┤
│ abc123       │ AgentChain  │ CHAIN    │ OK         │ 2025-01-15 10:30:00 │ 2500      │ What is the revenue? │ The revenue is $1M…  │
│ def456       │ AgentChain  │ CHAIN    │ ERROR      │ 2025-01-15 10:25:00 │ 5200      │ Show me the metrics  │                      │
└──────────────┴─────────────┴──────────┴────────────┴─────────────────────┴───────────┴──────────────────────┴──────────────────────┘

$ arize_toolkit --json traces list --model-id "TW9kZWw6..." --count 5

# Export to CSV with all attributes flattened as columns
$ arize_toolkit traces list --model-name business-intel-agent --csv traces.csv
Exported 20 traces to traces.csv
```

______________________________________________________________________

### `traces get`

```bash
arize_toolkit traces get TRACE_ID --model-name NAME [OPTIONS]
```

Gets all spans for a specific trace with their attributes and structured column data. By default shows only `attributes.input.value` and `attributes.output.value`. Use `--all` to auto-discover and include all available columns, or `--columns` to specify exact columns.

**Arguments**

- `TRACE_ID` — The trace ID to look up.

**Options**

- `--model-name` — Model name (either `--model-name` or `--model-id` required).
- `--model-id` — Model ID (base64-encoded).
- `--start-time` — Start of time window (ISO format). Defaults to 7 days ago.
- `--end-time` — End of time window (ISO format). Defaults to now.
- `--columns` — Comma-separated column names to include (e.g. `attributes.input.value,attributes.output.value`).
- `--all` — Include all available columns (auto-discovered via `get_span_columns`).
- `--count` — Number of spans per page. Default `20`.
- `--csv PATH` — Export results to a CSV file with flattened attributes as columns.

**Example**

```bash
$ arize_toolkit traces get abc123 --model-name business-intel-agent
                           Trace: abc123
┌──────────┬─────────────┬──────────┬────────────┬──────────┬───────────┐
│ spanId   │ name        │ spanKind │ statusCode │ parentId │ latencyMs │
├──────────┼─────────────┼──────────┼────────────┼──────────┼───────────┤
│ span-1   │ AgentChain  │ CHAIN    │ OK         │          │ 2500      │
│ span-2   │ Retriever   │ RETRIEVER│ OK         │ span-1   │ 800       │
│ span-3   │ LLM         │ LLM      │ OK         │ span-1   │ 1500      │
└──────────┴─────────────┴──────────┴────────────┴──────────┴───────────┘

# Export all spans with all attributes to CSV
$ arize_toolkit traces get abc123 --model-name business-intel-agent --csv trace.csv
Exported 3 spans to trace.csv

# Export only specific columns
$ arize_toolkit traces get abc123 --model-id "TW9kZWw6..." --columns "attributes.input.value,attributes.output.value" --csv trace.csv

# JSON output includes raw attributes as a JSON string
$ arize_toolkit --json traces get abc123 --model-id "TW9kZWw6..."
```

______________________________________________________________________

### `traces columns`

```bash
arize_toolkit traces columns --model-name NAME [OPTIONS]
```

Lists all available span column names for a model. Use this to discover which `attributes.*` columns can be passed to `traces get --columns`.

**Options**

- `--model-name` — Model name (either `--model-name` or `--model-id` required).
- `--model-id` — Model ID (base64-encoded).
- `--start-time` — Start of time window (ISO format). Defaults to 7 days ago.
- `--end-time` — End of time window (ISO format). Defaults to now.

**Example**

```bash
$ arize_toolkit traces columns --model-name business-intel-agent
attributes.input.value
attributes.output.value
attributes.llm.model_name
attributes.llm.token_count.total
attributes.llm.token_count.prompt
attributes.llm.token_count.completion
attributes.metadata
...

$ arize_toolkit --json traces columns --model-name business-intel-agent
[
  "attributes.input.value",
  "attributes.output.value",
  "attributes.llm.model_name",
  ...
]
```
