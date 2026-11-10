# Installation

[Back to the README](../README.md)

This repository provides two independent skills: `stacks` (documentation only)
and `scaffold` (executes an approved plan). Install either or both in the
coding agent you use for development. The installer selects the destination;
each skill's workflow stays the same across agents.

| Skill | Install it when | Permissions it needs |
|---|---|---|
| `stacks` | You want to define or audit a technology stack | Reads the project and writes `docs/stack.md` or `docs/stack-audit.md`; never executes project commands |
| `scaffold` | You have a `docs/stack.md` and want the project skeleton built | Runs commands, installs packages from public registries, and writes project files; never commits, pushes, or deploys |

The recommended flow is `stacks` first, then `scaffold`. `scaffold` requires
an existing `docs/stack.md` and offers to run `stacks` when it is missing.
Installing `scaffold` lets the agent run generators and package managers, so
review your agent's permission settings before using it.

## Quick start

From your application project, run:

```bash
npx skills add alefiengo/stacks --skill stacks
npx skills add alefiengo/stacks --skill scaffold
```

Run the commands you need. Select the target agents, then start a new session
in that project. The
Skills CLI requires Node.js 22.20 or later. For installation without the CLI,
use the [manual procedure](#manual-installation).

## Choose an agent

Each command below installs into the current project. Replace `stacks` with
`scaffold` after `--skill` to install the generator skill. Add `-g` for user scope.
By default the installer links each agent directory to a canonical copy of the
skill; add `--copy` to create independent copies, for example where symlinks
are not supported. A copy needs a new installation or update to receive changes.

### Claude Code

```bash
npx skills add alefiengo/stacks --skill stacks -a claude-code
```

### Codex

```bash
npx skills add alefiengo/stacks --skill stacks -a codex
```

### Antigravity (agy)

For the Antigravity editor:

```bash
npx skills add alefiengo/stacks --skill stacks -a antigravity
```

For Antigravity CLI (`agy`):

```bash
npx skills add alefiengo/stacks --skill stacks -a antigravity-cli
```

### OpenCode

```bash
npx skills add alefiengo/stacks --skill stacks -a opencode
```

### pi agent

```bash
npx skills add alefiengo/stacks --skill stacks -a pi
```

Agent identifiers and destinations follow the
[Skills CLI agent reference](https://github.com/vercel-labs/skills/blob/main/docs/agents.md).

## Installation paths

The installer places `stacks/` and `scaffold/` under these directories (a link to the
canonical copy by default, or a copy with `--copy`):

| Agent | Project directory | User directory (`-g`) |
|---|---|---|
| Claude Code | `.claude/skills/` | `~/.claude/skills/` |
| Codex | `.agents/skills/` | `~/.agents/skills/` |
| Antigravity / agy | `.agents/skills/` | `~/.gemini/config/skills/` |
| OpenCode | `.agents/skills/` | `~/.config/opencode/skills/` |
| pi | `.agents/skills/` | `~/.agents/skills/` |

Project paths are relative to the application project; user paths are relative
to the user's home directory. Keep the package's relative paths intact.

## Use the skills

Start a new agent session in the application project and request either
`stacks` mode:

```text
Use the stacks skill to define this project's technology stack.
```

```text
Use the stacks skill to audit this repository's technology stack.
```

Define mode produces `docs/stack.md`; audit mode produces
`docs/stack-audit.md`. Add `Choose sensible defaults and complete the document
autonomously, recording assumptions` to delegate the decisions.

Once `docs/stack.md` is reviewed, ask for the project skeleton:

```text
Use the scaffold skill to create the project from docs/stack.md.
```

`scaffold` shows a plan with every command, file, and package and waits for
your approval. Delegated authorization given to `stacks` covers documentation
only, so the plan is always approved separately. Version 1 covers Python and
TypeScript. It leaves every change uncommitted for your review.

If the host does not discover skills automatically, ask it to read the
installed SKILL.md and follow its references. For example:

```text
Read .agents/skills/stacks/SKILL.md and use it to audit this project's stack.
```

Use the actual installed path; Claude Code's project path starts with
`.claude/skills/`. For `scaffold`, point to `scaffold/SKILL.md` instead. Pi also
supports an explicit directory on startup:

```bash
pi --skill .agents/skills/stacks
pi --skill .agents/skills/scaffold
```

## Manual installation

No installer runtime is needed for file copying:

1. Download this repository or clone it to a separate source directory:

   ```bash
   git clone https://github.com/alefiengo/stacks.git stacks-source
   ```

2. Create a directory named after each skill you want (`stacks/`,
   `scaffold/`) under your agent's
   [project or user skill directory](#installation-paths).
3. Copy the contents of each skill's repository directory
   (`skills/stacks/`, `skills/scaffold/`) into the matching directory. From the
   directory that contains `stacks-source`, set `DEST` to the destination from
   the [paths table](#installation-paths) (the example is a Codex project
   installation) and run the block for each skill:

   ```bash
   DEST=/path/to/application-project/.agents/skills/stacks
   mkdir -p "$DEST"
   cp -R stacks-source/skills/stacks/. "$DEST"/
   ```

   ```bash
   DEST=/path/to/application-project/.agents/skills/scaffold
   mkdir -p "$DEST"
   cp -R stacks-source/skills/scaffold/. "$DEST"/
   ```

   Each installed directory contains:

   ```text
   stacks/
   ├── SKILL.md
   ├── LICENSE
   ├── references/
   └── templates/
   ```

   ```text
   scaffold/
   ├── SKILL.md
   ├── LICENSE
   ├── references/
   └── templates/
   ```

4. Keep the complete contents of the directory. Review an existing
   installation before replacing files, then start a new agent session.

Each `skills/<name>/` directory holds only that skill's runtime package, so
installing one skill never requires the other. Neither skill adds application
dependencies by itself; `scaffold` installs the packages the approved plan
names into the target project. Maintainer scripts, repository instructions,
and configuration at the repository root are not part of an installed package.

## Manage the installation

```bash
# Show installed skills
npx skills list

# Check for updates
npx skills check

# Update the installed skills
npx skills update stacks
npx skills update scaffold
```

For other agents and installer options, see the upstream
[agent reference](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
and [command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## Troubleshooting

- **Skill not found:** check the project, selected agent, installation scope,
  and SKILL.md location; start a new session after installing.
- **Reference not found:** restore the complete `references/` and `templates/`
  directories from `skills/stacks/` or `skills/scaffold/`. SKILL.md alone is
  not the full package.
- **`scaffold` asks for `docs/stack.md`:** the file is required. Run `stacks`
  first, or place an approved `docs/stack.md` in the target project.
- **`scaffold` cannot run commands:** the host has no shell or file writes. It
  returns the plan and file contents in the conversation and states that
  nothing was executed or saved.
- **Document not saved:** allow writes to the target project or use the full
  Markdown returned in the conversation.
- **Versions pending:** permit the relevant official sources when appropriate
  or retain the verification gaps for later review.
