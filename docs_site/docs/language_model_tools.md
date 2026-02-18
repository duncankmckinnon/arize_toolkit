# Language-Model Tools

## Overview

- **Prompts** – version-controlled chat / completion templates ( system + user + assistant messages, tools, variables … ). You can create new prompts, fetch existing ones, update metadata, or iterate through prior versions.
- **Evaluators** – automated scoring systems that assess LLM outputs using either LLM-based templates or custom Python code. Evaluators can detect issues like hallucinations, check response quality, or apply custom business logic.
- **Annotations** – labels or scores attached to individual inference records, typically produced by human evaluation or another model.

For more information about prompts in Arize check out the **[documentation on Arize prompts](https://arize.com/docs/ax/develop/prompt-hub)**.

For more information about evaluators in Arize check out the **[documentation on Arize evaluators](https://arize.com/docs/ax/evaluate/evaluators)**.

For more information about annotations in Arize check out the **[documentation on Arize annotations](https://arize.com/docs/ax/evaluate/human-annotations)**.

`arize_toolkit.Client` exposes helpers for all three areas:

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
| Evaluators | List all evaluators | [`get_evaluators`](#get_evaluators) |
| | Retrieve by *name* | [`get_evaluator`](#get_evaluator) |
| | Create template evaluator | [`create_template_evaluator`](#create_template_evaluator) |
| | Create code evaluator | [`create_code_evaluator`](#create_code_evaluator) |
| | Version a template evaluator | [`create_template_evaluator_version`](#create_template_evaluator_version) |
| | Version a code evaluator | [`create_code_evaluator_version`](#create_code_evaluator_version) |
| | Edit evaluator metadata | [`edit_evaluator`](#edit_evaluator) |
| | Delete an evaluator | [`delete_evaluator`](#delete_evaluator) |
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

## Evaluator Operations

### `get_evaluators`

```python
evaluators: list[dict] = client.get_evaluators()
```

Returns all evaluators in the current space. Supports filtering by search text, exact name, or task type.

**Parameters**

- `search` – (optional) Search string to filter evaluators.
- `name` – (optional) Exact name to filter by.
- `task_type` – (optional) Filter by type: `"template_evaluation"` or `"code_evaluation"`.

**Returns**

A list of dictionaries, each containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – `"template_evaluation"` or `"code_evaluation"`
- `commitHash` – Latest version commit hash
- `commitMessage` – Latest version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Example**

```python
# List all evaluators
for e in client.get_evaluators():
    print(e["name"], e["taskType"])

# List only code evaluators
code_evals = client.get_evaluators(task_type="code_evaluation")

# Search by keyword
hallucination_evals = client.get_evaluators(search="hallucination")
```

______________________________________________________________________

### `get_evaluator`

```python
evaluator: dict = client.get_evaluator(name: str)
```

Fetch a single evaluator by exact name.

**Parameters**

- `name` – The evaluator name as shown in the Arize UI.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – `"template_evaluation"` or `"code_evaluation"`
- `commitHash` – Latest version commit hash
- `commitMessage` – Latest version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Example**

```python
evaluator = client.get_evaluator("Hallucination Detector")
print(evaluator["id"], evaluator["taskType"])
```

______________________________________________________________________

### `create_template_evaluator`

```python
evaluator: dict = client.create_template_evaluator(
    name="Hallucination Detector",
    template="Does the response contain factual errors?\n\nContext: {{context}}\nResponse: {{output}}",
    metric_name="hallucination_score",
    description="Detects hallucinations in LLM responses",
    classification_choices={"Yes": 0, "No": 1},
    direction="maximize",
    commit_message="Initial version",
)
```

Creates a template (LLM-based) evaluator that uses an LLM with a prompt template to automatically evaluate LLM outputs.

**Required parameters**

- `name` – Display name for the evaluator in the Arize UI.
- `template` – Prompt template with `{{variables}}` for the LLM evaluator. Variables like `{{context}}`, `{{output}}`, `{{input}}` will be filled from span attributes.
- `metric_name` – Name of the evaluator metric/output (e.g., `"hallucination_score"`).

**Optional parameters**

- `commit_message` – Version control message (default: `"Initial version"`).
- `description` – Human-readable description of what this evaluator does.
- `tags` – List of tags for the evaluator.
- `classification_choices` – Dictionary mapping labels to scores for categorical evaluations (e.g., `{"Yes": 0, "No": 1}` or `{"Poor": 0, "Good": 0.5, "Excellent": 1}`).
- `direction` – Whether higher or lower scores are better: `"maximize"` or `"minimize"` (default: `"maximize"`).
- `data_granularity_type` – Evaluation granularity: `"span"`, `"trace"`, or `"session"` (default: `"span"`).
- `include_explanations` – Whether to include explanations in the evaluation (default: `True`).
- `use_function_calling` – Whether to use function calling if available (default: `False`).
- `position` – Display position/order of the evaluator (default: `0`).
- `rails` – Rails associated with the config.
- `query_filter` – Optional query filter over a given data granularity.
- `llm_integration_name` – Name of the LLM integration to use. Defaults to the first available integration in the space.
- `llm_model_name` – The LLM model name (e.g., `"gpt-4o"`).
- `llm_invocation_parameters` – Parameters used when running the LLM (e.g., `{"temperature": 0.0}`).
- `llm_provider_parameters` – Parameters used to initialize the LLM provider.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – The task type (`"template_evaluation"`)
- `commitHash` – Version commit hash
- `commitMessage` – Version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Examples**

```python
# Binary classification evaluator
hallucination_eval = client.create_template_evaluator(
    name="Hallucination Detector",
    template="Does the response contain factual errors?\n\nContext: {{context}}\nResponse: {{output}}\n\nAnswer: Yes or No",
    metric_name="hallucination_score",
    description="Detects hallucinations in LLM responses",
    classification_choices={"Yes": 0, "No": 1},
    direction="maximize",
)

# Multi-level quality evaluator with custom LLM
quality_eval = client.create_template_evaluator(
    name="Response Quality",
    template="Rate the quality of this response:\n\nQuestion: {{input}}\nResponse: {{output}}\n\nRating: Poor, Fair, Good, or Excellent",
    metric_name="quality_score",
    classification_choices={"Poor": 0, "Fair": 0.33, "Good": 0.67, "Excellent": 1.0},
    direction="maximize",
    llm_integration_name="My OpenAI Integration",
    llm_model_name="gpt-4o",
)
```

______________________________________________________________________

### `create_code_evaluator`

```python
imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""

code = """class HelloWorldEvaluator(CodeEvaluator):
    def evaluate(
        self,
        *,
        dataset_row: Optional[Mapping[str, JSONSerializable]] = None,
        **_: Any,
    ) -> EvaluationResult:
        span_attribute = dataset_row.get("attributes.llm.output_messages.0.message.content") if dataset_row else None
        is_hello_world = span_attribute == "Hello, World!"
        label = "contains hello world" if is_hello_world else "does not contain hello world"
        return EvaluationResult(
            score=float(is_hello_world),
            label=label,
            explanation=(
                "span_attribute matches 'Hello, World!'"
                if is_hello_world
                else f"span_attribute does not match 'Hello, World!' (found: {span_attribute})"
            ),
        )"""

evaluator: dict = client.create_code_evaluator(
    name="Hello World Checker",
    code_block=code,
    evaluation_class="HelloWorldEvaluator",
    metric_name="hello_world_score",
    span_attributes=["attributes.llm.output_messages"],
    description="Checks if output matches Hello World",
    package_imports=imports,
)
```

Creates a code (Python-based) evaluator that uses custom Python code to evaluate LLM outputs. This is useful for deterministic checks, business logic, or calculations that don't require an LLM.

#### Code Evaluator Format

The code block must follow a specific format required by the Arize platform:

1. **Class** – Must extend `CodeEvaluator` (e.g., `class MyEval(CodeEvaluator):`)
1. **Method** – Must define an `evaluate` method
1. **Return type** – The `evaluate` method should return an `EvaluationResult(score=..., label=..., explanation=...)`
1. **Data access** – Span data is passed via the `dataset_row` parameter as a mapping of attribute paths to values

The required base class imports (`EvaluationResult`, `CodeEvaluator`, `JSONSerializable`) are provided by the Arize platform and should be listed in `package_imports`:

```python
package_imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""
```

**Validation** – The toolkit validates that:

- `code_block` contains a class extending `CodeEvaluator`
- `evaluation_class` matches the class name defined in `code_block`
- The class defines an `evaluate` method
- `package_imports` (if provided) contains only valid Python import statements
- `span_attributes` is a non-empty list

**Required parameters**

- `name` – Display name for the evaluator in the Arize UI.
- `code_block` – Python code defining the evaluator class. Must extend `CodeEvaluator` and contain an `evaluate` method.
- `evaluation_class` – Name of the evaluator class in the code block (must match exactly).
- `metric_name` – Name of the evaluator metric/output (e.g., `"response_length_score"`).
- `span_attributes` – List of span attribute names to pass as inputs (e.g., `["attributes.output.value", "attributes.input.value"]`).

**Optional parameters**

- `commit_message` – Version control message (default: `"Initial version"`).
- `description` – Human-readable description of what this evaluator does.
- `tags` – List of tags for the evaluator.
- `data_granularity_type` – Evaluation granularity: `"span"`, `"trace"`, or `"session"` (default: `"span"`).
- `position` – Display position/order of the evaluator (default: `0`).
- `package_imports` – Python import statements required by the evaluator code (must be valid `import` / `from ... import` lines).
- `evaluation_input_params` – Additional input parameters as a JSON object.
- `query_filter` – Optional query filter over a given data granularity.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – The task type (`"code_evaluation"`)
- `commitHash` – Version commit hash
- `commitMessage` – Version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Examples**

```python
imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""

# Response length checker
length_code = """class ResponseLengthEvaluator(CodeEvaluator):
    def evaluate(self, *, dataset_row=None, **_):
        output = dataset_row.get("attributes.output.value") if dataset_row else None
        length = len(output) if output else 0
        if length < 50:
            return EvaluationResult(score=0, label="too_short", explanation="Response under 50 chars")
        elif length > 500:
            return EvaluationResult(score=0, label="too_long", explanation="Response over 500 chars")
        else:
            return EvaluationResult(score=1, label="appropriate")"""

length_eval = client.create_code_evaluator(
    name="Response Length Checker",
    code_block=length_code,
    evaluation_class="ResponseLengthEvaluator",
    metric_name="response_length_score",
    span_attributes=["attributes.output.value"],
    description="Checks if response length is appropriate",
    package_imports=imports,
)

# Custom business logic evaluator
policy_code = """class PolicyComplianceEvaluator(CodeEvaluator):
    def evaluate(self, *, dataset_row: Optional[Mapping[str, JSONSerializable]]=None, **_):
        output = dataset_row.get("attributes.output.value", "") if dataset_row else ""
        prohibited = ["guarantee", "promise", "always"]
        violations = [t for t in prohibited if t in output.lower()]
        if violations:
            return EvaluationResult(
                score=0,
                label="non_compliant",
                explanation=f"Found prohibited terms: {', '.join(violations)}",
            )
        return EvaluationResult(score=1, label="compliant")"""

policy_eval = client.create_code_evaluator(
    name="Policy Compliance",
    code_block=policy_code,
    evaluation_class="PolicyComplianceEvaluator",
    metric_name="policy_compliance_score",
    span_attributes=["attributes.output.value", "attributes.input.value"],
    description="Ensures responses comply with company policies",
    package_imports=imports,
)
```

______________________________________________________________________

### `create_template_evaluator_version`

```python
evaluator: dict = client.create_template_evaluator_version(
    evaluator_id="eval123",
    metric_name="hallucination_score",
    template="Updated prompt: {{output}}",
    commit_message="Improved prompt wording",
)
```

Creates a new version of an existing template evaluator with updated configuration.

**Required parameters**

- `evaluator_id` – The ID of the evaluator to create a new version for.
- `metric_name` – The name of the evaluator metric.
- `template` – The updated prompt template with `{{variables}}`.

**Optional parameters**

- `commit_message` – Version control message for this version.
- `position` – Display position/order of the evaluator (default: `0`).
- `include_explanations` – Whether to include explanations (default: `True`).
- `use_function_calling` – Whether to use function calling if available (default: `False`).
- `rails` – Rails associated with the config.
- `query_filter` – Optional query filter over a given data granularity.
- `classification_choices` – Dictionary mapping labels to scores.
- `direction` – `"maximize"` or `"minimize"`.
- `data_granularity_type` – `"span"`, `"trace"`, or `"session"`.
- `llm_integration_name` – Name of the LLM integration to use.
- `llm_model_name` – The LLM model name.
- `llm_invocation_parameters` – Parameters used when running the LLM.
- `llm_provider_parameters` – Parameters used to initialize the LLM provider.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – The task type (`"template_evaluation"`)
- `commitHash` – New version commit hash
- `commitMessage` – New version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Example**

```python
updated = client.create_template_evaluator_version(
    evaluator_id="eval123",
    metric_name="hallucination_score",
    template="Revised: Does the response contain errors?\n\nContext: {{context}}\nResponse: {{output}}",
    commit_message="Simplified prompt for better accuracy",
    classification_choices={"Yes": 0, "No": 1},
    llm_integration_name="My OpenAI Integration",
    llm_model_name="gpt-4o",
)
print(updated["commitHash"])
```

______________________________________________________________________

### `create_code_evaluator_version`

```python
imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""

evaluator: dict = client.create_code_evaluator_version(
    evaluator_id="eval123",
    metric_name="response_length_score",
    code_block="class Eval(CodeEvaluator):\n    def evaluate(self, *, dataset_row: Optional[Mapping[str, JSONSerializable]]=None, **_):\n        return EvaluationResult(score=1, label='pass')",
    evaluation_class="Eval",
    span_attributes=["attributes.output.value"],
    commit_message="Updated scoring logic",
    package_imports=imports,
)
```

Creates a new version of an existing code evaluator with updated code and configuration.

**Required parameters**

- `evaluator_id` – The ID of the evaluator to create a new version for.
- `metric_name` – The name of the evaluator metric.
- `code_block` – Updated Python code defining the evaluator class (must extend `CodeEvaluator` with an `evaluate` method).
- `evaluation_class` – Name of the evaluator class in the code block.
- `span_attributes` – List of span attribute names to pass as inputs.

**Optional parameters**

- `commit_message` – Version control message for this version.
- `position` – Display position/order of the evaluator (default: `0`).
- `data_granularity_type` – `"span"`, `"trace"`, or `"session"`.
- `package_imports` – Python import statements required by the evaluator code (must be valid import lines).
- `evaluation_input_params` – Additional input parameters as a JSON object.
- `query_filter` – Optional query filter over a given data granularity.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Evaluator display name
- `description` – Evaluator description
- `taskType` – The task type (`"code_evaluation"`)
- `commitHash` – New version commit hash
- `commitMessage` – New version commit message
- `tags` – List of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Example**

```python
imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""

new_code = """class ResponseLengthEvaluator(CodeEvaluator):
    def evaluate(self, *, dataset_row: Optional[Mapping[str, JSONSerializable]]=None, **_):
        output = dataset_row.get("attributes.output.value") if dataset_row else None
        length = len(output) if output else 0
        score = min(length / 200, 1.0)  # Normalized score
        return EvaluationResult(score=score, label="length_check")"""

updated = client.create_code_evaluator_version(
    evaluator_id="eval456",
    metric_name="response_length_score",
    code_block=new_code,
    evaluation_class="ResponseLengthEvaluator",
    span_attributes=["attributes.output.value"],
    commit_message="Switched to normalized scoring",
    package_imports=imports,
)
print(updated["commitHash"])
```

______________________________________________________________________

### `edit_evaluator`

```python
evaluator: dict = client.edit_evaluator(
    evaluator_id="eval123",
    name="Updated Name",
    description="Updated description",
    tags=["production", "llm"],
)
```

Edits an evaluator's metadata (name, description, tags). This does not create a new version — it updates the top-level evaluator record.

**Parameters**

- `evaluator_id` – **Required.** The ID of the evaluator to edit.
- `name` – (optional) New name for the evaluator.
- `description` – (optional) New description.
- `tags` – (optional) Complete replacement list of tags.

**Returns**

A dictionary containing:

- `id` – Unique evaluator ID
- `name` – Updated evaluator display name
- `description` – Updated evaluator description
- `taskType` – `"template_evaluation"` or `"code_evaluation"`
- `commitHash` – Latest version commit hash
- `commitMessage` – Latest version commit message
- `tags` – Updated list of tags
- `createdAt` – Creation timestamp
- `updatedAt` – Last update timestamp
- `createdBy` – User who created the evaluator

**Example**

```python
updated = client.edit_evaluator(
    evaluator_id="eval123",
    name="Hallucination Detector v2",
    tags=["production", "hallucination", "llm"],
)
print(updated["name"])
```

______________________________________________________________________

### `delete_evaluator`

```python
success: bool = client.delete_evaluator(evaluator_id: str)
```

Permanently deletes an evaluator and all of its versions.

**Parameters**

- `evaluator_id` – **Required.** The ID of the evaluator to delete.

**Returns**

- `bool` – `True` if the evaluator was deleted successfully.

**Example**

```python
# Get the evaluator ID first
evaluator = client.get_evaluator("Old Evaluator")
success = client.delete_evaluator(evaluator["id"])
print("Deleted" if success else "Failed")
```

______________________________________________________________________

## Annotation Operations

### `create_annotation`

```python
success: bool = client.create_annotation(
    name="human_label",
    updated_by="duncan",
    record_id="abc123",
    annotation_type="label",  # "label", "score", or "text"
    annotation_config_id="config_123",
    model_name="fraud-detection-v3",
    label="fraud",  # required when annotation_type="label"
    model_environment="production",
    start_time="2024-05-01T10:00:00Z",  # optional, defaults to now
)
```

Adds a label, score, or text annotation to a specific record.

**Required parameters**

- `name` – Logical annotation name (e.g. "ground_truth").
- `updated_by` – User or process writing the annotation.
- `record_id` – Identifier of the record being annotated.
- `annotation_type` – "label", "score", or "text".
- `annotation_config_id` – ID of the annotation configuration.
- *Either* `model_name` **or** `model_id`.
- `label`, `score`, or `text` depending on `annotation_type`.

**Optional parameters**

- `model_environment` – Environment name; defaults to "tracing".
- `start_time` – Timestamp; defaults to now.

**Returns**

`True` when the annotation is accepted.

**Examples**

```python
# Label annotation
ok = client.create_annotation(
    name="sentiment",
    updated_by="qa_bot",
    record_id="rec_123",
    annotation_type="label",
    annotation_config_id="config_456",
    label="positive",
    model_name="support-bot",
)

# Score annotation
ok = client.create_annotation(
    name="quality_score",
    updated_by="qa_bot",
    record_id="rec_123",
    annotation_type="score",
    annotation_config_id="config_789",
    score=0.9,
    model_name="support-bot",
)

# Text annotation
ok = client.create_annotation(
    name="feedback",
    updated_by="human_reviewer",
    record_id="rec_123",
    annotation_type="text",
    annotation_config_id="config_012",
    text="This response was very helpful and accurate",
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

# 3. Create evaluators to automatically assess responses
# Template evaluator (LLM-based)
client.create_template_evaluator(
    name="Helpfulness Detector",
    template="Was this response helpful?\n\nQuestion: {{input}}\nResponse: {{output}}\n\nAnswer: Yes or No",
    metric_name="helpfulness_score",
    classification_choices={"Yes": 1, "No": 0},
    direction="maximize",
)

# Code evaluator (Python-based)
imports = """from typing import Any, Optional, Mapping
from arize.experimental.datasets.experiments.evaluators.base import (
    EvaluationResult,
    CodeEvaluator,
    JSONSerializable,
)"""

code = """class ResponseQualityEvaluator(CodeEvaluator):
    def evaluate(self, *, dataset_row: Optional[Mapping[str, JSONSerializable]]=None, **_):
        output = dataset_row.get("attributes.output.value") if dataset_row else None
        if not output:
            return EvaluationResult(score=0, label="empty", explanation="No output found")
        length = len(output)
        has_greeting = any(w in output.lower() for w in ["hello", "hi", "hey"])
        score = min(length / 200, 1.0) * (1.1 if has_greeting else 1.0)
        return EvaluationResult(score=min(score, 1.0), label="scored")"""

client.create_code_evaluator(
    name="Response Quality Check",
    code_block=code,
    evaluation_class="ResponseQualityEvaluator",
    metric_name="response_quality_score",
    span_attributes=["attributes.output.value"],
    package_imports=imports,
)

# 4. List all evaluators in the space
for e in client.get_evaluators():
    print(e["name"], e["taskType"])

# 5. Attach a human label to the response record later
client.create_annotation(
    name="user_feedback",
    updated_by="analyst",
    record_id="resp_789",
    annotation_type="score",
    annotation_config_id="config_1234",
    score=4.5,
    model_name="support-bot",
)
```
