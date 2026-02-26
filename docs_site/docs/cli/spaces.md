# Spaces

## Overview

The `spaces` command group manages Arize spaces within your organization. Spaces are the top-level container for models, monitors, and other Arize resources.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`spaces list`](#spaces-list) | List all spaces in the organization | `get_all_spaces` |
| [`spaces get`](#spaces-get) | Get a space by name | `get_space` |
| [`spaces create`](#spaces-create) | Create a new space | `create_new_space` |
| [`spaces switch`](#spaces-switch) | Switch the active space | `switch_space` |
| [`spaces create-key`](#spaces-create-key) | Create a space admin API key | `create_space_admin_api_key` |

______________________________________________________________________

### `spaces list`

```bash
arize_toolkit spaces list
```

Lists all spaces in the current organization with their IDs and creation dates.

**Example**

```bash
$ arize_toolkit spaces list
                    Spaces
┌──────────────┬─────────────────┬────────────┐
│ id           │ name            │ createdAt  │
├──────────────┼─────────────────┼────────────┤
│ abc123       │ production      │ 2024-06-01 │
│ def456       │ staging         │ 2024-08-15 │
└──────────────┴─────────────────┴────────────┘
```

______________________________________________________________________

### `spaces get`

```bash
arize_toolkit spaces get NAME
```

Retrieves details for a single space by name.

**Arguments**

- `NAME` — The space name.

**Example**

```bash
arize_toolkit spaces get production
arize_toolkit --json spaces get production
```

______________________________________________________________________

### `spaces create`

```bash
arize_toolkit spaces create NAME [--private | --public] [--no-switch]
```

Creates a new space. By default the space is private and the CLI switches to it immediately.

**Arguments**

- `NAME` — Name for the new space.

**Options**

- `--private / --public` — Visibility. Defaults to `--private`.
- `--no-switch` — Don't set the new space as active after creation.

**Example**

```bash
$ arize_toolkit spaces create "ml-experiments" --public
Space 'ml-experiments' created (id: xyz789).
```

______________________________________________________________________

### `spaces switch`

```bash
arize_toolkit spaces switch NAME [--org ORG]
```

Switches the active space for subsequent client operations.

**Arguments**

- `NAME` — The space name to switch to.

**Options**

- `--org` (optional) — Also switch to a different organization.

**Example**

```bash
arize_toolkit spaces switch staging
```

______________________________________________________________________

### `spaces create-key`

```bash
arize_toolkit spaces create-key NAME
```

Creates a new admin API key for the current space.

**Arguments**

- `NAME` — A label for the API key.

**Example**

```bash
arize_toolkit --json spaces create-key "ci-pipeline-key"
```
