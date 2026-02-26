---
name: arize-traces
description: Retrieve and debug trace data from the Arize ML observability platform. Use when users want to list recent traces, look up a specific trace by trace ID, get all spans within a trace, analyze trace performance (latency, tokens, cost), or export trace data. Triggers on "list traces", "show traces", "look at traces", "get traces", "trace ID", "show me the spans", "see the spans", "dig into a trace", "trace detail", "trace performance", "what traces", "debug trace", "span lookup", "trace latency", "trace tokens", "trace cost", "export traces". Prefer this skill over arize-toolkit-cli when the request is specifically about traces or spans.
---

# Arize Traces

Retrieve trace and span data from Arize using the `arize_toolkit` CLI.

---

## Important: Token Usage & Column Selection

When first retrieving trace or span data, **ask the user** whether they want:

1. **Recommended columns** (lower token usage) — a curated subset of the most useful attributes: `name`, `spanKind`, `statusCode`, `latencyMs`, `parentId`, `attributes.input.value`, `attributes.output.value`, `attributes.llm.model_name`, `attributes.llm.token_count.prompt`, `attributes.llm.token_count.completion`, `attributes.tool.name`
2. **All columns** (higher token usage) — every available attribute via `--all`. Note: this pulls 30+ fields per span including many empty values, which significantly increases context window usage in longer sessions.

Once the user chooses, **use that approach for the rest of the session** unless they request otherwise.

Always use `--json` output (global flag before the subcommand) — Rich table output wraps poorly and uses more tokens. Truncate `input.value` and `output.value` with jq `[:120]` in list views; show full values only when inspecting individual spans.

---

## Workflow

```
1. Check Setup → 2. List Traces → 3. Choose Column Detail → 4. Get Trace Detail → 5. Summarize
```

---

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

If no profile exists, ask the user for their API key, organization name, and space name, then create the profile:

```bash
arize_toolkit config init --api-key "API_KEY" --org "ORG_NAME" --space "SPACE_NAME"
```

---

## Step 2: List Traces

List recent traces using `--json` and `--count 5` (start small, paginate if needed):

```bash
# Compact summary (recommended default)
arize_toolkit --json traces list --model-name my-agent --count 5 | jq '.[] | {name, traceId, statusCode, latencyMs, input: .["attributes.input.value"][:120]}'

# With time window
arize_toolkit --json traces list --model-name my-agent --count 5 --start-time 2025-01-01T00:00:00Z

# Sort ascending (oldest first)
arize_toolkit --json traces list --model-name my-agent --count 5 --sort asc

# More results when needed
arize_toolkit --json traces list --model-name my-agent --count 20

# Export to CSV
arize_toolkit traces list --model-name my-agent --csv traces.csv

# Use model ID instead of name
arize_toolkit --json traces list --model-id "TW9kZWw6..."
```

Present results as a table of traces with: trace ID, root span name, status, latency, start time.

---

## Step 3: Choose Column Detail

Before fetching span data, **ask the user** using AskUserQuestion:

- **Recommended columns** (lower token usage) — core span fields plus key LLM attributes. Suitable for most debugging and inspection tasks.
- **All columns** (higher token usage) — every available attribute. Useful for deep debugging or discovering unexpected attributes. Note: pulls 30+ fields per span, many empty.

Remember their choice and use it for subsequent trace queries in the session.

To discover what columns exist for a model:

```bash
arize_toolkit --json traces columns --model-name my-agent
```

---

## Step 4: Get Trace Detail

Once the user picks a trace ID, get all spans using their chosen column detail level.

**Recommended columns** (lower token usage):

```bash
arize_toolkit --json traces get TRACE_ID --model-name my-agent \
  --columns "attributes.input.value,attributes.output.value,attributes.llm.model_name,attributes.llm.token_count.prompt,attributes.llm.token_count.completion,attributes.tool.name"
```

**All columns** (higher token usage):

```bash
arize_toolkit --json traces get TRACE_ID --model-name my-agent --all
```

**Export to CSV** (does not consume context tokens):

```bash
arize_toolkit traces get TRACE_ID --model-name my-agent --all --csv trace.csv
```

---

## Step 5: Summarize Results

Present trace detail as:

1. **Span tree** — show parent-child relationships using `parentId` (root has `parentId: ""`)
1. **Per-span row** — name, kind, latency, status, truncated input/output
1. **Errors** — highlight spans with error status codes

---

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

---

## Common Workflows

### Quick trace inspection

```bash
# List recent traces
arize_toolkit --json traces list --model-name my-agent --count 5 | jq '.[] | {name, traceId, statusCode, latencyMs, input: .["attributes.input.value"][:120]}'

# Get spans with recommended columns
arize_toolkit --json traces get TRACE_ID --model-name my-agent \
  --columns "attributes.input.value,attributes.output.value,attributes.llm.model_name,attributes.llm.token_count.prompt,attributes.llm.token_count.completion,attributes.tool.name"
```

### Parse spans with JSON output (recommended)

Always prefer `--json` over Rich table output for trace inspection — it avoids terminal wrapping issues and is easier to filter. Use `arize_toolkit --json` (global flag, before the subcommand).

**Compact span summary** — name, kind, latency, truncated input/output:

```bash
arize_toolkit --json traces get TRACE_ID --model-name my-agent | jq '.[] | {name, spanKind, statusCode, latencyMs, input: .["attributes.input.value"][:80], output: .["attributes.output.value"][:80]}'
```

**All attributes, formatted per-span** — uses `--json --all` and pipes through Python to produce clean readable output with empty fields filtered out:

```bash
arize_toolkit --json traces get TRACE_ID --model-name my-agent --all 2>&1 | python3 -c "
import sys, json

data = json.load(sys.stdin)
for idx, span in enumerate(data):
    print(f'=== Span {idx+1}: {span.get(\"name\", \"unknown\")} ===')
    for k, v in span.items():
        if k == 'name':
            continue
        val = str(v).strip()
        if not val or val == 'None':
            continue
        if len(val) > 300:
            val = val[:300] + '...'
        print(f'  {k}: {val}')
    print()
"
```

**Single span by name** — get all non-empty attributes for a specific span (uses a jq file to avoid zsh `!=` escaping issues):

```bash
cat > /tmp/span.jq << 'JQEOF'
first(.[] | select(.name == "SPAN_NAME")) | with_entries(select(.value != null and .value != ""))
JQEOF

arize_toolkit --json traces get TRACE_ID --model-name my-agent --all | jq -f /tmp/span.jq
```

**List traces as compact summary**:

```bash
arize_toolkit --json traces list --model-name my-agent | jq '.[] | {name, traceId, statusCode, latencyMs, input: .["attributes.input.value"][:80]}'
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

---

## Tips

- **Always use `--json`** — place it before the subcommand: `arize_toolkit --json traces ...`
- **Start with `--count 5`** — paginate up if the user needs more
- **Ask the user about column detail level** on first trace retrieval, then stick with their choice
- **Truncate input/output in list views** — use jq `[:120]` on value fields to keep context small
- **Use jq files for `!=` filters** — zsh escapes `!` in inline jq causing errors. Write filters to a temp file and use `jq -f`:
  ```bash
  cat > /tmp/filter.jq << 'JQEOF'
  .[] | with_entries(select(.value != null and .value != ""))
  JQEOF
  arize_toolkit --json traces get TRACE_ID --model-name my-agent --all | jq -f /tmp/filter.jq
  ```
- **Export to CSV for large datasets** — CSV export does not consume context tokens
- Default time window is 7 days; use `--start-time` / `--end-time` for custom ranges
- Use `--help` on any command for full usage: `arize_toolkit traces list --help`

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found` | Install with `pip install arize_toolkit[cli]` |
| Authentication error | Check API key: `arize_toolkit config show` |
| No traces returned | Check model name and time window; traces default to last 7 days |
| Missing columns | Run `traces columns` to discover available attributes |
| Wrong space/org | Use `--space` / `--org` flags or switch profile |

---

## API Constraints

- Query complexity limit is 1000 — keep `--count` at 10-20 and paginate
- `environmentName` is always `"tracing"` for trace/span data (handled automatically by the CLI)

---

## References

- [references/TRACE_QUERIES.md](references/TRACE_QUERIES.md) — raw GraphQL queries, column name catalog, filter patterns, token/cost queries
