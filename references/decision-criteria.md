# Decision Criteria

How to weigh options, classify health, and enforce the version/stability
policy. Applies to both modes (Mode B uses the health classes to grade the
as-is stack).

## Evaluation dimensions

Weigh mentally, in this order of typical importance:

1. **Maturity & stability** — production-proven, stable API surface.
2. **Maintenance & governance** — active releases, healthy bus factor,
   credible stewardship (foundation, company, or strong maintainer).
3. **Ecosystem coherence** — plays well with the rest of the chosen stack;
   fewer paradigms per project beats one "best" tool per slot.
4. **Adoption & hiring** — community size, documentation quality, how easy
   it is to onboard a new engineer.
5. **Operational cost** — dependency footprint, memory, cold start, license.
6. **Cloud fit** — works on the target platform (containers, HTTP, managed
   integrations, gRPC/HTTP-2 support where needed).
7. **Migration path** — cost to walk away later; prefer boring exits.

## Health classes

- **HEALTHY** — confident default. Verify the version; done.
- **CAUTION** — viable with known tradeoffs or a fast-moving landscape. Say
  the tradeoff out loud when recommending.
- **AVOID** — do not recommend for new work without a strong user constraint
  (legacy, EOL, security posture, stagnant maintenance). Always name a
  replacement.

## Settled vs shifting categories

- **Settled** (state default + one-line why; health-check only, don't ask):
  package manager, linter/formatter, type checker, test runner, migration
  tool, logging library, container base image policy, secret scanning.
- **Shifting** (compare 2–3 with one-line tradeoffs and a recommendation):
  web/API framework, ORM, frontend meta-framework, auth provider, IaC,
  queue/broker technology, GraphQL tooling, MCP SDK feature level, gRPC
  codegen stack.

When in doubt, treat a category as shifting — one extra question is cheaper
than a wrong default.

## Conflict resolution priority

1. User constraints (explicit "must").
2. User avoid list ("never X").
3. Ecosystem coherence.
4. Health class.
5. Team familiarity.

Apply top-down. When a lower criterion wins over a higher one (rare), say so
in the rationale.

## Version & stability policy (binding for Mode A Phase 3)

- Recommend the **latest stable** of everything, **verified at generation
  time** from official sources. Never from memory, never stale.
- **Exclusions from "latest":**
  - majors younger than ~3 months, unless LTS or security-driven;
  - pre-releases (alpha, beta, RC, preview) — never recommended;
  - runtime lines: prefer LTS (JDK LTS releases; Node active LTS per the
    release schedule; Python latest stable minor).
- **Container images:** pin `major.minor` (e.g., `postgres:17`), never
  `:latest`.
- **Record** in `docs/stack.md`: dependency, version, source, verification
  date.
- No web access → `TBD — verify` placeholders and an explicit warning; never
  guess.

## Presenting tradeoffs

Maximum 3 options per decision. One line of pros/cons each. Always a clear
recommendation. "Let me decide" applies the recommendation and marks it
`default — revisit` in the output document.
