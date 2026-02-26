# Configuration

## Overview

The `config` command group manages CLI configuration profiles stored in `~/.arize_toolkit/config.toml`. Profiles let you store credentials and defaults for different Arize environments (production, staging, etc.) and switch between them.

| Command | Description |
|---------|-------------|
| [`config init`](#config-init) | Interactive setup — create or update a profile |
| [`config list`](#config-list) | List all saved profiles |
| [`config show`](#config-show) | Show details for a specific profile |
| [`config use`](#config-use) | Switch the default profile |

## Configuration File

Profiles are stored in TOML format at `~/.arize_toolkit/config.toml`:

```toml
[default]
api_key = "your-api-key"
organization = "my-org"
space = "production-space"
app_url = "https://app.arize.com"

[staging]
api_key = "staging-api-key"
organization = "my-org"
space = "staging-space"
app_url = "https://app.arize.com"
```

### Resolution Order

When determining which credentials to use, the CLI checks these sources from highest to lowest priority:

1. **CLI flags** — `--api-key`, `--org`, `--space`, `--app-url`
1. **Environment variables** — `ARIZE_DEVELOPER_KEY`, `ARIZE_ORGANIZATION`, `ARIZE_SPACE`, `ARIZE_APP_URL`
1. **Profile** — the `default` profile, or one specified with `--profile`

______________________________________________________________________

## Commands

### `config init`

```bash
arize_toolkit config init [--profile-name NAME]
```

Interactively prompts for credentials and saves them to a profile. The API key input is hidden for security.

**Options**

- `--profile-name` (optional) — Name for this profile. Defaults to `"default"`.

**Example**

```bash
$ arize_toolkit config init --profile-name staging
Arize Developer Key: ********
Organization name: my-org
Space name: staging-space
Arize app URL [https://app.arize.com]:
Profile 'staging' saved to /Users/you/.arize_toolkit/config.toml
```

______________________________________________________________________

### `config list`

```bash
arize_toolkit config list
```

Lists all saved profiles with their organization and space names.

**Example**

```bash
$ arize_toolkit config list
  default: org=my-org, space=production-space
  staging: org=my-org, space=staging-space
```

______________________________________________________________________

### `config show`

```bash
arize_toolkit config show [--profile-name NAME]
```

Displays the settings for a profile. The API key is masked for security.

**Options**

- `--profile-name` (optional) — Profile to show. Defaults to `"default"`.

**Example**

```bash
$ arize_toolkit config show --profile-name staging
  api_key: ***
  organization: my-org
  space: staging-space
  app_url: https://app.arize.com
```

______________________________________________________________________

### `config use`

```bash
arize_toolkit config use NAME
```

Switches the default profile. The previous default is preserved under the given name.

**Arguments**

- `NAME` — The profile to promote to `default`.

**Example**

```bash
$ arize_toolkit config use staging
Switched default profile to 'staging'.
```

After this command, running `arize_toolkit models list` will use the `staging` credentials by default. You can still override with `--profile`:

```bash
arize_toolkit --profile default models list
```
