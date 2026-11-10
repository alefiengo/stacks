# Installation

[Back to the README](../README.md)

Install the same `stacks` package in the coding agent you use for development.
The installer selects its destination; the skill's workflow stays the same.

## Quick start

From your application project, run:

```bash
npx skills add alefiengo/stacks --skill stacks
```

Select the target agents, then start a new session in that project. The
Skills CLI requires Node.js 22.20 or later. For installation without the CLI,
use the [manual procedure](#manual-installation).

## Choose an agent

Each command below installs into the current project. Add `-g` for user scope.
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

The installer places `stacks/` under these directories (a link to the
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

## Use the skill

Start a new agent session in the application project and request either mode:

```text
Use the stacks skill to define this project's technology stack.
```

```text
Use the stacks skill to audit this repository's technology stack.
```

Define mode produces `docs/stack.md`; audit mode produces
`docs/stack-audit.md`. Add `Choose sensible defaults and complete the document
autonomously, recording assumptions` to delegate the decisions.

If the host does not discover skills automatically, ask it to read the
installed SKILL.md and follow its references. For example:

```text
Read .agents/skills/stacks/SKILL.md and use it to audit this project's stack.
```

Use the actual installed path; Claude Code's project path starts with
`.claude/skills/`. Pi also supports an explicit directory on startup:

```bash
pi --skill .agents/skills/stacks
```

## Manual installation

No installer runtime is needed for file copying:

1. Download this repository or clone it to a separate source directory:

   ```bash
   git clone https://github.com/alefiengo/stacks.git stacks-source
   ```

2. Create a `stacks/` directory under your agent's
   [project or user skill directory](#installation-paths).
3. Copy the contents of the repository's `skills/stacks/` directory into it.
   From the directory that contains `stacks-source`, set `DEST` to the
   destination from the [paths table](#installation-paths) (the example is a
   Codex project installation) and run:

   ```bash
   DEST=/path/to/application-project/.agents/skills/stacks
   mkdir -p "$DEST"
   cp -R stacks-source/skills/stacks/. "$DEST"/
   ```

   The installed directory contains:

   ```text
   stacks/
   ├── SKILL.md
   ├── LICENSE
   ├── references/
   └── templates/
   ```

4. Keep the complete contents of the directory. Review an existing
   installation before replacing files, then start a new agent session.

The `skills/stacks/` directory holds only the runtime package. The skill adds
no application dependencies; maintainer scripts, repository instructions, and
configuration at the repository root are not part of the installed package.

## Manage the installation

```bash
# Show installed skills
npx skills list

# Check for updates
npx skills check

# Update stacks
npx skills update stacks
```

For other agents and installer options, see the upstream
[agent reference](https://github.com/vercel-labs/skills/blob/main/docs/agents.md)
and [command reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md).

## Troubleshooting

- **Skill not found:** check the project, selected agent, installation scope,
  and SKILL.md location; start a new session after installing.
- **Reference not found:** restore the complete `references/` and `templates/`
  directories from `skills/stacks/`. SKILL.md alone is not the full package.
- **Document not saved:** allow writes to the target project or use the full
  Markdown returned in the conversation.
- **Versions pending:** permit the relevant official sources when appropriate
  or retain the verification gaps for later review.
