# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow
[Semantic Versioning](https://semver.org/). Unreleased work is not a published
version.

## Unreleased

### Added

- `orchestration` skill: designs the agent team for an approved
  `docs/stack.md` (a lead and the fewest justified subagents, with missions,
  write scopes, capability classes, model tiers, handoffs, and the
  orchestration flow) in `docs/agents.md`. After the user approves an
  explicit plan, it writes Claude Code role files (`.claude/agents/`), Codex
  custom agents (`.codex/agents/`), and a marked lead block in `AGENTS.md`,
  recording which restrictions each host enforces and which are advisory. It
  never runs agents, package managers, or git, and never writes host
  settings or `docs/stack.md`. Install it with
  `npx skills add alefiengo/stacks --skill orchestration`. Acceptance
  scenarios OR01-OR35 cover it.
- `scaffold` skill, version 1: executes an approved plan derived from
  `docs/stack.md` to generate a Python or TypeScript project skeleton with
  lint, type checking, tests, a Dockerfile and Compose when decided, and a CI
  workflow, then records verification results in `docs/stack.md`. It requires
  an existing `docs/stack.md`, chooses no technologies, never commits, pushes,
  or deploys, and builds an image locally only when the approved plan names
  it. Install it with `npx skills add alefiengo/stacks --skill scaffold`.
  Acceptance scenarios SC01-SC26 cover it. Trials with Claude models generated
  and verified Python and TypeScript skeletons; failures found in the trials
  (git in a parent repository, formatters rewriting `docs/stack.md`, unclear
  `TBD — verify` handling) were fixed and rerun.
- Validator checks across every `skills/*/` package, including the shared
  secret-bearing file block in all three skills and the `docs/stack.md`
  fields that `scaffold` and `orchestration` read.
- Agent-specific installation instructions, with a manual file-copy route and
  an optional Skills CLI installer.
- Agent-independent capability guidance and portability acceptance scenarios.
- Acceptance scenarios for unresolved image digests, delegated audits,
  mode selection, document language, discovery without executing project
  tooling, private registries, existing documents in another structure,
  empty repositories, MCP transport security, installed agent skills,
  checkpoint exits, published documentation, target-stack requests,
  secret-bearing files beyond `.env`, unnamed cloud providers, and
  summarized registry responses.
- Curated Go and .NET references, and a worker and batch jobs profile.
- Offline validation with negative tests, and a continuous validation
  workflow for pushes and pull requests.
- MIT license, security reporting guidance, and a documented release process.

### Changed

- `scaffold` also checksums the root agent instruction files (`AGENTS.md`,
  `CLAUDE.md`) in preflight and keeps them byte-identical, so a generator
  cannot overwrite an `orchestration` lead block (scenario SC27). `stacks`
  and `scaffold` descriptions exclude agent-team design.
- Reorganized the README around the two-skill flow, with a diagram, a
  combined install command, and an example; added user guides for `stacks`
  and `scaffold`; merged the `scaffold` design record into the architecture
  document.
- Moved the runtime package to `skills/stacks/` (`SKILL.md`, `LICENSE`,
  `references/`, `templates/`) so installers copy only runtime files.
  Repository documentation, validation, and workflows stay at the repository
  root. Manual installation copies `skills/stacks/`.
- Tightened rules for inspection boundaries, secret-bearing files,
  source verification, existing-document updates, and MCP transport and
  authorization controls.
- Unified the shared vocabularies: decision status, inventory health, finding
  severity, verification state, and security-control status.
- Raised the minimum Python version for maintainer tools to 3.11.
- Described the Skills CLI default symlink mode and the `--copy` option, and
  a private route for vulnerability reports.
