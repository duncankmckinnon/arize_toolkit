# Custom Metrics

## Overview

The `custom-metrics` command group manages custom metrics — user-defined metric expressions evaluated against model data.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`custom-metrics list`](#custom-metrics-list) | List custom metrics | `get_all_custom_metrics` |
| [`custom-metrics get`](#custom-metrics-get) | Get a metric by name | `get_custom_metric` |
| [`custom-metrics create`](#custom-metrics-create) | Create a custom metric | `create_custom_metric` |
| [`custom-metrics update`](#custom-metrics-update) | Update a custom metric | `update_custom_metric` |
| [`custom-metrics delete`](#custom-metrics-delete) | Delete a custom metric | `delete_custom_metric` |
| [`custom-metrics copy`](#custom-metrics-copy) | Copy a metric to another model | `copy_custom_metric` |

______________________________________________________________________

### `custom-metrics list`

```bash
arize_toolkit custom-metrics list [--model-name NAME]
```

Lists custom metrics. If `--model-name` is provided, lists metrics for that model. If omitted, lists metrics across all models grouped by model name.

**Options**

- `--model-name` (optional) — Filter to a specific model.

**Example**

```bash
# All metrics for a specific model
arize_toolkit custom-metrics list --model-name "fraud-detection-v3"

# All metrics across all models (grouped output)
arize_toolkit custom-metrics list
```

______________________________________________________________________

### `custom-metrics get`

```bash
arize_toolkit custom-metrics get METRIC_NAME --model MODEL
```

Retrieves details for a single custom metric.

**Arguments**

- `METRIC_NAME` — The metric name.

**Options**

- `--model` (required) — The model name.

**Example**

```bash
arize_toolkit --json custom-metrics get "avg-confidence" --model "fraud-detection-v3"
```

______________________________________________________________________

### `custom-metrics create`

```bash
arize_toolkit custom-metrics create METRIC_NAME --metric EXPRESSION --model MODEL [OPTIONS]
```

Creates a new custom metric for a model.

**Arguments**

- `METRIC_NAME` — Name for the metric.

**Required Options**

- `--metric` — The metric expression/formula (e.g. `"select avg(prediction) from model"`).
- `--model` — Model name.

**Optional Options**

- `--environment` — Environment: `tracing`, `production`, `staging`, `development`. Defaults to `production`. For generative use cases, use `tracing`.
- `--description` — Metric description.

**Example**

```bash
arize_toolkit custom-metrics create "avg-confidence" \
    --metric "select avg(prediction_score) from model" \
    --model "fraud-detection-v3" \
    --environment production \
    --description "Average prediction confidence score"
```

______________________________________________________________________

### `custom-metrics update`

```bash
arize_toolkit custom-metrics update METRIC_NAME --model MODEL [OPTIONS]
```

Updates an existing custom metric.

**Arguments**

- `METRIC_NAME` — Current metric name.

**Required Options**

- `--model` — Model name.

**Optional Options**

- `--new-name` — New metric name.
- `--metric` — Updated expression.
- `--description` — Updated description.
- `--environment` — Updated environment.

**Example**

```bash
arize_toolkit custom-metrics update "avg-confidence" \
    --model "fraud-detection-v3" \
    --new-name "avg-pred-confidence" \
    --description "Updated description"
```

______________________________________________________________________

### `custom-metrics delete`

```bash
arize_toolkit custom-metrics delete METRIC_NAME --model MODEL [--yes]
```

Deletes a custom metric. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `METRIC_NAME` — The metric name.

**Options**

- `--model` (required) — Model name.
- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit custom-metrics delete "old-metric" --model "fraud-detection-v3" --yes
```

______________________________________________________________________

### `custom-metrics copy`

```bash
arize_toolkit custom-metrics copy METRIC_NAME --model MODEL [OPTIONS]
```

Copies a custom metric to another model, optionally renaming it.

**Arguments**

- `METRIC_NAME` — The source metric name.

**Required Options**

- `--model` — Source model name.

**Optional Options**

- `--new-model` — Target model name.
- `--new-name` — Name for the copied metric.
- `--new-description` — Description for the copy.
- `--new-environment` — Environment for the copy. Defaults to `production`.

**Example**

```bash
arize_toolkit custom-metrics copy "avg-confidence" \
    --model "fraud-detection-v3" \
    --new-model "fraud-detection-v4" \
    --new-name "avg-confidence-v4"
```
