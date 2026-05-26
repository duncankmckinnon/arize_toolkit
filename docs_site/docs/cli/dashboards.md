# Dashboards

## Overview

The `dashboards` command group manages Arize dashboards — customizable views that aggregate charts, metrics, and model information into a single page.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`dashboards list`](#dashboards-list) | List all dashboards | `get_all_dashboards` |
| [`dashboards get`](#dashboards-get) | Get a dashboard by name | `get_dashboard` |
| [`dashboards create`](#dashboards-create) | Create an empty dashboard | `create_dashboard` |
| [`dashboards create-volume`](#dashboards-create-volume) | Create a model volume dashboard | `create_model_volume_dashboard` |

______________________________________________________________________

### `dashboards list`

```bash
arize_toolkit dashboards list
```

Lists all dashboards in the current space.

**Example**

```bash
$ arize_toolkit dashboards list
                  Dashboards
┌──────────┬──────────────────┬────────────┐
│ id       │ name             │ createdAt  │
├──────────┼──────────────────┼────────────┤
│ d1       │ Model Overview   │ 2025-01-10 │
│ d2       │ Weekly Report    │ 2025-02-01 │
└──────────┴──────────────────┴────────────┘
```

______________________________________________________________________

### `dashboards get`

```bash
arize_toolkit dashboards get NAME
```

Retrieves a dashboard and all its widgets (line charts, bar charts, statistics, text).

**Arguments**

- `NAME` — The dashboard name.

**Example**

```bash
arize_toolkit --json dashboards get "Model Overview"
```

______________________________________________________________________

### `dashboards create`

```bash
arize_toolkit dashboards create NAME
```

Creates a new empty dashboard and returns its URL.

**Arguments**

- `NAME` — Name for the dashboard.

**Example**

```bash
$ arize_toolkit dashboards create "Q1 Report"
Created dashboard: https://app.arize.com/.../dashboards/abc123
```

______________________________________________________________________

### `dashboards create-volume`

```bash
arize_toolkit dashboards create-volume NAME [--model MODEL]...
```

Creates a dashboard pre-populated with line chart widgets showing prediction volume for each specified model. If no models are specified, includes all models in the space.

**Arguments**

- `NAME` — Name for the dashboard.

**Options**

- `--model` (optional) — Model names to include (repeatable). If omitted, all models in the space are included.

**Example**

```bash
# Dashboard for specific models
arize_toolkit dashboards create-volume "Volume Report" \
    --model "fraud-detection-v3" \
    --model "chatbot-prod"

# Dashboard for all models in the space
arize_toolkit dashboards create-volume "All Models Volume"
```
