# Monitors

## Overview

The `monitors` command group manages Arize monitors — automated checks that track performance, drift, and data-quality metrics and alert when thresholds are breached.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`monitors list`](#monitors-list) | List monitors for a model | `get_all_monitors` |
| [`monitors get`](#monitors-get) | Get a monitor by name | `get_monitor` |
| [`monitors create-performance`](#monitors-create-performance) | Create a performance monitor | `create_performance_monitor` |
| [`monitors create-drift`](#monitors-create-drift) | Create a drift monitor | `create_drift_monitor` |
| [`monitors create-data-quality`](#monitors-create-data-quality) | Create a data quality monitor | `create_data_quality_monitor` |
| [`monitors delete`](#monitors-delete) | Delete a monitor | `delete_monitor` |
| [`monitors copy`](#monitors-copy) | Copy a monitor to another model | `copy_monitor` |
| [`monitors values`](#monitors-values) | Get metric values over time | `get_monitor_metric_values` |
| [`monitors latest-value`](#monitors-latest-value) | Get the latest metric value | `get_latest_monitor_value` |

______________________________________________________________________

### `monitors list`

```bash
arize_toolkit monitors list [--model-name NAME] [--model-id ID] [--category CATEGORY]
```

Lists all monitors for a model. Optionally filter by category.

**Options**

- `--model-name` (optional) — Model name.
- `--model-id` (optional) — Model ID.
- `--category` (optional) — Filter: `drift`, `dataQuality`, or `performance`.

**Example**

```bash
arize_toolkit monitors list --model-name "fraud-detection-v3"
arize_toolkit monitors list --model-name "fraud-detection-v3" --category performance
```

______________________________________________________________________

### `monitors get`

```bash
arize_toolkit monitors get NAME --model MODEL
```

Retrieves detailed information for a single monitor.

**Arguments**

- `NAME` — The monitor name.

**Options**

- `--model` (required) — The model name.

**Example**

```bash
arize_toolkit --json monitors get "accuracy-check" --model "fraud-detection-v3"
```

______________________________________________________________________

### `monitors create-performance`

```bash
arize_toolkit monitors create-performance NAME --model MODEL --environment ENV [OPTIONS]
```

Creates a new performance monitor.

**Arguments**

- `NAME` — Name for the monitor.

**Required Options**

- `--model` — Model name.
- `--environment` — Environment: `tracing`, `production`, `validation`, or `training`.

**Key Options**

- `--performance-metric` — Metric name (e.g. `accuracy`, `auc`). Either this or `--custom-metric-id` is required.
- `--custom-metric-id` — Custom metric ID to monitor.
- `--operator` — Comparison operator: `greaterThan`, `lessThan`, `greaterThanOrEqual`, `lessThanOrEqual`. Defaults to `greaterThan`.
- `--threshold` — Alert threshold value.
- `--std-dev-multiplier` — Standard deviation multiplier. Defaults to `2.0`.
- `--evaluation-window` — Evaluation window in seconds. Defaults to `259200` (3 days).
- `--delay` — Delay in seconds before evaluation. Defaults to `0`.
- `--threshold-mode` — `single` or `double`. Defaults to `single`.
- `--threshold2` / `--operator2` — Second threshold settings (for `double` mode).
- `--email` — Email addresses for notifications (repeatable).
- `--integration-key-id` — Integration key IDs (repeatable).
- `--notes` — Notes for the monitor.

**Example**

```bash
arize_toolkit monitors create-performance "accuracy-alert" \
    --model "fraud-detection-v3" \
    --environment production \
    --performance-metric accuracy \
    --operator lessThan \
    --threshold 0.95 \
    --email "alerts@example.com"
```

______________________________________________________________________

### `monitors create-drift`

```bash
arize_toolkit monitors create-drift NAME --model MODEL [OPTIONS]
```

Creates a new drift monitor.

**Arguments**

- `NAME` — Name for the monitor.

**Required Options**

- `--model` — Model name.

**Key Options**

- `--drift-metric` — Drift metric: `psi`, `js`, `kl`, `ks`, `euclideanDistance`, or `cosineSimilarity`. Defaults to `psi`.
- `--dimension-category` — Category to monitor (e.g. `prediction`, `featureLabel`). Defaults to `prediction`.
- `--dimension-name` — Specific dimension name.
- `--operator`, `--threshold`, `--std-dev-multiplier`, `--evaluation-window`, `--delay`, `--threshold-mode`, `--threshold2`, `--operator2` — Same as performance monitors.
- `--email`, `--integration-key-id`, `--notes` — Notification and documentation options.

**Example**

```bash
arize_toolkit monitors create-drift "prediction-drift" \
    --model "fraud-detection-v3" \
    --drift-metric psi \
    --threshold 0.2
```

______________________________________________________________________

### `monitors create-data-quality`

```bash
arize_toolkit monitors create-data-quality NAME --model MODEL --data-quality-metric METRIC --environment ENV [OPTIONS]
```

Creates a new data quality monitor.

**Arguments**

- `NAME` — Name for the monitor.

**Required Options**

- `--model` — Model name.
- `--data-quality-metric` — Metric name (e.g. `percentEmpty`, `cardinality`, `avg`).
- `--environment` — Environment: `tracing`, `production`, `validation`, or `training`.

**Key Options**

- `--dimension-category` — Category to monitor. Defaults to `prediction`.
- `--dimension-name` — Specific dimension name.
- `--operator`, `--threshold`, `--std-dev-multiplier`, `--evaluation-window`, `--delay`, `--threshold-mode`, `--threshold2`, `--operator2` — Threshold settings.
- `--email`, `--integration-key-id`, `--notes` — Notification and documentation options.

**Example**

```bash
arize_toolkit monitors create-data-quality "null-check" \
    --model "fraud-detection-v3" \
    --data-quality-metric percentEmpty \
    --environment production \
    --operator greaterThan \
    --threshold 0.05
```

______________________________________________________________________

### `monitors delete`

```bash
arize_toolkit monitors delete NAME --model MODEL [--yes]
```

Deletes a monitor. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `NAME` — The monitor name.

**Options**

- `--model` (required) — The model name.
- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit monitors delete "old-monitor" --model "fraud-detection-v3" --yes
```

______________________________________________________________________

### `monitors copy`

```bash
arize_toolkit monitors copy MONITOR_NAME --model MODEL [--new-name NAME] [--new-model MODEL] [--new-space-id ID]
```

Copies a monitor to the same or a different model/space.

**Arguments**

- `MONITOR_NAME` — The source monitor name.

**Options**

- `--model` (required) — Source model name.
- `--new-name` (optional) — Name for the copied monitor.
- `--new-model` (optional) — Target model name.
- `--new-space-id` (optional) — Target space ID.

**Example**

```bash
arize_toolkit monitors copy "accuracy-alert" \
    --model "fraud-detection-v3" \
    --new-model "fraud-detection-v4" \
    --new-name "accuracy-alert-v4"
```

______________________________________________________________________

### `monitors values`

```bash
arize_toolkit monitors values MONITOR_NAME --model MODEL [--granularity GRANULARITY] [--start-time TIME] [--end-time TIME]
```

Fetches the monitor's metric values over time.

**Arguments**

- `MONITOR_NAME` — The monitor name.

**Options**

- `--model` (required) — Model name.
- `--granularity` — Time series granularity: `hour`, `day`, `week`, `month`. Defaults to `hour`.
- `--start-time` / `--end-time` (optional) — Time range in ISO format.

**Example**

```bash
arize_toolkit --json monitors values "accuracy-alert" \
    --model "fraud-detection-v3" \
    --granularity day \
    --start-time 2025-01-01
```

______________________________________________________________________

### `monitors latest-value`

```bash
arize_toolkit monitors latest-value MONITOR_NAME --model MODEL [--granularity GRANULARITY]
```

Returns the most recent metric value, threshold, and timestamp for a monitor.

**Arguments**

- `MONITOR_NAME` — The monitor name.

**Options**

- `--model` (required) — Model name.
- `--granularity` — Granularity: `hour`, `day`, `week`, `month`. Defaults to `hour`.

**Example**

```bash
$ arize_toolkit --json monitors latest-value "accuracy-alert" --model "fraud-detection-v3"
{
  "timestamp": "2025-02-24T12:00:00Z",
  "metric_value": 0.97,
  "threshold_value": 0.95
}
```
