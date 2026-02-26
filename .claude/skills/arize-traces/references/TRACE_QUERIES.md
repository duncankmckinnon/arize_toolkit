# Trace Query Reference

End-to-end CLI walkthrough for discovering projects, retrieving traces, and analyzing trace data.

______________________________________________________________________

## Table of Contents

1. [Find Available Spaces and Projects](#step-1-find-available-spaces-and-projects)
1. [Find the Target Project](#step-2-find-the-target-project)
1. [Discover Available Columns](#step-3-discover-available-columns)
1. [List Traces](#step-4-list-traces)
1. [Get Trace Detail](#step-5-get-trace-detail)
1. [Analyze Traces](#step-6-analyze-traces)
1. [Column Name Catalog](#column-name-catalog)

______________________________________________________________________

## Step 1: Find Available Spaces and Projects

Start by listing available spaces to understand the organization structure:

```bash
# List all spaces in the organization
arize_toolkit spaces list

# Switch to a specific space
arize_toolkit spaces switch "My Space"

# List all models/projects in the current space
arize_toolkit models list

# JSON output for scripting
arize_toolkit --json models list | jq '.[].name'
```

If you need to work in a different organization or space, override with flags:

```bash
arize_toolkit --org "Other Org" --space "Other Space" models list
```

______________________________________________________________________

## Step 2: Find the Target Project

Identify the project (model) that has tracing enabled:

```bash
# Get details for a specific project by name
arize_toolkit models get "business-intel-agent"

# JSON output to see the model ID
arize_toolkit --json models get "business-intel-agent" | jq '{name, id, modelType}'
```

The model name is what you pass to `--model-name` in all trace commands. Alternatively, use the base64-encoded model ID with `--model-id`.

______________________________________________________________________

## Step 3: Discover Available Columns

Before querying traces, discover what attribute columns exist for the project:

```bash
# List all available span columns
arize_toolkit traces columns --model-name business-intel-agent

# JSON output for scripting
arize_toolkit --json traces columns --model-name business-intel-agent

# With a specific time window
arize_toolkit traces columns --model-name business-intel-agent \
  --start-time 2025-01-01T00:00:00Z --end-time 2025-01-31T23:59:59Z
```

Common columns you'll see:

| Column | Description |
|--------|-------------|
| `attributes.input.value` | Span input text |
| `attributes.output.value` | Span output text |
| `attributes.llm.model_name` | LLM model used |
| `attributes.llm.token_count.total` | Total tokens |
| `attributes.llm.token_count.prompt` | Prompt tokens |
| `attributes.llm.token_count.completion` | Completion tokens |

See [Column Name Catalog](#column-name-catalog) for the full list.

______________________________________________________________________

## Step 4: List Traces

List recent traces (root spans) to find trace IDs for inspection:

```bash
# List recent traces (default: 20 most recent, Rich table)
arize_toolkit traces list --model-name business-intel-agent

# More traces, with time window
arize_toolkit traces list --model-name business-intel-agent \
  --count 50 --start-time 2025-01-01T00:00:00Z

# Oldest first
arize_toolkit traces list --model-name business-intel-agent --sort asc

# JSON output — extract just trace IDs
arize_toolkit --json traces list --model-name business-intel-agent | jq '.[].traceId'

# Export to CSV for external analysis
arize_toolkit traces list --model-name business-intel-agent --csv traces.csv
```

The output includes: `traceId`, `name`, `spanKind`, `statusCode`, `startTime`, `latencyMs`, and default attribute columns (`attributes.input.value`, `attributes.output.value`).

______________________________________________________________________

## Step 5: Get Trace Detail

Once you have a trace ID, retrieve all spans with their attributes:

```bash
# Default: shows input/output attributes
arize_toolkit traces get TRACE_ID --model-name business-intel-agent

# Include ALL available columns (auto-discovered)
arize_toolkit traces get TRACE_ID --model-name business-intel-agent --all

# Specific columns only (faster than --all)
arize_toolkit traces get TRACE_ID --model-name business-intel-agent \
  --columns "attributes.input.value,attributes.output.value,attributes.llm.model_name"

# JSON output for programmatic analysis
arize_toolkit --json traces get TRACE_ID --model-name business-intel-agent --all

# Export to CSV
arize_toolkit traces get TRACE_ID --model-name business-intel-agent --all --csv trace.csv
```

The output includes per-span: `spanId`, `traceId`, `name`, `spanKind`, `statusCode`, `parentId`, `startTime`, `latencyMs`, and requested attribute columns.

______________________________________________________________________

## Step 6: Analyze Traces

### Find error traces

```bash
arize_toolkit --json traces list --model-name business-intel-agent \
  | jq '[.[] | select(.statusCode == "ERROR")]'
```

### Find slow traces

```bash
arize_toolkit --json traces list --model-name business-intel-agent \
  | jq '[.[] | select(.latencyMs > 5000)] | sort_by(-.latencyMs)'
```

### Build a span tree from a trace

```bash
arize_toolkit --json traces get TRACE_ID --model-name business-intel-agent \
  | jq '[.[] | {name, spanKind, latencyMs, parentId, spanId}]'
```

Root spans have `parentId: null`. Child spans reference their parent via `parentId`.

### Compare token usage across traces

```bash
arize_toolkit --json traces list --model-name business-intel-agent --count 50 \
  | jq '[.[] | {traceId, name, latencyMs, tokens: .traceTokenCounts.aggregateTotalTokenCount}] | sort_by(-.tokens)'
```

### Export for deeper analysis

```bash
# Export traces list
arize_toolkit traces list --model-name business-intel-agent --count 100 --csv traces.csv

# Export a single trace's spans with all attributes
arize_toolkit traces get TRACE_ID --model-name business-intel-agent --all --csv spans.csv
```

### Summarizing trace results

When presenting trace detail, structure as:

1. **Span tree** — show parent-child relationships using `parentId` (root has `parentId: null`)
1. **Per-span row** — name, kind, latency, status, truncated input/output
1. **Errors** — highlight spans with `statusCode: ERROR`
1. **Performance** — identify slowest spans and token-heavy operations

______________________________________________________________________

## Column Name Catalog

Column names use the `attributes.*` prefix. Use `arize_toolkit traces columns` to discover all available columns dynamically.

### Core Input/Output (most commonly needed)

- `attributes.input.value` - Span input text
- `attributes.output.value` - Span output text
- `attributes.llm.input_messages` - LLM input messages (JSON)
- `attributes.llm.output_messages` - LLM output messages (JSON)

### LLM Details

- `attributes.llm.model_name` - Model name
- `attributes.llm.provider` - LLM provider
- `attributes.llm.system` - LLM system
- `attributes.llm.invocation_parameters` - Model parameters
- `attributes.llm.token_count.total` - Total tokens
- `attributes.llm.token_count.prompt` - Prompt tokens
- `attributes.llm.token_count.completion` - Completion tokens
- `attributes.llm.token_count.prompt_details.cache_read` - Cached prompt tokens
- `attributes.llm.token_count.completion_details.reasoning` - Reasoning tokens

### Cost

- `attributes.llm.cost.total` - Total cost
- `attributes.llm.cost.prompt` - Prompt cost
- `attributes.llm.cost.completion` - Completion cost

### Span Metadata

- `context.trace_id` - Trace ID (as column)
- `name` - Span name (as column)
- `start_time` - Start time (as column)
- `latency_ms` - Latency (as column)
- `status_code` - Status (as column)
- `attributes.metadata` - Custom metadata
- `attributes.session.id` - Session ID
- `attributes.user.id` - User ID

### Evaluations

Pattern: `eval.<eval_name>.<field>` where field is `label`, `score`, or `explanation`.

Example: `eval.matches_regex.label`, `eval.matches_regex.score`
