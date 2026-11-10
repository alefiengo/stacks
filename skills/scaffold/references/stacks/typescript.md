# TypeScript execution guide

Use this guide in Phase 2 — Generate, Phase 3 — Configure, and Phase 4 —
Verify when `docs/stack.md` decides a TypeScript or Node.js component. It
executes decisions; it never adds a tool, service, or file that the document
did not decide. Apply [execution safety](../execution-safety.md) to every
command and [verification](../verification.md) to every check.

Commands and options below were checked on 2026-11-10 against local `--help`
output and runs of pnpm, npm, Docker, and each generator, and against official
documentation. Options and defaults change between releases: re-verify each
one in every run and record how. Versions come only from raw registry
responses at run time, fetched with a direct HTTPS GET of
`https://registry.npmjs.org/<package>` (`dist-tags` and `versions`) or
`https://registry.npmjs.org/<package>/<version>`. Before approval, never use
`pnpm view` or `npm view`, as the
[command limits](../execution-safety.md#command-limits) explain.

## Generate

### Package manager and manifest

Use the package manager that L1 decided; pnpm is the `stacks` default. Write
`pnpm-workspace.yaml` with the
[script and release-age settings](#install-scripts-release-age-and-registries)
before the first `pnpm add` or `pnpm install` that the plan runs, merging it
into a file a generator wrote, and list it as a Phase 2 file; `create-hono`,
which installs by itself, is the exception below. Without a generator,
initialize and set the decided values first:

```bash
pnpm init --bare --no-init-package-manager
pnpm pkg set name=<name> packageManager=pnpm@<verified-version> engines.node=<decided-range>
pnpm pkg set private=true --json
```

- Plain `pnpm init` pins the newest pnpm, not the decided one, and adds
  `license`, `author`, and `main` fields. `--bare` writes only
  `"type": "module"`; with `--init-type commonjs`, used only if the document
  decided CommonJS, it writes an empty manifest.
- A `packageManager` version other than the installed pnpm is downloaded
  into a cache outside the root; name that download in the plan.
- npm: `npm init --yes`, then `npm pkg set` the same fields.
- Add only decided packages, with `@types/node` at the decided Node.js major:
  `pnpm add <package>` and `pnpm add -D typescript @types/node@<node-major> <tool>`.

### Frameworks and workers

Invoke a generator at an exact verified version through
`pnpm dlx <generator>@<verified-version>`, never `@latest`, in the directory
the plan names. Generators that refuse or prompt on a non-empty directory run
in a new subdirectory and are moved into the root, as
[execution safety](../execution-safety.md) describes.

| Decision | Command |
|---|---|
| Hono | `pnpm dlx create-hono@<v> <dir> --template <decided-adapter> --pm pnpm --install` |
| Fastify | No generator: `pnpm add fastify`, then the TypeScript setup below |
| NestJS | `pnpm dlx @nestjs/cli@<v> new <name> --package-manager pnpm --skip-git --skip-install --strict --no-observe` |
| Vite + React | `pnpm dlx create-vite@<v> <dir> --template react-ts --no-interactive --no-immediate` |
| Next.js | `pnpm dlx create-next-app@<v> <dir> --ts --app --use-pnpm --skip-install --disable-git` plus one flag per option below |

- `create-hono` prompts unless `--install` is given, so it always installs,
  with the template's `pnpm-workspace.yaml` rather than the decided settings.
  Its template is not in the package: check in the generator's source for the
  planned version where it downloads from. When checked, it fetched
  `templates/<template>` of the `honojs/starter` repository at the branch
  `v<major>.<minor>` of its own version, through `api.github.com` redirected
  to `codeload.github.com`. Name those hosts in the plan and apply the
  [runtime template rule](../execution-safety.md#supply-chain): before
  approval, read the template's `package.json` and `pnpm-workspace.yaml` at
  `https://raw.githubusercontent.com/honojs/starter/<ref>/templates/<template>/`
  and list each `allowBuilds` entry set to `true` and each lifecycle script as
  a script the install runs.
- `create-next-app --yes` reuses preferences saved on the host. Pass one flag
  per option its current reference lists, such as `--biome`, `--eslint`, or
  `--no-linter`; `--tailwind` or `--no-tailwind`; `--src-dir` or
  `--no-src-dir`; `--react-compiler` or `--no-react-compiler`;
  `--cache-components` or `--no-cache-components`; `--turbopack` or
  `--webpack`; `--import-alias <alias>`; `--api` or `--empty` only when the
  document decided that shape; and `--no-agents-md --no-agent-feedback`
  unless those were decided. An option the document did not decide is a
  question in the plan, never the generator's default.
- Its App Router templates import a font from `next/font/google`, which
  downloads font files from `fonts.googleapis.com` and the hosts its CSS
  names during `next build`; name that download in the plan or replace the
  font as a planned change. `next build` and `next dev` also send telemetry
  unless `NEXT_TELEMETRY_DISABLED=1` is set; set it for every `next` command
  the plan runs, or name telemetry as a network destination the user
  accepted.
- `fastify-cli generate --lang=ts` adds `@fastify/autoload`, `ts-node`, and
  Node's test runner; use it only if the document decided it.
- Generators add undecided extras: NestJS added `AGENTS.md`, Oxlint,
  Prettier, a `deploy` script, and `@nestjs/mau`; `create-vite` React
  templates add Oxlint (`--eslint` switches to ESLint). List each removal in
  the plan. Align the versions generators pick for TypeScript, `@types/node`,
  and linters with `docs/stack.md`, or report the mismatch.
- **Worker or batch job without a web framework:** a bare project with
  `src/index.ts`, the decided queue library, and no HTTP module. Handle
  `SIGTERM` by stopping intake and awaiting in-flight work; the test calls the
  job function directly.

## Configure

### Install scripts, release age, and registries

These settings are written in Phase 2, before the first install, so that the
first resolution already applies them. pnpm blocks dependency build scripts
by default: an unreviewed one fails the install with `ERR_PNPM_IGNORED_BUILDS`
(`strictDepBuilds`). Allow or deny packages with `allowBuilds` in
`pnpm-workspace.yaml`. pnpm does not read settings from the `pnpm` field of
`package.json`, and `.npmrc` holds only auth, registry, TLS, and proxy
settings, so never open or write it.

```yaml
allowBuilds:
  <package>: false   # true only when the plan allows it
minimumReleaseAge: <decided-minutes>
registries:          # only for a private registry the document decided
  "@<scope>": https://<private-registry-host>/
```

- Generators may write this file with their own entries. When a generator
  skips the install, merge the decided settings into its file before the
  first install. Read the generated file and report every `true` entry as an
  allowed script.
- Allowing a blocked script later is a new checkpoint; then run
  `pnpm approve-builds <package>` (`'!<package>'` denies).
- pnpm documents a default `minimumReleaseAge`; check it in pnpm's current
  settings documentation and do not rely on it. Set the decided value
  explicitly when the document decided a release-age gate, and confirm it
  with `pnpm config get minimumReleaseAge`, which prints only a configured
  value. A decided version inside the gate fails the install; ask instead of
  excluding it.
- A private registry the document decided goes in `registries`; its
  credentials stay in the user's own configuration outside the project, set
  by the user.
- npm: check the installed npm's `npm help install` for its script and
  release-age settings. Where it documents an `allowScripts` field in
  `package.json`, with `--strict-allow-scripts`, use that policy; otherwise
  pass `--ignore-scripts` to every `npm install` and `npm ci`. Pass
  `--min-release-age <days>` when decided and documented for the command.
  `--ignore-scripts` also skips the project's own lifecycle scripts and the
  `pre` and `post` scripts of `npm run` and `npm test`.
- Yarn skips third-party `postinstall` scripts by default (`enableScripts`)
  and has `npmMinimalAgeGate`; never write `npmAuthToken` to `.yarnrc.yml`.

### TypeScript, lint, format, and tests

- Without a generator tsconfig, run `pnpm exec tsc --init`: it sets `strict`
  and `"types": []`; set `"types": ["node"]` for Node.js code and `outDir`
  when the build emits files.
- Check peer ranges before the plan in the `peerDependencies` of
  `https://registry.npmjs.org/<package>/<version>`; a linter's TypeScript
  range can lag the newest TypeScript major. Ask about a conflict between
  decided versions; never pick another version.
- **Biome:** `pnpm exec biome init`, then set `files.includes` to the
  project's source and configuration (for example `src/**` and `*.json`).
  Biome also formats Markdown, so an unrestricted `biome check --write .`
  rewrites `docs/stack.md` and installed agent skills; a trial did exactly
  that. Its formatter rejected the pnpm-written `package.json`; run the
  restricted `pnpm exec biome check --write` once in Phase 3, named in the plan.
- **ESLint and Prettier:** follow the typescript-eslint quickstart
  (`eslint`, `@eslint/js`, `typescript-eslint`, and `eslint.config.mjs`) and
  add `prettier`. Prettier formats Markdown, so `prettier --check .` reaches
  `docs/` and agent skill directories, and the matching `--write .` rewrites
  them. Write a `.prettierignore`, named in the plan, that excludes `docs/`
  and the agent skill and configuration directories in the root, or pass
  explicit source and configuration paths. ESLint lints only files its
  configuration matches; an ESLint `--fix` stays on those paths unless a
  Markdown plugin was decided.
- **Vitest:** add `vitest` and the scripts `"test": "vitest run"` and
  `"typecheck": "tsc --noEmit"`. Write one passing test of a pure function, or
  an in-process request; export the app without starting the server:

  ```ts
  import { expect, test } from "vitest";
  import { app } from "./app.js";

  test("GET / responds", async () => {
    const res = await app.request("/");
    expect(res.status).toBe(200);
  });
  ```

  `app.request` is Hono's; Fastify uses `app.inject`. A component test needs a
  DOM environment package that the document must list.

### Environment, container, and services

- `.env.example` lists only the variable names the code reads, with empty
  values. Make sure `.gitignore` excludes `.env`.
- When L8 decided an image, use a multi-stage build. Corepack is not bundled
  with Node.js 25 or later; copy pnpm from its official image, per pnpm's
  Docker guide. Copy `pnpm-workspace.yaml` before installing, so the build
  keeps `allowBuilds`.

  ```dockerfile
  FROM node:<tag>@sha256:<verified-digest> AS base
  COPY --from=ghcr.io/pnpm/pnpm:<tag>@sha256:<verified-digest> /opt/pnpm /opt/pnpm
  RUN ln -s /opt/pnpm/pnpm /usr/local/bin/pnpm
  WORKDIR /app
  COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./

  FROM base AS build
  RUN pnpm install --frozen-lockfile
  COPY . .
  RUN pnpm run build

  FROM base AS prod-deps
  RUN pnpm install --frozen-lockfile --prod

  FROM node:<tag>@sha256:<verified-digest>
  ENV NODE_ENV=production
  WORKDIR /app
  COPY --from=prod-deps /app/node_modules ./node_modules
  COPY --from=build /app/dist ./dist
  USER node
  CMD ["node", "dist/<entry>.js"]
  ```

  Use the pnpm image tag of the `packageManager` version, with the Node
  base's C library (`-alpine` for Alpine). Run `node` directly so signals
  reach it; official Node images provide the `node` user. Add a
  `.dockerignore` excluding `node_modules` and `.env`.
- Digest: the SHA-256 of `docker buildx imagetools inspect --raw <image>:<tag>`
  must equal the `Digest` of `docker buildx imagetools inspect <image>:<tag>`.
- `compose.yaml` holds only decided services, each with a `healthcheck`, and
  dependents use `depends_on` with `condition: service_healthy`; values come
  from an `env_file` with placeholders.

### CI

For GitHub Actions, pnpm documents `pnpm/setup`, which reads the pnpm version
from `packageManager`. Disable its install and run the frozen one. A workflow
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
      - uses: pnpm/setup@<verified-sha> # v<release>
        with:
          runtime: node@<decided-major>
          install: false
      - run: pnpm install --frozen-lockfile
      - run: pnpm run lint
      - run: pnpm run typecheck
      - run: pnpm test
      - run: pnpm run build
```

- Resolve each SHA with the unauthenticated GitHub API requests that
  [execution safety](../execution-safety.md#supply-chain) shows.
- npm: `actions/setup-node` with `node-version-file` and `cache: npm`, then
  `npm ci --ignore-scripts`. Yarn: `yarn install --immutable`.

## Verify

Run in the project root, in this order, after the last file change. Before
the first of them, read the `scripts` of every manifest the run wrote or
changed: these commands run the lifecycle and `pre` or `post` scripts that
the [command limits](../execution-safety.md#command-limits) describe.

| Check | Command | Passing condition |
|---|---|---|
| Install from lock | `pnpm install --frozen-lockfile` | Exit 0, lockfile unchanged |
| Blocked scripts | `pnpm ignored-builds` | Lists no package outside the plan's denied ones |
| Lint (Biome) | `pnpm exec biome ci .` | Exit 0; never `--write` here |
| Lint (ESLint, Prettier) | `pnpm exec eslint .` and `pnpm exec prettier --check .` with the planned `.prettierignore`, or explicit paths | Exit 0 |
| Types | `pnpm exec tsc --noEmit`; Vite: `pnpm exec tsc -b` | Exit 0 |
| Tests | `pnpm test` | Exit 0, at least one test ran |
| Build | `pnpm run build` | Exit 0 |
| Compose, if decided | `docker compose config --quiet` | Exit 0 |
| Image, if the plan names it | `docker build --tag <local-tag> .` | Exit 0; never push |

- Vite's root `tsconfig.json` has only references, so `tsc --noEmit` there
  checks nothing; `tsc -b` checks each referenced project.
- Record each command, exit code, and date as [verification](../verification.md)
  defines. The CI workflow is recorded as defined, not as passing.
