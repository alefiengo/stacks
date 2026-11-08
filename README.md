# stacks

Define a technology stack or audit the one your project already uses.

An agent skill for choosing coherent technologies and documenting architecture
with rationale, evidence, and actionable recommendations. Works with Claude
Code, Codex, Antigravity, OpenCode, pi, and other agents that load Markdown skills.

## Install

Run from your application project:

```bash
npx skills add alefiengo/stacks --skill stacks
```

Choose the agents to install to, or select one directly:

```bash
npx skills add alefiengo/stacks --skill stacks -a claude-code
```

The optional Skills CLI installer requires Node.js 22.20 or later. Add `-g`
for a user-wide installation. The skill itself is Markdown; you can also
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

| Mode | Output | Contents |
|---|---|---|
| Define | `docs/stack.md` | Technology choices, rationale, assumptions, and version verification |
| Audit | `docs/stack-audit.md` | Current stack, evidence, findings, and prioritized actions |

The guided workflow asks one unresolved decision at a time. To delegate the
choices, add: `Choose sensible defaults and complete the document autonomously.`
Conversation follows your language; documents default to English unless you
request another language. Existing decisions are preserved when updating files.

## Coverage

- **Profiles:** REST, MCP, GraphQL, gRPC, web frontends, and microservices.
- **Curated defaults:** Python, TypeScript/Node, and Java; general criteria
  apply to other languages.
- **Layers:** runtime, framework, architecture, quality, tests, data, identity,
  local environment, CI/CD, infrastructure, observability, and security.

Recommendations respect project constraints. Versions are checked against
permitted official sources; unavailable checks remain pending. The skill
produces documentation for development and deployment decisions.

## Documentation

- [Installation](docs/INSTALLATION.md) — agent commands, paths, and manual setup.
- [Skill workflow](SKILL.md) — modes and reference routing.
- [Contributing](CONTRIBUTING.md) — maintenance and local validation.
- [Changelog](CHANGELOG.md) — changes between releases.
- [Security](SECURITY.md) — reporting a vulnerability.

## License

[MIT](LICENSE).
