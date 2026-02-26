---
name: arize-traces
description: Retrieve and debug trace data from the Arize ML observability platform. Use when users want to list recent traces, look up a specific trace by trace ID, get all spans within a trace, analyze trace performance (latency, tokens, cost), or export trace data. Triggers on requests involving Arize traces, span lookup, trace debugging, trace ID queries, or trace performance analysis.
---

# Arize Traces

Retrieve trace and span data from Arize using the `arize_toolkit` CLI.

______________________________________________________________________

## Workflow

```
1. Check Setup → 2. Discover Columns → 3. List Traces → 4. Get Trace Detail → 5. Summarize
```

______________________________________________________________________

## Step 1: Check Setup

Verify the CLI is installed:

```bash
arize_toolkit --version
```

If not installed:

```bash
pip install arize_toolkit[cli]
```

Verify configuration:

```bash
arize_toolkit config list
```

If no profile exists, initialize one:

```bash
arize_toolkit config init
```

______________________________________________________________________

## Step 2: Discover Available Columns

Before querying traces, discover what attribute columns are available for a model:

```bash
arize_toolkit traces columns --model-name my-agent
```

JSON output for scripting:

```bash
arize_toolkit --json traces columns --model-name my-agent
```

With a specific time window:

```bash
arize_toolkit traces columns --model-name my-agent \
  --start-time 2025-01-01T00:00:00Z --end-time 2025-01-31T23:59:59Z
```

This returns column names like `attributes.input.value`, `attributes.llm.model_name`, etc. Use these with `traces get --columns`.

______________________________________________________________________

## Step 3: List Traces

List recent traces (root spans) for a model to discover trace IDs:

```bash
# Rich table output (default)
arize_toolkit traces list --model-name my-agent

# With time window and count
arize_toolkit traces list --model-name my-agent --start-time 2025-01-01T00:00:00Z --count 50

# Sort ascending (oldest first)
arize_toolkit traces list --model-name my-agent --sort asc

# JSON output for scripting
arize_toolkit --json traces list --model-name my-agent | jq '.[].traceId'

# Export to CSV
arize_toolkit traces list --model-name my-agent --csv traces.csv

# Use model ID instead of name
arize_toolkit traces list --model-id "TW9kZWw6..."
```

Present results as a table of traces with: trace ID, root span name, status, latency, start time.

______________________________________________________________________

## Step 4: Get Trace Detail

Once the user picks a trace ID, get all spans with their attributes:

```bash
# Default: shows input/output attributes
arize_toolkit traces get TRACE_ID --model-name my-agent

# Include all available columns (auto-discovered)
arize_toolkit traces get TRACE_ID --model-name my-agent --all

# Specify exact columns
arize_toolkit traces get TRACE_ID --model-name my-agent \
  --columns "attributes.input.value,attributes.output.value,attributes.llm.model_name"

# Export to CSV
arize_toolkit traces get TRACE_ID --model-name my-agent --all --csv trace.csv

# JSON output
arize_toolkit --json traces get TRACE_ID --model-name my-agent
```

______________________________________________________________________

## Step 5: Summarize Results

Present trace detail as:

1. **Span tree** — show parent-child relationships using `parentId` (root has `parentId: ""`)
1. **Per-span row** — name, kind, latency, status, truncated input/output
1. **Errors** — highlight spans with error status codes

______________________________________________________________________

## CLI Options Reference

| Command | Option | Description |
|---------|--------|-------------|
| All | `--model-name` | Model name (either this or `--model-id` required) |
| All | `--model-id` | Model ID, base64-encoded (either this or `--model-name` required) |
| All | `--start-time` | Start of time window, ISO format (default: 7 days ago) |
| All | `--end-time` | End of time window, ISO format (default: now) |
| `list` | `--count` | Number of traces per page (default: 20) |
| `list` | `--sort` | Sort direction: `desc` or `asc` (default: `desc`) |
| `list` | `--csv PATH` | Export to CSV file |
| `get` | `TRACE_ID` | Trace ID to look up (positional argument) |
| `get` | `--columns` | Comma-separated column names to include |
| `get` | `--all` | Include all available columns (auto-discovered) |
| `get` | `--count` | Number of spans per page (default: 20) |
| `get` | `--csv PATH` | Export to CSV file |

______________________________________________________________________

## Common Workflows

### Quick trace inspection

```bash
arize_toolkit traces list --model-name my-agent --count 5
arize_toolkit traces get TRACE_ID --model-name my-agent --all
```

### Export traces for analysis

```bash
arize_toolkit traces list --model-name my-agent --count 100 --csv traces.csv
arize_toolkit traces get TRACE_ID --model-name my-agent --all --csv spans.csv
```

### Find error traces

```bash
arize_toolkit --json traces list --model-name my-agent | jq '[.[] | select(.statusCode == "ERROR")]'
```

### Use a different profile

```bash
arize_toolkit --profile staging traces list --model-name my-agent
```

______________________________________________________________________

## Tips

- Use `--json` flag for scripting and piping to `jq`
- Use `traces columns` first to discover available attributes before querying
- `--all` on `traces get` auto-discovers all columns but may be slower
- `--columns` is faster when you know exactly which attributes you need
- Default time window is 7 days; use `--start-time` / `--end-time` for custom ranges
- Use `--help` on any command for full usage: `arize_toolkit traces list --help`

______________________________________________________________________

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found` | Install with `pip install arize_toolkit[cli]` |
| Authentication error | Check API key: `arize_toolkit config show` |
| No traces returned | Check model name and time window; traces default to last 7 days |
| Missing columns | Run `traces columns` to discover available attributes |
| Wrong space/org | Use `--space` / `--org` flags or switch profile |

______________________________________________________________________

## API Constraints

- Query complexity limit is 1000 — keep `--count` at 10-20 and paginate
- `environmentName` is always `"tracing"` for trace/span data (handled automatically by the CLI)

______________________________________________________________________

## References

- [references/TRACE_QUERIES.md](references/TRACE_QUERIES.md) — raw GraphQL queries, column name catalog, filter patterns, token/cost queries
