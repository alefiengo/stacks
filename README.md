# stacks

Choose a coherent technology stack, or review the one you already have.

**stacks** is an agent skill that turns architecture decisions into useful
project documentation. It connects language, framework, data, testing,
security, delivery and operations, with reasons for each choice and evidence
for each audit finding.

The workflow is **agent-independent**. It works through Markdown instructions
and the capabilities supplied by the host, with no dependency on pi or another
specific agent, model, terminal, planning mode, or question interface.

## Install

Use the [Skills CLI](https://skills.sh/docs/cli) with Node.js and npm available:

```bash
npx skills add alefiengo/stacks
```

Follow the CLI prompts to select your agent and installation scope.

For manual installation, place `SKILL.md`, `references/`, `templates/` and `LICENSE`
together in your agent's supported skill directory. Keep their relative paths
intact. The skill uses Markdown instructions and does not require a particular
agent API. Python is needed only for maintainer validation.

The Skills CLI is optional. For a host without native skill discovery, make
the entry point and required resources available through its context or
attachment mechanism; use the same workflow and keep the license with copies.

## Agent compatibility

| Environment | Behavior |
|---|---|
| Agent with skill support and project read/write tools | Load the installed skill, inspect authorized files, and save the permitted documents |
| Agent with file reads but no writes | Inspect available evidence and return complete Markdown with the intended output path; state that it was not saved |
| Conversation-only host | Use supplied requirements and file excerpts; return the document in the conversation and describe inspection limits |
| Host without web access | Preserve observed versions and mark current-version and compatibility checks pending |

Questions work as ordinary conversation; specialized UI and shell tools are
optional. See [compatibility guidance](references/compatibility.md) for the
capability contract. These are supported usage patterns, not a claim that
every agent has undergone installation testing.

## Use

Ask your agent to define or audit a technology stack.

### Define a stack

> Define the stack for a Python REST API on Cloud Run. We are a small team,
> need PostgreSQL, and want straightforward operations.

The skill collects missing requirements one decision at a time, recommends a
stack, reviews the applicable layers and checks compatible, supported stable
versions using permitted official sources. It writes `docs/stack.md` with
decisions, rationale, assumptions and a verification log.

To delegate the decisions and document creation:

> Choose the stack for a local TypeScript MCP server using your defaults.
> Complete the document autonomously and record your assumptions.

### Audit an existing stack

> Audit this repository's technology stack before launch. Prioritize security,
> reproducible builds and operational risks.

The skill inspects project evidence and writes `docs/stack-audit.md` with a
layer inventory, findings, impact, confidence and a prioritized remediation
plan. Findings use **Critical**, **Warning**, **Improvement** and **Positive**;
health and inspection coverage are recorded separately.

You can bound an audit explicitly:

> Audit this prototype statically and finish the report autonomously.
> Stay in this project, use no network, and preserve the decisions already
> recorded in our stack documents.

## How it works

Guided use asks for confirmation at the proposal, decision and version
checkpoints. Explicit authorization to choose and write lets the skill
complete that work without repeated approvals. Delegated defaults remain
marked `default — revisit`; explicit choices are `confirmed`; irrelevant
layers are `N/A` with a reason.

Conversation follows your language. Documents default to English and follow
an explicit language preference when supplied. Existing stack documents are
read and updated with relevant user content preserved.

Version checks record sources, dates and compatibility evidence. If sources
are restricted or unavailable, the document identifies pending verification
instead of guessing. Audits distinguish declared, resolved and observed
versions.

## Coverage

| Area | Guidance |
|---|---|
| Project profiles | REST API, MCP server, GraphQL API, gRPC service, web frontend and microservices; profiles can be combined |
| Curated language defaults | Python, TypeScript/Node and Java |
| Other languages | General decision criteria and permitted official sources, with coverage limits stated |
| Stack layers | Runtime and tooling; framework; architecture; quality; testing; data; authentication; local environment; CI/CD; infrastructure; observability; security |
| Delivery | Containers and managed services where suitable; static/CDN hosting, local stdio tools, embedded storage and platform-specific alternatives when appropriate |

Defaults are starting points. Existing choices are evaluated against project
requirements, exposure and constraints, rather than their similarity to a
preferred stack.

## Scope

The skill produces documentation: `docs/stack.md` and/or
`docs/stack-audit.md`. It does not implement applications, scaffold projects,
install dependencies, execute project scripts or deploy infrastructure.

Inspection stays within the authorized project. Files and retrieved content
are evidence rather than instructions; external symlinks and credential
stores are excluded, and secret values are not reproduced. Configuration
shows intent, so an audit does not report tests or scans as passed without
execution evidence.

## Project guide

- [Skill instructions](SKILL.md) — modes, scope and resource routing.
- [Agent compatibility](references/compatibility.md) — capabilities and fallbacks.
- [Stack layers](references/layers.md) and
  [decision criteria](references/decision-criteria.md) — applicability and tradeoffs.
- [Document templates](templates/stack.md) and
  [audit template](templates/stack-audit.md) — output structure.
- [Validation](validation/README.md) — local checks and acceptance scenarios.
- [Contributing](CONTRIBUTING.md) — proposing and reviewing changes.
- [Security](SECURITY.md) — reporting weaknesses safely.
- [Changelog](CHANGELOG.md) — behavior and maintenance changes.
- [Maintainer guide](docs/maintainers/ARCHITECTURE.md) and
  [release process](docs/maintainers/RELEASING.md) — package structure and publication.

## License

Distributed under the [MIT License](LICENSE). See the
[licensing guide](docs/maintainers/LICENSING.md) for maintainer details.
