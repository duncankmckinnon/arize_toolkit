# Model Tools

## Overview
In Arize, models reflect the inputs and outputs of your machine learning system.  They are the core unit of observability in Arize.  For more information about models in Arize check out the **[documentation on Arize observability](https://docs.arize.com/arize/machine-learning/machine-learning/what-is-ml-observability)**.

In `arize_toolkit`, the `Client` exposes helpers for:

1. Discovering and retrieving existing models
2. Getting model inference volume over a given time period
3. Deleting model data over a given time period
4. Pulling performance metrics over time
5. Getting a link to the model in the Arize UI

For completeness, the full set of model helpers is repeated below.
Click on the function name to jump to the detailed section.

| Operation | Helper |
|-----------|--------|
| List every model | [`get_all_models`](#get_all_models) |
| Fetch a single model by *name* | [`get_model`](#get_model) |
| Fetch a single model by *id* | [`get_model_by_id`](#get_model_by_id) |
| Quick-link to a model in the UI | [`get_model_url`](#get_model_url) |
| Get traffic volume by *name* | [`get_model_volume`](#get_model_volume) |
| Get traffic volume by *id* | [`get_model_volume_by_id`](#get_model_volume_by_id) |
| Aggregate total traffic | [`get_total_volume`](#get_total_volume) |
| Delete data by *name* | [`delete_data`](#delete_data) |
| Delete data by *id* | [`delete_data_by_id`](#delete_data_by_id) |
| Pull a metric time-series | [`get_performance_metric_over_time`](#get_performance_metric_over_time) |

## Model Operations
The model operations are a collection of tools that help you retrieve information about models.

---

### `get_all_models`
```python
models: list[dict] = client.get_all_models()
```

**Returns**

A list of dictionaries – one per model – containing metadata such as:

* `id` – the canonical identifier for the model
* `name` – the human-readable name shown in the Arize UI
* `createdAt` – the date and time the model was created
* `environment` – the logical environment inside the model

**Example**

```python
for m in client.get_all_models():
  print(f"{m['name']}: {m['id']}")
```

---

### `get_model`
```python
model: dict = client.get_model(model_name: str)
```
**Parameters**

* `model_name` – The *human-readable* name shown in the Arize UI.

**Returns**

A single model record.

* `id` – the canonical identifier for the model
* `name` – the human-readable name shown in the Arize UI
* `createdAt` – the date and time the model was created
* `environment` – the logical environment inside the model

**Example**

```python
fraud_model = client.get_model("fraud-detection-v3")
print(f"Model id={fraud_model['id']}")
```

---

### `get_model_by_id`
```python
model: dict = client.get_model_by_id(model_id: str)
```
This is useful when you have stored the canonical id in a database or CI pipeline.
Most of the object retrieval methods have methods for fetching by id or name.

**Parameters**

* `model_id` – the canonical identifier for the model

**Returns**

A single model record.  

* `id` – the canonical identifier for the model
* `name` – the human-readable name shown in the Arize UI
* `createdAt` – the date and time the model was created
* `environment` – the logical environment inside the model

**Example**   
```python
model = client.get_model_by_id("******")
print(f"Model id={model['id']}")
```

---

### `get_model_url`
```python
url: str = client.get_model_url(model_name: str)
```
Builds a deep-link that opens the model inside the Arize UI – handy for dashboards, Slack
links, or emails.

**Parameters**

* `model_name` – The *human-readable* name shown in the Arize UI.

**Returns**

A URL to the model inside the Arize UI.

**Example**

```python
import webbrowser
from arize_toolkit import Client

client = Client(
organization=os.getenv("ORG"),
space=os.getenv("SPACE"),
arize_developer_key=os.getenv("ARIZE_DEVELOPER_KEY")
)

# Open the model in the Arize UI
webbrowser.open(client.get_model_url("fraud-detection-v3"))
```

---

## Traffic & Volume
Traffic and volume tools are used to get the aggregate number of inferences for a model over a given time period.
These metrics can be used to understand consumption patterns and track usage over time.

All of the traffic and volume tools have a default lookback period of 30 days, but this can be overridden by providing `start_time` and `end_time`. The maximum lookback period will depend on the retention policy of the model.

**Note:** These will only return data about inferences **spans for generative use cases are not included**

---

### `get_model_volume`
```python
count: int = client.get_model_volume(
  model_name: str,
  start_time: str | datetime | None = None,  # optional
  end_time: str | datetime | None = None,    # optional
)
```
Provides the number of inference records stored for the named model in the given interval
(`ISO-8601` date strings or any format accepted by the Arize API).

**Parameters**

* `model_name` – The *human-readable* name shown in the Arize UI.
* `start_time` (optional) – The start of the interval to query. If omitted, the client will look back 30 days from `end_time` (or from *now* if `end_time` is also omitted).
* `end_time` (optional) – The end of the interval to query. If omitted, the current time is used.

**Returns**

The number of inferences for the named model in the given interval.

**Example**

```python
count = client.get_model_volume("fraud-detection-v3", "2024-04-01", "2024-04-30")
print(f"Volume: {count:,}")
```

---

### `get_model_volume_by_id`
```python
count: int = client.get_model_volume_by_id(
  model_id: str,
  start_time: str | datetime | None = None,  # optional
  end_time: str | datetime | None = None,    # optional
)
```
Identical to `get_model_volume` but keyed by `model_id`.

**Parameters**

* `model_id` – the canonical identifier for the model
* `start_time` (optional) – The start of the interval to query. Same defaults as `get_model_volume`.
* `end_time` (optional) – The end of the interval to query. Same defaults as `get_model_volume`.

**Returns**

The number of inferences for the named model in the given interval.

**Example**

```python
count = client.get_model_volume_by_id("******", "2024-04-01", "2024-04-30")
print(f"Volume: {count:,}")
```

---

### `get_total_volume`
```python
total: int, by_model: dict = client.get_total_volume(
  start_time: str | datetime | None = None,  # optional
  end_time: str | datetime | None = None,    # optional
)
```
This is a convenience method that returns the *total* number of inferences across all models in the space and a dict of
model names and their respective inference counts for the given interval.

**Parameters**

* `start_time` (optional) – Start of the aggregation window. Defaults to 30 days ago if both dates are omitted.
* `end_time` (optional) – End of the aggregation window. Defaults to now if omitted.

**Returns**

* `total` – aggregate traffic inside the space
* `by_model` – dict keyed by model name

**Example**

```python
total, by_model = client.get_total_volume("2024-04-01", "2024-04-30")
print(f"Space traffic: {total:,}")
top_models = sorted(by_model.items(), key=lambda x: x[1], reverse=True)
```

---

## Data Deletion

The deletion tools are used to remove specific slices of data from the Arize platform. Often this is used when there is incorrect or malformed data that will disrupt the monitoring for a model. Once the data is deleted you can re-ingest the data for the selected period as needed.

---

### `delete_data`
```python
is_deleted: bool = client.delete_data(
  model_name: str,
  start_time: str | datetime, 
  end_time: str | datetime | None = None,    # optional
  environment: Literal["PRODUCTION", "PREPRODUCTION"] = "PRODUCTION",  # optional
)
```
Deletes all inference records for the named model in the given interval.

**Parameters**

* `model_name` – The *human-readable* name shown in the Arize UI.
* `start_time` – The start of the interval to delete. Accepts a parsable date string or datetime object.
* `end_time` (optional) – The end of the interval to delete. Defaults to the current time.
* `environment` (optional) – Which environment to purge (`"PRODUCTION"` or `"PREPRODUCTION"`). Defaults to `"PRODUCTION"`.

**Returns**

A boolean indicating whether the purge request was accepted and executed by the API. _Note: it may take a few minutes for the records to stop appearing in the UI._

**Example**

```python
success = client.delete_data("fraud-detection-v3", "2024-04-01", "2024-04-30")
if success:
  print("Data deleted ✅")
else:
  print("Data deletion failed ❌")
```

---

### `delete_data_by_id`
```python
is_deleted: bool = client.delete_data_by_id(
  model_id: str,
  start_time: str | datetime, 
  end_time: str | datetime | None = None,    # optional
  environment: Literal["PRODUCTION", "PREPRODUCTION"] = "PRODUCTION",  # optional
)
```
Identical to `delete_data` but keyed by `model_id`.

**Parameters**

* `model_id` – the canonical identifier for the model
* `start_time` – The start of the interval to delete.
* `end_time` (optional) – The end of the interval to delete. Defaults to the current time.
* `environment` (optional) – Which environment to purge (`"PRODUCTION"` or `"PREPRODUCTION"`). Defaults to `"PRODUCTION"`.

**Returns**

A boolean indicating whether the purge request was accepted and executed by the API.

**Example**

```python
success = client.delete_data_by_id("******", "2024-04-01", "2024-04-30")
if success:
  print("Data deleted ✅")
else:
  print("Data deletion failed ❌")    
```

---

## Performance Metrics
The performance metrics tools are used to retrieve time-series data about a model's performance. Arize supports a wide range of metrics for different types of models, including accuracy, F1 score, RMSE, NDCG. Most of the time you can specify the metric name and it will map to the correct metric automatically. 

**Note:** For metrics that aren't supported, we will add custom metric support in a future release.

---

### `get_performance_metric_over_time`
```python
from pandas import DataFrame

performance_metrics: list[dict] | DataFrame = client.get_performance_metric_over_time(
  metric: str,
  environment: str,
  model_id: str | None = None,
  model_name: str | None = None,
  start_time: str | datetime | None = None,
  end_time: str | datetime | None = None,
  granularity: str = "month",  # optional – default
  to_dataframe: bool = True,
)
```

Pulls a time-series of a model's performance metric. The data can either be returned as a list of dictionaries or a `pandas.DataFrame`.  In either case, the data is indexed by timestamp at the requested granularity. 

For this method (and a few others), you can pass either `model_id` or `model_name` to identify the model. If both are provided, `model_id` takes precedence. For tools that allow you to pass in either, using `model_name` will first query the model by name and then use the id in subsequent requests.

**Parameters**

* `metric` – One of Arize's performance metric identifiers (`"accuracy"`, `"f1_score"`, …).
* `environment` – The logical environment inside the model (`"production"`, `"training"`, `"validation"`).
* `model_id` (optional) – The canonical identifier for the model. Must provide either `model_id` **or** `model_name`.
* `model_name` (optional) – The *human-readable* name shown in the Arize UI. Must provide either `model_id` **or** `model_name`.
* `start_time` (optional) – Start of the window to query. If omitted, defaults to 30 days ago.
* `end_time` (optional) – End of the window to query. If omitted, defaults to now.
* `granularity` (optional, default `"month"`) – Bucket size for the time-series (`"hour"`, `"day"`, `"week"`, `"month"`).
* `to_dataframe` (optional, default `True`) – If `True`, wrap the response in a `pandas.DataFrame`; otherwise return a list of dicts.

**Returns**

A list of dictionaries or `pandas.DataFrame` with the following keys or columns:

* `metricDisplayDate` – The timestamp of the metric value
* `metricValue` – The value of the metric

**Example**

```python
from pandas import DataFrame

f1_df = client.get_performance_metric_over_time(
  metric="f1_score",
  environment="production",
  model_id="******",
  start_time="2024-04-01",
  end_time="2024-04-30",
  granularity="day",
  to_dataframe=True
)
f1_df.plot(x="metricDisplayDate", y="metricValue")
```

---

## End-to-End Example

Below is a miniature script that showcases how the model operations can be used in a typical troubleshooting loop:

```python
from arize_toolkit import Client

client = Client(
  organization="my-org",
  space="my-space",
)

model_name = "fraud-detection-v3"

# 1. Confirm the model exists
model = client.get_model(model_name)
print(f"Model ✔ {model['id']}")

# 2. Check traffic last week
vol = client.get_model_volume(model_name, "2024-05-01", "2024-05-08")
print(f"Volume last 7 days: {vol}")

# 3. Pull daily F1 score for the last 7 days as a dataframe
f1_df = client.get_performance_metric_over_time(
  metric="f1_score",
  environment="production",
  model_id=model["id"],
  start_time="2024-05-01",
  end_time="2024-05-08",
  granularity="day",
  to_dataframe=True
)

# 4. Plot the F1 score over time
f1_df.plot(x="metricDisplayDate", y="metricValue")

# 5. Drill into the UI
print(client.get_model_url(model_name))
```

