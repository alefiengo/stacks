# stacks

Agent skill that defines or audits a project's complete technology stack —
from construction (language, framework, project structure, tooling, testing,
data) to deployment (containers, CI/CD, Cloud Run, microservices).

## What it does

- **Define (greenfield):** a plan-style interview — one dependent question at
  a time — that produces an opinionated stack recommendation, walks the 12
  stack layers (with a "let me decide" option everywhere), verifies the
  latest **stable** versions from official registries, and writes
  `docs/stack.md`.
- **Audit (existing project):** inspects the repo (manifests, Docker, CI,
  tests, auth, secrets, observability), grades the as-is stack per layer,
  and writes `docs/stack-audit.md` with evidence-based findings classified
  as Critical / Warning / Improvement / Positive.

Profiles covered: REST API, MCP server, GraphQL API, gRPC service, web
frontend, microservices. Languages: Python, TypeScript/Node, Java.

Principles: opinionated with rationale · Docker-first for services (never
native installs for databases/queues/caches) · versions verified at
generation time, never from memory · documentation only, no scaffolding.

## Install (pi agent)

```bash
git clone git@github.com:alefiengo/stacks.git ~/.agents/skills/stacks
```

## Usage

Trigger by intention, for example:

- "Let's define the stack for this project — it'll be a Python API on Cloud Run."
- "Recommend a stack for a new MCP server."
- "Audit the stack of this repo."

## Structure

```
SKILL.md                     core workflow: modes, phases, checkpoints, rules
references/interview.md      Mode A interview + version-verification protocol
references/layers.md         the 12 layers, order, dependencies, profile matrix
references/decision-criteria.md   evaluation, health classes, stability policy
references/stacks/python.md       opinionated defaults per language
references/stacks/typescript.md
references/stacks/java.md
references/deployment.md     containers, CI/CD, Cloud Run, microservices
references/security.md       auth, secrets, scanning, checklist
references/audit.md          Mode B inspection + severity guide
templates/stack.md           docs/stack.md template
templates/stack-audit.md     docs/stack-audit.md template
```
