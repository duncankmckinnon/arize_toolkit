---
name: arize-toolkit-cli
description: Manage Arize platform resources using the arize_toolkit CLI. Use when users want to list, create, update, or delete Arize resources (models, monitors, prompts, evaluators, custom metrics, dashboards, spaces, organizations, users, or data imports) via the command line, configure CLI profiles, or perform platform administration tasks. Triggers on "list models", "create monitor", "ax", "arize_toolkit", "CLI", "arize cli", or any request to manage Arize platform resources from the terminal.
---

# Arize Toolkit CLI

Manage Arize platform resources from the command line using `arize_toolkit`.

______________________________________________________________________

## Workflow

```
1. Check Setup → 2. Resolve Config → 3. Run Command → 4. Summarize Output
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

______________________________________________________________________

## Step 2: Resolve Configuration

The CLI resolves configuration in this priority order:

1. **CLI flags**: `--api-key`, `--org`, `--space`, `--app-url`
1. **Environment variables**: `ARIZE_DEVELOPER_KEY`, `ARIZE_ORGANIZATION`, `ARIZE_SPACE`, `ARIZE_APP_URL`
1. **Config profile**: `~/.arize_toolkit/config.toml`

### Check if a profile exists

```bash
arize_toolkit config list
```

### If no profile, initialize one

```bash
arize_toolkit config init
```

This runs an interactive setup. For non-interactive setup, use flags:

```bash
arize_toolkit --api-key "KEY" --org "ORG" --space "SPACE" models list
```

______________________________________________________________________

## Step 3: Run Commands

### Global Options (apply to all commands)

| Flag | Description |
|------|-------------|
| `--profile NAME` | Use a specific config profile |
| `--json` | Output as JSON instead of Rich tables |
| `--api-key KEY` | Override API key |
| `--org NAME` | Override organization |
| `--space NAME` | Override space |
| `--app-url URL` | Override app URL |

### Command Groups

| Group | Alias | Description |
|-------|-------|-------------|
| `config` | | Manage CLI configuration profiles |
| `spaces` | | Manage Arize spaces |
| `orgs` | | Manage organizations |
| `users` | | Manage users and space membership |
| `models` | `projects` | Manage models/projects |
| `monitors` | | Create and manage monitors |
| `prompts` | | Manage LLM prompt templates |
| `custom-metrics` | | Manage custom metrics |
| `evaluators` | | Manage LLM and code evaluators |
| `dashboards` | | Manage dashboards |
| `imports` | | Manage data import jobs (files/tables) |
| `traces` | | Query and inspect traces and spans |

See [references/COMMANDS.md](references/COMMANDS.md) for full command reference.

______________________________________________________________________

## Step 4: Summarize Output

- When `--json` is used, pipe through `jq` for filtering
- Present results clearly to the user
- For list commands, summarize count and key details
- For create/update/delete, confirm the action completed

______________________________________________________________________

## Common Workflows

### List all models in a space

```bash
arize_toolkit models list
```

### Get model performance metrics

```bash
arize_toolkit models performance accuracy production --model-name "my-model" --granularity day
```

### Create a performance monitor with email alerts

```bash
arize_toolkit monitors create-performance "My Monitor" \
  --model "my-model" \
  --environment production \
  --performance-metric accuracy \
  --threshold 0.9 \
  --operator lessThan \
  --email alerts@example.com
```

### Copy a monitor to another model

```bash
arize_toolkit monitors copy "My Monitor" --model "source-model" --new-model "target-model"
```

### Create a prompt template

```bash
arize_toolkit prompts create "my-prompt" \
  --messages '[{"role": "system", "content": "You are helpful."}, {"role": "user", "content": "{{query}}"}]' \
  --input-variable-format mustache
```

### Create a prompt from a file

```bash
arize_toolkit prompts create "my-prompt" --messages @prompt_messages.json
```

### List recent traces for a model

```bash
arize_toolkit traces list --model-name "my-agent"
```

### Get all spans for a trace

```bash
arize_toolkit traces get TRACE_ID --model-name "my-agent"
```

### Export trace spans to CSV with all attributes

```bash
arize_toolkit traces get TRACE_ID --model-name "my-agent" --csv spans.csv
```

### Export traces to CSV with filtered attributes

```bash
arize_toolkit traces list --model-name "my-agent" --csv traces.csv
arize_toolkit traces get TRACE_ID --model-id "ID" --columns "input.value,output.value" --csv spans.csv
```

### Export data as JSON for scripting

```bash
arize_toolkit --json models list | jq '.[].name'
```

### Use a different profile

```bash
arize_toolkit --profile staging monitors list --model-name "my-model"
```

______________________________________________________________________

## Tips

- Use `--json` flag for scripting and piping to `jq`
- Use `@filepath` syntax for complex JSON arguments (schema, messages, templates, code)
- `models` and `projects` are interchangeable aliases
- All destructive commands (delete) prompt for confirmation
- `spaces switch` and `spaces create` automatically persist the new space/org to your config profile, so subsequent commands use the new space
- Use `--help` on any command for full usage details: `arize_toolkit monitors create-performance --help`

______________________________________________________________________

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `command not found` | Install with `pip install arize_toolkit[cli]` |
| Authentication error | Check API key: `arize_toolkit config show` |
| Wrong space/org | Use `--space` / `--org` flags or switch profile |
| Complex JSON args | Use `@file.json` syntax instead of inline JSON |

______________________________________________________________________

## References

- [references/COMMANDS.md](references/COMMANDS.md) - Full command reference with all options
