# Model Operations

### Overview

The `Client` class exposes a small, composable API for reading, writing, and analysing **model
level** information in an Arize Space.  
This page documents every model-related helper that ships with
`arize-toolkit`, grouped by the day-to-day questions that arise when you are operating an ML
system:

1. “What models do I have, and where are they?”  
2. “How much traffic have they processed?”  
3. “Can I delete a slice of data?”  
4. “What does performance look like over time?”

For completeness, the full set of model helpers is repeated below.  
Click any function name to jump to the detailed section.

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

### Setup

Before you can use any of the toolkit operations, you need to initialize a `Client` object.
Remember that you can set a `sleep_time` parameter to control the rate at which the toolkit
makes requests to the Arize API. This is useful if you are making a large number of requests in a
short period of time, or getting rate limited by the API.

```python
from arize_toolkit import Client

client = Client(
    organization=os.getenv("ORG"),
    space=os.getenv("SPACE"),
    arize_developer_key=os.getenv("ARIZE_DEVELOPER_KEY")
)
```

### Model Operations

#### `get_all_models`
```python
models: list[dict] = client.get_all_models()
```
**Returns**  
A list of dictionaries – one per model – containing metadata such as:
* `id` – the canonical identifier for the model
* `name` – the human-readable name shown in the Arize UI
* `createdAt` – the date and time the model was created
* `environment` – the logical environment inside the model

**Example usage**
```python
for m in client.get_all_models():
    print(f"{m['name']}: {m['id']}")
```

---

#### `get_model`
```python
model: dict = client.get_model(model_name: str)
```
* **Parameters**
  * `model_name` – The *human-readable* name shown in the Arize UI.

* **Returns**  
  A single model record.  
  * `id` – the canonical identifier for the model
  * `name` – the human-readable name shown in the Arize UI
  * `createdAt` – the date and time the model was created
  * `environment` – the logical environment inside the model

* **Example**
  ```python
  fraud_model = client.get_model("fraud-detection-v3")
  print(f"Model id={fraud_model['id']}")
  ```

---

#### `get_model_by_id`
```python
model: dict = client.get_model_by_id(model_id: str)
```
This is useful when you have stored the canonical id in a database or CI pipeline.
Most of the object retrieval methods have methods for fetching by id or name.

* **Parameters**
  * `model_id` – the canonical identifier for the model

* **Returns**  
  A single model record.  
  * `id` – the canonical identifier for the model
  * `name` – the human-readable name shown in the Arize UI
  * `createdAt` – the date and time the model was created
  * `environment` – the logical environment inside the model

* **Example**
  ```python
  model = client.get_model_by_id("******")
  print(f"Model id={model['id']}")
  ```

---

#### `get_model_url`
```python
url: str = client.get_model_url(model_name: str)
```
Builds a deep-link that opens the model inside the Arize UI – handy for dashboards, Slack
links, or emails.

* **Parameters**
  * `model_name` – The *human-readable* name shown in the Arize UI.

* **Returns**  
  A URL to the model inside the Arize UI.

* **Example**
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

### Traffic & Volume

#### `get_model_volume`
```python
count: int = client.get_model_volume(
    model_name: str,
    start_time: str | datetime,
    end_time: str | datetime,
)
```
Provides the number of inference records stored for the named model in the given interval
(`ISO-8601` date strings or any format accepted by the Arize API).

* **Parameters**
  * `model_name` – The *human-readable* name shown in the Arize UI.
  * `start_time` – The start of the interval to query. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to query. Can be a string in a parsable format or a datetime object.

* **Returns**  
  The number of inferences for the named model in the given interval.

* **Example**
  ```python
  count = client.get_model_volume("fraud-detection-v3", "2024-04-01", "2024-04-30")
  print(f"Volume: {count:,}")
  ```

---

#### `get_model_volume_by_id`
```python
count: int = client.get_model_volume_by_id(
    model_id: str,
    start_time: str | datetime,
    end_time: str | datetime,
)
```
Identical to `get_model_volume` but keyed by `model_id`.

* **Parameters**
  * `model_id` – the canonical identifier for the model
  * `start_time` – The start of the interval to query. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to query. Can be a string in a parsable format or a datetime object.

* **Returns**  
  The number of inferences for the named model in the given interval.

* **Example**
  ```python
  count = client.get_model_volume_by_id("******", "2024-04-01", "2024-04-30")
  print(f"Volume: {count:,}")
  ```

---

#### `get_total_volume`
```python
total: int, by_model: dict = client.get_total_volume(
    start_time: str | datetime,
    end_time: str | datetime,
)
```
This is a convenience method that returns the *total* number of inferences across all models in the space and a dict of
model names and their respective inference counts for the given interval.

* **Parameters**
  * `start_time` – The start of the interval to query. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to query. Can be a string in a parsable format or a datetime object.

* **Returns**
  1. `total` – aggregate traffic inside the space
  2. `by_model` – dict keyed by model name

* **Example**
  ```python
  total, by_model = client.get_total_volume("2024-04-01", "2024-04-30")
  print(f"Space traffic: {total:,}")
  top_models = sorted(by_model.items(), key=lambda x: x[1], reverse=True)
  ```
---

### Data Deletion

#### `delete_data`
```python
is_deleted: bool = client.delete_data(
    model_name: str,
    start_time: str | datetime,
    end_time: str | datetime,
)
```
Deletes all inference records for the named model in the given interval.

* **Parameters**
  * `model_name` – The *human-readable* name shown in the Arize UI.
  * `start_time` – The start of the interval to delete. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to delete. Can be a string in a parsable format or a datetime object.

* **Returns**  
  A boolean indicating whether the purge request was accepted and executed by the API. _Note: it may take a few minutes for the records to stop appearing in the UI._

* **Example**
  ```python
  success = client.delete_data("fraud-detection-v3", "2024-04-01", "2024-04-30")
  if success:
    print("Data deleted ✅")
  else:
    print("Data deletion failed ❌")
  ```

---

#### `delete_data_by_id`
```python
is_deleted: bool = client.delete_data_by_id(
    model_id: str,
    start_time: str | datetime,
    end_time: str | datetime,
)
```
Identical to `delete_data` but keyed by `model_id`.

* **Parameters**
  * `model_id` – the canonical identifier for the model
  * `start_time` – The start of the interval to delete. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to delete. Can be a string in a parsable format or a datetime object.

* **Returns**  
  A boolean indicating whether the purge request was accepted and executed by the API.

* **Example**
  ```python
  success = client.delete_data_by_id("******", "2024-04-01", "2024-04-30")
  if success:
    print("Data deleted ✅")
  else:
    print("Data deletion failed ❌")    
  ```

---

### Performance Metrics

#### `get_performance_metric_over_time`
```python
from pandas import DataFrame

performance_metrics: list[dict] | DataFrame = client.get_performance_metric_over_time(
    metric: str,
    environment: str,
    model_id: str,
    start_time: str | datetime,
    end_time: str | datetime,
    granularity: str = "day",
    to_dataframe: bool = True,
)
```

Pulls a time-series of a model's performance metric. The data can either be returned as a list of dictionaries or a `pandas.DataFrame`.  In either case, the data is indexed by timestamp at the requested granularity. 

For this method (and a few others), you can pass either `model_id` or `model_name` to identify the model. If both are provided, `model_id` takes precedence. For tools that allow you to pass in either, using `model_name` will first query the model by name and then use the id in subsequent requests.

* **Parameters**
  * `metric` – One of Arize’s performance metric identifiers (`"accuracy"`, `"f1_score"`, …)
  * `environment` – The logical environment inside the model (`"production"`, `"training"`…)
  * `model_id` – The canonical identifier for the model. Either `model_id` or `model_name` must be provided.
  * `model_name` – The *human-readable* name shown in the Arize UI. Either `model_id` or `model_name` must be provided.
  * `start_time` – The start of the interval to query. Can be a string in a parsable format or a datetime object.
  * `end_time` – The end of the interval to query. Can be a string in a parsable format or a datetime object.
  * `granularity` – Bucket size (`"day"`, `"hour"`, `"week"`)
  * `to_dataframe` – Convenience flag that wraps the response in a `pandas.DataFrame`

* **Returns**  
  A list of dictionaries or a `pandas.DataFrame`.

  The list of dictionaries or `pandas.DataFrame` contains the following keys or columns:
  * `metricDisplayDate` – The timestamp of the metric value
  * `metricValue` – The value of the metric

* **Example**
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
### Putting it together

Below is a miniature script that showcases a typical troubleshooting loop:

```python
from arize_toolkit import Client
import os, pprint, pandas as pd

client = Client(
    organization=os.getenv("ORGANIZATION"),
    space=os.getenv("SPACE"),
    arize_developer_key=os.getenv("ARIZE_DEVELOPER_KEY")
)

model_name = "fraud-detection-v3"

# 1. Confirm the model exists
model = client.get_model(model_name)
print("Model ✔", model["id"])

# 2. Check traffic last week
vol = client.get_model_volume(model_name, "2024-05-01", "2024-05-08")
print("Volume last 7 days:", vol)

# 3. Pull daily F1 score
f1_df = client.get_performance_metric_over_time(
    metric="f1_score",
    environment="production",
    model_id=model["id"],
    start_time="2024-05-01",
    end_time="2024-05-08",
    granularity="day",
    to_dataframe=True
)
f1_df.plot(x="metricDisplayDate", y="metricValue")

# 4. Drill into the UI
print("Open:", client.get_model_url(model_name))
```

Save it, run it, and you will have a clear snapshot of production health – without ever
leaving Python.

