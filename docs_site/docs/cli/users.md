# Users

## Overview

The `users` command group manages users and space membership. Use these commands to look up users and control who has access to which spaces.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`users get`](#users-get) | Search for a user by name or email | `get_user` |
| [`users assign`](#users-assign) | Assign users to spaces | `assign_space_membership` |
| [`users remove`](#users-remove) | Remove a user from a space | `remove_space_member` |

______________________________________________________________________

### `users get`

```bash
arize_toolkit users get SEARCH
```

Searches for a user by name or email address.

**Arguments**

- `SEARCH` — Name or email to search for.

**Example**

```bash
arize_toolkit users get "jane@example.com"
arize_toolkit --json users get "Jane Doe"
```

______________________________________________________________________

### `users assign`

```bash
arize_toolkit users assign USER_NAMES... [--spaces SPACE]... [--role ROLE]
```

Assigns one or more users to one or more spaces. If `--spaces` is omitted, the current space is used.

**Arguments**

- `USER_NAMES` — One or more user names (positional, space-separated).

**Options**

- `--spaces` — Space names to assign to. Can be repeated for multiple spaces.
- `--role` — Role to assign. Choices: `admin`, `member`, `readOnly`, `annotator`. Defaults to `member`.

**Example**

```bash
# Assign a single user to the current space
arize_toolkit users assign "jane@example.com"

# Assign multiple users to multiple spaces with a specific role
arize_toolkit users assign "jane@example.com" "bob@example.com" \
    --spaces production --spaces staging --role admin
```

______________________________________________________________________

### `users remove`

```bash
arize_toolkit users remove USER_NAME [--space SPACE]
```

Removes a user from a space. If `--space` is omitted, the current space is used.

**Arguments**

- `USER_NAME` — The user name to remove.

**Options**

- `--space` (optional) — The space to remove the user from.

**Example**

```bash
arize_toolkit users remove "bob@example.com" --space staging
```
