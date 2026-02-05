# Documentation Patterns

Formatting guidelines for documentation files in `docs_site/docs/`.

## Table of Contents

1. [Document Structure](#document-structure)
1. [Function Documentation](#function-documentation)
1. [Overview Table](#overview-table)
1. [Code Examples](#code-examples)
1. [Index Updates](#index-updates)

______________________________________________________________________

## Document Structure

### Main Title and Overview

```markdown
# Tool Name Tools

## Overview

Brief introduction linking to Arize docs: **[Relevant Arize Docs](https://docs.arize.com/...)**

Capabilities covered:
1. Capability one
2. Capability two
3. Capability three

| Operation | Helper |
|-----------|--------|
| Get a resource | [`get_resource`](#get_resource) |
| Get all resources | [`get_all_resources`](#get_all_resources) |
| Create a resource | [`create_resource`](#create_resource) |
```

### Section Organization

- Group related operations under H2 headings
- Use horizontal rules (`---`) before each function
- Keep related functions together

______________________________________________________________________

## Function Documentation

### Standard Function Format

````markdown
---

### `function_name`

```python
result: type = client.function_name(
    required_param: str,
    optional_param: str | None = None,  # optional
    another_opt: bool = False           # optional
)
```

Brief description of what the function does.

**Parameters**

* `required_param` – Description of the required parameter
* `optional_param` *(optional)* – Description. Default: `None`
* `another_opt` *(optional)* – Description. Default: `False`

**Returns**

A dictionary containing:
* `id` – The unique identifier
* `name` – The resource name
* `field` – Description of field

**Example**

```python
from arize_toolkit import Client

client = Client(organization="my-org", space="my-space")

result = client.function_name("value")
print(f"Resource ID: {result['id']}")
```
````

### Simple Function Format

````markdown
---

### `get_resource`

```python
result: dict = client.get_resource(resource_name: str)
```

Retrieves a resource by its name.

**Parameters**

* `resource_name` – The name of the resource to retrieve

**Returns**

A dictionary containing resource information including `id`, `name`, and `type`.

**Example**

```python
resource = client.get_resource("my-resource")
print(resource["id"])
```
````

### Function with Complex Parameters

````markdown
---

### `create_resource`

```python
url: str = client.create_resource(
    name: str,
    resource_type: Literal["type1", "type2", "type3"],
    config: dict | ResourceConfig,                      # optional
    description: str | None = None,                     # optional
    tags: list[str] | None = None                       # optional
)
```

Creates a new resource in the current space.

**Parameters**

* `name` – *Human-readable name* for the resource
* `resource_type` – Type of resource. One of: `"type1"`, `"type2"`, `"type3"`
* `config` *(optional)* – Configuration object or dictionary. If dict, must contain:
  - `setting1` (str): Primary setting
  - `setting2` (int): Numeric setting
* `description` *(optional)* – Description of the resource
* `tags` *(optional)* – List of tags to apply

**Returns**

URL to the newly created resource in the Arize UI.

**Example**

```python
# With dictionary config
url = client.create_resource(
    name="my-resource",
    resource_type="type1",
    config={"setting1": "value", "setting2": 42},
    description="Example resource"
)

# With typed config object
from arize_toolkit.models import ResourceConfig

config = ResourceConfig(setting1="value", setting2=42)
url = client.create_resource(
    name="my-resource",
    resource_type="type1",
    config=config
)
```
````

### Mutually Exclusive Parameters

```markdown
**Parameters**

* `resource_name` – The name of the resource. **Provide either** `resource_name` **or** `resource_id`.
* `resource_id` – The ID of the resource. **Provide either** `resource_name` **or** `resource_id`.
```

______________________________________________________________________

## Overview Table

### Standard Format

```markdown
| Operation | Helper |
|-----------|--------|
| Get a resource by name | [`get_resource`](#get_resource) |
| Get a resource by ID | [`get_resource_by_id`](#get_resource_by_id) |
| Get all resources | [`get_all_resources`](#get_all_resources) |
| Create a resource | [`create_resource`](#create_resource) |
| Update a resource | [`update_resource`](#update_resource) |
| Delete a resource | [`delete_resource`](#delete_resource) |
| Generate resource URL | [`resource_url`](#resource_url) |
```

### Anchors

The anchor (e.g., `#get_resource`) must match the H3 heading exactly:

- `### \`get_resource\``→`#get_resource\`
- `### \`get_all_resources\``→`#get_all_resources\`

______________________________________________________________________

## Code Examples

### Language Specification

Always specify language for syntax highlighting:

````markdown
```python
# Python code
```

```json
# JSON data
```

```bash
# Shell commands
```
````

### Realistic Examples

```python
# Good - realistic values
client = Client(organization="acme-corp", space="production")
model = client.get_model("customer-churn-predictor")

# Avoid - generic values
client = Client(organization="org", space="space")
model = client.get_model("test")
```

### Error Handling Examples

```python
from arize_toolkit import Client
from arize_toolkit.exceptions import ArizeAPIException

client = Client(organization="my-org", space="my-space")

try:
    resource = client.get_resource("my-resource")
except ArizeAPIException as e:
    print(f"Error: {e}")
```

______________________________________________________________________

## Index Updates

### docs_site/docs/index.md

Add link to new documentation page:

```markdown
## Available Tools

- [Model Tools](model_tools.md) - Access and manage models
- [Monitor Tools](monitor_tools.md) - Create and manage monitors
- [New Tool Tools](new_tool_tools.md) - Description of new tools
```

### mkdocs.yml

Add entry under 'Tools' nav section:

```yaml
nav:
  - Home: index.md
  - Quickstart: quickstart.md
  - Tools:
    - Model Tools: model_tools.md
    - Monitor Tools: monitor_tools.md
    - New Tool Tools: new_tool_tools.md  # Add here
```

______________________________________________________________________

## Style Conventions

### Emphasis

- **Backticks** for: `function_names()`, `parameter_names`, `values`, `file_paths/`
- **Bold** for: **Notes**, **Important**, key terms, **Parameters**, **Returns**
- *Italics* for: *Human-readable name*, *optional*, emphasis within descriptions

### Notes and Warnings

```markdown
**Note:** Important information about this function.

**Important:** Critical information users must know.

**Warning:** Information about potential issues or breaking changes.
```

### Links

```markdown
# Internal section link
See [`other_function`](#other_function) for related functionality.

# External Arize docs
See **[Arize Monitors](https://docs.arize.com/arize/monitors)** for more details.

# Other doc file
See [Model Tools](model_tools.md) for model operations.
```

______________________________________________________________________

## Checklist

Before committing documentation:

- [ ] Main title is H1 with "Tools" suffix
- [ ] Overview section with numbered capabilities
- [ ] Overview table with all functions
- [ ] Each function has signature, parameters, returns, example
- [ ] Code blocks specify language
- [ ] Examples use realistic values
- [ ] Anchors in overview table match function headings
- [ ] Added to index.md if new page
- [ ] Added to mkdocs.yml if new page
