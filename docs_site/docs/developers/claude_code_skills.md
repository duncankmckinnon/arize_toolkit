# Claude Code Plugins

This repository is a [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) that distributes AI-assisted development tools as installable plugins. See the [Plugin Marketplace](../plugins/index.md) page for full details on available plugins and installation.

## Quick Install

```shell
# Add the marketplace
claude plugin marketplace add duncankmckinnon/arize_toolkit

# Install user-facing tools (GraphQL, CLI, Traces)
claude plugin install arize-toolkit@arize-toolkit

# Install developer tools (new-query-workflow)
claude plugin install arize-toolkit-dev@arize-toolkit
```

## Available Plugins

### arize-toolkit (User-Facing)

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `arize-toolkit-cli` | `/arize-toolkit:arize-toolkit-cli` | Manage Arize resources via the CLI |
| `arize-traces` | `/arize-toolkit:arize-traces` | Retrieve and debug trace data |

### arize-toolkit-dev (Developer)

| Skill | Invocation | Description |
|-------|-----------|-------------|
| `arize-graphql-analytics` | `/arize-toolkit:arize-graphql-analytics` | Query and explore the Arize GraphQL API, build and validate queries |
| `new-query-workflow` | `/arize-toolkit-dev:new-query-workflow` | Complete workflow for adding new GraphQL queries/mutations |

Skills are also triggered automatically when Claude detects a relevant task — for example, asking "list my models" will invoke the CLI skill.

## Local Development

To test plugins locally without installing from the marketplace:

```bash
claude --plugin-dir ./plugins/arize-toolkit --plugin-dir ./plugins/arize-toolkit-dev
```

## Plugin Structure

```
.claude-plugin/
└── marketplace.json          # Marketplace catalog

plugins/
├── arize-toolkit/            # User-facing plugin
│   ├── .claude-plugin/
│   │   └── plugin.json
│   └── skills/
│       ├── arize-toolkit-cli/
│       └── arize-traces/
└── arize-toolkit-dev/        # Developer plugin
    ├── .claude-plugin/
    │   └── plugin.json
    └── skills/
        ├── arize-graphql-analytics/
        └── new-query-workflow/
```

## Creating New Skills

To add a new skill to this repository:

1. Choose the appropriate plugin (`arize-toolkit` for user-facing, `arize-toolkit-dev` for developer tools)
1. Create a directory under `plugins/<plugin-name>/skills/` with your skill name
1. Add a `SKILL.md` file with frontmatter (`name`, `description`)
1. Optionally add a `references/` folder for supporting documentation
1. The skill will be available after reinstalling the plugin

See the existing skills for examples of the format and structure.
