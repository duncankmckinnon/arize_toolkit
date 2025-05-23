# Language-Model Tools

## Overview

- **Prompts** – version-controlled chat / completion templates ( system + user + assistant messages, tools, variables … ). You can create new prompts, fetch existing ones, update metadata, or iterate through prior versions.
- **Annotations** – labels or scores attached to individual inference records, typically produced by human evaluation or another model.

`arize_toolkit.Client` exposes helpers for both areas:

| Area | Operation | Helper |
|------|-----------|--------|
| Prompts | List every prompt | [`get_all_prompts`](#get_all_prompts) |
| | Retrieve by *name* | [`get_prompt`](#get_prompt) |
| | Retrieve by *id* | [`get_prompt_by_id`](#get_prompt_by_id) |
| | Quick-link to prompt | [`prompt_url`](#prompt_url) |
| | List all versions | [`get_all_prompt_versions`](#get_all_prompt_versions) |
| | Render a formatted prompt | [`get_formatted_prompt`](#get_formatted_prompt) |
| | Create a prompt / version | [`create_prompt`](#create_prompt) |
| | Update metadata (by id) | [`update_prompt_by_id`](#update_prompt_by_id) |
| | Update metadata (by name) | [`update_prompt`](#update_prompt) |
| | Delete by *id* | [`delete_prompt_by_id`](#delete_prompt_by_id) |
| | Delete by *name* | [`delete_prompt`](#delete_prompt) |
| Annotations | Create annotation | [`create_annotation`](#create_annotation) |

______________________________________________________________________

## Prompt Operations

### `get_all_prompts`

```python
prompts: list[dict] = client.get_all_prompts()
```

Returns a list of all top-level prompts in the current space.

Each dictionary includes keys such as `id`, `name`, `description`, `tags`, `createdAt`, `provider`, `modelName`.

**Parameters**

- _None_ – this helper takes no arguments.

**Returns**

A list of dictionaries – one per prompt – each containing at minimum:

- `id` – Canonical prompt id
- `name` – Prompt name
- `description` – Prompt description (may be empty)
- `tags` – List of tags
- `commitMessage` – Last commit message
- `createdBy` – User that created the prompt
- `messages` – Prompt message list
- `inputVariableFormat` – Variable-interpolation style ("f_string", "mustache", "none")
- `toolChoice` – Tool choice
- `toolCalls` – Tool calls
- `llmParameters` – Invocation parameters (temperature, max_tokens, etc.)
- `createdAt` – Timestamp
- `updatedAt` – Timestamp
- `provider` – LLM provider
- `modelName` – Model name used for generations

**Example**

```python
for p in client.get_all_prompts():
    print(p["name"], p["id"])
```

______________________________________________________________________

### `get_prompt`

```python
prompt: dict = client.get_prompt(prompt_name: str)
```

Fetch a prompt by *name*.

**Parameters**

- `prompt_name` – Name shown in the Arize UI.

**Returns**

A dictionary with the same keys documented under **`get_all_prompts`** but restricted to a single prompt.

- `id` – Canonical prompt id
- `name` – Prompt name
- `description` – Prompt description (may be empty)
- `tags` – List of tags
- `commitMessage` – Last commit message
- `createdBy` – User that created the prompt
- `messages` – Prompt message list
- `inputVariableFormat` – Variable-interpolation style ("f_string", "mustache", "none")
- `toolChoice` – Tool choice
- `toolCalls` – Tool calls
- `llmParameters` – Invocation parameters (temperature, max_tokens, etc.)
- `createdAt` – Timestamp
- `updatedAt` – Timestamp
- `provider` – LLM provider
- `modelName` – Model name used for generations

**Example**

```python
prompt = client.get_prompt("greeting_prompt")
print(prompt["createdAt"])
```

______________________________________________________________________

### `get_prompt_by_id`

```python
prompt: dict = client.get_prompt_by_id(prompt_id: str)
```

Fetch a prompt by canonical id.

**Parameters**

- `prompt_id` – Canonical prompt id

**Returns**

Dictionary with the prompt data.

- `id` – Canonical prompt id
- `name` – Prompt name
- `description` – Prompt description (may be empty)
- `tags` – List of tags
- `commitMessage` – Last commit message
- `createdBy` – User that created the prompt
- `messages` – Prompt message list
- `inputVariableFormat` – Variable-interpolation style ("f_string", "mustache", "none")
- `toolChoice` – Tool choice
- `toolCalls` – Tool calls
- `llmParameters` – Invocation parameters (temperature, max_tokens, etc.)
- `createdAt` – Timestamp
- `updatedAt` – Timestamp
- `provider` – LLM provider
- `modelName` – Model name used for generations

**Example**

```python
prompt = client.get_prompt_by_id("******")
print(prompt["name"])
```

______________________________________________________________________

### `prompt_url`

The client surfaces convenience helpers to build deep-links:

```python
client.prompt_url(prompt_id)
client.prompt_version_url(prompt_id, prompt_version_id)
```

**Parameters**

- `prompt_id` – Canonical prompt id (for `prompt_url`)
- `prompt_version_id` – Canonical version id (for `prompt_version_url`)

**Returns**

A string URL deep-linking to the prompt or prompt version in the Arize UI.

**Example**

```python
url = client.prompt_url("******")
print(url)
```

______________________________________________________________________

### `get_all_prompt_versions`

```python
versions: list[dict] = client.get_all_prompt_versions(prompt_name: str)
```

Retrieve every saved version of a prompt (ordered newest → oldest).

**Parameters**

- `prompt_name` – Name of the prompt whose versions you wish to list.

**Returns**

List of dictionaries. Each dictionary contains:

- `id` – Version id
- `commitMessage` – Commit message for the version
- `messages` – List of messages for the version
- `inputVariableFormat` – Variable-interpolation style
- `llmParameters` – Invocation parameters
- `createdBy` – User that created the version
- `createdAt` – Timestamp
- `provider` – LLM provider
- `modelName` – Model name used for generations
- `toolChoice` - Tool choice
- `toolCalls` - Tool calls

**Example**

```python
for v in client.get_all_prompt_versions("greeting_prompt"):
    print(v["id"], v["commitMessage"])
```

______________________________________________________________________

### `get_formatted_prompt`

```python
formatted = client.get_formatted_prompt(
    prompt_name="greeting_prompt",
    user_name="Alice",
)
print(formatted.text)  # ready-to-send prompt
```

Takes a named prompt plus keyword variables and returns a `FormattedPrompt` object whose `.text` property contains the fully-rendered template.

**Parameters**

- `prompt_name` – Name of the prompt template
- `**variables` – Arbitrary keyword arguments that map to template variables inside the prompt

**Returns**

A `FormattedPrompt` instance with:

- `text` – Rendered prompt string
- `variables` – Dict of variables used when rendering

**Example**

```python
fp = client.get_formatted_prompt("welcome", user="Bob")
print(fp.text)
```

______________________________________________________________________

## Creating & Updating Prompts

### `create_prompt`

```python
url = client.create_prompt(
    name="greeting_prompt",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello {user_name}!"},
    ],
    description="Greets the user by name",
    tags=["example", "greeting"],
    provider="openAI",
    model_name="gpt-3.5-turbo",
)
```

Creates a *new* prompt or a *new version* of an existing prompt (if `name` already exists). The helper accepts many optional fields mirroring the Arize Prompt schema:

**Parameters**

- `name` – **Required.** Prompt name.
- `messages` – **Required.** List of role/content dicts.
- `commit_message` – (optional) Commit message; default "created prompt".
- `description` – (optional) Prompt description.
- `tags` – (optional) List of tags.
- `input_variable_format` – (optional) "f_string", "mustache", or "none".
- `provider` – (optional) LLM provider ("openAI", "awsBedrock", ...).
- `model_name` – (optional) Model name within the provider.
- `tools` – (optional) Function-calling tool configuration.
- `tool_choice` – (optional) Tool choice.
- `invocation_params` – (optional) Temperature, top_p, etc.
- `provider_params` – (optional) Provider-specific settings.

**Returns**

A string URL path that opens the newly created prompt (or prompt version) in the Arize UI.

**Example**

```python
url = client.create_prompt(
    name="greeting_prompt",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello {user_name}!"},
    ],
)
```

______________________________________________________________________

### `update_prompt`

Rename or edit description/tags of a **top-level** prompt.

```python
is_updated: bool = client.update_prompt(
    prompt_name="greeting_prompt",
    description="Greets the user by name",
)
```

**Parameters**

- `prompt_name` – Existing prompt name to update.
- `updated_name` – (optional) New name for the prompt. Omit to keep the current name.
- `description` – (optional) New description. Omit to leave unchanged.
- `tags` – (optional) Complete replacement list of tags. Omit to leave unchanged.

**Returns**

- `bool` – `True` if the prompt metadata was updated successfully, `False` otherwise.

**Example**

```python
client.update_prompt(
    prompt_name="greeting_prompt",
    description="Greets the user by name",
)
```

______________________________________________________________________

### `update_prompt_by_id`

Rename or edit description/tags of a **top-level** prompt.

```python
is_updated: bool = client.update_prompt_by_id(
    prompt_id="******",
    description="Greets the user by name",
)
```

**Parameters**

- `prompt_id` – Canonical prompt id
- `updated_name` – (optional) New name for the prompt. Omit to keep the current name.
- `description` – (optional) New description. Omit to leave unchanged.
- `tags` – (optional) Complete replacement list of tags. Omit to leave unchanged.

**Returns**

- `bool` – `True` if the prompt metadata was updated successfully, `False` otherwise.

**Example**

```python
client.update_prompt_by_id(
    prompt_id="******",
    description="Greets the user by name",
)
```

______________________________________________________________________

## Deleting Prompts

Remove a prompt entirely (all versions).

### `delete_prompt`

Remove a prompt entirely (all versions).

```python
is_deleted: bool = client.delete_prompt(prompt_name: str)
```

**Parameters**

- `prompt_name` – Existing prompt name to delete.

**Returns**

- `bool` – `True` if the prompt was deleted successfully, `False` otherwise.

**Example**

```python
is_deleted: bool = client.delete_prompt(
    prompt_name="greeting_prompt",
)
print("Deleted" if is_deleted else "Failed")
```

______________________________________________________________________

### `delete_prompt_by_id`

Remove a prompt entirely (all versions).

```python
is_deleted: bool = client.delete_prompt_by_id(prompt_id: str)
```

**Parameters**

- `prompt_id` – Canonical prompt id

**Returns**

- `bool` – `True` if the prompt was deleted successfully, `False` otherwise.

**Example**

```python
is_deleted = client.delete_prompt_by_id(
    prompt_id="******",
)
print("Deleted" if is_deleted else "Failed")
```

______________________________________________________________________

## Annotation Operations

### `create_annotation`

```python
success: bool = client.create_annotation(
    name="human_label",
    updated_by="duncan",
    record_id="abc123",
    annotation_type="label",  # "label" or "score"
    model_name="fraud-detection-v3",
    label="fraud",  # required when annotation_type="label"
    note="Checked by expert",
    model_environment="production",
    start_time="2024-05-01T10:00:00Z",  # optional, defaults to now
)
```

Adds a label/score to a specific record.

**Required parameters**

- `name` – Logical annotation name (e.g. "ground_truth").
- `updated_by` – User or process writing the annotation.
- `record_id` – Identifier of the record being annotated.
- `annotation_type` – "label" or "score".
- *Either* `model_name` **or** `model_id`.
- `label` **or** `score` depending on `annotation_type`.

**Optional parameters**

- `note` – Free-text note.
- `model_environment` – Environment name; defaults to "tracing".
- `start_time` – Timestamp; defaults to now.

**Returns**

`True` when the annotation is accepted.

**Example**

```python
ok = client.create_annotation(
    name="score",
    updated_by="qa_bot",
    record_id="rec_123",
    annotation_type="score",
    score=0.9,
    model_name="support-bot",
)
print("Saved" if ok else "Failed")
```

______________________________________________________________________

## End-to-End Example

```python
from arize_toolkit import Client

client = Client(
    organization="my-org",
    space="my-space",
)

# 1. Create a prompt
prompt_url = client.create_prompt(
    name="troubleshoot_prompt",
    messages=[
        {"role": "system", "content": "You are a support bot."},
        {"role": "user", "content": "{question}"},
    ],
)
print(prompt_url)

# 2. Render the prompt for a specific question
formatted = client.get_formatted_prompt(
    "troubleshoot_prompt", question="Why is my widget broken?"
)
print(formatted.text)

# 3. Attach a human label to the response record later
client.create_annotation(
    name="user_feedback",
    updated_by="analyst",
    record_id="resp_789",
    annotation_type="score",
    score=4.5,
    model_name="support-bot",
)
```
