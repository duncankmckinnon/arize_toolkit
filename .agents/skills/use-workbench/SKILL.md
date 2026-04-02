______________________________________________________________________

## name: use-workbench description: Use when writing or editing a workbench plan (.workbench/\*.md), designing task graphs for parallel agent execution, or preparing work for the wb CLI to dispatch

# Writing Workbench Plans

How to write effective plans for the `wb` CLI to execute with parallel AI agents.

## Overview

Workbench (`wb`) is a multi-agent orchestrator that takes a markdown plan, breaks it into independent tasks, and dispatches parallel AI coding agents (Claude Code, Gemini CLI, Codex, or custom) to implement, test, and review each task in isolated git worktrees.

Each task becomes a standalone agent session — the agent only sees its own task description, not the rest of the plan. This means the plan must be thorough enough that each task is self-sufficient.

## When to Use

- Writing a new `.workbench/*.md` plan file
- Breaking a feature or refactor into parallel agent tasks
- Reviewing whether a plan will execute correctly before running `wb run`
- Debugging why agents produced incorrect output (usually a plan clarity issue)

## Plan Format

```markdown
# Plan Title

## Context

<What is this project? What are we building? Why?>

<Key architectural decisions and constraints>

## Conventions

<Project-specific patterns agents must follow:>
- <Language/framework version>
- <Import conventions>
- <Error handling patterns>
- <Naming conventions>
- <Test patterns and test command>

## Task: Short title
Files: src/auth.py, src/middleware.py
Depends: database-setup

Detailed description of what to implement...

### Expected behavior
<Concrete specification of what the code should do>

### Test plan
<What tests to write, what command to run, what passing looks like>
```

### Plan Sections

- `## Context` — Injected into every agent's prompt. Describe the project, what's being built, and why.
- `## Conventions` — Injected into every agent's prompt. Specify language version, test framework, import style, naming conventions. Without this, agents follow their own defaults.
- `## Task: <title>` — Each task becomes an independent agent session in its own git worktree.

### Task Metadata

- **Files:** — Comma-separated list of files the task creates or modifies. Prevents parallel tasks from conflicting.
- **Depends:** — Comma-separated task slugs this task depends on. Tasks with unmet dependencies wait until earlier waves complete.
- Aliases: `Scope:` works like `Files:`, `After:`/`Dependencies:` work like `Depends:`.

### Dependency Slugs

Dependencies reference other tasks by their title converted to a slug (lowercase, non-alphanumeric replaced with `-`). For example, `## Task: Database Setup` has slug `database-setup`.

**Keep task titles short (2-4 words).** The title becomes the dependency slug, and long titles produce unwieldy slugs that are error-prone to type in `Depends:` lines. Compare:

| Title | Slug | Verdict |
|-------|------|---------|
| Prompt builder | `prompt-builder` | Good |
| Agent adapters | `agent-adapters` | Good |
| Structured prompt builder with plan context injection | `structured-prompt-builder-with-plan-context-injection` | Too long |
| Update agents to use adapters and tmux | `update-agents-to-use-adapters-and-tmux` | Too long |

Treat the title as a label, not a description — the task body has all the detail.

## Writing Good Task Descriptions

Each task runs in an **isolated worktree** — the agent only sees its own task description, not other tasks. Every task description must contain:

1. **What to build** — Concrete deliverables, not vague goals
1. **Where it goes** — Exact file paths for new and modified files
1. **How it works** — Function signatures, type definitions, behavior specs
1. **How it fits** — Imports, interfaces with existing code, how other modules will use this
1. **Patterns to follow** — "Use the same pattern as X" with enough detail to follow it
1. **Test expectations** — What tests to write, what command to run, what passing looks like
1. **Edge cases** — Error handling, boundary conditions, validation rules
1. **What NOT to do** — Constraints, anti-patterns, things that seem obvious but are wrong in this codebase

If the task depends on interfaces from an earlier wave, describe those interfaces in full — the agent cannot see the other task's output.

### Example: Good vs Bad

**Bad** (too vague, agent will guess):

```markdown
## Task: Add authentication
Add auth to the app.
```

**Good** (self-contained, specific):

```markdown
## Task: JWT auth middleware
Files: src/auth/middleware.py, src/auth/tokens.py, tests/test_auth.py

Create JWT-based authentication middleware for the FastAPI app.

### Implementation
- `src/auth/tokens.py`: `create_token(user_id: str) -> str` and `verify_token(token: str) -> dict`
  using PyJWT. Tokens expire after 24h. Secret from `AUTH_SECRET` env var.
- `src/auth/middleware.py`: FastAPI dependency `require_auth(request: Request) -> User`
  that extracts Bearer token from Authorization header, verifies it, and returns the user.
- Follow the existing middleware pattern in `src/middleware/logging.py`.

### Tests
- `tests/test_auth.py`: test token creation, verification, expiry, and invalid tokens.
- Run: `pytest tests/test_auth.py`
```

## Designing for Parallelism

Tasks in the same wave run simultaneously in separate worktrees. They **cannot see each other's changes**, and modifying the same files causes merge conflicts.

**Strategies:**

- Group work by file ownership — each task owns distinct files
- Push shared infrastructure (types, configs) to earlier waves using `Depends:`
- If two tasks must touch the same file, make one depend on the other

### Example: Parallel-Safe Plan

```markdown
## Task: User model
Files: src/models/user.py, migrations/001_users.sql

## Task: Product model
Files: src/models/product.py, migrations/002_products.sql

## Task: API endpoints
Files: src/api/routes.py, src/api/handlers.py
Depends: user-model, product-model
```

Wave 1 runs the two model tasks in parallel (different files). Wave 2 runs the API task after both complete.

## Planning Process

Creating a good plan is the most important step. Follow these phases:

### Phase 1: Understand the Problem

- What is the user trying to achieve? What's the end state?
- What are the constraints (performance, compatibility, existing patterns)?
- What's changing? What's staying the same?

Ask clarifying questions if anything is ambiguous. It's better to ask now than to have 6 agents each make a different assumption.

### Phase 2: Survey the Codebase

Read the code before designing tasks:

- Project structure, module organization, entry points
- Existing patterns — how are similar things already done?
- Dependencies and interfaces between modules
- Test infrastructure — framework, location, test command
- Build and config files

### Phase 3: Design the Task Graph

Break work into tasks with the execution model in mind:

- Each task runs in an isolated worktree
- File overlap between parallel tasks creates merge conflicts
- Push shared infrastructure to earlier waves
- Maximize parallelism by grouping work by file ownership

### Phase 4: Write Detailed Descriptions

Follow the checklist in "Writing Good Task Descriptions" above. Every task must include enough context for an agent that has never seen the rest of the plan.

### Phase 5: Validate

Before running:

- [ ] Can each task be implemented knowing only its own description?
- [ ] Are file sets disjoint within each wave?
- [ ] Do dependent tasks describe the interfaces they depend on?
- [ ] Is the test command specified and will it work in a fresh worktree?
- [ ] Are there implicit assumptions that should be explicit?

## Agent Pipeline

Each task goes through: **implement -> test -> review -> fix**

- **Implementor** — Writes code and commits to the task branch
- **Tester** — Runs tests, writes new tests if specified, emits `VERDICT: PASS` or `VERDICT: FAIL`
- **Reviewer** — Reviews the diff for correctness and quality, emits a verdict
- **Fixer** — If test/review fails, receives feedback and makes targeted fixes (up to `--max-retries`)
- **Merger** — If merge conflicts occur between parallel branches, resolves them automatically

Stages can be skipped with `--skip-test` or `--skip-review`.

## Directive Overrides

The instructions given to each agent role can be overridden from the CLI:

```bash
wb run plan.md --reviewer-directive "Focus only on security vulnerabilities and data validation."
wb run plan.md --tester-directive "Run pytest with -x flag. Only test the new code, not existing tests."
```

This is useful when you want agents to focus on specific aspects without modifying the plan itself.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Task says "add auth" with no details | Specify exact files, function signatures, error handling, test command |
| Two parallel tasks edit the same file | Add `Depends:` to serialize them, or extract shared changes to an earlier task |
| Task depends on another but doesn't describe the interface | Copy function signatures and types into the dependent task's description |
| No `## Context` or `## Conventions` section | Agents follow their own defaults — specify language version, test framework, import style |
| Test command missing or wrong | Agent may skip tests or run the wrong suite — always include `Run: <command>` |
| Task title is a full sentence | Keep titles to 2-4 words — they become dependency slugs |
| Line number references for code to change | Line numbers shift — describe code by content/pattern instead |

## Branching Strategy

By default, `wb run` fetches `origin/main` and creates a new session branch (`workbench-N`) from the latest remote state. This ensures work starts from the most up-to-date code and avoids merge conflicts when the session branch is later merged back.

### Flags

| Flag | Base branch | Source | Use case |
|------|-------------|--------|----------|
| *(default)* | `main` | `origin/main` (fetched) | Standard — start from latest remote |
| `--local` | `main` | local `main` | Build on uncommitted/unpushed local work |
| `--base feature-x` | `feature-x` | `origin/feature-x` (fetched) | Branch from a specific remote branch |
| `--base feature-x --local` | `feature-x` | local `feature-x` | Branch from a local feature branch |
| `-b workbench-3` | *(existing)* | *(existing)* | Resume a previous session branch |

### When to use `--local`

Use `--local` when your base branch has local commits you haven't pushed yet and you want workbench to build on top of them. Without `--local`, workbench fetches from origin and your unpushed work won't be included.

### When to use `--base`

Use `--base` when you're working off a branch other than `main` — for example, a long-running feature branch, a release branch, or another team member's branch. Combined with `--local`, it lets you build on any local branch.

### Resuming with `-b`

Use `-b workbench-N` (or `--session-branch`) to resume a previous session. This skips branch creation entirely and continues merging into the existing session branch. Pair with `--start-wave N` to skip already-completed waves.

## Profiles

Profiles configure which agent CLI and instructions are used for each pipeline role. When no profile exists, built-in defaults apply.

### Roles and fields

Roles: `implementor`, `tester`, `reviewer`, `fixer`, `merger`

Each role supports:

- `agent` — CLI command (default: `claude`). Supported: `claude`, `gemini`, `codex`, or any custom CLI.
- `directive` — Full replacement for the role's default instructions.
- `directive_extend` — Text appended to the default instructions. Cannot be combined with `directive` on the same role.

### YAML format

Create or edit `.workbench/profile.yaml`:

```yaml
roles:
  reviewer:
    agent: gemini
    directive: "Focus on security and correctness."
  tester:
    directive_extend: "Also check edge cases for null inputs."
  implementor:
    agent: codex
```

Only include roles and fields you want to override — everything else uses built-in defaults.

### Named profiles

Store multiple configurations as `profile.<name>.yaml`:

```bash
wb profile init --name fast --set reviewer.agent=gemini --set implementor.agent=codex
wb run plan.md --profile-name fast
```

### Profile CLI commands

```bash
wb profile init                                        # create profile.yaml from defaults
wb profile init --global                               # create in ~/.workbench/
wb profile init --set reviewer.agent=gemini            # create with inline overrides
wb profile init --name fast --set reviewer.agent=gemini  # create a named profile
wb profile show                                        # print resolved profile
wb profile show --name fast                            # show a named profile
wb profile set reviewer.agent gemini                   # update a field
wb profile set reviewer.agent codex --name fast        # update a named profile
wb profile diff                                        # show differences from defaults
wb profile diff --name fast                            # diff a named profile
```

### Merge order

Profiles merge in order: built-in defaults < `~/.workbench/profile.yaml` < `.workbench/profile.yaml` < `--profile` flag < CLI flags. Named profiles (`--profile-name`) replace the default filename at each level.

## TDD Mode

With `--tdd`, the pipeline becomes: **test (write failing) → implement (make pass) → test (verify) → review → fix**

In TDD mode, the tester writes comprehensive failing tests first. The implementor then writes code to make all tests pass and reports whether the tests are comprehensive. Normal test verification and review follow.

## Updating workbench

To update workbench and its skills to the latest version:

```bash
pip install --upgrade wbcli    # upgrade the package
wb setup --update              # overwrite project-level skill files with the latest version
```

For user-level skills:

```bash
wb setup --global --update     # update user-level skills
```

If using `--symlink`, skill files stay in sync automatically — no `--update` needed.

## Key commands

- `wb run <plan>` — execute a plan with parallel agents
- `wb run plan.md --name auth-feature` — name the session branch
- `wb run plan.md --keep-branches` — keep task branches after merging
- `wb run plan.md --tdd` — test-driven: tests first, then implement
- `wb run plan.md --base feature-x` — branch from a specific branch
- `wb run plan.md --local` — branch from local ref instead of fetching
- `wb run plan.md -b my-session -w 2` — resume session from wave 2
- `wb run plan.md --profile-name fast` — use a named profile
- `wb preview <plan>` — dry-run to see parsed tasks and waves
- `wb status` — show active worktrees
- `wb stop` — kill all active agent sessions
- `wb stop --cleanup` — also remove worktrees and branches
- `wb clean` — remove all workbench worktrees
- `wb setup` — create .workbench/, install skills locally, prepare repo
- `wb setup --agent gemini` — install skills for Gemini CLI
- `wb setup --profile` — also create a profile.yaml with the detected agent
- `wb setup --update` — force-update skills to the latest version
- `wb setup --global` — install skills to user-level paths (no .workbench/ creation)
- `wb setup --global --agent claude` — install to ~/.claude/skills/
- `wb setup --global --agent gemini` — install to ~/.agents/skills/
- `wb profile init` — create profile.yaml from defaults
- `wb profile init --name fast --set reviewer.agent=gemini` — create a named profile with overrides
- `wb profile show` — print resolved profile
- `wb profile set <key> <value>` — update a profile field
- `wb profile diff` — show differences from defaults
