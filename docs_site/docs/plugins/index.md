# Claude Code Plugin Marketplace

Arize Toolkit includes a [Claude Code](https://code.claude.com) plugin marketplace that provides AI-assisted workflows for interacting with the Arize platform. These plugins give Claude Code specialized knowledge about the Arize API, CLI, and development patterns.

## Available Plugins

### arize-toolkit

User-facing plugin with skills for querying and managing the Arize platform.

| Skill | Description |
|-------|-------------|
| `arize-graphql-analytics` | Query and explore the Arize GraphQL API, build and validate queries/mutations |
| `arize-toolkit-cli` | Manage Arize resources (models, monitors, prompts, traces, etc.) via the CLI |
| `arize-traces` | Retrieve and debug trace data — list traces, inspect spans, analyze performance |

### arize-toolkit-dev

Developer plugin with workflows for contributing to the Arize Toolkit codebase.

| Skill | Description |
|-------|-------------|
| `new-query-workflow` | Complete 7-phase workflow for adding new GraphQL queries/mutations with models, types, tests, CLI commands, and docs |

## Installation

### Add the marketplace

```shell
/plugin marketplace add duncankmckinnon/arize_toolkit
```

### Install plugins

```shell
# Install user-facing tools
/plugin install arize-toolkit@arize-toolkit

# Install developer tools
/plugin install arize-toolkit-dev@arize-toolkit
```

### Use skills

Once installed, skills are available via namespaced slash commands:

```shell
# Query Arize data via GraphQL
/arize-toolkit:arize-graphql-analytics

# Manage resources with the CLI
/arize-toolkit:arize-toolkit-cli

# Debug traces
/arize-toolkit:arize-traces

# Add a new query to the codebase (developers)
/arize-toolkit-dev:new-query-workflow
```

Skills are also triggered automatically when Claude detects a relevant task — for example, asking "list my models" will invoke the CLI skill.

## Plugin Details

### arize-graphql-analytics

Provides a complete workflow for querying the Arize GraphQL API:

1. **Check API Key** — verifies `ARIZE_API_KEY` is set
1. **Fetch Schema** — introspects the full GraphQL schema
1. **Build Query** — constructs queries using Relay connection patterns
1. **Execute** — runs queries via `curl`
1. **Summarize** — presents results in a readable format

Includes reference docs for common query patterns, Relay connections, mutations, filtering, and error handling.

### arize-toolkit-cli

Covers all CLI command groups:

- `config` — profile management
- `spaces` / `orgs` / `users` — organization navigation
- `models` / `projects` — model and project management
- `monitors` — monitor creation, copying, and alerting
- `prompts` — prompt template management
- `custom-metrics` / `evaluators` — metrics and evaluation
- `dashboards` — dashboard creation
- `imports` — data import from cloud storage and databases
- `traces` — trace listing and span inspection

### arize-traces

Specialized trace debugging workflow:

1. **Discover Columns** — finds available trace/span attributes
1. **List Traces** — queries traces with time windows, sorting, and filtering
1. **Get Trace Detail** — retrieves full span trees with parent-child relationships
1. **Export** — supports CSV and JSON output for analysis

### new-query-workflow

Seven-phase development workflow with validation checkpoints:

1. **GraphQL Development** — develop and test the query
1. **Component Discovery** — identify required types, models, file locations
1. **Gap Analysis** — determine what to create vs. reuse
1. **Implementation** — create enums, models, queries, client methods
1. **Testing** — type, model, query, and client tests
1. **CLI Integration** — add CLI commands with Click
1. **Documentation** — update tool docs and index

## Local Development

To test plugins locally without installing from the marketplace:

```bash
# Load both plugins for development
claude --plugin-dir ./plugins/arize-toolkit --plugin-dir ./plugins/arize-toolkit-dev
```

## Plugin Structure

```
plugins/
├── arize-toolkit/
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       ├── arize-graphql-analytics/
│       │   ├── SKILL.md
│       │   └── references/
│       ├── arize-toolkit-cli/
│       │   ├── SKILL.md
│       │   └── references/
│       └── arize-traces/
│           ├── SKILL.md
│           └── references/
└── arize-toolkit-dev/
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
        └── new-query-workflow/
            ├── SKILL.md
            └── references/
```

The marketplace catalog is defined in `.claude-plugin/marketplace.json` at the repository root.
