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
| Create new Space | [`create_new_space`](#create_new_space) |
| Create Space Admin API Key | [`create_space_admin_api_key`](#create_space_admin_api_key) |
| Get User by Name or Email | [`get_user`](#get_user) |
| Assign Space Membership (by name) | [`assign_space_membership`](#assign_space_membership) |
| Assign Space Membership (by ID) | [`assign_space_membership_by_id`](#assign_space_membership_by_id) |
| Remove Space Member (by name) | [`remove_space_member`](#remove_space_member) |
| Remove Space Member (by ID) | [`remove_space_member_by_id`](#remove_space_member_by_id) |
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

### `get_user`

```python
user: dict = client.get_user(search: str)
```

Searches for a user by name or email and retrieves their details. This is useful for finding user IDs needed for operations like assigning space membership.

**Parameters**

- `search` (str) – Search term to match against user name or email. The search performs a partial match.

**Returns**

A dictionary containing user information:

- `id` (str): Unique identifier for the user
- `name` (str): Name of the user
- `email` (str): Email of the user
- `status` (str): User status ('active' or 'inactive')
- `accountRole` (str): User's account role ('admin' or 'member')
- `userType` (str): Type of user ('human' or 'bot')
- `createdAt` (datetime): When the user was created

**Raises**

- `ValueError` – If search is empty
- `ArizeAPIException` – If no user is found matching the search criteria

**Example**

```python
# Find a user by email
user = client.get_user(search="john@example.com")
print(f"Found user: {user['name']} (ID: {user['id']})")

# Find a user by name
user = client.get_user(search="John")
print(f"User email: {user['email']}")
print(f"Account role: {user['accountRole']}")

# Use with assign_space_membership
user = client.get_user(search="jane@example.com")
client.assign_space_membership_by_id(user_ids=user["id"], role="admin")
```

______________________________________________________________________

### `assign_space_membership`

```python
memberships: List[dict] = client.assign_space_membership(
    user_names: Union[str, List[str]],
    space_names: Optional[Union[str, List[str]]] = None,
    role: str = "member",
    custom_role_id: Optional[str] = None
)
```

Assigns one or more users to one or more spaces with the specified role using user names/emails and space names. This method looks up user IDs and space IDs automatically, then creates a membership for each combination.

**Parameters**

- `user_names` (Union\[str, List[str]\]) – A single user name/email or list of user names/emails to assign
- `space_names` (Optional\[Union\[str, List[str]\]\]) – A single space name or list of space names. If not provided, uses the current space.
- `role` (str, optional) – The role to assign. One of: 'admin', 'member', 'readOnly', 'annotator'. Defaults to 'member'.
- `custom_role_id` (Optional[str]) – Custom role ID to use instead of a standard role. Cannot be used together with the role parameter.

**Returns**

A list of space membership dictionaries, each containing:

- `id` (str): The membership ID
- `role` (str): The assigned role
- `user` (dict): User information including id, email, and name

**Raises**

- `ValueError` – If user_names is empty
- `ArizeAPIException` – If a user or space is not found, or if there is an error assigning the membership

**Example**

```python
# Assign a single user to the current space as a member (by email)
memberships = client.assign_space_membership(user_names="john@example.com")

# Assign multiple users to multiple spaces as admins (by names)
memberships = client.assign_space_membership(
    user_names=["john@example.com", "jane@example.com"],
    space_names=["Production", "Staging"],
    role="admin",
)

# Assign a user with a custom role
memberships = client.assign_space_membership(
    user_names="john@example.com", custom_role_id="custom_role_xyz"
)

for membership in memberships:
    print(f"Assigned {membership['user']['email']} as {membership['role']}")
```

______________________________________________________________________

### `assign_space_membership_by_id`

```python
memberships: List[dict] = client.assign_space_membership_by_id(
    user_ids: Union[str, List[str]],
    space_ids: Optional[Union[str, List[str]]] = None,
    role: str = "member",
    custom_role_id: Optional[str] = None
)
```

Assigns one or more users to one or more spaces with the specified role using user IDs and space IDs directly.

**Parameters**

- `user_ids` (Union\[str, List[str]\]) – A single user ID or list of user IDs to assign
- `space_ids` (Optional\[Union\[str, List[str]\]\]) – A single space ID or list of space IDs. If not provided, uses the current space.
- `role` (str, optional) – The role to assign. One of: 'admin', 'member', 'readOnly', 'annotator'. Defaults to 'member'.
- `custom_role_id` (Optional[str]) – Custom role ID to use instead of a standard role. Cannot be used together with the role parameter.

**Returns**

A list of space membership dictionaries, each containing:

- `id` (str): The membership ID
- `role` (str): The assigned role
- `user` (dict): User information including id, email, and name

**Raises**

- `ValueError` – If user_ids is empty
- `ArizeAPIException` – If there is an error assigning the membership

**Example**

```python
# Assign a single user to the current space as a member
memberships = client.assign_space_membership_by_id(user_ids="user_123")

# Assign multiple users to multiple spaces as admins
memberships = client.assign_space_membership_by_id(
    user_ids=["user_1", "user_2", "user_3"],
    space_ids=["space_a", "space_b"],
    role="admin",
)

# Combine with get_user to look up IDs first
user = client.get_user(search="john@example.com")
memberships = client.assign_space_membership_by_id(user_ids=user["id"], role="admin")
```

______________________________________________________________________

### `remove_space_member`

```python
result: dict = client.remove_space_member(
    user_name: str,
    space_name: Optional[str] = None
)
```

Removes a user from a space using user name/email and space name. This method looks up the user ID and space ID automatically.

**Parameters**

- `user_name` (str) – The name or email of the user to remove
- `space_name` (Optional[str]) – The name of the space to remove the user from. If not provided, uses the current space.

**Returns**

A dictionary containing:

- `space_id` (str): The ID of the space the user was removed from
- `space_name` (str): The name of the space

**Raises**

- `ValueError` – If user_name is empty
- `ArizeAPIException` – If the user or space is not found, or if there is an error removing the member

**Example**

```python
# Remove a user from the current space (by email)
result = client.remove_space_member(user_name="john@example.com")
print(f"Removed user from space: {result['space_name']}")

# Remove a user from a specific space (by names)
result = client.remove_space_member(
    user_name="john@example.com", space_name="Production"
)
print(f"Removed user from space: {result['space_name']}")
```

______________________________________________________________________

### `remove_space_member_by_id`

```python
result: dict = client.remove_space_member_by_id(
    user_id: str,
    space_id: Optional[str] = None
)
```

Removes a user from a space using user ID and space ID directly.

**Parameters**

- `user_id` (str) – The ID of the user to remove
- `space_id` (Optional[str]) – The ID of the space to remove the user from. If not provided, uses the current space.

**Returns**

A dictionary containing:

- `space_id` (str): The ID of the space the user was removed from
- `space_name` (str): The name of the space

**Raises**

- `ValueError` – If user_id is empty
- `ArizeAPIException` – If there is an error removing the member

**Example**

```python
# Remove a user from the current space
result = client.remove_space_member_by_id(user_id="user_to_remove")
print(f"Removed user from space: {result['space_name']}")

# Remove a user from a specific space
result = client.remove_space_member_by_id(
    user_id="user_123", space_id="specific_space_id"
)
print(f"Removed user from space: {result['space_name']}")

# Combine with get_user to look up ID first
user = client.get_user(search="john@example.com")
result = client.remove_space_member_by_id(user_id=user["id"])
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
