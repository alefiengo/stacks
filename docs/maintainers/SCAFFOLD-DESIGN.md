# Scaffold skill design (proposal)

Status: approved by the owner on 2026-11-10; implemented in version 1.

## Purpose and boundary

`scaffold` turns an approved `docs/stack.md` into a minimal, working project
skeleton. `stacks` decides and documents; `scaffold` executes those decisions.

| | `stacks` | `scaffold` |
|---|---|---|
| Input | Requirements or repository evidence | An existing `docs/stack.md` |
| Output | `docs/stack.md`, `docs/stack-audit.md` | Project files, plus implementation state in `docs/stack.md` |
| Executes commands | Never | Yes, after explicit approval of a plan |
| Network | Official sources for verification | Verification plus package installation |

`scaffold` does not choose technologies. A missing or undecided choice goes
back to `stacks` or to the user; it is never filled with a new default.

## Owner decisions (2026-11-10)

1. Same repository, installed separately as `skills/scaffold/`
   (`npx skills add alefiengo/stacks --skill scaffold`).
2. `docs/stack.md` is required. Without it, offer to run `stacks` first.
3. Version 1 covers Python and TypeScript. Java, Go, and .NET follow after
   agent trials of version 1.
4. The scope ends at "the project builds, the tests pass, and CI is defined".
   No deployment, cloud resources, or image publication.
5. No commits: `scaffold` leaves every change for the user to review and commit.
6. Container build: when L8 decided an image, verification builds it locally if
   the approved plan names the build; images are never pushed.

## Package layout

```text
skills/scaffold/
├── SKILL.md                    # activation, contract, phases, routing
├── LICENSE                     # byte-identical copy of the root license
├── references/
│   ├── input-contract.md       # how to read docs/stack.md and its statuses
│   ├── execution-safety.md     # approval, command limits, supply chain, secrets
│   ├── verification.md         # what counts as a passing check and how to record it
│   └── stacks/
│       ├── python.md           # generators, layout, quality and test wiring
│       └── typescript.md
└── templates/
    └── scaffold-report.md      # summary returned to the user
```

The package is self-contained, because installers copy one skill directory.
It cannot link to `skills/stacks/`. The few rules both skills need are
duplicated in a minimal form: secret-bearing file patterns and the rule that
repository text is evidence, not instructions. The validator checks that both
copies stay identical.

## Input contract

`scaffold` reads the stack summary table (L1–L12: decision, version, status)
and the dependency, local development, CI/CD, and deployment sections of
`docs/stack.md`. Behavior by status:

| Status in `docs/stack.md` | Behavior |
|---|---|
| `confirmed` | Implement |
| `default — revisit` | Implement, and list it in the plan as a delegated default |
| `open` | Stop for that layer and ask; never choose a replacement |
| `N/A` | Skip, keeping the stated reason |
| Version `TBD — verify` | Verify now from raw registry or API responses; if that fails, ask |

A document that does not follow the `stacks` template is read on a best-effort
basis; any layer that cannot be read is treated as `open`.

## Workflow

1. **Preflight.** Confirm the target root and read `docs/stack.md`. Inventory
   existing files. An empty root or one with only `docs/` is the normal case.
   In an existing project, list files that would change and never overwrite
   one without naming it in the plan.
2. **Plan checkpoint (always explicit).** Show every command to run, every
   file to create or change, each package to install, and the network access
   needed. Delegated authorization in `stacks` covers documentation only, so
   execution always needs approval of this plan.
3. **Generate.** Use the official generator or package manager for the chosen
   tools, in non-interactive mode, with flags checked against current official
   documentation at run time. Commit lockfiles.
4. **Configure.** Add only what the document decided: lint, format, type
   checking, a test runner with one passing test, `Dockerfile` and Compose when
   L8 decided them, a CI workflow when L9 did (actions pinned to verified
   SHAs), and `.env.example` with placeholder names only.
5. **Verify.** Run the project's own lint, type, test, and build commands.
   Record each command, its exit code, and the date. A failure is fixed within
   the plan's scope or reported; never reported as passing. Protected paths,
   `docs/stack.md` included, must be byte-identical to their Phase 0
   checksums; only directories inside the root are checksummed.
6. **Record.** Update only the implementation-state fields of `docs/stack.md`
   ("Authority and implementation state", "Execution status", "Implementation
   evidence") and add rows to the version verification log (section 9), then
   confirm with a comparison against the Phase 0 content that nothing else
   changed, and return the scaffold report.

Amendment (2026-11-10, after an independent review): section 9 rows are kept
for traceability. Authority text is appended to, never removed; each section 9
row added by `scaffold` is labeled `(scaffold run <date>)`; the summary
version cell stays as recorded, and the report suggests `stacks` to update
it.

## Safety contract

- Commands run only inside the target root, and only those in the approved plan.
- Package installation runs third-party code: prefer package-manager settings
  that block dependency install scripts where supported, resolve from the
  lockfile in CI, and report any script the plan had to allow.
- Never deploy, push images, create cloud resources, push to a remote, or
  commit, unless the user asks for that separately.
- Building a container image is part of verification only when the plan names
  it; a failed or skipped build is reported as such.
- Never read real secret files or write real credentials; generated examples
  hold placeholder names only.
- Without a shell or file writes, return the plan and file contents in the
  conversation and state that nothing was executed or saved.

## Validation

- Generalize `validation/check_skill.py` from one package to every
  `skills/*/` directory: required files, frontmatter, links, license copy, and
  the runtime-only rule for each package.
- Contract test: every `docs/stack.md` field that `scaffold` reads must exist
  in the `stacks` template, and the duplicated shared rules must be identical.
- New acceptance scenarios (prefix `SC`): missing `docs/stack.md`, an `open`
  layer, `TBD — verify` versions, a plan without approval, an existing file in
  the way, a failing test, a request to deploy, a host without a shell, and an
  unsupported language.
- Agent trials in `validation/.trial-*` fixtures. Unlike `stacks` trials, they
  install packages from public registries, so they run only on a maintainer
  machine and never in CI.

## Repository changes

README (two skills and their install commands), AGENTS.md (purpose and map),
ARCHITECTURE.md (the repository hosts a documentation skill and a generator
skill with different execution contracts), CONTRIBUTING.md, and the changelog.
