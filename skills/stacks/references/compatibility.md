# Agent compatibility

`stacks` is an agent-independent Markdown workflow. Its entry point, references,
and templates contain the behavior; no vendor SDK, extension, custom command,
or model-specific feature is required. Load this guidance in both modes.

## Minimum contract

The host must make the skill instructions and needed resources available and
allow a conversation with the user. Native skill discovery is convenient but
optional: a host can also supply the entry point and referenced resources as
context. Loading only SKILL.md without its referenced resources is incomplete.

Honor the host's instruction hierarchy, permissions, and the user's scope.
The skill cannot grant filesystem, network, or application access that the host
does not provide. Do not change host configuration or install integrations
to compensate for missing capabilities during a stack task.

## Capability adaptation

| Host capability | Use when available | Fallback when absent or disallowed |
|---|---|---|
| Native skill discovery | Let the host load the installed entry point and route references | Supply the Markdown entry point and needed resources through the host's supported context mechanism |
| Structured questions | Present the same single decision and choices using the supported interface | Ask one plain-text question with concrete choices and free text |
| Planning or task UI | Optionally track the workflow phases | Follow the phases in conversation; do not require a special plan mode |
| Project file discovery and reads | Inspect bounded files through the host's authorized file tools | Use user-provided excerpts as scoped evidence; do not infer an empty or inspected repository |
| Local shell | Run only the [discovery commands](#discovery-commands) when useful | Use file tools or supplied evidence; shell execution is not required |
| Official-source browsing or retrieval | Verify current releases and compatibility within permitted sources | Mark values `TBD — verify` and record each source as `consulted`, `attempted`, or `not queried` |
| Project file writes | Safely update the permitted document under the target root | Return the complete Markdown in conversation with the intended path and an explicit not-saved statement |

Record verification and coverage with the
[shared states](decision-criteria.md#verification-and-coverage-states).

When evidence is missing, continue any useful work that does not depend on it.
If the task materially needs a particular file or resource, request only the
relevant content through the available interface. An audit of supplied excerpts
is a partial review of those excerpts, not a complete repository inspection.
If no reliable current date is available, use an explicitly supplied date or
mark the check date unknown; do not invent a dated verification record.

## Discovery commands

A shell, when available, is limited to commands that list or read files:

- Allowed: listing and searching within the authorized root, such as `ls`,
  `find`, `grep`, `git ls-files`, and `git rev-parse HEAD`, and reading individual files as text.
  Exclude [secret-bearing files](security.md#secret-bearing-files) from
  content searches and reads; listing their paths is enough.
- Not allowed: package managers, build tools, and their wrappers (for example
  `./gradlew`, `./mvnw`, `mvn`, `npm ls`, `pip`, `uv`, or
  `docker compose config`), and any command that runs project code or
  evaluates project configuration, plugins, or scripts. Such commands can
  execute repository-controlled code or contact registries.

Resolved versions come only from lockfiles read as text. When no lockfile
records a value, report the resolved version as `unknown`; do not run a
resolver to obtain it. The same limits apply to equivalent host file tools.

## Paths and delivery

Resolve resources relative to the installed skill or its host-provided resource
identifiers. Resolve project evidence and outputs relative to the authorized
target project, which may differ from the skill's installation location.
Do not assume a home directory, operating system, shell, workspace variable,
or vendor-specific installation path. Retain the license with distributed copies.

If the host cannot safely validate a destination or preserve an existing file,
use the conversation fallback rather than an unsafe write. Label the document
as intended for `docs/stack.md` or `docs/stack-audit.md`, and state that no file
was saved. If the existing document cannot be read, do not claim it was merged
or preserved; request its relevant content or deliver a separate proposal.

Do not create per-agent wrapper files inside the audited project or copy this
repository's maintainer AGENTS.md into that project as part of skill execution.
Repository maintenance instructions are separate from the portable runtime.

## Shared workflow

Each host uses the same entry point, references, and templates. Native skill
loading and explicit context loading both use this capability contract; a
missing capability changes delivery or verification, not the stack decision
process. Keep resource loading separate from the target project's inputs.

See the [core workflow](../SKILL.md) for scope and authorization rules.
