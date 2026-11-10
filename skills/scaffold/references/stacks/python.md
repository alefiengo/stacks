# Python execution guide

Use this guide in Phase 2 — Generate, Phase 3 — Configure, and Phase 4 —
Verify when `docs/stack.md` decides a Python component. It executes decisions;
it never adds a tool, service, or file that the document did not decide. Apply
[execution safety](../execution-safety.md) to every command and
[verification](../verification.md) to every check.

Commands and options below were checked against uv's local `--help` output and
the official uv, Django, Docker, pytest, ruff, mypy, and GitHub documentation.
Options and defaults change between releases: re-verify each one against the
installed tool's `--help` or its current official documentation in every run,
and record how. Versions come only from raw registry responses at run time,
fetched with a direct HTTPS GET such as `https://pypi.org/pypi/<package>/json`.

## Generate

Initialize with uv when L1 decided it. `uv init` fails if `pyproject.toml`
already exists in the target; an existing file goes through the plan, never an
overwrite.

| Decision | Command, run in the project root |
|---|---|
| Packaged application, `src/` layout | `uv init --app --package --no-workspace --vcs none --author-from none --python <decided-version>` |
| Unpackaged application (flat, `main.py`) | `uv init --app --no-package --no-workspace --vcs none --author-from none --python <decided-version>` |
| Library | `uv init --lib --no-workspace --vcs none --author-from none --python <decided-version>` |
| Only `pyproject.toml` (Django) | `uv init --bare --no-workspace --python <decided-version>`, then `uv python pin <decided-version>` |

- `--no-workspace` keeps uv from joining a workspace it discovers above the
  root: without it, `uv init` adds the project as a member of a parent
  directory's workspace and writes that parent's `pyproject.toml`, outside the
  root. It affects only `uv init`; later uv commands still treat the project
  as a member of a parent workspace whose `members` match it, and write that
  workspace's `uv.lock` outside the root. `scaffold` cannot read outside the
  root to rule that out, so, right after `uv init`, add an empty
  `[tool.uv.workspace]` table to the project's `pyproject.toml`, which makes
  the project its own workspace root; name it in the plan. Re-verify both
  behaviors for the installed uv.
- `--vcs none` leaves version control to the user; use `--vcs git` only if the
  plan names repository creation. `--author-from none` keeps the host's Git
  identity out of `pyproject.toml` unless the plan names an author.
- `--python` sets `requires-python` and, except with `--bare`, writes
  `.python-version`. Check both against the decided version afterwards; with
  `--bare`, `uv python pin <decided-version>` writes the pin that CI and
  `uv python install` read.
- Without `--python`, uv derives the floor from an interpreter it finds,
  which may not be the decided one.
- When no matching interpreter is installed, uv downloads a managed one into
  its own data directory, outside the root; by default from the
  `python-build-standalone` releases on GitHub. Check the source in uv's
  current settings documentation and name the download in the plan, or pass
  `--no-python-downloads` and stop if the interpreter is missing. uv's cache
  is also outside the root; name it in the plan.
- The default build backend comes from uv; use `--build-backend` only when the
  document decided another one.

Add only the decided packages, at the decided constraints:

```bash
uv add --no-build <runtime-package>==<verified-version> ...
uv add --dev --no-build <lint-type-test-package>==<verified-version> ...
uv lock --no-build      # only when pyproject.toml changed outside uv add
```

Use `--group <name>` instead of `--dev` only when the document names separate
dependency groups. `uv add` writes `uv.lock`; keep it in the project.

### Frameworks and workers

- **FastAPI or Litestar:** neither has a project generator in this workflow.
  Create the uv project, add the framework and the decided ASGI server, and,
  only when the component exposes HTTP, add one module with a health endpoint
  and a test for it. Verify the import path, decorator, and test client in the
  framework's current documentation; the test client may need an HTTP client
  package that the document must already list.
- **Django:** run the generator through the project environment after adding
  Django, so the installed, locked version generates the code:

  ```bash
  uv init --bare --no-workspace --python <decided-version>
  # add the empty [tool.uv.workspace] table to pyproject.toml here
  uv python pin <decided-version>
  uv add --no-build django==<verified-version>
  uv run django-admin startproject <config-package> .
  ```

  `.` uses the root as the project directory. Do not pass `--template`: a
  template runs third-party content. Keep Django's layout instead of `src/`.
- **Worker or batch job without a web framework:** a packaged application with
  the entry point in `[project.scripts]`, the decided queue library, and no
  HTTP module. The test calls the job function directly.

## Configure

### Install scripts

Building a source distribution runs its build backend, which is arbitrary
code. Block it by default in `pyproject.toml`, a non-secret file uv reads:

```toml
[tool.uv]
no-build = true
# no-build-package = ["<package>"]  # use instead of no-build to block named packages only
```

- With `no-build`, any package without a usable wheel fails to install, and
  uv reuses cached wheels from earlier builds. A package that needs a source
  build is a new checkpoint: list the package, the reason, and the narrower
  setting that allows it.
- uv still builds first-party projects and editable requirements, so the
  project's own build backend runs; report it as allowed.
- Never open an existing `.pypirc`. A private index the document decided goes
  in `[[tool.uv.index]]` in `pyproject.toml`; its credentials stay outside the
  project, in the `UV_INDEX_<NAME>_USERNAME` and `UV_INDEX_<NAME>_PASSWORD`
  variables that the user sets.

### Quality and tests

Put the decided tools' settings in `pyproject.toml`; keep them short and add
rules only when the document decided them:

```toml
[tool.ruff.lint]
select = ["E", "F", "I"]

[tool.mypy]
strict = true

[tool.pytest]
testpaths = ["tests"]
```

- `[tool.pytest]` uses native TOML values but only recent pytest releases read
  it; check the decided version's configuration docs and otherwise use
  `[tool.pytest.ini_options]`.
- With pyright instead of mypy, use `[tool.pyright]` and its
  `typeCheckingMode`; confirm the pyright distribution and how it runs from the
  current official documentation before naming it in the plan.
- With Django, a plugin such as a mypy or pytest plugin for Django is added only
  if the document decided it; otherwise tests use Django's own runner.
- Write one minimal test that passes against generated code, for example the
  health endpoint or the job function, in `tests/` (Django: the app's tests
  module).
- Generator output may not meet the configured checks: Django's
  `startproject` output failed `ruff format --check` and strict mypy in a
  trial. Format it once in Phase 3 with `uv run ruff format` on the project's
  source and test paths, named in the plan. A type error that needs an undecided stub package or a weaker setting
  is reported, not hidden by relaxing the configuration.

### Environment, container, and services

- `.env.example` lists only the variable names the generated code reads, with
  empty values. Make sure `.gitignore` excludes `.env` before anything could
  create it.
- When L8 decided an image, follow uv's official Docker guide: a builder stage
  that installs dependencies before copying the source, then a final stage.
  Add a `.dockerignore` that excludes `.venv` and `.env`. Copying only
  `/app/.venv` works only for a packaged project installed with
  `--no-editable` whose entry point is in `[project.scripts]`. An unpackaged
  application, including Django from `--bare`, is not installed into
  `.venv`: also copy its code paths into the final stage and run
  `/app/.venv/bin/python <module-or-manage.py>` with the decided arguments.
  A passing image build proves the build, not that the container starts.

  ```dockerfile
  FROM python:<tag>@sha256:<verified-digest> AS builder
  COPY --from=ghcr.io/astral-sh/uv:<verified-version>@sha256:<verified-digest> /uv /uvx /bin/
  ENV UV_PYTHON_DOWNLOADS=0 UV_NO_BUILD=1
  WORKDIR /app
  RUN --mount=type=cache,target=/root/.cache/uv \
      --mount=type=bind,source=uv.lock,target=uv.lock \
      uv sync --frozen --no-install-project --no-editable --no-dev
  COPY . /app
  RUN --mount=type=cache,target=/root/.cache/uv \
      uv sync --locked --no-editable --no-dev

  FROM python:<tag>@sha256:<verified-digest>
  RUN useradd --system --uid 10001 app
  COPY --from=builder /app/.venv /app/.venv
  # Unpackaged application: COPY --from=builder /app/<code-path> /app/<code-path>
  USER app
  CMD ["/app/.venv/bin/<entry-point>"]
  # Unpackaged: CMD ["/app/.venv/bin/python", "<module-or-manage.py>", "<decided-arguments>"]
  ```

  The first sync mounts only `uv.lock`, so `[tool.uv]` settings are not read
  there; `UV_NO_BUILD=1` keeps source builds blocked. Use the same base tag in
  both stages; the final stage needs the builder's Python at the same path.
  Re-verify `useradd` options for the base image's distribution.
- Image references use a readable tag plus a digest. Take the digest from the
  registry's raw manifest: the SHA-256 of
  `docker buildx imagetools inspect --raw <image>:<tag>` must equal the
  `Digest` that `docker buildx imagetools inspect <image>:<tag>` reports.
- `compose.yaml` contains only decided services, such as PostgreSQL, each with
  a `healthcheck` (`test`, `interval`, `timeout`, `retries`) and dependents
  using `depends_on` with `condition: service_healthy`. Values come from an
  `env_file` with placeholders; never inline a credential.

### CI

When L9 decided a host, write one workflow for it. A GitHub Actions workflow
needs `on:`; use the triggers section 6 decided, and if it decided none, ask
in the plan:

```yaml
on:
  <decided-trigger>:   # for example pull_request, or push with branches
permissions:
  contents: read
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@<verified-sha> # v<release>
      - uses: astral-sh/setup-uv@<verified-sha> # v<release>
        with:
          version: "<verified-uv-version>"
      - run: uv python install
      - run: uv sync --locked
      - run: uv run ruff check
      - run: uv run ruff format --check
      - run: uv run mypy <source-dirs> tests
      - run: uv run pytest
```

- Resolve each SHA with the unauthenticated GitHub API requests that
  [execution safety](../execution-safety.md#supply-chain) shows.
- `uv python install` honors `.python-version`; without that file it does not
  install the decided version, so the plan pins it. `actions/setup-python`
  with `python-version-file` is the documented alternative.
- For another decided host, express the same steps in its syntax with its
  equivalent pinning mechanism.

## Verify

Run in the project root, in this order, after the last file change:

| Check | Command | Passing condition |
|---|---|---|
| Lockfile current | `uv lock --check` | Exit 0 |
| Install from lock | `uv sync --locked` | Exit 0, lockfile unchanged |
| Lint | `uv run ruff check` | Exit 0; never add `--fix` here |
| Format | `uv run ruff format --check` | Exit 0, no file rewritten |
| Types (mypy) | `uv run mypy <source-dirs> tests` | Exit 0 |
| Tests | `uv run pytest` | Exit 0, at least one test collected |
| Django checks | `uv run python manage.py check` | Exit 0 |
| Django tests | `uv run python manage.py test` | Exit 0 and at least one test ran |
| Image, if the plan names it | `docker build --tag <local-tag> .` | Exit 0; never push |

- pytest exits 5 when it collects no tests; that is `failed`. Django's runner
  exits 0 with `NO TESTS RAN`, which is also `failed`.
- A type-check row applies only to the decided checker; replace it with the
  pyright command when pyright was decided.
- Record each command, exit code, and date as [verification](../verification.md)
  defines. The CI workflow is recorded as defined, not as passing.
