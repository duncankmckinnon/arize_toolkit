# Monitor Tools

## Overview

Arize monitors allow you to track performance, drift, and data-quality issues in real-time and receive alerts when thresholds are breached. For more information about monitors in Arize check out the **[documentation on Arize monitors](https://docs.arize.com/arize/machine-learning/machine-learning/how-to-ml/monitors)**.

For monitoring operations, the `Client` exposes helpers for:

1. Discovering existing monitors
1. Creating new performance / drift / data-quality monitors
1. Deleting monitors
1. Copying monitors to other models

For completeness, the full set of monitor helpers is repeated below.\
Click any function name to jump to the detailed section.

| Operation | Helper |
|-----------|--------|
| List every monitor for a model | [`get_all_monitors`](#get_all_monitors) |
| Retrieve a monitor by *name* | [`get_monitor`](#get_monitor) |
| Retrieve a monitor by *id* | [`get_monitor_by_id`](#get_monitor_by_id) |
| Quick-link to a monitor in the UI | [`get_monitor_url`](#get_monitor_url) |
| Get monitor metric values over time | [`get_monitor_metric_values`](#get_monitor_metric_values) |
| Get latest monitor metric value | [`get_latest_monitor_value`](#get_latest_monitor_value) |
| Create a **performance** monitor | [`create_performance_monitor`](#create_performance_monitor) |
| Create a **drift** monitor | [`create_drift_monitor`](#create_drift_monitor) |
| Create a **data-quality** monitor | [`create_data_quality_monitor`](#create_data_quality_monitor) |
| Delete by *name* | [`delete_monitor`](#delete_monitor) |
| Delete by *id* | [`delete_monitor_by_id`](#delete_monitor_by_id) |
| Copy a monitor | [`copy_monitor`](#copy_monitor) |

## Monitor Operations

Monitor operations are type agnostic tools for retrieving information about monitors.

______________________________________________________________________

### `get_all_monitors`

```python
monitors: list[dict] = client.get_all_monitors(
    model_name: str | None = None,
    model_id: str | None = None,
    monitor_category: str | None = None,  # "performance", "drift", "dataQuality"
)
```

Fetches details for all monitors associated with a specific model. This function requires either `model_name` or `model_id`.
If both are provided, `model_id` takes precedence.

**Parameters**

- `model_name` (optional) – *Human-readable* model name. Provide **either** `model_id` **or** `model_name`.
- `model_id` (optional) – Canonical model identifier. Provide **either** `model_id` **or** `model_name`.
- `monitor_category` (optional) – Filter by category (`"performance"`, `"drift"`, `"dataQuality"`). If omitted, returns all.

**Returns**

A list of dictionaries, one per monitor. Each dictionary contains the monitor's basic details.

- `id` – the canonical identifier for the monitor
- `name` – the human-readable name shown in the Arize UI
- `createdAt` – the date and time the monitor was created
- `monitorCategory` – the category of the monitor (`"performance"`, `"drift"`, `"dataQuality"`)
- `notes` – the notes for the monitor
- `creator` – the creator of the monitor

**Example**

```python
for m in client.get_all_monitors(
    model_name="fraud-detection-v3", monitor_category="performance"
):
    print(m["name"], m["status"])
```

______________________________________________________________________

### `get_monitor`

```python
monitor: dict = client.get_monitor(
  model_name: str,
  monitor_name: str,
)
```

Retrieves a single monitor by *name*.

**Parameters**

- `model_name` – *Human-readable* model name
- `monitor_name` – Monitor name as shown in the UI

**Returns**

A dictionary containing the monitor's details.

- `id` – the canonical identifier for the monitor
- `name` – the human-readable name shown in the Arize UI
- `createdAt` – the date and time the monitor was created
- `monitorCategory` – the category of the monitor (`"performance"`, `"drift"`, `"dataQuality"`)
- `notes` – the notes for the monitor
- `creator` – the creator of the monitor
- `status` – the status of the monitor
- `threshold` – the threshold value for the monitor
- `operator` – the operator for the monitor
- `thresholdMode` – the mode for the monitor
- `threshold2` – the second threshold value for the monitor
- `operator2` – the second operator for the monitor
- `stdDevMultiplier` – the standard deviation multiplier for the monitor
- `predictionClassValue` – the prediction class value for the monitor
- `positiveClassValue` – the positive class value for the monitor
- `downtimeStart` – the start time for the monitor
- `downtimeDurationHrs` – the duration for the monitor
- `downtimeFrequencyDays` – the frequency for the monitor
- `scheduledRuntimeEnabled` – whether the monitor is scheduled to run
- `scheduledRuntimeCadenceSeconds` – the cadence for the monitor
- `scheduledRuntimeDaysOfWeek` – the days of the week for the monitor
- `evaluationWindowLengthSeconds` – the evaluation window length for the monitor
- `delaySeconds` – the delay for the monitor
- `emailAddresses` – the email addresses for the monitor
  ... other fields omitted due to differing monitor types

**Example**

```python
monitor = client.get_monitor(
    model_name="fraud-detection-v3", monitor_name="Accuracy < 80%"
)
print(monitor)
```

______________________________________________________________________

### `get_monitor_by_id`

```python
monitor: dict = client.get_monitor_by_id(monitor_id: str)
```

Fetches a monitor using its canonical id. This is useful when you have stored the canonical id in a database or CI pipeline.
Most of the object retrieval methods have methods for fetching by id or name.

**Parameters**

- `monitor_id` – Canonical monitor id

**Returns**

A dictionary containing the monitor's details.

- `id` – the canonical identifier for the monitor
- `name` – the human-readable name shown in the Arize UI
- `createdAt` – the date and time the monitor was created
- `monitorCategory` – the category of the monitor (`"performance"`, `"drift"`, `"dataQuality"`)
- `notes` – the notes for the monitor
- `creator` – the creator of the monitor
- `status` – the status of the monitor
- `threshold` – the threshold value for the monitor
- `operator` – the operator for the monitor
- `thresholdMode` – the mode for the monitor
- `threshold2` – the second threshold value for the monitor
- `operator2` – the second operator for the monitor
- `stdDevMultiplier` – the standard deviation multiplier for the monitor
- `predictionClassValue` – the prediction class value for the monitor
- `positiveClassValue` – the positive class value for the monitor
- `downtimeStart` – the start time for the monitor
- `downtimeDurationHrs` – the duration for the monitor
- `downtimeFrequencyDays` – the frequency for the monitor
- `scheduledRuntimeEnabled` – whether the monitor is scheduled to run
- `scheduledRuntimeCadenceSeconds` – the cadence for the monitor
- `scheduledRuntimeDaysOfWeek` – the days of the week for the monitor
- `evaluationWindowLengthSeconds` – the evaluation window length for the monitor
- `delaySeconds` – the delay for the monitor
- `emailAddresses` – the email addresses for the monitor
  ... other fields omitted due to differing monitor types

**Example**

```python
monitor = client.get_monitor_by_id("1234567890")
print(monitor)
```

______________________________________________________________________

### `get_monitor_url`

```python
url: str = client.get_monitor_url(monitor_name: str, model_name: str)
```

Builds a deep-link that opens the monitor in the Arize UI – handy for dashboards or Slack alerts.

**Parameters**

- `monitor_name` – Name of the monitor in the UI
- `model_name` – Name of the model the monitor belongs to

**Returns**

A URL string.

**Example**

```python
url = client.get_monitor_url(
    monitor_name="Accuracy < 80%", model_name="fraud-detection-v3"
)
print(url)
```

______________________________________________________________________

### `get_monitor_metric_values`

```python
result: dict = client.get_monitor_metric_values(
    model_name: str,
    monitor_name: str,
    start_date: datetime | str,
    end_date: datetime | str,
    time_series_data_granularity: str = "hour",  # "hour", "day", "week", "month",
    to_dataframe: bool = False,
)
```

Retrieves historical metric values for a specific monitor over a time range. This is useful for analyzing monitor performance trends and threshold violations over time.

**Parameters**

- `model_name` – *Human-readable* model name
- `monitor_name` – Monitor name as shown in the UI
- `start_date` – Start date for the time range (datetime object or ISO string)
- `end_date` – End date for the time range (datetime object or ISO string)
- `time_series_data_granularity` – Data aggregation granularity. Options: `"hour"`, `"day"`, `"week"`, `"month"`. Default is `"hour"`.
- `to_dataframe` – Whether to return the result as a pandas DataFrame. Default is `False`.

**Returns**

A dictionary containing:

- `key` – The metric key/identifier
- `dataPoints` – List of dictionaries with `x` (timestamp) and `y` (metric value) pairs
- `thresholdDataPoints` – List of dictionaries with `x` (timestamp) and `y` (threshold value) pairs, or `None` if no threshold is set

If `to_dataframe` is `True`, returns a pandas DataFrame with columns:

- `timestamp` – The timestamp of the metric value
- `metric_value` – The metric value
- `threshold_value` – The threshold value (float or None if no threshold is set)

**Example**

```python
# Get hourly metric values for the last 7 days
from datetime import datetime, timedelta

end_date = datetime.now()
start_date = end_date - timedelta(days=7)

result = client.get_monitor_metric_values(
    model_name="fraud-detection-v3",
    monitor_name="Accuracy < 80%",
    start_date=start_date,
    end_date=end_date,
)

# Process the metric values
for point in result["dataPoints"]:
    timestamp = point["x"]
    metric_value = point["y"]
    print(f"{timestamp}: {metric_value}")

# With to_dataframe=True
df = client.get_monitor_metric_values(
    model_name="fraud-detection-v3",
    monitor_name="Accuracy < 80%",
    start_date=start_date,
    end_date=end_date,
    to_dataframe=True,
    time_series_data_granularity="day",
)

# Plot the data
import matplotlib.pyplot as plt

df.plot(x="timestamp", y=["metric_value", "threshold_value"], style=["-", "--"])
plt.title("Monitor Metric Values Over Time")
plt.show()
```

______________________________________________________________________

### `get_latest_monitor_value`

```python
result: dict = client.get_latest_monitor_value(
    model_name: str,
    monitor_name: str,
    time_series_data_granularity: Literal["hour", "day", "week", "month"] = "hour",
)
```

Retrieves the most recent metric value for a specific monitor. This is useful for quickly checking the current state of a monitor without fetching historical data.

**Parameters**

- `model_name` – *Human-readable* model name
- `monitor_name` – Monitor name as shown in the UI
- `time_series_data_granularity` – Data aggregation granularity. Options: `"hour"`, `"day"`, `"week"`, `"month"`. Default is `"hour"`.

**Returns**

A dictionary containing:

- `timestamp` – The timestamp of the latest metric value
- `metric_value` – The latest metric value
- `threshold_value` – The current threshold value (float or None if no threshold is set)

**Example**

```python
# Get the latest value for a performance monitor
result = client.get_latest_monitor_value(
    model_name="fraud-detection-v3",
    monitor_name="Accuracy < 80%",
    time_series_data_granularity="hour",
)

print(f"Latest timestamp: {result['timestamp']}")
print(f"Current value: {result['metric_value']}")
print(f"Threshold: {result['threshold_value']}")

# Check if monitor is currently triggered
if result["metric_value"] > result["threshold_value"]:
    print("Alert! Monitor is currently in triggered state")
```

______________________________________________________________________

## Creating Monitors

The three helpers below share a very large surface-area of parameters – most of which are optional.\
Only the truly required fields are marked as such; everything else can be omitted and will fall back to sensible defaults or be ignored by Arize.

### `create_performance_monitor`

```python
monitor_url: str = client.create_performance_monitor(
  name: str,
  model_name: str,
  model_environment_name: str,              # "production", "validation", "training", "tracing"
  operator: str = "greaterThan",           # optional – comparison for threshold
  performance_metric: str | None = None,   # required *unless* custom_metric_id provided
  custom_metric_id: str | None = None,     # alternative to performance_metric
  notes: str | None = None,
  threshold: float | None = None,
  std_dev_multiplier: float = 2.0,
  prediction_class_value: str | None = None,
  positive_class_value: str | None = None,
  # ––– Alert scheduling / downtime (all optional) –––
  downtime_start: datetime | str | None = None,
  downtime_duration_hrs: int | None = None,
  downtime_frequency_days: int | None = None,
  scheduled_runtime_enabled: bool = False,
  scheduled_runtime_cadence_seconds: int | None = None,
  scheduled_runtime_days_of_week: list[int] | None = None,
  evaluation_window_length_seconds: int = 259200,  # 3 days
  delay_seconds: int = 0,
  # ––– Double threshold mode (optional) –––
  threshold_mode: str = "single",
  threshold2: float | None = None,
  operator2: str | None = None,
  std_dev_multiplier2: float | None = None,
  # ––– Notifications –––
  email_addresses: list[str] | None = None,
  filters: list[dict] | None = None,
)
```

Creates a new performance monitor. Returns a URL path to the newly created monitor.

**Required parameters**

- `name` – Friendly monitor name.
- `model_name` – Model to attach the monitor to.
- `model_environment_name` – Which environment to scope to (`"production"`, …).
- *One of* `performance_metric` *or* `custom_metric_id` *or* `custom_metric_name`.

**Optional parameters**

- `operator` – Comparison operator for the primary threshold. Defaults to `"greaterThan"`.\
  Valid choices include `"greaterThan"`, `"lessThan"`, `"equalTo"`, `"greaterThanOrEqualTo"`, and `"lessThanOrEqualTo"`.
- `notes` – Free-form notes or run-book link for the monitor.
- `threshold` – Static numeric threshold that triggers an alert when crossed.\
  If omitted, Arize derives a dynamic threshold using `std_dev_multiplier`.
- `std_dev_multiplier` – Number of standard deviations to use when computing the dynamic threshold.\
  Default is `2.0`.
- `prediction_class_value` – For multi-class classification, the specific prediction class to evaluate.
- `positive_class_value` – The label to treat as the positive class when computing binary metrics.
- `custom_metric_id` – ID of a custom metric to evaluate instead of a built-in performance metric.
- `custom_metric_name` – Name of a custom metric to evaluate instead of a built-in performance metric.
- `downtime_start` – Datetime or parseable string marking the start of a recurring downtime window.
- `downtime_duration_hrs` – Duration, in hours, of each downtime window.
- `downtime_frequency_days` – Number of days between successive downtime windows.
- `scheduled_runtime_enabled` – Run the monitor on a fixed schedule rather than continuously.\
  Defaults to `False`.
- `scheduled_runtime_cadence_seconds` – Period (in seconds) between scheduled evaluations\
  (effective only when `scheduled_runtime_enabled` is `True`).
- `scheduled_runtime_days_of_week` – List of ISO weekday numbers (`1` = Mon … `7` = Sun) on which the monitor may run.
- `evaluation_window_length_seconds` – Size of the rolling aggregation window.\
  Default is `259 200` s (3 days).
- `delay_seconds` – How long to wait before evaluating newly-arrived data (to accommodate ingestion lag).\
  Default is `0`.
- `threshold_mode` – `"single"` (default) for a one-sided threshold or `"double"` for upper & lower bounds.
- `threshold2` – Secondary threshold value used when `threshold_mode` is `"double"`.
- `operator2` – Comparison operator for the secondary threshold.
- `std_dev_multiplier2` – Standard-deviation multiplier for the secondary adaptive threshold.
- `email_addresses` – List of email addresses that should receive alert notifications. Currently only supports direct email alerting, not other integrations.
- `filters` – List of filters to apply to the monitor.

**Returns**

A URL path to the newly created monitor.

**Example**

```python
monitor_url = client.create_performance_monitor(
    name="Accuracy < 80%",
    model_name="fraud-detection-v3",
    model_environment_name="production",
    performance_metric="accuracy",
    threshold=0.8,
)
print("Created:", monitor_url)
```

______________________________________________________________________

### `create_drift_monitor`

```python
monitor_url: str = client.create_drift_monitor(
  name: str,
  model_name: str,
  drift_metric: str = "psi",              # "psi", "js", "kl", "ks" …
  dimension_category: str = "prediction", # or "featureLabel", etc.
  operator: str = "greaterThan",
  dimension_name: str | None = None,       # not needed for prediction drift
  notes: str | None = None,
  threshold: float | None = None,
  std_dev_multiplier: float = 2.0,
  prediction_class_value: str | None = None,
  positive_class_value: str | None = None,
  downtime_start: datetime | str | None = None,
  downtime_duration_hrs: int | None = None,
  downtime_frequency_days: int | None = None,
  scheduled_runtime_enabled: bool = False,
  scheduled_runtime_cadence_seconds: int | None = None,
  scheduled_runtime_days_of_week: list[int] | None = None,
  evaluation_window_length_seconds: int = 259200,  # 3 days
  delay_seconds: int = 0,
  email_addresses: list[str] | None = None,
  filters: list[dict] | None = None,
)
```

Creates a new drift monitor. Returns a URL path to the newly created monitor.

**Required parameters**

- `name` – Friendly monitor name.
- `model_name` – Model to attach the monitor to.
- `drift_metric` – Metric to monitor (`"psi"`, `"js"`, `"kl"`, `"ks"`).
- `dimension_category` – Category of the dimension to monitor (`"prediction"`, `"featureLabel"`, etc.).

**Optional parameters**

- `operator` – Comparison operator for the primary threshold. Defaults to `"greaterThan"`.\
  Valid choices include `"greaterThan"`, `"lessThan"`, `"equalTo"`, `"greaterThanOrEqualTo"`, and `"lessThanOrEqualTo"`.
- `dimension_name` – Name of the dimension to monitor. Not needed for prediction drift.
- `notes` – Free-form notes or run-book link for the monitor.
- `threshold` – Static numeric threshold that triggers an alert when crossed.\
  If omitted, Arize derives a dynamic threshold using `std_dev_multiplier`.
- `std_dev_multiplier` – Number of standard deviations to use when computing the dynamic threshold.\
  Default is `2.0`.
- `prediction_class_value` – For multi-class classification, the specific prediction class to evaluate.
- `positive_class_value` – The label to treat as the positive class when computing binary metrics.
- `downtime_start` – Datetime or parseable string marking the start of a recurring downtime window.
- `downtime_duration_hrs` – Duration, in hours, of each downtime window.
- `downtime_frequency_days` – Number of days between successive downtime windows.
- `scheduled_runtime_enabled` – Run the monitor on a fixed schedule rather than continuously.\
  Defaults to `False`.
- `scheduled_runtime_cadence_seconds` – Period (in seconds) between scheduled evaluations\
  (effective only when `scheduled_runtime_enabled` is `True`).
- `scheduled_runtime_days_of_week` – List of ISO weekday numbers (`1` = Mon … `7` = Sun) on which the monitor may run.
- `evaluation_window_length_seconds` – Size of the rolling aggregation window.\
  Default is `259 200` s (3 days).
- `delay_seconds` – How long to wait before evaluating newly-arrived data (to accommodate ingestion lag).\
  Default is `0`.
- `email_addresses` – List of email addresses that should receive alert notifications. Currently only supports direct email alerting, not other integrations.
- `filters` – List of filters to apply to the monitor.

**Returns**

A URL path to the newly created monitor.

**Example**

```python
monitor_url = client.create_drift_monitor(
    name="PSI > 0.2",
    model_name="fraud-detection-v3",
    drift_metric="psi",
    dimension_category="prediction",
    operator="greaterThan",
)
print("Created:", monitor_url)
```

______________________________________________________________________

### `create_data_quality_monitor`

```python
monitor_url: str = client.create_data_quality_monitor(
  name: str,
  model_name: str,
  data_quality_metric: str,                # e.g. "percentEmpty", "cardinality"
  model_environment_name: str,
  operator: str = "greaterThan",
  dimension_category: str = "prediction",
  notes: str | None = None,
  threshold: float | None = None,
  std_dev_multiplier: float = 2.0,
  prediction_class_value: str | None = None,
  positive_class_value: str | None = None,
  downtime_start: datetime | str | None = None,
  downtime_duration_hrs: int | None = None,
  downtime_frequency_days: int | None = None,
  scheduled_runtime_enabled: bool = False,
  scheduled_runtime_cadence_seconds: int | None = None,
  scheduled_runtime_days_of_week: list[int] | None = None,
  evaluation_window_length_seconds: int = 259200,  # 3 days
  delay_seconds: int = 0,
  email_addresses: list[str] | None = None,
  filters: list[dict] | None = None,
)
```

Creates a data-quality monitor. Returns a URL path to the newly created monitor.

**Required parameters**

- `name` – Friendly monitor name.
- `model_name` – Model to attach the monitor to.
- `data_quality_metric` – Metric to monitor (`"percentEmpty"`, `"cardinality"`, etc.).
- `model_environment_name` – Which environment to scope to (`"production"`, …).

**Optional parameters**

- `operator` – Comparison operator for the primary threshold. Defaults to `"greaterThan"`.\
  Valid choices include `"greaterThan"`, `"lessThan"`, `"equalTo"`, `"greaterThanOrEqualTo"`, and `"lessThanOrEqualTo"`.
- `dimension_category` – Category of the dimension to monitor (`"prediction"`, `"featureLabel"`, etc.).
- `notes` – Free-form notes or run-book link for the monitor.
- `threshold` – Static numeric threshold that triggers an alert when crossed.\
  If omitted, Arize derives a dynamic threshold using `std_dev_multiplier`.
- `std_dev_multiplier` – Number of standard deviations to use when computing the dynamic threshold.\
  Default is `2.0`.
- `prediction_class_value` – For multi-class classification, the specific prediction class to evaluate.
- `positive_class_value` – The label to treat as the positive class when computing binary metrics.
- `downtime_start` – Datetime or parseable string marking the start of a recurring downtime window.
- `downtime_duration_hrs` – Duration, in hours, of each downtime window.
- `downtime_frequency_days` – Number of days between successive downtime windows.
- `scheduled_runtime_enabled` – Run the monitor on a fixed schedule rather than continuously.\
  Defaults to `False`.
- `scheduled_runtime_cadence_seconds` – Period (in seconds) between scheduled evaluations\
  (effective only when `scheduled_runtime_enabled` is `True`).
- `scheduled_runtime_days_of_week` – List of ISO weekday numbers (`1` = Mon … `7` = Sun) on which the monitor may run.
- `evaluation_window_length_seconds` – Size of the rolling aggregation window.
- `delay_seconds` – How long to wait before evaluating newly-arrived data (to accommodate ingestion lag).
- `email_addresses` – List of email addresses that should receive alert notifications. Currently only supports direct email alerting, not other integrations.
- `filters` – List of filters to apply to the monitor.

**Returns**

A URL path to the newly created monitor.

**Example**

```python
monitor_url = client.create_data_quality_monitor(
    name="Data Quality",
    model_name="fraud-detection-v3",
    data_quality_metric="percentEmpty",
    model_environment_name="production",
    operator="greaterThan",
    dimension_category="prediction",
)
print("Created:", monitor_url)
```

______________________________________________________________________

## Deleting Monitors

### `delete_monitor`

```python
is_deleted: bool = client.delete_monitor(
  monitor_name: str,
  model_name: str,
)
```

Deletes a monitor by *name* and returns a boolean indicating success.

**Parameters**

- `monitor_name` – Name of the monitor to delete
- `model_name` – Name of the model the monitor belongs to

**Returns**

`True` if the monitor was deleted, `False` otherwise.

**Example**

```python
is_deleted = client.delete_monitor(
    monitor_name="Accuracy < 80%", model_name="fraud-detection-v3"
)
print("Deleted:", is_deleted)
```

______________________________________________________________________

### `delete_monitor_by_id`

```python
is_deleted: bool = client.delete_monitor_by_id(monitor_id: str)
```

Deletes a monitor by canonical id. For use when you have stored the canonical id in a database or CI pipeline.

**Parameters**

- `monitor_id` – Canonical id of the monitor to delete

**Returns**

`True` if the monitor was deleted, `False` otherwise.

**Example**

```python
is_deleted = client.delete_monitor_by_id("1234567890")
print("Deleted:", is_deleted)
```

______________________________________________________________________

## Copying Monitors

This method can also be used to change specific fields of a monitor, while maintaining the rest when the monitor is copied. This can be useful when you are adding monitors for multiple features, but you want to have specific settings used for each. In this scenario you can create the monitor for the first feature, and then copy everything but the name and the feature to any other features you need to monitor.

### `copy_monitor`

```python
new_monitor_url: str = client.copy_monitor(
  current_monitor_name: str,
  current_model_name: str,
  new_monitor_name: str | None = None,
  new_model_name: str | None = None,
  new_space_id: str | None = None,
  # Any field from the original monitor can be overridden via **kwargs
)
```

Copies an existing monitor, optionally overriding fields. If `new_model_name` is not provided, the monitor is created in the same model using any provided `new_monitor_name` and any overridden fields. If `new_monitor_name` is not provided, the new monitor will use the same name as the original monitor.

**Parameters**

- `current_monitor_name` – Name of the monitor to copy
- `current_model_name` – Name of the model the monitor belongs to
- `new_monitor_name` – Name of the new monitor
- `new_model_name` – Name of the new model
- `new_space_id` – ID of the space to copy the monitor to
- `**kwargs` – Any field from the original monitor can be overridden by passing in the field name and new value.

**Returns**

A URL path to the newly created monitor.

**Example**

```python
# Create a drift monitor for feature1
drift_monitor_url = client.create_drift_monitor(
    name="feature1 PSI > 0.259",
    model_name="fraud-detection-v3",
    drift_metric="psi",
    dimension_category="featureLabel",
    dimension_name="feature1",
    operator="greaterThan",
    threshold=0.259,
)

# Copy the monitor for feature2
new_monitor_url = client.copy_monitor(
    current_monitor_name="feature1 PSI > 0.259",
    current_model_name="fraud-detection-v3",
    new_monitor_name="feature2 PSI > 0.259",
    dimension_name="feature2",
)
```

______________________________________________________________________

## End-to-End Example

Below is a miniature script that showcases how the monitor operations can be used to setup a basic monitoring system:

```python
from arize_toolkit import Client

client = Client(
    organization="my-org",
    space="my-space",
)

# 1. Delete any existing monitors
for m in client.get_all_monitors(
    model_name="fraud-detection-v3", monitor_category="drift"
):
    client.delete_monitor(monitor_name=m["name"], model_name="fraud-detection-v3")


# 2. Create a basic performance monitor
performance_monitor_url = client.create_performance_monitor(
    name="Accuracy < 80%",
    model_name="fraud-detection-v3",
    model_environment_name="production",
    performance_metric="accuracy",
    threshold=0.8,
    email_addresses=["alerts@my-org.com"],
)

# 3. Create a basic data-quality monitor
data_quality_monitor_url = client.create_data_quality_monitor(
    name="Data Quality",
    model_name="fraud-detection-v3",
    data_quality_metric="percentEmpty",
    model_environment_name="production",
    operator="greaterThan",
    dimension_category="prediction",
    email_addresses=["alerts@my-org.com"],
)

# 4. Create a basic drift monitor
prediction_drift_monitor_url = client.create_drift_monitor(
    name="PSI > 0.2",
    model_name="fraud-detection-v3",
    drift_metric="psi",
    dimension_category="prediction",
    operator="greaterThan",
    threshold=0.2,
    email_addresses=["alerts@my-org.com"],
)

# 5. Copy the drift monitor for a feature
feature_drift_monitor_url = client.copy_monitor(
    current_monitor_name="PSI > 0.2",
    current_model_name="fraud-detection-v3",
    new_monitor_name="feature PSI > 0.2",
    dimension_category="featureLabel",
    dimension_name="feature",
)

# 6. Print the monitor URLs
print(f"Performance monitor: {performance_monitor_url}")
print(f"Data quality monitor: {data_quality_monitor_url}")
print(f"Prediction drift monitor: {prediction_drift_monitor_url}")
print(f"Feature drift monitor: {feature_drift_monitor_url}")
```
