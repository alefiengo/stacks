# Skill architecture

The repository hosts three independent agent skills with different execution
contracts:

| | `stacks` | `scaffold` | `orchestration` |
|---|---|---|---|
| Purpose | Decide and document a technology stack | Execute an approved `docs/stack.md` | Design the agent team for the decided stack |
| Input | Requirements or repository evidence | An existing `docs/stack.md` | An existing `docs/stack.md`, plus the project tree |
| Output | `docs/stack.md`, `docs/stack-audit.md` | Project files, plus implementation state in `docs/stack.md` | `docs/agents.md`, then approved agent files and a lead block in `AGENTS.md` |
| Executes commands | Never | Yes, after explicit approval of a plan | Only checksums, version queries, and approved file checks |
| Network | Official sources for verification | Verification plus package installation | Official host documentation |

User-facing descriptions are in the [stacks guide](../stacks.md), the
[scaffold guide](../scaffold.md), and the
[orchestration guide](../orchestration.md). This document explains how the
skills are built and why.

## Package layout

```text
skills/
├── stacks/
│   ├── SKILL.md            # activation, operating contract, modes, routing
│   ├── LICENSE             # byte-identical copy of the root license
│   ├── references/         # loaded on demand; stacks/ holds language defaults
│   └── templates/          # docs/stack.md and docs/stack-audit.md
├── scaffold/
│   ├── SKILL.md            # activation, contract, phases, routing
│   ├── LICENSE
│   ├── references/         # input contract, execution safety, verification;
│   │                       # stacks/ holds one execution guide per language
│   └── templates/          # the scaffold report
└── orchestration/
    ├── SKILL.md            # activation, contract, modes, routing
    ├── LICENSE
    ├── references/         # input contract, team design, safety;
    │                       # hosts/ holds one file-format guide per host
    └── templates/          # docs/agents.md and the materialization report
```

The skill installer copies one whole skill directory into the user's project
or user-level skill directory, so everything in it is installed. Keeping each
runtime in its own directory means an installed package contains only runtime
files; repository instructions, maintainer documentation, validation tools,
and workflows stay at the repository root and are never copied. Each directory
name matches its skill `name`, and each `LICENSE` keeps the notice with
installed copies.

Because an installer copies a single directory, no skill links to another,
and each works when the others are absent. `scaffold` and `orchestration`
without a `docs/stack.md` offer to run `stacks` rather than referring to its
files.

All three runtimes are independent of a particular agent or API. Native skill
loading, file tools, retrieval, structured questions, and planning UI are
capabilities the host may provide. Missing capabilities use explicit
fallbacks: ordinary conversation, supplied evidence, pending external checks,
or complete content returned without claiming it was saved or executed.

## stacks

`stacks` is a knowledge package, not an application generator. Its entry
point routes rather than repeating detail:

| Resource | Responsibility | Loaded when |
|---|---|---|
| [SKILL.md](../../skills/stacks/SKILL.md) | Activation, operating contract, modes, routing | Skill activation |
| [Compatibility](../../skills/stacks/references/compatibility.md) | Host capability contract, discovery limits, and safe fallbacks | Always, in both modes |
| [Interview](../../skills/stacks/references/interview.md) | Missing requirements, guided decisions, release verification | Define mode |
| [Layers](../../skills/stacks/references/layers.md) | Twelve-layer inventory and applicability | Decisions or inventory |
| [Decision criteria](../../skills/stacks/references/decision-criteria.md) | Tradeoffs, health, support, compatibility | Recommendation or audit |
| Language references | Contextual Python, TypeScript/Node, Java, Go, and .NET defaults | Selected or inspected component |
| [Deployment](../../skills/stacks/references/deployment.md) and [security](../../skills/stacks/references/security.md) | Cross-cutting operational decisions | Applicable layers |
| [Audit guide](../../skills/stacks/references/audit.md) | Inspection, evidence, severity, prioritized actions | Audit mode |
| [Templates](../../skills/stacks/templates/stack.md) | Output structure and rendering instructions | Writing project documents |

Define mode combines declared constraints, a bounded intake, contextual
defaults, and permitted official verification sources, then writes
`docs/stack.md`. Audit mode combines scoped repository evidence and permitted
external checks, then writes `docs/stack-audit.md`. Both modes preserve
existing user content and write documentation only: they do not install
dependencies, execute project scripts, create application configuration, or
deploy.

The layer reference and both templates retain L1–L12; an irrelevant layer is
`N/A` with a reason. The shared vocabularies are decision status, inventory
health, finding severity, verification state, and security-control status.
They have different meanings and canonical definitions in the decision
criteria, the audit guide, and the security guidance. Guided checkpoints need
an explicit reply unless prior authorization covers the choice and the write;
unknown facts stay unknown even when the user delegates a decision.

## scaffold

`scaffold` executes decisions; it never makes them. Its
[SKILL.md](../../skills/scaffold/SKILL.md) links every reference and the
report template, and each reference loads in the phase that needs it.

It reads the `docs/stack.md` summary and acts on each layer's status:

| Status in `docs/stack.md` | Behavior |
|---|---|
| `confirmed` | Implement |
| `default — revisit` | Implement, listed in the plan as a delegated default |
| `open` | Stop for that layer and ask; never choose a replacement |
| `N/A` | Skip, keeping the stated reason |
| Version `TBD — verify` | Resolve in preflight from raw registry or API responses; ask if that fails |

A run has six phases: preflight, an always-explicit plan checkpoint, generate,
configure, verify, and record. Before approval it only lists and reads files
and sends read-only requests to official registry and API endpoints; it runs
no package manager, generator, or git command. After approval it runs only the
plan's commands; anything else is a new checkpoint.

Its execution contract:

- No commits, pushes, deployments, cloud resources, or published images.
  A container image is built locally only when `docs/stack.md` decided one
  and the approved plan names the build.
- Commands run inside the target root. Outside it, only package-manager
  caches and stores, managed interpreter downloads, and the local image store
  are written, all named in the plan.
- Dependency install and lifecycle scripts stay blocked unless the plan lists
  them, and runtime-fetched templates are read before approval.
- Formatters and fixers are restricted to planned paths. `docs/stack.md` and
  installed agent skills are checksummed in preflight; verification proves
  they are unchanged, and recording changes only the implementation-state
  fields and labeled rows in the version log.
- Each check is recorded as `passed`, `failed`, or `not run` with its command
  and exit code. CI is recorded as defined, never as passing.

Owner decisions of 2026-11-10: same repository, installed separately;
`docs/stack.md` required; version 1 covers Python and TypeScript; the scope
ends at "builds, tests pass, CI defined"; no commits; local image builds when
planned. After an independent review, `scaffold` also appends labeled rows to
the version log of `docs/stack.md`, so each verified version stays traceable.

## orchestration

`orchestration` defines who works on the project; it never runs the team.
Its [SKILL.md](../../skills/orchestration/SKILL.md) routes to an input
contract, a host-neutral design guide, a safety guide, one file-format
reference per host, and two templates.

Mode A designs: it reads `docs/stack.md` and the project tree, proposes a
lead and the fewest subagents the stack justifies (each tied to the layers or
components it serves), specifies roles and the delegation flow, and writes
`docs/agents.md`. Mode B materializes: it re-verifies each host's format in
its official documentation, shows every file and which restrictions the host
enforces, and after explicit approval writes the role files and the lead
block, then checks their format and that protected inputs are unchanged.

- **The lead is the main session**, guided by a marked block in the root
  `AGENTS.md`, because hosts give the main session the user conversation,
  approvals, and delegation. Claude Code reads `AGENTS.md` when no
  `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working
  directory or above it, or through an `@AGENTS.md` import; Codex reads it
  directly. The block yields to any skill or workflow that governs the
  current task, so it never overrides `stacks` or `scaffold`. Running the lead as a Claude Code session agent was rejected
  because it replaces the default system prompt.
- **Host-neutral design, host-specific files.** The design uses capability
  classes, model tiers, and write scopes. Only `references/hosts/` holds host
  formats, each with its check date and official source, and each run
  re-verifies them; this is the one exception to the agent-independence rule.
- **Enforced versus advisory.** Claude Code's `tools` allowlist removes tools;
  Codex custom agents inherit the parent's sandbox and approvals, and its
  shell is also how agents read files, so every capability rule the skill
  writes there is an instruction only; it writes no feature flags. Codex also loads project agents only in a trusted
  project. The design records the
  difference per role instead of promising isolation a host does not provide.
- **Narrow outputs.** Agent definitions steer later sessions, so writing them
  is a sensitive change: never host settings, user-level directories,
  permission modes, hooks, MCP servers, or memory, and a design delegation
  never covers the files.

Owner decisions of 2026-11-11: the skill is named `orchestration`, lives in
this repository, requires `docs/stack.md`, writes a host-neutral design first
and host files only after approval, and covers Claude Code and Codex.

## Contracts between the skills

Two contracts are shared by value, not by link, and the validator keeps them
consistent:

- **Secret-bearing file patterns.** A marked block in the `stacks`
  [security guidance](../../skills/stacks/references/security.md), the
  `scaffold` execution safety reference, and the `orchestration` safety
  reference must be byte-identical. It governs which files no skill opens.
- **`docs/stack.md` fields.** `scaffold` reads the stack summary, dependency
  specification, local development, CI/CD, version verification log, and open
  decisions sections, and writes only the implementation-state fields
  (authority and implementation state, execution status, implementation
  evidence) and labeled version-log rows. Each field it names must exist in
  the [stack template](../../skills/stacks/templates/stack.md). Decision
  statuses and verification states are defined by `stacks` and quoted, not
  redefined, by `scaffold`. `orchestration` reads a further set of fields
  (project profile, decisions and rationale, commands, security checklist)
  and writes none; its input contract names each one, and the validator
  checks them against the template too.

`scaffold` execution and `orchestration` host files are never covered by an
authorization delegated in another skill; each needs approval of its concrete
plan.

## Design choices

- Curated defaults reduce repeated research while preserving user constraints.
  They are starting points, not a basis for negative findings on their own.
- Docker is a useful local default for networked service dependencies; delivery
  requirements decide whether the application needs a container.
- Verification happens at run time rather than through a stale catalog of
  current versions embedded in Markdown.
- Evidence and coverage are explicit, so partial results stay useful without
  claiming completeness.
- Execution is split from decision so that a reviewed document, not an
  improvised chain of commands, drives what gets installed.
- Behavior is validated with agent trials in disposable fixtures, and every
  trial result is re-verified on disk; `scaffold` trials install packages and
  run only on a maintainer machine.
- Maintainer checks use the Python standard library. Adding a toolchain should
  solve a demonstrated maintenance problem.

For change validation, see [CONTRIBUTING.md](../../CONTRIBUTING.md). For
publication, see [RELEASING.md](RELEASING.md).
