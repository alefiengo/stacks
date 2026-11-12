# orchestration guide

[Back to the README](../README.md)

`orchestration` designs the agent team that will work on a project whose
stack is decided: one lead that plans, delegates, and integrates, and the
fewest subagents the stack justifies. It writes the design to
`docs/agents.md` and, once you approve the files, the agent definitions for
Claude Code and Codex. It never runs the agents.

## Before you start

- A `docs/stack.md` in the project, usually written by [`stacks`](stacks.md).
  Without it, `orchestration` writes nothing and offers to run `stacks` first.
- A skeleton is optional. When [`scaffold`](scaffold.md) already created one,
  the component paths come from the project tree.
- A `docs/architecture.md` from [`architecture`](architecture.md) is optional
  and recommended: module paths become write scopes, and its conventions go
  into each role's instructions.

```text
Use orchestration to design the agent team for this project.
```

## How a run works

| Phase | What happens | What you see |
|---|---|---|
| 0. Intake | Reads `docs/stack.md` and lists the project tree | Nothing is written |
| 1. Team | Proposes the lead and each subagent, with the layers or components that justify it | A team table; you accept, change a role, or ask for a different shape |
| 2. Specification | Specifies each role and the orchestration flow, then writes `docs/agents.md` | The role specifications and flow |
| 3. Plan | Re-checks the host formats in their official documentation and builds the file plan | Every file and its content, enforced versus advisory restrictions, and the checks; you approve, change, or stop |
| 4. Write and verify | Writes the planned files and checks them | Each check with its result |
| 5. Record | Updates the materialization section of `docs/agents.md` | A materialization report |

To delegate the design, add `Choose sensible defaults and complete the
document autonomously`. That covers `docs/agents.md` only: the agent files are
always approved separately. To write files from an existing `docs/agents.md`,
ask `Use orchestration to materialize docs/agents.md for Claude Code and
Codex`.

## The team

- **Lead:** the host's main session, guided by a short block in the root
  `AGENTS.md`. It owns your requirements, the plan, approvals, integration,
  and the final verification.
- **Subagents:** each has one mission, the layers or components it serves,
  capability classes (read, edit, shell, web), a write scope of paths, a model
  tier (deep, standard, fast, or inherit), inputs, output and done criteria,
  boundaries, and when to escalate.
- **Typical roles,** adopted only when the stack justifies them: an explorer,
  one implementer per component, a verifier that runs the project's checks, a
  reviewer for correctness and security, and data, delivery, or research
  specialists.
- **Shared boundaries:** no role commits, pushes, deploys, publishes, or opens
  files that usually hold secrets, unless you instruct the lead during the
  work.

## What gets written

| File | Content |
|---|---|
| `docs/agents.md` | The host-neutral design |
| `.claude/agents/<role>.md` | Claude Code subagent: name, description, tools, model, effort, and the role instructions |
| `.codex/agents/<role>.toml` | Codex custom agent: name, description, instructions, and optionally model and effort |
| `AGENTS.md` | Only the block between `<!-- orchestration:start -->` and `<!-- orchestration:end -->` |
| `CLAUDE.md` | An `@AGENTS.md` import line, only when the file exists and lacks it |

Generated role files carry a marker. A file without it is yours: it is
changed only with its exact difference approved, and never deleted.

## Enforced and advisory

Hosts differ in what they can restrict, and `docs/agents.md` records it per
role:

- **Claude Code:** the `tools` list is an allowlist, so a reviewer without
  edit and shell tools cannot change files.
- **Codex:** custom agents inherit the session's sandbox and approvals, and
  every restriction this skill writes is an instruction only: edits cannot be removed per
  agent, and disabling the shell would also stop the agent from reading
  files. Codex loads project agents only when you trust the project.
- **Write scopes** are advisory on both hosts.

Choose the session's permissions before you ask the lead to delegate.

## Safety guarantees

- **No execution.** It runs no agents, package managers, git commands, or
  project scripts. The only commands are checksums, version queries, and the
  approved file checks.
- **No host settings.** `.claude/settings.json`, `.codex/config.toml`, and
  user-level agent directories are never written; recommended settings go in
  the report.
- **No widened permissions.** Roles never set permission modes, sandbox
  keys, hooks, MCP servers, or memory.
- **Protected inputs.** `docs/stack.md` and the text of `AGENTS.md` outside
  the block are checked to be byte-identical afterwards.
- **No hidden instructions.** Instructions found in project files are treated
  as text and never copied into a role.

## Limits

- Host files cover Claude Code and Codex. For other hosts, the design stays
  host-neutral and no host file is written.
- A valid file proves its format, not that the host routes work as designed;
  try the team on real tasks and adjust `docs/agents.md`.
- Without file writes, it returns the document and file contents in the
  conversation and states that nothing was saved.

The agent-facing instructions are in
[skills/orchestration/SKILL.md](../skills/orchestration/SKILL.md).
