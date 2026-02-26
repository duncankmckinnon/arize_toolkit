# Traces

## Overview

The `traces` command group queries and inspects trace and span data from Arize models with tracing enabled.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`traces list`](#traces-list) | List recent traces for a model | `list_traces` |
| [`traces get`](#traces-get) | Get all spans for a specific trace | `get_trace` |

______________________________________________________________________

### `traces list`

```bash
arize_toolkit traces list --model-name NAME [OPTIONS]
```

Lists recent traces (root spans) for a model. Returns trace IDs, names, status, and latency.

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
┌──────────────┬─────────────┬──────────┬────────────┬─────────────────────┬───────────┐
│ traceId      │ name        │ spanKind │ statusCode │ startTime           │ latencyMs │
├──────────────┼─────────────┼──────────┼────────────┼─────────────────────┼───────────┤
│ abc123       │ AgentChain  │ CHAIN    │ OK         │ 2025-01-15 10:30:00 │ 2500      │
│ def456       │ AgentChain  │ CHAIN    │ ERROR      │ 2025-01-15 10:25:00 │ 5200      │
└──────────────┴─────────────┴──────────┴────────────┴─────────────────────┴───────────┘

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

Gets all spans for a specific trace with their full attributes.

**Arguments**

- `TRACE_ID` — The trace ID to look up.

**Options**

- `--model-name` — Model name (either `--model-name` or `--model-id` required).
- `--model-id` — Model ID (base64-encoded).
- `--start-time` — Start of time window (ISO format). Defaults to 7 days ago.
- `--end-time` — End of time window (ISO format). Defaults to now.
- `--columns` — Comma-separated attribute names to filter (default: all attributes). Attribute keys use dotted notation without the `attributes.` prefix (e.g. `input.value,output.value`).
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

# Export only specific attributes
$ arize_toolkit traces get abc123 --model-id "TW9kZWw6..." --columns "input.value,output.value" --csv trace.csv

# JSON output includes raw attributes as a JSON string
$ arize_toolkit --json traces get abc123 --model-id "TW9kZWw6..."
```
