# Command-Line Interface

## Overview

The Arize Toolkit CLI lets you manage models, monitors, prompts, evaluators, dashboards, traces, and more directly from your terminal — no Python scripting required.

Every command maps 1-to-1 to a method on the Python `Client`, so anything you can do in code you can also do from the command line.

Key features:

1. **Rich table output** by default, with a `--json` flag for machine-readable JSON
1. **Configuration profiles** stored in `~/.arize_toolkit/config.toml` (similar to AWS CLI profiles)
1. **`projects` alias** — `arize_toolkit projects list` and `arize_toolkit models list` are interchangeable

## Installation

The CLI is an optional extra. Install it alongside the core library:

```bash
pip install arize_toolkit[cli]
```

This pulls in [Click](https://click.palletsprojects.com/) for command parsing, [Rich](https://rich.readthedocs.io/) for terminal output, and TOML libraries for profile management.

## Quick Setup

### 1. Create a configuration profile

```bash
arize_toolkit config init
```

You will be prompted for your **Developer API Key**, **organization name**, **space name**, and **app URL**. The result is saved to `~/.arize_toolkit/config.toml`.

### 2. Verify the connection

```bash
arize_toolkit spaces list
```

If everything is configured correctly you will see a table of spaces in your organization.

### 3. Try a few commands

```bash
# List all models / projects
arize_toolkit models list

# Get details for a specific model (JSON output)
arize_toolkit --json models get "fraud-detection-v3"

# List monitors filtered by category
arize_toolkit monitors list --model-name "fraud-detection-v3" --category performance

# List all prompts
arize_toolkit prompts list
```

## Global Options

Every command accepts the following flags. They can appear **before** the subcommand:

| Flag | Description |
|------|-------------|
| `--profile NAME` | Use a named configuration profile instead of `default` |
| `--json` | Output raw JSON instead of Rich tables |
| `--api-key KEY` | Override the API key for this invocation |
| `--org NAME` | Override the organization name |
| `--space NAME` | Override the space name |
| `--app-url URL` | Override the Arize app URL |
| `--help` | Show help for any command or group |

**Configuration resolution order** (highest priority first):

1. CLI flags (`--api-key`, `--org`, `--space`)
1. Environment variables (`ARIZE_DEVELOPER_KEY`, `ARIZE_ORGANIZATION`, `ARIZE_SPACE`)
1. Profile from `~/.arize_toolkit/config.toml`

## Command Groups

| Group | Description | Page |
|-------|-------------|------|
| `config` | Manage configuration profiles | [Configuration](config.md) |
| `spaces` | List, create, and switch spaces | [Spaces](spaces.md) |
| `orgs` | List and create organizations | [Organizations](orgs.md) |
| `users` | Search users and manage space membership | [Users](users.md) |
| `models` / `projects` | List models, check volume, pull performance metrics | [Models & Projects](models.md) |
| `monitors` | Create, list, copy, and delete monitors | [Monitors](monitors.md) |
| `prompts` | Manage prompt templates and versions | [Prompts](prompts.md) |
| `custom-metrics` | Create and manage custom metrics | [Custom Metrics](custom_metrics.md) |
| `evaluators` | Manage LLM and code evaluators | [Evaluators](evaluators.md) |
| `dashboards` | Create and view dashboards | [Dashboards](dashboards.md) |
| `traces` | List traces, get spans, and discover available columns | [Traces](traces.md) |
| `imports` | Manage file and table import jobs | [Data Imports](imports.md) |

## JSON Mode

Pass `--json` before the subcommand to get raw JSON output. This is useful for piping results to `jq` or other tools:

```bash
# Pretty-print all model names
arize_toolkit --json models list | jq '.[].name'

# Store monitor details in a file
arize_toolkit --json monitors get "accuracy-monitor" --model "fraud-detection-v3" > monitor.json
```

## Profiles

Profiles let you maintain separate configurations for different environments:

```bash
# Create a profile for staging
arize_toolkit config init --profile-name staging

# Use it for a single command
arize_toolkit --profile staging models list

# Switch the default profile
arize_toolkit config use staging
```

See [Configuration](config.md) for full details.
