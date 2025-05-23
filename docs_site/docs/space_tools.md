# Space & Organization Tools

## Overview

These tools and properties on the `Client` object help you manage the client's active connection to specific Arize Spaces and Organizations. They also provide convenient methods for generating URLs to various entities within the Arize platform, based on the currently configured space.

| Operation | Helper Method/Property |
|-----------------------------|-----------------------------|
| Switch active Space | [`switch_space`](#switch_space) |
| Get current Space URL | [`space_url`](#space_url) (Property) |
| Get Model URL | [`model_url`](#model_url) |
| Get Custom Metric URL | [`custom_metric_url`](#custom_metric_url) |
| Get Monitor URL | [`monitor_url`](#monitor_url) |
| Get Prompt Hub Prompt URL | [`prompt_url`](#prompt_url) |
| Get Prompt Hub Version URL | [`prompt_version_url`](#prompt_version_url) |

______________________________________________________________________

## Client Methods & Properties

______________________________________________________________________

### `switch_space`

```python
new_space_url: str = client.switch_space(space: str, organization: Optional[str] = None)
```

Switches the client's active space and, optionally, the organization. This method updates the client's internal `space_id` and `org_id` to reflect the new context. It's useful when you need to work with multiple Arize spaces or organizations within the same script or session.

**Parameters**

- `space` (str) – The name of the Arize space to switch to.
- `organization` (Optional[str]) – The name of the Arize organization. If omitted, the client's current organization (used during initialization) is assumed.

**Returns**

- `str` – The full URL to the new active space in the Arize UI.

**Example**

```python
# Collect all models from all spaces in all organizations
org_space_pairs = [
    ("other_org", "other_org1_space_1"),
    ("other_org", "other_org1_space_2"),
    ("other_org_2", "other_org2_space_1"),
    ("other_org_2", "other_org2_space_2"),
]
all_models = client.get_all_models()
for org, space in org_space_pairs:
    space_url = client.switch_space(space=space, organization=org)
    all_models.extend(client.get_all_models())
```

______________________________________________________________________

### `space_url`

```python
current_space_url: str = client.space_url
```

This is a read-only property that returns the full URL to the current active space in the Arize UI. The URL is constructed using the client's `arize_app_url`, `org_id`, and `space_id`.

**Returns**

- `str` – The URL of the current active space.

**Example**

```python
print(f"The URL for the current space is: {client.space_url}")
```

______________________________________________________________________

### `model_url`

```python
model_page_url: str = client.model_url(model_id: str)
```

Constructs and returns a direct URL to a specific model's page within the current active space in the Arize UI.

**Parameters**

- `model_id` (str) – The unique identifier of the model.

**Returns**

- `str` – The full URL to the model's page.

**Example**

```python
your_model_id = "abcdef123456"
url = client.model_url(model_id=your_model_id)
print(f"Link to model {your_model_id}: {url}")
```

______________________________________________________________________

### `custom_metric_url`

```python
metric_page_url: str = client.custom_metric_url(model_id: str, custom_metric_id: str)
```

Constructs and returns a direct URL to a specific custom metric's page, associated with a model, within the Arize UI.

**Parameters**

- `model_id` (str) – The unique identifier of the model to which the custom metric belongs.
- `custom_metric_id` (str) – The unique identifier of the custom metric.

**Returns**

- `str` – The full URL to the custom metric's page.

**Example**

```python
your_model_id = "model123"
your_metric_id = "metricABC"
url = client.custom_metric_url(model_id=your_model_id, custom_metric_id=your_metric_id)
print(f"Link to custom metric {your_metric_id} for model {your_model_id}: {url}")
```

______________________________________________________________________

### `monitor_url`

```python
monitor_page_url: str = client.monitor_url(monitor_id: str)
```

Constructs and returns a direct URL to a specific monitor's page within the Arize UI.

**Parameters**

- `monitor_id` (str) – The unique identifier of the monitor.

**Returns**

- `str` – The full URL to the monitor's page.

**Example**

```python
your_monitor_id = "monitorXYZ"
url = client.monitor_url(monitor_id=your_monitor_id)
print(f"Link to monitor {your_monitor_id}: {url}")
```

______________________________________________________________________

### `prompt_url`

```python
prompt_hub_url: str = client.prompt_url(prompt_id: str)
```

Constructs and returns a direct URL to a specific prompt in the Arize Prompt Hub.

**Parameters**

- `prompt_id` (str) – The unique identifier of the prompt.

**Returns**

- `str` – The full URL to the prompt's page in the Prompt Hub.

**Example**

```python
# Assume 'your_prompt_id' is a valid ID
your_prompt_id = "prompt789"
url = client.prompt_url(prompt_id=your_prompt_id)
print(f"Link to prompt {your_prompt_id} in Prompt Hub: {url}")
```

______________________________________________________________________

### `prompt_version_url`

```python
prompt_version_page_url: str = client.prompt_version_url(prompt_id: str, prompt_version_id: str)
```

Constructs and returns a direct URL to a specific version of a prompt in the Arize Prompt Hub.

**Parameters**

- `prompt_id` (str) – The unique identifier of the prompt.
- `prompt_version_id` (str) – The unique identifier of the prompt version.

**Returns**

- `str` – The full URL to the specific prompt version's page in the Prompt Hub.

**Example**

```python
# Assume these are valid IDs
your_prompt_id = "promptABC"
your_version_id = "version123"
url = client.prompt_version_url(
    prompt_id=your_prompt_id, prompt_version_id=your_version_id
)
print(f"Link to prompt {your_prompt_id} version {your_version_id}: {url}")
```
