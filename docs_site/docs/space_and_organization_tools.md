# Space & Organization Tools

## Overview

These tools and properties on the `Client` object help you manage the client's active connection to specific Arize Spaces and Organizations. They also provide convenient methods for generating URLs to various entities within the Arize platform, based on the currently configured space.

| Operation | Helper Method/Property |
|-----------------------------|-----------------------------|
| Switch active Space/Organization | [`switch_space`](#switch_space) |
| Get all Organizations | [`get_all_organizations`](#get_all_organizations) |
| Get all Spaces in Organization | [`get_all_spaces`](#get_all_spaces) |
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
new_space_url: str = client.switch_space(space: Optional[str] = None, organization: Optional[str] = None)
```

Switches the client's active space and, optionally, the organization. This method updates the client's internal `space_id` and `org_id` to reflect the new context. It's useful when you need to work with multiple Arize spaces or organizations within the same script or session.

**Parameters**

- `space` (Optional[str]) – The name of the Arize space to switch to. If omitted, defaults to the first space in the organization.
- `organization` (Optional[str]) – The name of the Arize organization to switch to. If omitted, the client's current organization is used.

**Returns**

- `str` – The full URL to the new active space in the Arize UI.

**Behavior**

- If no arguments are provided, the space and organization remain unchanged.
- If only the space is provided, the current organization is used.
- If only the organization is provided, the first space in the provided organization is used.
- If both are provided, switches to the specified space in the specified organization.

**Example**

```python
# Switch to a specific space in the current organization
space_url = client.switch_space(space="my_new_space")

# Switch to a specific organization (using first space in that org)
space_url = client.switch_space(organization="my_other_org")

# Switch to a specific space in a specific organization
space_url = client.switch_space(space="specific_space", organization="specific_org")

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

### `get_all_organizations`

```python
organizations: List[dict] = client.get_all_organizations()
```

Retrieves all organizations in the current account. This method returns a list of organization dictionaries containing details about each organization the current user has access to.

**Returns**

A list of organization dictionaries, each containing:

- `id` (str): Unique identifier for the organization
- `name` (str): Name of the organization
- `createdAt` (datetime): When the organization was created
- `description` (str): Description of the organization

**Raises**

- `ArizeAPIException` – If there is an error retrieving organizations from the API

**Example**

```python
# Get all organizations
organizations = client.get_all_organizations()
for org in organizations:
    print(f"Organization: {org['name']} (ID: {org['id']})")
    print(f"  Created: {org['createdAt']}")
    print(f"  Description: {org['description']}")
```

______________________________________________________________________

### `get_all_spaces`

```python
spaces: List[dict] = client.get_all_spaces()
```

Retrieves all spaces in the current organization. This method returns a list of space dictionaries containing details about each space in the currently active organization.

**Returns**

A list of space dictionaries, each containing:

- `id` (str): Unique identifier for the space
- `name` (str): Name of the space
- `createdAt` (datetime): When the space was created
- `description` (str): Description of the space
- `private` (bool): Whether the space is private

**Raises**

- `ArizeAPIException` – If there is an error retrieving spaces from the API

**Example**

```python
# Get all spaces in the current organization
spaces = client.get_all_spaces()
for space in spaces:
    print(f"Space: {space['name']} (ID: {space['id']})")
    print(f"  Created: {space['createdAt']}")
    print(f"  Private: {space['private']}")
    print(f"  Description: {space['description']}")

# Switch to each space and get model count
for space in spaces:
    client.switch_space(space=space["name"])
    models = client.get_all_models()
    print(f"Space '{space['name']}' has {len(models)} models")
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
