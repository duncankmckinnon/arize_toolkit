# Models & Projects

## Overview

The `models` command group retrieves information about models (also called **projects** in the context of LLM tracing). The `projects` command is an exact alias — every subcommand works the same way under either name.

```bash
# These are identical:
arize_toolkit models list
arize_toolkit projects list
```

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`models list`](#models-list) | List all models in the space | `get_all_models` |
| [`models get`](#models-get) | Get a model by name | `get_model` |
| [`models volume`](#models-volume) | Get prediction volume | `get_model_volume` |
| [`models total-volume`](#models-total-volume) | Get total prediction count | `get_total_volume` |
| [`models performance`](#models-performance) | Pull performance metrics over time | `get_performance_metric_over_time` |
| [`models delete-data`](#models-delete-data) | Delete data from a model | `delete_data` |

______________________________________________________________________

### `models list`

```bash
arize_toolkit models list
```

Lists all models in the current space with ID, name, type, and creation date.

**Example**

```bash
$ arize_toolkit models list
                         Models
┌──────────┬────────────────────┬─────────────────┬────────────┐
│ id       │ name               │ modelType       │ createdAt  │
├──────────┼────────────────────┼─────────────────┼────────────┤
│ m1       │ fraud-detection-v3 │ classification  │ 2024-06-01 │
│ m2       │ chatbot-prod       │ generative      │ 2024-09-15 │
└──────────┴────────────────────┴─────────────────┴────────────┘
```

```bash
# JSON output with jq
arize_toolkit --json models list | jq '.[].name'
```

______________________________________________________________________

### `models get`

```bash
arize_toolkit models get NAME
```

Retrieves detailed information for a single model.

**Arguments**

- `NAME` — The model name.

**Example**

```bash
arize_toolkit models get "fraud-detection-v3"
arize_toolkit --json projects get "chatbot-prod"
```

______________________________________________________________________

### `models volume`

```bash
arize_toolkit models volume NAME [--start-time TIME] [--end-time TIME]
```

Returns prediction volume for a model, broken down by environment.

**Arguments**

- `NAME` — The model name.

**Options**

- `--start-time` (optional) — Start time in ISO format (e.g. `2025-01-01T00:00:00`). Defaults to 30 days ago.
- `--end-time` (optional) — End time in ISO format. Defaults to now.

**Example**

```bash
arize_toolkit models volume "fraud-detection-v3" --start-time 2025-01-01
arize_toolkit --json models volume "fraud-detection-v3"
```

______________________________________________________________________

### `models total-volume`

```bash
arize_toolkit models total-volume [--model-name NAME] [--model-id ID] [--start-time TIME] [--end-time TIME]
```

Returns the total prediction count as a single number.

**Options**

- `--model-name` (optional) — Model name.
- `--model-id` (optional) — Model ID.
- `--start-time` / `--end-time` (optional) — Time range in ISO format.

**Example**

```bash
$ arize_toolkit models total-volume --model-name "fraud-detection-v3"
Total volume: 142857

$ arize_toolkit --json models total-volume --model-name "fraud-detection-v3"
{"total_volume": 142857}
```

______________________________________________________________________

### `models performance`

```bash
arize_toolkit models performance METRIC ENVIRONMENT [OPTIONS]
```

Pulls a performance metric time-series for a model.

**Arguments**

- `METRIC` — Performance metric name (e.g. `accuracy`, `auc`, `f1`).
- `ENVIRONMENT` — Environment name (e.g. `production`, `training`).

**Options**

- `--model-name` (optional) — Model name.
- `--model-id` (optional) — Model ID.
- `--granularity` — Time granularity: `hour`, `day`, `week`, `month`. Defaults to `month`.
- `--start-time` / `--end-time` (optional) — Time range in ISO format.

**Example**

```bash
arize_toolkit models performance accuracy production --model-name "fraud-detection-v3" --granularity day
arize_toolkit --json models performance auc production --model-name "fraud-detection-v3"
```

______________________________________________________________________

### `models delete-data`

```bash
arize_toolkit models delete-data NAME [--start-time TIME] [--end-time TIME] [--yes]
```

Deletes data from a model within the specified time range. **This is a destructive action** — the CLI will prompt for confirmation unless `--yes` is passed.

**Arguments**

- `NAME` — The model name.

**Options**

- `--start-time` / `--end-time` (optional) — Time range in ISO format.
- `--yes` — Skip the confirmation prompt.

**Example**

```bash
arize_toolkit models delete-data "old-model" --start-time 2024-01-01 --end-time 2024-06-01
```
