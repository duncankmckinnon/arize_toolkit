# Arize Toolkit

A Python toolkit for interacting with Arize. This package is a collection of tools for building workflows that involve model monitoring and observability. The entrypoint for the toolkit is the `Client` class, which is used to interact with the Arize API.

## Disclaimer
Although this package is used for development work with and within the Arize platform, it is not an Arize supported product.
It is a community-supported project developed and maintained by an Arize Engineer.

## Installation

```bash
pip install arize-toolkit
```

## Quick Start

### Client Parameters
- `organization`: Your organization name from the Arize UI
- `space`: Your space name within the organization from the Arize UI
- `arize_developer_key`: API authentication token
  - Found in the Arize UI under `Settings > Space Settings and Keys > API Key`
  - Can be provided directly or loaded from the `ARIZE_DEVELOPER_KEY` environment variable
- `arize_app_url`: The URL of the Arize app (only needs to be set for on-prem deployments)
- `sleep_time`: Optional delay between paginated requests (in seconds)

#### Example: Initialize the client
```python
from arize_toolkit import Client

# Initialize the client
client = Client(
    organization="your_org_name",
    space="your_space_name",
    arize_developer_key="your_arize_developer_key",  # Or set ARIZE_DEVELOPER_KEY environment variable
    arize_app_url = "https://app.arize.com", # The URL of the Arize app
    sleep_time = 0, # The sleep time between API requests
)
```

## Function Set

The following set of functions for interacting with the Arize API are available:
- `set_sleep_time(sleep_time: int) -> Client`: Set the sleep time between API requests
- `switch_space(space: str, ...) -> str`: Switch the space for the client
- `get_model(model_name: str) -> dict`: Get a specific model by name
- `get_model_by_id(model_id: str) -> dict`: Get a specific model by ID
- `get_all_models() -> list[dict]`: Get all models in your space
- `get_model_volume_by_id(model_id: str, start_time: str, end_time: str) -> int`: Get the volume for a specific model by ID and time range
- `get_model_volume(model_name: str, start_time: str, end_time: str) -> int`: Get the volume for a specific model by name and time range
- `get_total_volume(start_time: str, end_time: str) -> int, dict`: Get the total volume in the space and the volume by model
- `delete_data_by_id(model_id: str, start_time: str, end_time: str) -> bool`: Delete data for a specific model by ID and time range
- `delete_data(model_name: str, start_time: str, end_time: str) -> bool`: Delete data for a specific model by name and time range
- `get_model_url(model_name: str) -> str`: Get the URL for a specific model
- `get_performance_metric_over_time(metric: str, environment: str, model_id: str, ...) -> list[dict] | pandas.DataFrame`: Get the performance metric over time for a specific model
- `create_annotation(name: str, updated_by: str, record_id: str, annotation_type: str, model_id: str, ...) -> bool`: Create an annotation for a specific record in a model
- `get_all_prompts() -> list[dict]`: Get all prompts in the space
- `get_prompt_by_id(prompt_id: str) -> dict`: Get a specific prompt by ID
- `get_prompt(prompt_name: str) -> dict`: Get a specific prompt by name
- `get_formatted_prompt(prompt_name: str, **variables) -> FormattedPrompt`: Get a formatted prompt with the provided variables
- `get_all_prompt_versions(prompt_name: str) -> list[dict]`: Get all prompt versions for a specific prompt
- `update_prompt_by_id(prompt_id: str, name: str, description: str, tags: list[str]) -> dict`: Update a prompt by ID
- `update_prompt(prompt_name: str, description: str, tags: list[str]) -> dict`: Update a prompt by name
- `delete_prompt_by_id(prompt_id: str) -> bool`: Delete a prompt by ID
- `delete_prompt(prompt_name: str) -> bool`: Delete a prompt by name
- `get_all_custom_metrics(model_name: str) -> list[dict]`: Get all custom metrics for a specific model or all models in the space
- `get_all_custom_metrics_for_model(model_name: str, model_id: str) -> list[dict]`: Get all custom metrics for a specific model
- `get_custom_metric_by_id(metric_id: str) -> dict`: Get a specific custom metric by ID
- `get_custom_metric(model_name: str, metric_name: str) -> dict`: Get a specific custom metric by name
- `get_custom_metric_url(model_name: str, metric_name: str) -> str`: Get the URL for a specific custom metric
- `create_custom_metric(metric: str, metric_name: str, model_id: str, ...) -> str`: Create a new custom metric for a model
- `delete_custom_metric_by_id(metric_id: str, model_id: str) -> str`: Delete a custom metric by ID
- `delete_custom_metric(model_name: str, metric_name: str) -> str`: Delete a custom metric by name
- `update_custom_metric_by_id(metric_id: str, model_id: str, metric: str, ...) -> str`: Update a custom metric by ID
- `update_custom_metric(metric_name: str, model_name: str, metric: str, ...) -> str`: Update a custom metric by name
- `copy_custom_metric(current_metric_name: str, current_model_name: str, ...) -> str`: Copy a custom metric from one model to another
- `get_all_monitors(model_id: str, model_name: str, monitor_category: str) -> list[dict]`: Get all monitors for a specific model
- `get_monitor_by_id(monitor_id: str) -> dict`: Get a specific monitor by ID
- `get_monitor(monitor_name: str, model_name: str) -> dict`: Get a specific monitor by name
- `get_monitor_url(monitor_name: str, model_name: str) -> str`: Get the URL for a specific monitor
- `create_performance_monitor(name: str, model_name: str, ...) -> str`: Create a new performance monitor
- `create_data_quality_monitor(name: str, model_name: str, ...) -> str`: Create a new data quality monitor
- `create_drift_monitor(name: str, model_name: str, ...) -> str`: Create a new drift monitor
- `delete_monitor_by_id(monitor_id: str) -> str`: Delete a monitor by ID
- `delete_monitor(monitor_name: str, model_name: str) -> str`: Delete a monitor by name
- `copy_monitor(current_monitor_name: str, current_model_name: str, ...) -> str`: Copy a monitor from one model to another

### Examples: Models
The following examples demonstrate how to use the client to interact with models.
The model name and ID functions are interchangeable.

```python
# Get all models in your space
models = client.get_all_models()

# Get a specific model by name
model = client.get_model("my_model_name")

# Get a specific model by ID
model_by_id = client.get_model_by_id("my_model_id")

# Get the URL for a specific model
model_url = client.get_model_url("my_model_name")

# Get the inference volume for a specific model over a time range
model_volume = client.get_model_volume("my_model_name", "2024-01-01", "2024-01-02")

# Get the volume for a specific model by ID over a time range
model_volume_by_id = client.get_model_volume_by_id("my_model_id", "2024-01-01", "2024-01-02")

# Get the total volume in your space over a time range
total_volume, volume_by_model = client.get_total_volume("2024-01-01", "2024-01-02")

# Get performance metrics over time for a specific model
performance_metric_over_time = client.get_performance_metric_over_time("f1_score", "production", "my_model_id", "2024-01-01", "2024-01-02", granularity="day", to_dataframe=False)

# Delete data for a specific model by ID and time range
data_deleted_by_id = client.delete_data_by_id("my_model_id", "2024-01-01", "2024-01-02")

# Delete data for a specific model by name and time range
data_deleted = client.delete_data("my_model_name", "2024-01-01", "2024-01-02")
```

### Examples: LLM Features
The following examples demonstrate how to use the client to interact with LLM features like Annotations and Prompts.

```python
# Create an annotation for a specific model
annotation_created = client.create_annotation("my_model_id", "2024-01-01", "2024-01-02", "my_note", "PRODUCTION")

# Get all prompts in the space
all_prompts = client.get_all_prompts()

# Get a specific prompt by ID
prompt_by_id = client.get_prompt_by_id("my_prompt_id")

# Get a specific prompt by name
prompt = client.get_prompt("my_prompt_name")

# Get a formatted prompt with variables
formatted_prompt = client.get_formatted_prompt("my_prompt_name", prompt_variable_example="What is machine learning?")

# Update a prompt's metadata
updated_prompt = client.update_prompt("my_prompt_name", description="New description", tags=["tag1", "tag2"])

# Delete a prompt by name
deleted = client.delete_prompt("my_prompt_name")

# Get all prompt versions for a specific prompt
prompt_versions = client.get_all_prompt_versions("my_prompt_name")
```

### Examples: Custom Metrics
The following examples demonstrate how to use the client to interact with custom metrics.

```python
# Create a new custom metric for a model
custom_metric_url = client.create_custom_metric("SELECT avg(prediction) FROM model", "avg_prediction", "my_model_id")

# Get a specific custom metric by ID
custom_metric_by_id = client.get_custom_metric_by_id(custom_metric_id)

# Get a specific custom metric by name
custom_metric = client.get_custom_metric("avg_prediction", "my_model_name")

# Get the URL for a specific custom metric
custom_metric_url = client.get_custom_metric_url("avg_prediction", "my_model_name")

# Update a custom metric
updated_custom_metric = client.update_custom_metric(custom_metric_id, "SELECT avg(score) FROM model", "avg_score", "my_model_id")

# Copy a custom metric from one model to another
new_custom_metric_url = client.copy_custom_metric("avg_prediction", "my_model_name", "new_model_name")

# Delete a custom metric by ID
custom_metric_deleted_by_id = client.delete_custom_metric_by_id(custom_metric_id, "my_model_id")

# Delete a custom metric by name
custom_metric_deleted = client.delete_custom_metric("avg_score", "my_model_name")
```

### Examples: Monitors
The following examples demonstrate how to use the client to interact with monitors.

```python
# Create a new performance monitor
performance_monitor_url = client.create_performance_monitor("my_monitor_name", "my_model_name", ...)

# Create a new data quality monitor
data_quality_monitor_url = client.create_data_quality_monitor("my_monitor_name", "my_model_name", ...)

# Create a new drift monitor
drift_monitor_url = client.create_drift_monitor("my_monitor_name", "my_model_name", ...) 

# Get all performance monitors for a specific model
all_performance_monitors = client.get_all_monitors("my_model_id", "my_model_name", "performance")

# Get all monitors for a specific model
all_monitors = client.get_all_monitors("my_model_id", "my_model_name")

# Get a specific monitor by ID
monitor_by_id = client.get_monitor_by_id("my_monitor_id")

# Get a specific monitor by name
monitor = client.get_monitor("my_monitor_name", "my_model_name")

# Get the URL for a specific monitor
monitor_url = client.get_monitor_url("my_monitor_name", "my_model_name")

# Delete a monitor by ID
monitor_deleted_by_id = client.delete_monitor_by_id("my_monitor_id")

# Delete a monitor by name
monitor_deleted = client.delete_monitor("my_monitor_name", "my_model_name")

# Copy a monitor from one model to another
new_monitor_url = client.copy_monitor("my_monitor_name", "my_model_name", "new_model_name")
```

## Development
For information about extending the client's architecture and development patterns, see [Development](docs_site/docs/developers/development.md).

