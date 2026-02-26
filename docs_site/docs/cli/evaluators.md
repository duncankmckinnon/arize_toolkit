# Evaluators

## Overview

The `evaluators` command group manages Arize evaluators — automated evaluation pipelines that can use either LLM-based templates or Python code to assess model outputs.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`evaluators list`](#evaluators-list) | List evaluators | `get_evaluators` |
| [`evaluators get`](#evaluators-get) | Get an evaluator by name | `get_evaluator` |
| [`evaluators create-template`](#evaluators-create-template) | Create an LLM template evaluator | `create_template_evaluator` |
| [`evaluators create-code`](#evaluators-create-code) | Create a Python code evaluator | `create_code_evaluator` |
| [`evaluators edit`](#evaluators-edit) | Edit evaluator metadata | `edit_evaluator` |
| [`evaluators delete`](#evaluators-delete) | Delete an evaluator | `delete_evaluator` |

______________________________________________________________________

### `evaluators list`

```bash
arize_toolkit evaluators list [--search TEXT] [--name TEXT] [--task-type TYPE]
```

Lists evaluators with optional filtering.

**Options**

- `--search` (optional) — Search by name substring.
- `--name` (optional) — Filter by exact name.
- `--task-type` (optional) — Filter by type: `template_evaluation` or `code_evaluation`.

**Example**

```bash
arize_toolkit evaluators list
arize_toolkit evaluators list --task-type template_evaluation
```

______________________________________________________________________

### `evaluators get`

```bash
arize_toolkit evaluators get NAME
```

Retrieves full details for an evaluator, including its configuration.

**Arguments**

- `NAME` — The evaluator name.

**Example**

```bash
arize_toolkit --json evaluators get "hallucination-detector"
```

______________________________________________________________________

### `evaluators create-template`

```bash
arize_toolkit evaluators create-template NAME --template TEXT --metric-name NAME [OPTIONS]
```

Creates an LLM-based template evaluator that uses a prompt to evaluate model outputs.

**Arguments**

- `NAME` — Name for the evaluator.

**Required Options**

- `--template` — The prompt template string, or `@filepath` to read from a file. Use `{{variables}}` for template substitution.
- `--metric-name` — Name for the output metric.

**Key Options**

- `--commit-message` — Version message. Defaults to `"Initial version"`.
- `--description` — Evaluator description.
- `--tag` — Tags (repeatable).
- `--classification-choices` — JSON mapping labels to scores (e.g. `'{"Yes":0,"No":1}'`).
- `--direction` — Score direction: `maximize` or `minimize`. Defaults to `maximize`.
- `--data-granularity` — Granularity: `span`, `trace`, or `session`. Defaults to `span`.
- `--include-explanations / --no-explanations` — Include LLM explanations. Defaults to enabled.
- `--use-function-calling / --no-function-calling` — Use function calling. Defaults to disabled.
- `--llm-integration-name` — LLM integration name.
- `--llm-model-name` — LLM model name (e.g. `gpt-4o`).

**Example**

```bash
# Inline template
arize_toolkit evaluators create-template "hallucination-detector" \
    --template "Does the response contain factual errors?\n\nContext: {{context}}\nResponse: {{output}}" \
    --metric-name hallucination_score \
    --classification-choices '{"Yes": 0, "No": 1}' \
    --description "Detects hallucinations in LLM responses"

# Template from file
arize_toolkit evaluators create-template "relevance-eval" \
    --template @templates/relevance.txt \
    --metric-name relevance_score \
    --llm-model-name gpt-4o
```

______________________________________________________________________

### `evaluators create-code`

```bash
arize_toolkit evaluators create-code NAME --metric-name NAME --code TEXT --evaluation-class CLASS --span-attribute ATTR... [OPTIONS]
```

Creates a Python code evaluator. The code must define a class that extends `CodeEvaluator` with an `evaluate` method.

**Arguments**

- `NAME` — Name for the evaluator.

**Required Options**

- `--metric-name` — Name for the output metric.
- `--code` — Python code string, or `@filepath` to read from a file.
- `--evaluation-class` — The class name in the code block.
- `--span-attribute` — Span attributes to pass as inputs (repeatable, e.g. `--span-attribute output --span-attribute input`).

**Key Options**

- `--commit-message` — Version message. Defaults to `"Initial version"`.
- `--description` — Evaluator description.
- `--tag` — Tags (repeatable).
- `--data-granularity` — Granularity: `span`, `trace`, or `session`. Defaults to `span`.
- `--package-imports` — Python import statements.

**Example**

```bash
arize_toolkit evaluators create-code "response-length" \
    --metric-name response_length \
    --code @evaluators/length_check.py \
    --evaluation-class ResponseLengthEvaluator \
    --span-attribute output \
    --description "Checks response length"
```

______________________________________________________________________

### `evaluators edit`

```bash
arize_toolkit evaluators edit EVALUATOR_ID [--name NAME] [--description TEXT] [--tag TAG]...
```

Edits an evaluator's metadata. Does not create a new version.

**Arguments**

- `EVALUATOR_ID` — The evaluator ID.

**Options**

- `--name` (optional) — Updated name.
- `--description` (optional) — Updated description.
- `--tag` (optional) — Updated tags (repeatable).

**Example**

```bash
arize_toolkit evaluators edit "eval-123" --name "hallucination-v2" --tag production
```

______________________________________________________________________

### `evaluators delete`

```bash
arize_toolkit evaluators delete EVALUATOR_ID [--yes]
```

Deletes an evaluator. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `EVALUATOR_ID` — The evaluator ID.

**Options**

- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit evaluators delete "eval-123" --yes
```
