# stacks

Define a technology stack, audit the one your project already uses, and turn
the approved decisions into a working project skeleton.

This repository hosts two agent skills that load as Markdown skills in Claude
Code, Codex, Antigravity, OpenCode, pi, and other agents. Installation paths
follow the Skills CLI reference. Workflow trials of both skills so far used
Claude models; other agents have not been trialed yet.

| Skill | What it does | Permissions it needs |
|---|---|---|
| `stacks` | Chooses coherent technologies and documents architecture with rationale, evidence, and recommendations. Writes `docs/stack.md` or `docs/stack-audit.md`. Never executes project commands or installs packages. | Reads the project; writes documentation |
| `scaffold` | Executes an approved plan derived from `docs/stack.md`: runs generators, installs packages, configures lint, tests, and CI, and verifies the result. Version 1 covers Python and TypeScript. | Runs commands, installs packages from public registries, and writes project files |

## Recommended flow

1. Run `stacks` to define the stack and review `docs/stack.md`.
2. Run `scaffold` in the same project. It reads `docs/stack.md`, shows a plan
   with every command, file, and package, and runs nothing until you approve
   that plan.
3. Review the generated files and commit them yourself.

`scaffold` does not choose technologies. A missing or undecided choice goes
back to `stacks` or to you. It never commits, pushes, deploys, creates cloud
resources, or publishes images. When `docs/stack.md` decided a container image
and the approved plan names the build, it builds the image locally only.

## Install

Run from your application project. Install each skill separately:

```bash
npx skills add alefiengo/stacks --skill stacks
npx skills add alefiengo/stacks --skill scaffold
```

Choose the agents to install to, or select one directly:

```bash
npx skills add alefiengo/stacks --skill stacks -a claude-code
npx skills add alefiengo/stacks --skill scaffold -a claude-code
```

The two skills are independent packages and do not require each other.
Installing `scaffold` grants an agent the ability to run commands and install
packages, so review your agent's permission settings before using it.
`stacks` stays documentation-only.

The optional Skills CLI installer requires Node.js 22.20 or later. Add `-g`
for a user-wide installation. By default it links each agent directory to a
canonical copy; add `--copy` to copy the files instead. The skills themselves
are Markdown; you can also
[install the files manually](docs/INSTALLATION.md#manual-installation).

See the [installation guide](docs/INSTALLATION.md) for commands and paths for
Claude Code, Codex, Antigravity/agy, OpenCode, and pi.

## Use

Ask your agent in the application project:

```text
Use stacks to define a Python REST API stack with PostgreSQL and Cloud Run.
```

```text
Use stacks to audit this repository's technology stack and prioritize findings.
```

```text
Use scaffold to create the project from docs/stack.md.
```

| Skill and mode | Output | Contents |
|---|---|---|
| `stacks` define | `docs/stack.md` | Technology choices, rationale, assumptions, and version verification |
| `stacks` audit | `docs/stack-audit.md` | Current stack, evidence, findings, and prioritized actions |
| `scaffold` | Project files and a scaffold report | Generated skeleton, lint, tests, CI, recorded verification results, and implementation state in `docs/stack.md` |

The guided `stacks` workflow asks one unresolved decision at a time. To
delegate the choices, add: `Choose sensible defaults and complete the document
autonomously.` That delegation covers documentation only; `scaffold` always
asks you to approve its plan before running commands.
Conversation follows your language; documents use the language you request,
else an existing document's language, else English. Existing decisions are preserved when updating files.

## Coverage

- **Profiles:** REST, MCP, GraphQL, gRPC, web frontends, microservices, and
  background workers or batch jobs.
- **Curated defaults:** Python, TypeScript/Node, Java, Go, and .NET; general criteria
  apply to other languages.
- **Layers:** runtime, framework, architecture, quality, tests, data, identity,
  local environment, CI/CD, infrastructure, observability, and security.

Recommendations respect project constraints. Versions are checked against
permitted official sources; unavailable checks remain pending. `stacks`
produces documentation for development and deployment decisions; `scaffold`
implements only what that documentation decided, for Python and TypeScript in
version 1.

## Documentation

- [Installation](docs/INSTALLATION.md) — agent commands, paths, and manual setup.
- [`stacks` workflow](skills/stacks/SKILL.md) — modes and reference routing.
- [`scaffold` workflow](skills/scaffold/SKILL.md) — phases and reference routing.
- [Contributing](CONTRIBUTING.md) — maintenance and local validation.
- [Changelog](CHANGELOG.md) — changes between releases.
- [Security](SECURITY.md) — reporting a vulnerability.

## License

[MIT](LICENSE).
