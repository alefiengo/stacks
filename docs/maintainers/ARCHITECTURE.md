# Skill architecture

The repository hosts two skills with different execution contracts.

- `stacks` turns project requirements or repository evidence into technology
  stack documentation. It is a knowledge package, not an application
  generator: it never executes project commands or installs packages.
- `scaffold` executes an approved plan derived from `docs/stack.md` and
  generates a minimal project skeleton: it runs generators and package
  managers, configures lint, tests, and CI, and verifies the result. Version 1
  covers Python and TypeScript. It chooses no technologies, never commits,
  pushes, or deploys, and builds a container image locally only when the
  approved plan names it. The approved
  [design](SCAFFOLD-DESIGN.md) records the decisions.

The sections below describe `stacks` unless they name `scaffold`.

## Package layout

Each skill is packaged separately. The `stacks` runtime lives in
`skills/stacks/`: `SKILL.md`, `LICENSE`, `references/`, and `templates/`. The
`scaffold` runtime lives in `skills/scaffold/`: `SKILL.md`, `LICENSE`,
`references/` (input contract, execution safety, verification, and a guide per
language under `references/stacks/`), and `templates/` (the report). The skill
installer copies one whole skill directory into the user's project or
user-level skill directory, so everything in it is installed. Keeping each
runtime in its own directory means an installed package contains only runtime
files; repository instructions, maintainer documentation, validation tools,
and workflows stay at the repository root and are never copied. Each directory
name matches its skill `name`, and each `LICENSE` is a byte-identical copy of
the root license so installed copies retain the notice.

The packages are independent. Because an installer copies a single directory,
neither skill links to the other, and each works when the other is absent.
`scaffold` without a `docs/stack.md` offers to run `stacks` rather than
referring to its files.

## Resource boundaries

The table covers `stacks`. The `scaffold` package follows the same routing
pattern: its [SKILL.md](../../skills/scaffold/SKILL.md) links every reference
and the report template, and each reference loads only in the phase that needs
it.

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
| [Validation](../../validation/README.md) | Repository checks and acceptance scenarios | Maintainer work |

References are loaded on demand. The entry point should route rather than
repeat every detail. Resource paths are relative to the installed skill;
project inputs and outputs are relative to the separately authorized target.

The runtime is independent of a particular agent or API. Native skill loading,
file tools, retrieval, structured questions, and planning UI are capabilities
that the host may provide. Missing capabilities use explicit fallbacks: ordinary
conversation, supplied evidence, pending external checks, or a complete document
returned without claiming a file was saved. Maintainer tooling and AGENTS.md
are not runtime dependencies.

## Modes and artifacts

Define mode combines declared constraints, a bounded intake, contextual
defaults, and permitted official verification sources. It writes
`docs/stack.md`. Audit mode combines scoped repository evidence and permitted
external checks, then writes `docs/stack-audit.md`. A target stack document
is optional and requires a request or prior authorization.

Both modes preserve existing user content and write documentation only.
Without safe file writes, they return the complete intended document in the
conversation and explicitly state that it has not been saved.
They do not install dependencies, execute project scripts, create application
configuration, or deploy. Maintainer validation scripts belong to this
repository and are separate from the installed skill's project workflow.

## Shared contracts

The layer reference and both templates retain L1–L12. Applicability is
contextual: mark an irrelevant layer N/A and explain why. The shared
vocabularies are decision status, inventory health, finding severity,
verification state, and security-control status. They have different meanings;
use their canonical definitions (in decision criteria, the audit guide, and
security guidance) instead of merging them.

Guided checkpoints require an explicit reply unless prior authorization
already covers the choice and writing. Unknown facts remain unknown even
when the user delegates a decision. Available package versions are not
automatically compatible, supported, stable, or verified.

## Contracts between the skills

Two contracts are shared by value, not by link, and the validator keeps them
consistent:

- **Secret-bearing file patterns.** A marked block in the `stacks`
  [security guidance](../../skills/stacks/references/security.md) and in the
  `scaffold` execution safety reference must be byte-identical. It governs
  which files neither skill opens.
- **`docs/stack.md` fields.** `scaffold` reads the stack summary, dependency
  specification, local development, CI/CD, version verification log, and open
  decisions sections, and writes only the implementation-state fields (authority
  and implementation state, execution status, implementation evidence). Each
  field it names must exist in the
  [stack template](../../skills/stacks/templates/stack.md). Decision statuses
  and verification states are defined by `stacks` and quoted, not redefined, by
  `scaffold`.

`scaffold` execution is never covered by an authorization delegated in
`stacks`; it needs approval of the concrete plan, and commands outside that
plan need a new checkpoint.

## Design choices

- Curated defaults reduce repeated research while preserving user constraints.
  They are starting points, not a basis for negative findings on their own.
- Docker is a useful local default for networked service dependencies; delivery
  requirements decide whether the application needs a container.
- Verification happens at recommendation time rather than through a stale
  catalog of current versions embedded in Markdown.
- Evidence and coverage are explicit so a partial audit remains useful without
  claiming a complete assessment.
- Maintainer checks use the Python standard library. Adding a toolchain should
  solve a demonstrated maintenance problem.

For change validation, see [CONTRIBUTING.md](../../CONTRIBUTING.md). For
publication, see [RELEASING.md](RELEASING.md).
