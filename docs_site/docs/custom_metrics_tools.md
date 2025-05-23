# Custom Metrics Tools

## Overview

Custom metrics allow you to define bespoke SQL-like aggregations (e.g. `SELECT avg(prediction) FROM model`) and surface them across Arize. They are particularly useful when the built-in metrics do not capture a domain-specific definition of performance or quality. Use **[these reference documents](https://docs.arize.com/arize/machine-learning/machine-learning/how-to-ml/custom-metrics-api/custom-metric-syntax)** to understand the syntax of the SQL expressions in Arize Custom Metrics.

`arize-toolkit` exposes helpers for:

1. Discovering existing custom metrics
1. Creating new metrics
1. Updating or deleting metrics
1. Copying metrics between models

| Operation | Helper |
|-----------|--------|
| List every custom metric (space-wide) | [`get_all_custom_metrics`](#get_all_custom_metrics) |
| List metrics for a single model | [`get_all_custom_metrics_for_model`](#get_all_custom_metrics_for_model) |
| Retrieve a metric by *name* | [`get_custom_metric`](#get_custom_metric) |
| Retrieve a metric by *id* | [`get_custom_metric_by_id`](#get_custom_metric_by_id) |
| Quick-link to a metric in the UI | [`get_custom_metric_url`](#get_custom_metric_url) |
| Create a metric | [`create_custom_metric`](#create_custom_metric) |
| Update by *name* | [`update_custom_metric`](#update_custom_metric) |
| Update by *id* | [`update_custom_metric_by_id`](#update_custom_metric_by_id) |
| Delete by *name* | [`delete_custom_metric`](#delete_custom_metric) |
| Delete by *id* | [`delete_custom_metric_by_id`](#delete_custom_metric_by_id) |
| Copy a metric to another model | [`copy_custom_metric`](#copy_custom_metric) |

______________________________________________________________________

## Custom Metrics Operations

These operations can be used to retrieve information about custom metrics.

### `get_all_custom_metrics`

```python
all_metrics: dict | list[dict] = client.get_all_custom_metrics(model_name: str | None = None)
```

If `model_name` is omitted the method iterates over **every** model in the space and returns

```python
{
    "model_name": [
        # list of metrics for the model
        {
            "id": "******",
            "name": "metric_name",
            "description": "metric_description",
            "metric": "SELECT avg(prediction) FROM model",
            "requiresPositiveClass": True,
            "createdAt": "2021-01-01T00:00:00Z",
        },
        ...,
    ]
}
```

When `model_name` is provided the return value is instead the list of metric dictionaries for the given model.

**Parameters**

- `model_name` – (optional) *Human-readable* model name. If omitted all models are scanned.

**Returns**

Either a list of metric dictionaries **or** a dict keyed by model name.

Each metric dictionary contains:

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
# list metrics for one model
for m in client.get_all_custom_metrics(model_name="fraud-detection-v3"):
    print(f"{m['name']}: {m['metric']}")

# space-wide inventory
space_metrics = client.get_all_custom_metrics()
print(f"Models with metrics: {space_metrics.keys()}")
```

______________________________________________________________________

### `get_all_custom_metrics_for_model`

```python
metrics: list[dict] = client.get_all_custom_metrics_for_model(
    model_name: str | None = None,
    model_id: str | None = None,
)
```

**Parameters**

- `model_name` – (optional) *Human-readable* model name. Must provide **either** `model_name` **or** `model_id`.
- `model_id` – (optional) Canonical model id. Must provide **either** `model_name` **or** `model_id`.

**Returns**

List of metric dictionaries

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
metrics = client.get_all_custom_metrics_for_model(model_name="fraud-detection-v3")
print(metrics)
```

______________________________________________________________________

### `get_custom_metric`

```python
metric: dict = client.get_custom_metric(
    model_name: str,
    metric_name: str,
)
```

Fetches a metric by *name* within a given model.

**Parameters**

- `model_name` – *Human-readable* model name
- `metric_name` – Metric name (case-sensitive)

**Returns**

A dictionary representing the metric.

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
metric = client.get_custom_metric(
    model_name="fraud-detection-v3", metric_name="is_fraud_like"
)
print(metric)
```

______________________________________________________________________

### `get_custom_metric_by_id`

```python
metric: dict = client.get_custom_metric_by_id(custom_metric_id: str)
```

Retrieve a metric using its canonical id.

**Parameters**

- `custom_metric_id` – Canonical metric id

**Returns**

A dictionary representing the metric.

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
metric = client.get_custom_metric_by_id("******")
print(metric)
```

______________________________________________________________________

### `get_custom_metric_url`

```python
url: str = client.get_custom_metric_url(model_name: str, metric_name: str)
```

Returns a deep-link to the metric inside the Arize UI.

**Parameters**

- `model_name` – *Human-readable* model name
- `metric_name` – Metric name

**Returns**

A string URL.

**Example**

```python
url = client.get_custom_metric_url(
    model_name="fraud-detection-v3", metric_name="is_fraud_like"
)
print(url)
```

______________________________________________________________________

## Creating and Updating Custom Metrics

These helpers are used to create and modify custom metrics.

### `create_custom_metric`

```python
metric_url: str = client.create_custom_metric(
    metric: str,                       # SQL expression e.g. "SELECT avg(prediction) FROM model"
    metric_name: str,
    model_name: str | None = None,
    model_id: str | None = None,
    metric_description: str | None = None,
    metric_environment: str | None = None,   # "production", "staging", "development"
)
```

Creates a new metric and returns a UI path to it.

**Parameters**

- `metric` – SQL expression / formula. (format is `SELECT <formula> FROM model` - `model` is a reserved keyword that must be present)
- `metric_name` – Friendly name shown in the UI.
- `model_name` – *Human-readable* model name. Must provide **either** `model_name` **or** `model_id`.
- `model_id` – Canonical model id. Must provide **either** `model_name` **or** `model_id`.
- `metric_description` – (optional) Free-text description.
- `metric_environment` – (optional) Environment label; defaults to `"production"`.

**Example**

```python
url = client.create_custom_metric(
    metric="SELECT avg(latency) FROM model",
    metric_name="Average latency",
    model_name="fraud-detection-v3",
    metric_description="Mean latency over all predictions",
)
print("Created at:", url)
```

______________________________________________________________________

### `update_custom_metric`

```python
updated: dict = client.update_custom_metric(
    custom_metric_name: str,
    model_name: str,
    name: str | None = None,
    metric: str | None = None,
    description: str | None = None,
    environment: str | None = None,
)
```

Same as the *by-id* variant but performs the lookup for you.

**Parameters**

- `custom_metric_name` – Metric name
- `model_name` – *Human-readable* model name
- `name` – (optional) New metric name
- `metric` – (optional) New SQL expression
- `description` – (optional) New description
- `environment` – (optional) New environment label

**Returns**

A dictionary representing the updated metric.

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
updated = client.update_custom_metric(
    custom_metric_name="P95 prediction",
    model_name="fraud-detection-v3",
    description="95th percentile of prediction value",
)
```

______________________________________________________________________

### `update_custom_metric_by_id`

```python
updated: dict = client.update_custom_metric_by_id(
    custom_metric_id: str,
    model_id: str,
    name: str | None = None,
    metric: str | None = None,
    description: str | None = None,
    environment: str | None = None,
)
```

Any field left as `None` retains its previous value.

**Parameters**

- `custom_metric_id` – Metric id
- `model_id` – Canonical model id
- `name` – (optional) New metric name
- `metric` – (optional) New SQL expression
- `description` – (optional) New description
- `environment` – (optional) New environment label

**Returns**

A dictionary representing the updated metric.

- `id` – Canonical metric id
- `name` – Metric name
- `description` – Free-text description
- `metric` – SQL formula / expression
- `requiresPositiveClass` – Whether the metric requires a positive-class label
- `createdAt` – Datetime created

**Example**

```python
updated = client.update_custom_metric_by_id(
    custom_metric_id="******",
    model_id="******",
    description="95th percentile of prediction value",
)
```

______________________________________________________________________

## Deleting Custom Metrics

These helpers are used to delete custom metrics.

### `delete_custom_metric`

```python
is_deleted: bool = client.delete_custom_metric(
    model_name: str,
    metric_name: str,
)
```

Convenience wrapper that performs lookup then delegates to `delete_custom_metric_by_id`.

**Parameters**

- `model_name` – *Human-readable* model name
- `metric_name` – Metric name

**Returns**

`True` when deletion succeeds.

**Example**

```python
is_deleted = client.delete_custom_metric(
    model_name="fraud-detection-v3",
    metric_name="P95 prediction",
)
print(f"Deleted: {is_deleted}")
```

______________________________________________________________________

### `delete_custom_metric_by_id`

```python
is_deleted: bool = client.delete_custom_metric_by_id(
    custom_metric_id: str,
    model_id: str,
)
```

Deletes by canonical id.

**Parameters**

- `custom_metric_id` – Metric id
- `model_id` – Canonical model id

**Returns**

`True` when deletion succeeds.

**Example**

```python
client.delete_custom_metric_by_id(
    custom_metric_id="******",
    model_id="******",
)
print(f"Deleted: {is_deleted}")
```

______________________________________________________________________

## Copying Custom Metrics

These helpers are used to copy custom metrics between models. These methods are useful when you need to keep the definition of a metric but use it across different models.

When copying a metric, you can choose to change the name, environment, or description of the new metric, or keep all properties the same by omitting the optional parameters.

### `copy_custom_metric`

```python
new_metric_url: str = client.copy_custom_metric(
    current_metric_name: str,
    current_model_name: str,
    new_model_name: str | None = None,
    new_model_id: str | None = None,
    new_metric_name: str | None = None,
    new_metric_description: str | None = None,
    new_model_environment: str = "production",
)
```

Copies a metric from one model to another. Must provide either `new_model_name` or `new_model_id` to specify the destination model (cannot copy the same metric to the same model).

**Parameters**

- `current_metric_name` – Name of the metric to copy
- `current_model_name` – Source model name
- `new_model_name` (optional) – Destination model name. Must provide either `new_model_name` or `new_model_id`.
- `new_model_id` (optional) – Destination model id. Must provide either `new_model_name` or `new_model_id`.
- `new_metric_name` (optional) – Name for the new metric (defaults to original)
- `new_metric_description` (optional) – Override the description
- `new_model_environment` (optional) – Environment label for the new metric

**Returns**

A URL path to the newly created metric.

**Example**

```python
url = client.copy_custom_metric(
    current_metric_name="avg_latency",
    current_model_name="fraud-detection-v3",
    new_model_name="fraud-detection-v4",
    new_metric_name="avg_latency_v4",
)
print(url)
```

______________________________________________________________________

## End-to-End Example

```python
from arize_toolkit import Client

client = Client(
    organization="my-org",
    space="my-space",
)

# create metric
metric_url = client.create_custom_metric(
    metric="SELECT percentile(prediction, 0.95) FROM model",
    metric_name="P95 prediction",
    model_name="fraud-detection-v3",
)
print(metric_url)

# list metrics for the model
print(client.get_all_custom_metrics_for_model(model_name="fraud-detection-v3"))

# update the metric description
updated_metric = client.update_custom_metric(
    custom_metric_name="P95 prediction",
    model_name="fraud-detection-v3",
    description="95th percentile of prediction value",
)
print(updated_metric)

# delete the metric
client.delete_custom_metric(
    model_name="fraud-detection-v3",
    metric_name="P95 prediction",
)
```
