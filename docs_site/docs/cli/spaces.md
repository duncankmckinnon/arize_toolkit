# Spaces

## Overview

The `spaces` command group manages Arize spaces within your organization. Spaces are the top-level container for models, monitors, and other Arize resources.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`spaces list`](#spaces-list) | List all spaces in the organization | `get_all_spaces` |
| [`spaces get`](#spaces-get) | Get a space by name | `get_space` |
| [`spaces create`](#spaces-create) | Create a new space | `create_new_space` |
| [`spaces switch`](#spaces-switch) | Switch the active space | `switch_space` |
| [`spaces update`](#spaces-update) | Update a space's properties | `update_space` |
| [`spaces users`](#spaces-users) | List users with access to the space | `get_space_users` |
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

### `spaces update`

```bash
arize_toolkit spaces update [OPTIONS]
```

Updates the properties of a space. By default updates the active space. Only the options you provide will be changed.

**Options**

- `--name` — New name for the space.
- `--space-id` — ID of the space to update (defaults to active space).
- `--private / --public` — Set visibility.
- `--description` — New description.
- `--gradient-start-color` — Hex color code for gradient start.
- `--gradient-end-color` — Hex color code for gradient end.
- `--ml-models-enabled / --ml-models-disabled` — Toggle ML models.

**Example**

```bash
# Update the current space's description
arize_toolkit spaces update --description "Production monitoring"

# Rename and make private
arize_toolkit spaces update --name "Production" --private

# Update a specific space by ID
arize_toolkit spaces update --space-id abc123 --public
```

______________________________________________________________________

### `spaces users`

```bash
arize_toolkit spaces users [--search TEXT] [--user-type human|bot]
```

Lists all users with access to the current space, including explicit members, account admins, and organization admins.

**Options**

- `--search` — Filter users by name or email.
- `--user-type` — Filter by user type: `human` or `bot`.

**Example**

```bash
# List all space users
$ arize_toolkit spaces users
                     Space Users
┌──────────┬──────────────┬─────────────────────┬────────┬──────────────────────┐
│ id       │ name         │ email               │ role   │ membership           │
├──────────┼──────────────┼─────────────────────┼────────┼──────────────────────┤
│ user123  │ Jane Doe     │ jane@example.com    │ admin  │ EXPLICIT_MEMBERSHIP  │
│ user456  │ John Smith   │ john@example.com    │ member │ EXPLICIT_MEMBERSHIP  │
│ user789  │ Org Admin    │ orgadm@example.com  │        │ ORGANIZATION_ADMIN   │
└──────────┴──────────────┴─────────────────────┴────────┴──────────────────────┘

# Search for a specific user
arize_toolkit spaces users --search "jane@example.com"

# List only bot users
arize_toolkit spaces users --user-type bot

# JSON output
arize_toolkit --json spaces users
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
