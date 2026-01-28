# Space & Organization Tools

## Overview

These tools and properties on the `Client` object help you manage the client's active connection to specific Arize Spaces and Organizations. They also provide convenient methods for creating new spaces, managing API keys, and generating URLs to various entities within the Arize platform, based on the currently configured space.

**Note:** When creating a `Client`, both `organization` and `space` parameters are optional. If not provided:

- If no organization is specified, the client will automatically use the first organization in your account
- If no space is specified, the client will automatically use the first space in the selected organization

| Operation | Helper Method/Property |
|-----------------------------|-----------------------------|
| Switch active Space/Organization | [`switch_space`](#switch_space) |
| Get all Organizations | [`get_all_organizations`](#get_all_organizations) |
| Get all Spaces in Organization | [`get_all_spaces`](#get_all_spaces) |
| Create new Organization and Space | [`create_new_organization_and_space`](#create_new_organization_and_space) |
| Create new Space | [`create_new_space`](#create_new_space) |
| Create Space Admin API Key | [`create_space_admin_api_key`](#create_space_admin_api_key) |
| Get current Space URL | [`space_url`](#space_url) (Property) |
| Get Model URL | [`model_url`](#model_url) |
| Get Custom Metric URL | [`custom_metric_url`](#custom_metric_url) |
| Get Monitor URL | [`monitor_url`](#monitor_url) |
| Get Prompt Hub Prompt URL | [`prompt_url`](#prompt_url) |
| Get Prompt Hub Version URL | [`prompt_version_url`](#prompt_version_url) |

______________________________________________________________________

## Client Initialization

The `Client` constructor accepts optional `organization` and `space` parameters, providing flexible initialization options:

```python
# Explicit organization and space
client = Client(
    organization="my_organization", space="my_space", arize_developer_key="your_api_key"
)

# Auto-select first organization and space
client = Client(arize_developer_key="your_api_key")

# Specify organization, auto-select first space in that org
client = Client(organization="my_organization", arize_developer_key="your_api_key")

client.switch_space(space="my_space")
```

**Auto-selection Behavior:**

- If no organization is provided, the client selects the first organization in your account
- If no space is provided, the client selects the first space in the selected organization
- This makes it easy to get started quickly while still allowing precise control when needed

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

### `create_new_organization_and_space`

```python
space_url: str = client.create_new_organization_and_space(
    org_name: str,
    space_name: str,
    org_description: Optional[str] = None,
    space_private: bool = False,
    set_as_active: bool = True
)
```

Creates a new organization and adds a new space to it. A new organization must have at least one space to work correctly, so this method creates both together.

**Parameters**

- `org_name` (str) – Name for the new organization
- `space_name` (str) – Name for the new space in the organization
- `org_description` (Optional[str], optional) – Description for the organization. Defaults to None.
- `space_private` (bool, optional) – Whether the space should be private. Defaults to False.
- `set_as_active` (bool, optional) – Whether to switch the client to the new organization and space. Defaults to True.

**Returns**

- `str` – The URL of the newly created space

**Raises**

- `ArizeAPIException` – If there is an error creating the organization or space

**Example**

```python
# Create a new organization with a space and switch to it
space_url = client.create_new_organization_and_space(
    org_name="My New Organization",
    space_name="Production Space",
    org_description="Organization for production ML models",
)
print(f"Created new organization and space: {space_url}")

# The client is now connected to the new organization and space
print(f"Current organization: {client.organization}")
print(f"Current space: {client.space}")

# Create organization and space without switching to it
space_url = client.create_new_organization_and_space(
    org_name="Another Organization", space_name="Dev Space", set_as_active=False
)
# Client remains connected to previous organization/space
```

______________________________________________________________________

### `create_new_space`

```python
space_id: str = client.create_new_space(name: str, private: bool = True)
```

Creates a new space in the current organization. This method allows you to programmatically create new spaces for organizing your ML models and data.

**Parameters**

- `name` (str) – Name for the new space
- `private` (bool, optional) – Whether the space should be private. Defaults to True.
- `set_as_active` (bool, optional) – Whether the client should switch to the new space. Defaults to True.

**Returns**

- `str` – The unique identifier (ID) of the newly created space

**Raises**

- `ArizeAPIException` – If there is an error creating the space

**Example**

```python
# Create a private space (default)
new_space_id = client.create_new_space("My Production Space")
print(f"Created private space with ID: {new_space_id}")

# Create a public space
public_space_id = client.create_new_space("Public Demo Space", private=False)
print(f"Created public space with ID: {public_space_id}")
```

______________________________________________________________________

### `create_space_admin_api_key`

```python
api_key_info: dict = client.create_space_admin_api_key(name: str)
```

Creates an admin API key for the active space. This method generates API keys with admin-level permissions for the space, useful for automated workflows and service accounts.

**Parameters**

- `name` (str) – Name for the API key (for identification purposes)

**Returns**

A dictionary containing:

- `apiKey` (str): The generated API key
- `expiresAt` (datetime, optional): When the key expires (None if permanent)
- `id` (str): Unique identifier for the key

**Raises**

- `ArizeAPIException` – If there is an error creating the API key

**Example**

```python
# Create a new space - this will be set as the current space
new_space = client.create_new_space("Production Bot Space")

# Create a new api key for the current space
key_info = client.create_space_admin_api_key("Production Bot Space Key")

print(f"API Key: {key_info['apiKey']}")
print(f"Key ID: {key_info['id']}")
if key_info["expiresAt"]:
    print(f"Expires: {key_info['expiresAt']}")
else:
    print("Key does not expire")
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
