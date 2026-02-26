# Organizations

## Overview

The `orgs` command group manages Arize organizations. Organizations are the top-level account container that hold one or more spaces.

| Command | Description | Client Method |
|---------|-------------|---------------|
| [`orgs list`](#orgs-list) | List all organizations | `get_all_organizations` |
| [`orgs create`](#orgs-create) | Create a new organization and space | `create_new_organization_and_space` |

______________________________________________________________________

### `orgs list`

```bash
arize_toolkit orgs list
```

Lists all organizations in your account with their IDs and creation dates.

**Example**

```bash
$ arize_toolkit orgs list
               Organizations
┌──────────┬──────────────┬────────────┐
│ id       │ name         │ createdAt  │
├──────────┼──────────────┼────────────┤
│ org123   │ acme-corp    │ 2024-01-15 │
└──────────┴──────────────┴────────────┘
```

______________________________________________________________________

### `orgs create`

```bash
arize_toolkit orgs create ORG_NAME SPACE_NAME [--description TEXT] [--space-private | --space-public]
```

Creates a new organization with an initial space.

**Arguments**

- `ORG_NAME` — Name for the new organization.
- `SPACE_NAME` — Name for the initial space within the organization.

**Options**

- `--description` (optional) — A description for the organization.
- `--space-private / --space-public` — Whether the initial space is private. Defaults to `--space-public`.

**Example**

```bash
$ arize_toolkit orgs create "new-team" "main-space" --description "Team workspace"
Created: https://app.arize.com/organizations/new-team/spaces/main-space
```
