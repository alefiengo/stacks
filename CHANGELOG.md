# Changelog

All notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow
[Semantic Versioning](https://semver.org/). Unreleased work is not a published
version.

## Unreleased

### Added

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
  secret-bearing file block and the `docs/stack.md` fields `scaffold` reads.
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
