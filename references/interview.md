# Interview Guide (Mode A)

Plan-style interview for stack definition. Core behaviors:

- **One question per message.** Never bundle.
- **Never ask what is known.** The user's opening message ("we're building a
  Python API") pre-answers questions — mark them answered and skip.
- **Adapt.** Each question depends on previous answers; skip whatever became
  irrelevant (a stateless stdio MCP server has no data layer).
- **Explain briefly** why you ask when the reason is not obvious.
- **"Let me decide"** must be available whenever a sensible default exists.

## Intake rules (before the first question)

1. Repo scan: empty? manifests present? If manifests exist and the user asked
   for a *new* stack, confirm they want a redefinition (or switch to Mode B).
2. Collect declared facts from the conversation: language, profile, hosting,
   constraints. Record them as answered.
3. Determine the profile list — combinations are common (REST API + web
   frontend = fullstack web).

## Phase 1 — Scope questions

### Q1 — What are you building? *(skip if declared)*

Options: REST API · MCP server · GraphQL API · gRPC service · Web frontend ·
Microservices system · Combination (describe).

If the answer includes both a frontend and an API, ask one follow-up: single
codebase (e.g., a fullstack meta-framework) or separate frontend and backend?
This shapes the L3 structure decision later.

### Q2 — Language? *(skip if declared)*

Options: Python · TypeScript · Java · No preference — recommend one.

If no preference, recommend by profile fit and say why:
- MCP server → Python or TypeScript (first-class official SDKs).
- REST/GraphQL API → Python (velocity, data ecosystem), TypeScript (shared
  types with a JS frontend), Java (enterprise durability, larger teams).
- gRPC service → any; the contract is polyglot — follow team strength.
- Web frontend → TypeScript.
- Microservices → default to the team's strongest language; polyglot only
  with a reason.

### Q3 — Who is it for and at what scale?

Options: Just me / internal tool · Small team or early product (<1k users) ·
Product with growth targets.

Why it matters: managed vs self-hosted services, auth provider tier, and how
much operational investment the stack should assume.

### Q4 — Where will it run?

Options: Google Cloud Run · Another managed platform (Fly.io, Render, App
Runner…) · Self-hosted (VM/Kubernetes) · Undecided — recommend.

Default recommendation for backend profiles: Cloud Run, unless a constraint
says otherwise. Profile notes: gRPC services work on Cloud Run with HTTP/2
enabled; remote MCP servers use Streamable HTTP on Cloud Run; frontends may
prefer static hosting/CDN.

### Q5 — Any hard constraints?

Free text or "none". Examples: an existing database to integrate with,
corporate standards, compliance (SOC 2, GDPR, HIPAA), air-gapped
environments, team familiarity. Constraints override every later default.

### Q6 — *(microservices only)* How many services, and how big is the team?

Feeds the monorepo vs polyrepo and modular-monolith guidance in L3/L10.

### Phase 1 checkpoint — recommendation

Present the proposed stack:

```
Recommended stack (proposal — nothing decided yet)

| Layer | Recommendation | Why (one line) |
| ...   | ...            | ...            |

Rationale: 2–3 sentences grounded in their specific answers.
Alternatives for the contentious picks (usually L2) get one line each.

Use this stack? → [use as is] / [swap one thing] / [different direction]
```

- **use as is** → Phase 2 with the table pre-confirmed for settled layers.
- **swap one thing** → ask which piece, regenerate only that delta, re-confirm.
- **different direction** → return to Q1/Q2.

## Phase 2 — Layer decisions

Walk `references/layers.md` order (L1→L12). Rules:

- Skip non-applicable layers (skip rules in `references/layers.md`).
- **Settled categories** (package manager, formatter, test runner, migration
  tool): state the default + one-line why as a health check, don't ask.
- **Shifting categories** (web framework, ORM, auth provider, IaC, queue
  technology, frontend meta-framework, MCP SDK, GraphQL tooling): ask, with
  2–3 options, one-line tradeoffs, a recommendation, and "let me decide".
  Option details come from `references/stacks/<language>.md`.
- Cross-cutting defaults: `references/deployment.md` for L8–L10,
  `references/security.md` for L7/L12.

Key dependencies to respect while asking:

- L6 engine choice precedes L6 ORM/migration choice.
- L6 cache/queue questions only if the user reported background work,
  caching, or session needs.
- L7 auth questions only if the service is exposed beyond the local network.
- L10 scaling/IaC questions depend on the Q4 platform answer.
- L9 CI questions depend on the git host (ask it here if never established;
  default GitHub).

### Phase 2 checkpoint — consolidated decision table

```
| # | Layer | Decision | Status |
|---|-------|----------|--------|
Status: confirmed / default — revisit

Does this all look right? → [yes, write it up] / [adjust layer N]
```

## Phase 3 — Version verification protocol

1. **Compile** the dependency list from confirmed decisions: runtime, package
   manager, frameworks, libraries, compose service images, container base
   images, auth provider tier.
2. **Verify each** against its official source, current at generation time:
   - Python packages → PyPI JSON API (`https://pypi.org/pypi/<pkg>/json`),
     ignore pre-releases.
   - Node packages → npm registry (`https://registry.npmjs.org/<pkg>`,
     `dist-tags.latest`).
   - Java artifacts → Maven Central (`https://search.maven.org`).
   - Runtimes → python.org, nodejs.org release schedule, JDK LTS pages.
   - Container images → Docker Hub / ghcr tags; pin `major.minor`, never
     `latest`.
3. **Apply the stability policy** (`references/decision-criteria.md`):
   latest stable, no majors <3 months old unless LTS or security-driven, no
   pre-releases. Anything excluded is listed in the document as "not adopted:
   <reason>".
4. **Checkpoint 3** — show the version table (dependency → version → source)
   and get confirmation.
5. **Write** `docs/stack.md` from `templates/stack.md`, including the
   verification log (date + source per dependency).

No web access → `TBD — verify` placeholders and an explicit warning to the
user; never guess.
