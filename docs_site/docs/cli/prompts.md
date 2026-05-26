# Prompts

## Overview

The `prompts` command group manages prompt templates and their versions. Prompts store LLM message templates with variable substitution, tool configurations, and provider settings.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`prompts list`](#prompts-list) | List all prompts | `get_all_prompts` |
| [`prompts get`](#prompts-get) | Get a prompt by name | `get_prompt` |
| [`prompts versions`](#prompts-versions) | List all versions of a prompt | `get_all_prompt_versions` |
| [`prompts create`](#prompts-create) | Create a prompt or new version | `create_prompt` |
| [`prompts update`](#prompts-update) | Update prompt metadata | `update_prompt` |
| [`prompts delete`](#prompts-delete) | Delete a prompt | `delete_prompt` |

______________________________________________________________________

### `prompts list`

```bash
arize_toolkit prompts list
```

Lists all prompts in the current space.

**Example**

```bash
$ arize_toolkit prompts list
                        Prompts
┌──────────┬───────────────────┬──────────────┬────────────┐
│ id       │ name              │ description  │ createdAt  │
├──────────┼───────────────────┼──────────────┼────────────┤
│ p1       │ qa-system-prompt  │ QA pipeline  │ 2025-01-10 │
│ p2       │ summarizer        │ Summarize... │ 2025-02-01 │
└──────────┴───────────────────┴──────────────┴────────────┘
```

______________________________________________________________________

### `prompts get`

```bash
arize_toolkit prompts get NAME
```

Retrieves full details for a prompt including messages, provider settings, and tools.

**Arguments**

- `NAME` — The prompt name.

**Example**

```bash
arize_toolkit --json prompts get "qa-system-prompt"
```

______________________________________________________________________

### `prompts versions`

```bash
arize_toolkit prompts versions NAME
```

Lists all versions of a prompt with their commit messages.

**Arguments**

- `NAME` — The prompt name.

**Example**

```bash
arize_toolkit prompts versions "qa-system-prompt"
```

______________________________________________________________________

### `prompts create`

```bash
arize_toolkit prompts create NAME --messages JSON [OPTIONS]
```

Creates a new prompt or a new version if a prompt with the same name already exists.

**Arguments**

- `NAME` — The prompt name.

**Required Options**

- `--messages` — A JSON array of message objects, either inline or from a file using `@filepath`.

**Optional Options**

- `--commit-message` — Commit message. Defaults to `"created prompt"`.
- `--description` — Prompt description.
- `--tag` — Tags (repeatable).
- `--provider` — LLM provider: `openAI`, `awsBedrock`, `azureOpenAI`, `vertexAI`, `custom`.
- `--model-name` — LLM model name (e.g. `gpt-4o`).
- `--input-variable-format` — Variable format: `f_string`, `mustache`, `none`.

**Message Format**

Messages should be a JSON array:

```json
[
  {"role": "system", "content": "You are a helpful assistant."},
  {"role": "user", "content": "{question} {context}"}
]
```

**Examples**

```bash
# Inline JSON
arize_toolkit prompts create "qa-prompt" \
    --messages '[{"role":"system","content":"Answer questions."},{"role":"user","content":"{question}"}]' \
    --provider openAI \
    --model-name gpt-4o

# From a file
arize_toolkit prompts create "qa-prompt" \
    --messages @messages.json \
    --description "QA system prompt" \
    --tag production --tag v2
```

______________________________________________________________________

### `prompts update`

```bash
arize_toolkit prompts update NAME [--new-name NAME] [--description TEXT] [--tag TAG]...
```

Updates a prompt's metadata (name, description, tags). This does not create a new version — use `prompts create` with the same name for that.

**Arguments**

- `NAME` — The current prompt name.

**Options**

- `--new-name` (optional) — Rename the prompt.
- `--description` (optional) — Updated description.
- `--tag` (optional) — Updated tags (repeatable). Replaces existing tags.

**Example**

```bash
arize_toolkit prompts update "qa-prompt" --new-name "qa-prompt-v2" --tag production
```

______________________________________________________________________

### `prompts delete`

```bash
arize_toolkit prompts delete NAME [--yes]
```

Deletes a prompt and all its versions. Prompts for confirmation unless `--yes` is passed.

**Arguments**

- `NAME` — The prompt name.

**Options**

- `--yes` — Skip confirmation.

**Example**

```bash
arize_toolkit prompts delete "old-prompt" --yes
```
