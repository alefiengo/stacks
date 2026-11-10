# Decision criteria

Use these criteria in both modes of the [core workflow](../SKILL.md): compare
choices in Mode A and assess the observed stack in Mode B. The
[audit guide](audit.md) defines finding severity and evidence requirements.

## Evaluation dimensions

Weigh these dimensions in this usual order, adjusted to explicit requirements:

1. **Maturity & stability** — production-proven, stable API surface.
2. **Maintenance & stewardship** — active releases, healthy bus factor,
   credible stewardship (foundation, company, or strong maintainer), security
   response history (advisories handled and fixed releases shipped), signed or
   attested releases, and publishing practices such as protected release
   accounts and trusted publishing where the ecosystem supports them.
3. **License & governance** — verify the current license of the selected
   edition or release and whether its terms fit the intended use (internal,
   hosted, redistributed, or offered as a service). Record relicensing risk,
   who controls the roadmap, and any community fork or alternative worth
   comparing. Never state a license from memory.
4. **Ecosystem coherence** — plays well with the rest of the chosen stack;
   prefer a coherent system over independent tool rankings.
5. **Adoption & hiring** — community size, documentation quality, how easy
   it is to onboard a new engineer.
6. **Operational cost** — dependency footprint, memory, cold start, and paid
   tiers or support costs.
7. **Cloud fit** — works on the target platform (containers, HTTP, managed
   integrations, gRPC/HTTP-2 support where needed).
8. **Migration path** — cost of changing tools later; favor documented,
   practical exit paths.

## Health classes

This is the only definition of inventory health; other resources link here.

- **HEALTHY** — supported and coherent for the observed requirements, with
  adequate evidence. It does not certify the absence of vulnerabilities.
- **CAUTION** — viable with an evidenced tradeoff that matters to this project.
  Explain that tradeoff when recommending; missing evidence alone is UNKNOWN.
- **AT RISK** — a concrete issue with support, compatibility, security, or
  operations affects the project. Explain evidence, impact, and mitigation;
  recommend a replacement when justified.
- **UNKNOWN** — evidence is insufficient or verification was unavailable.
  State what must be checked; absence of evidence is not a demonstrated defect.
- **N/A** — the layer or component is outside the applicable scope, with reason.

Health describes fitness in context, independently of finding severity
(Critical / Warning / Improvement / Positive). A recommendation preference
does not make an alternative unhealthy. Do not turn uncertainty into a risk
claim or assign severity merely because a project differs from a default.

## Settled vs shifting categories

- **Settled** (state the contextual default and a one-line rationale; do not
  ask): package manager, linter/formatter, type checker, test runner,
  migration tool, logging library, container base image policy, secret
  scanning.
- **Shifting** (compare 2–3 with one-line tradeoffs and a recommendation):
  web/API framework, ORM, frontend meta-framework, auth provider, IaC,
  queue/broker technology, GraphQL tooling, MCP SDK feature level, gRPC
  codegen stack.

When in doubt, compare the tradeoff. Ask about a shifting category only if it
is unresolved, materially affects the outcome, and is not explicitly
delegated. Otherwise record the recommendation as `default — revisit` with its
rationale and assumption for review.

## Conflict resolution priority

1. User constraints (explicit "must").
2. User avoid list ("never X").
3. Ecosystem coherence.
4. Health class.
5. Team familiarity.

Apply top-down. Explain conflicts rather than silently overriding explicit
constraints. If requirements are incompatible, surface the unresolved choice
and mark it `open` until the user resolves it; do not claim a compliant
recommendation exists. Evidence of security or support risk must be disclosed
even when a user constraint retains the tool.

## Version and stability policy

Apply this policy to proposed versions in Mode A Phase 3 and to verified
recommendations in an audit. Preserve observed versions separately.

- Recommend the **latest compatible, supported stable** combination,
  **verified at generation time** using permitted official sources. Never
  invent current versions, support status, or compatibility from memory.
- Verify runtime support, framework/plugin matrices, peer dependencies,
  driver requirements, and Java BOM constraints. A registry version proves
  availability, not interoperability. Record why a newer release is excluded.
  Check release metadata and exclude yanked, withdrawn, or retracted releases
  from new recommendations; distinguish deprecation from a verified security
  advisory. In audits preserve observed versions and assess affected use.
- Prefer supported LTS runtime lines where available, subject to the stack's
  compatibility and security needs. A major younger than about three months
  warrants adoption-risk review; this is a heuristic, never a reason to keep
  an unsupported or vulnerable release. Exclude prereleases from normal
  recommendations; an explicit user requirement must be labeled as an
  exception with its risks, rather than called stable.
- **Container images:** use a verified readable tag plus immutable
  `@sha256:<digest>` for the intended platform when available. Tags, including
  `major.minor` and exact patch tags, can move. Do not call a tag-only selector
  reproducible; document the remaining verification/update work. Never invent
  a digest or use `:latest` as the recommended production selector.
- **Private or scoped registries:** do not query public registries for
  packages that resolve from a private or scoped registry, and never report a
  same-name public package as theirs. Mark them `TBD — verify` with the reason
  "private source". Determine the registry from registry URLs in lockfiles and
  index declarations in manifests, read as text; do not open `.npmrc` or
  `.pypirc`. A public npm scope is not private by itself; if a non-public
  scope's registry cannot be determined, treat it as a private source.
- **Record** per dependency in `docs/stack.md`: selected version/selector,
  exact source URL, verification or attempt date, verification state, and
  compatibility evidence. SaaS tiers and non-versioned services have policies,
  not fabricated version numbers. Do not claim transitive resolution without
  an actual lockfile or resolver result.
- With no access, restricted sources, partial access, or failed lookups, mark
  each unresolved value `TBD — verify`, retain verified entries, record the
  reason, and disclose that verification is partial. Never bypass source
  restrictions or claim a version, digest, or compatibility check succeeded
  without evidence.

## Verification and coverage states

Use these vocabularies exactly in checkpoints, both templates, and the
[compatibility guidance](compatibility.md). Each one answers a different
question; do not substitute one for another.

| Vocabulary | Values | Applies to |
|---|---|---|
| Item verification state | `verified` / `partial` / `unverified` | One dependency, image, or external claim |
| Overall verification status | `complete` / `partial` / `unavailable` | The whole document |
| Source access | `consulted` / `attempted` / `not queried` | One source for one item |
| Inspection coverage | `inspected` / `partial` / `not inspected` / `N/A` | One audit area |

- **verified** — a consulted official source established the value and the
  recorded compatibility evidence; **partial** — some of that was established,
  and the record states what remains; **unverified** — nothing was established.
- `TBD — verify` is the cell value for an unresolved version, digest, or
  compatibility claim. Its row is `unverified`, or `partial` when part of the
  check succeeded. It is never `verified`.
- Overall status is `complete` only when every applicable item is `verified`;
  `partial` when at least one is not; `unavailable` when no source could be
  consulted.
- **consulted** — the source was retrieved and read; **attempted** — a lookup
  was tried and failed, with reason; **not queried** — no lookup happened,
  for example because the source is disallowed, private, or unreachable from
  the host. Never present `attempted` or `not queried` as evidence.
- **inspected** — the area was read within scope; **partial** — sampled or
  limited, with the limit stated; **not inspected** — not read, which is not
  evidence of absence; **N/A** — the area does not exist in this project.

## Presenting tradeoffs

Maximum 3 concrete options per decision, plus "choose for me" when a sensible
default exists and free text. One line of pros/cons each; a clear recommendation
grounded in the context.

Decision status uses `confirmed / default — revisit / open / N/A`:

- **confirmed** — the user explicitly selected or accepted the choice.
- **default — revisit** — "choose for me", a delegated or assumed default, or
  an immaterial decision resolved without asking. Delegation does not turn
  assumptions into confirmed facts.
- **open** — an unresolved conflict or a decision the user leaves open. List
  every `open` item in the document's pending section with its impact.
- **N/A** — the layer or decision does not apply, with a reason.

Use these states consistently across checkpoints and documents. Keep
classifications separate: decision status records who selected a choice;
inventory health records its contextual fitness; verification state records
the evidence obtained. Security-control status follows the
[security guide](security.md). None of these alone proves implementation or a
successful operational check.
