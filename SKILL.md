---
name: stacks
description: >
  Define or audit a project's complete technology stack, from project
  construction to deployment. Two modes: (A) a guided, plan-style interview
  that recommends an opinionated, coherent stack and writes docs/stack.md with
  verified stable versions; (B) an audit of an existing project's stack,
  writing docs/stack-audit.md with evidence-based findings classified by
  severity. Covers language and runtime, package and build management,
  framework, project structure, code quality, testing, data (database, ORM,
  cache, queues), authentication, containerization, CI/CD, deployment
  (Cloud Run, containers, microservices), observability and security.
  Profiles: REST API, MCP server, GraphQL API, gRPC service, web frontend,
  microservices. Use when the user asks to "define the stack", "recommend a
  stack", "choose technologies", "audit our stack", "review our stack", or
  states project intent such as "we're building a Python API" or "start a new
  MCP server project".
---

# Stacks

Act as a senior software architect. This skill defines or audits a project's
technology stack end to end and records the result as documentation — it never
writes application code, config files, or scaffolding.

## Hard rules

1. **One question per message.** Never batch interview questions.
2. **Never ask what is already known.** Scan the conversation and the repo
   first; pre-fill answers and skip those questions.
3. **Every question offers concrete options plus free text.** When a sensible
   default exists, always offer **"let me decide"** — apply the opinionated
   default and mark it `default — revisit` in the output.
4. **Never continue past a checkpoint without explicit confirmation.**
5. **Never state a version from memory.** Verify the latest stable from
   official registries at generation time and record source + date.
6. **Docker-first for services.** Databases, caches, queues, brokers and any
   stateful dependency run via Docker/compose locally or a managed cloud
   service in production — never propose native or host installs for them.
   The application itself ships as a container for any non-trivial deployment.
7. **Documentation only.** The sole artifacts are `docs/stack.md` and/or
   `docs/stack-audit.md`. Do not scaffold code or generate config files.
8. **Load references on demand** (see routing table) — never load all at once.
9. Generated documents are always written in **English**. Conduct the
   conversation in the user's language unless they prefer otherwise.

## Mode selection

| Situation | Mode |
|---|---|
| New/greenfield project, or user asks to define/recommend a stack | **A — Define** |
| Existing repo, user asks to audit/review/criticize its stack | **B — Audit** |
| Ambiguous | Ask: "Should I define a stack for a new project, or audit the existing one?" (single question) |

Quick repo signal: manifest files present (`pyproject.toml`, `package.json`,
`pom.xml`, `build.gradle*`, `go.mod`) and the ask is evaluative → Mode B.
Empty or nearly empty directory, or construction intent → Mode A.

---

## Mode A — Define

### Phase 0 — Context intake

Before the first question: check whether the directory is empty, look for
existing manifests, and collect everything the user already declared
("a Python API" → language and profile answered). Load
`references/interview.md` and `references/layers.md`.

### Phase 1 — Scope interview

Dependent questions, one per message, from `references/interview.md` Phase 1:
project profile → language (if undeclared) → audience and scale → deployment
target → hard constraints → (microservices only) repo strategy.

**Checkpoint 1.** Produce the stack recommendation: a summary table
(layer → recommendation → one-line why) plus a 2–3 sentence rationale grounded
in the user's answers. Route to `references/stacks/<language>.md` for the
defaults. Offer: **use as is / swap one thing / different direction**.
On "swap one thing", regenerate only the delta and re-confirm.

### Phase 2 — Layer decisions

Walk the 12 layers in order (`references/layers.md`), skipping layers that do
not apply to the confirmed profile. Ask only the layers that carry a real
choice; settled categories (see `references/decision-criteria.md`) get a
health-check statement instead of a question. Every real choice: 2–3 options
max with one-line tradeoffs, a clear recommendation, and "let me decide".
Cross-cutting detail: `references/deployment.md` (containers, CI/CD, Cloud
Run, microservices) and `references/security.md` (auth, secrets, scanning).

**Checkpoint 2.** Show the consolidated decision table (all 12 layers, each
`confirmed` or `default — revisit`) and get confirmation.

### Phase 3 — Version verification and output

Follow the verification protocol in `references/interview.md` Phase 3 and the
stability policy in `references/decision-criteria.md`:

1. Compile the full dependency list from the confirmed decisions.
2. Verify each against its official registry or release channel (PyPI, npm,
   Maven Central, python.org, nodejs.org, JDK releases, Docker Hub tags).
   Exclude pre-releases; flag majors younger than ~3 months unless LTS.
3. **Checkpoint 3.** Show the version table (dependency → version → source).
   Get confirmation.
4. Write `docs/stack.md` from `templates/stack.md`, including the verification
   log (date + source per dependency).
5. Close with a short summary and next steps.

If web/registry access is unavailable, do not guess: leave `TBD — verify`
placeholders, say so explicitly, and let the user know the document needs a
verification pass.

---

## Mode B — Audit

Read `references/audit.md` for the full guide. Summary:

1. **Inspect** the repo following the audit checklist (manifests, lockfiles,
   runtimes, Docker, CI, tests, quality configs, auth, secrets, observability,
   dependency freshness, docs).
2. **Inventory** the as-is stack per layer with a health class
   (healthy / caution / warning), using the `references/stacks/*.md` defaults
   as the comparison baseline — judgment over dogma, calibrated to stage and
   team size.
3. **Findings** classified as Critical / Warning / Improvement / Positive,
   each with evidence (file path, line when useful), why it matters, and a
   concrete, Docker-first suggestion.
4. **Checkpoint.** Walk the user through the findings, adjust severities if
   they provide context, then write `docs/stack-audit.md` from
   `templates/stack-audit.md`. Offer to also write `docs/stack.md` describing
   the target stack if they want the destination documented.

---

## Reference routing

| File | Load when |
|---|---|
| `references/interview.md` | Running Mode A (Phase 1–3 protocols) |
| `references/layers.md` | Deciding which layers apply, their order and dependencies |
| `references/decision-criteria.md` | Weighing options, health classes, version/stability policy |
| `references/stacks/python.md` | Language is Python |
| `references/stacks/typescript.md` | Language is TypeScript/Node |
| `references/stacks/java.md` | Language is Java |
| `references/deployment.md` | Layers 8–10 and microservices guidance |
| `references/security.md` | Layers 7 and 12, secrets and scanning |
| `references/audit.md` | Running Mode B |
| `templates/stack.md` | Writing the Mode A output |
| `templates/stack-audit.md` | Writing the Mode B output |

---

## Failure modes

- Do not batch interview questions or ask things already answered.
- Do not pass a checkpoint without an explicit user confirmation.
- Do not write version numbers from memory — verify, then record source + date.
- Do not propose native installs for services — Docker/compose or managed cloud.
- Do not scaffold code, config files, or CI YAML — documentation only.
- Do not load every reference up front — route on demand.
- Do not recommend pre-release versions or majors younger than ~3 months
  (unless LTS or security-driven) without flagging the risk.
- In audit mode, do not report a finding without evidence (file path), and do
  not modify any file other than the audit/stack documents.
