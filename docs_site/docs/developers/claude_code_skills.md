# Claude Code Skills

This repository includes [Claude Code](https://claude.ai/claude-code) skills that assist with development tasks. These skills provide specialized workflows and knowledge for working with the Arize Toolkit codebase.

## Available Skills

### arize-graphql-analytics

**Purpose**: Query and analyze data from the Arize platform using GraphQL, or help build/validate GraphQL queries and mutations.

**Use when**:

- Exploring the Arize GraphQL schema
- Building new GraphQL queries or mutations
- Debugging GraphQL operations
- Understanding available types, fields, and relationships

**Key features**:

- Full schema introspection
- Query building with proper Relay connection patterns
- Mutation construction with input type discovery
- Curl command generation for testing

**Invocation**: `/arize-graphql-analytics` or automatically triggered when asking about GraphQL queries

### new-query-workflow

**Purpose**: Complete workflow for adding new GraphQL queries or mutations to the Arize Toolkit with all supporting components.

**Use when**:

- Adding a new GraphQL query or mutation
- Implementing new API functionality
- Need guidance on the full development workflow

**Workflow phases**:

1. **GraphQL Development** - Develop and validate the query using schema introspection
1. **Component Discovery** - Identify required types, models, and file locations
1. **Gap Analysis** - Determine what needs to be created vs. reused
1. **Implementation** - Create types, models, queries, and client methods
1. **Testing** - Add tests for all new components
1. **Documentation** - Update tool documentation

**Invocation**: `/new-query-workflow`

**Sub-skills included**:

- `query-creation` - New query implementation patterns
- `model-creation` - GraphQL model definitions
- `type-creation` - Enum and type definitions
- `client-tools` - Client method patterns
- `query-tests` - Query test patterns
- `model-tests` - Model test patterns
- `client-tests` - Client test patterns
- `doc-creation` - Documentation patterns
- `project-patterns` - Overall development guidelines

## Using Skills

Skills are invoked in Claude Code using slash commands:

```
/arize-graphql-analytics
```

Or by describing what you want to do - Claude will automatically use the appropriate skill:

```
"Help me add a query to get all monitors for a model"
```

## Skill Location

Skills are stored in `.claude/skills/` directory:

```
.claude/skills/
├── arize-graphql-analytics/
│   ├── SKILL.md
│   └── references/
│       ├── EXAMPLES.md
│       └── PATTERNS.md
└── new-query-workflow/
    ├── SKILL.md
    └── references/
        ├── doc-patterns.md
        ├── implementation-patterns.md
        └── test-patterns.md
```

## Creating New Skills

To add a new skill to this repository:

1. Create a directory under `.claude/skills/` with your skill name
1. Add a `SKILL.md` file with frontmatter (name, description, etc.)
1. Optionally add a `references/` folder for supporting documentation
1. The skill will be automatically available in Claude Code sessions

See the existing skills for examples of the format and structure.
