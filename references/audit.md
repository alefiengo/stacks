# Audit Guide (Mode B)

How to audit an existing project's stack: what to inspect, how to grade, and
how to write findings.

## Principles

- **Evidence-based.** Every finding cites a file path (line number when
  useful). Never report a finding on a file you have not read.
- **Constructive.** Acknowledge what is solid before listing problems.
  Calibrate severity to context: stage, team size, and exposure.
- **No code changes.** The audit writes `docs/stack-audit.md` (and
  `docs/stack.md` only if the user asks for the target stack). Suggestions
  are concrete but the user applies them.
- **Docker-first applies to suggestions too.**
- **Judgment over dogma.** Compare against the `stacks/*.md` defaults, but
  a Flask app serving three internal endpoints is fine; the same stack
  behind a payments API is a Warning or Critical finding.

## Inspection checklist (in order)

1. **Manifests:** `pyproject.toml` / `package.json` / `pom.xml` /
   `build.gradle(.kts)` — dependencies, scripts, tool configs.
2. **Lockfiles:** uv.lock / pnpm-lock.yaml / package-lock.json /
   gradle.lockfile present? Reproducible builds?
3. **Runtime versions:** `.python-version`, `.nvmrc`, `engines` fields,
   Dockerfile bases — any EOL or near-EOL runtimes?
4. **Docker:** Dockerfile(s) — multi-stage? root user? pinned bases? Compose
   files? `.dockerignore`?
5. **CI:** `.github/workflows/` — what gates exist (lint, types, tests,
   scans, deploys)? Secrets handled via platform store?
6. **Tests:** present at all? Layout? Coverage config? Integration tests vs
   unit-only?
7. **Code quality:** linter/formatter/type checker configured and wired
   into CI?
8. **Data:** migrations tool in place? Schema in VCS? Backup story (managed
   DB with automated backups)?
9. **Auth & secrets:** hand-rolled crypto or sessions? `.env` files
   committed (check `git ls-files`)? Hardcoded credentials in configs?
10. **Observability:** structured logging? Health endpoint? Metrics/traces?
11. **Freshness:** scan the top ~10 core dependencies against their
    registries — outdated majors, deprecated packages, abandoned libs.
12. **Docs:** README accuracy; existing stack/architecture docs.

## Severity definitions

- **Critical** — exploitable, data-loss, or EOL *today*: committed secrets,
  no auth on exposed mutating endpoints, injection-prone query building,
  EOL runtime, secrets baked into images.
- **Warning** — operational debt that will bite: no CI, no tests, no
  lockfile, unmaintained core dependency, no health checks, no backups.
- **Improvement** — a materially better current default exists: tooling
  consolidation (two tools where one suffices), aging-but-working choices
  with modern equivalents, missing scanning layers.
- **Positive** — worth keeping. Always include some: they anchor trust and
  protect good decisions from future churn.

## Finding format

```
[SEVERITY][L{layer}] Short title
Evidence: path/to/file:line
Why it matters: one or two sentences.
Suggestion: concrete, Docker-first where relevant.
```

## Report structure

Use `templates/stack-audit.md`:

1. **Context** — repo, stage, team size, audit purpose.
2. **Inspection scope** — what was examined (checklist sections covered).
3. **As-is inventory** — table per layer: detected choice, version, health
   class.
4. **Findings** — table sorted by severity.
5. **Prioritized actions** — quick wins first, then structural work.
6. **Target stack (optional)** — only if the user wants the destination
   documented; then also offer `docs/stack.md`.

## Calibration

- Stage matters: a prototype without CI is an Improvement; a product
  without CI is a Warning.
- Exposure matters: public + mutating without auth is Critical; internal
  read-only may be Warning.
- Team size matters: heavy process for a 1-person project is a finding too
  (Improvement: simplify).
