# Repository decisions

Decisions about the repo as a whole. Each app keeps its own log in `apps/<app>/docs/DECISIONS.md`, for example
[Wizarding Thanksgiving's](../apps/wizard-thanksgiving/docs/DECISIONS.md). Newest at the bottom.

---

## R1 — A collection: one folder per app under `apps/`
*2026-11-25*

**Decision:** The repo is a collection of BUSY Bar tools, apps and animations. Each app is self-contained in
`apps/<folder>/`: its BUSY JS project in `app/`, optional generators and tests, and its own README and decision log.
Wizarding Thanksgiving moved from the repo root to `apps/wizard-thanksgiving/` with its history intact.

**Why:** More apps and tools are coming. A fixed per-app convention (`app/`, optional `prebuild.sh` and
`tests/check.sh`) lets one set of tools build, test, deploy and release any app without per-app scripts.

---

## R2 — Shared code goes in `lib/` and `tools/`, and is promoted when a second app needs it
*2026-11-25*

**Decision:**
- `lib/python/busybar/` holds what's already generic: the `.anim` writer and reader (`anim.py`), and LED-style
  previews (`preview.py`).
- `tools/` holds the shared scripts: `check`, `deploy`, `release`, `new-app` and `screens`.
- App-specific code stays with the app, such as Wizarding Thanksgiving's canvas, fonts, effects and sprites. Move a
  module into `lib/` when a second app wants it, not before.

**Why:** It avoids guessing at abstractions from a single example, while making the obviously reusable parts easy to
find.

---

## R3 — Formal GitHub Releases, built by CI from version tags
*2026-11-25 · replaces the earlier `releases/` folder*

**Decision:**
- Uploadable packages are published as **GitHub Releases**, not committed to the repo.
- `tools/release.sh <app>` tags `<app-folder>-v<version>` from a clean, current `main`.
- `.github/workflows/release.yml` checks that the tag matches the manifest version and is on `main`, builds and tests
  from the **committed** assets, and publishes the release with `<app-id>-<version>.tgz`, install steps and a
  SHA-256.

**Why:**
- Releases give one download page per version with notes and checksums, without binaries piling up in git history.
- Building from committed assets means users get exactly what was reviewed and tested on a device. Re-rendering on
  Linux could shift a pixel, because `libm` differs between platforms.
- Uploading a renamed `.tgz` works: installing `wizard.thanksgiving-1.0.0.tgz` through the stage → install → launch
  API was verified on a bar.

---

## R4 — Branch model: `main` (releases) ← `dev` (integration) ← `<contributor>/<topic>`
*2026-11-25*

**Decision:**
- `main` is the formal release branch. `dev` is the integration branch.
- All work happens on `<github-username>/<topic>` branches cut from `dev`, with a topic prefix such as `feat-`,
  `fix-`, `new-app-`, `tool-`, `docs-` or `hotfix-`.
- PRs go into `dev` (squash merge). Releases promote `dev` → `main` (merge commit). Hotfixes branch from `main` and
  are merged back into `dev`.
- Both protected branches require a PR and the CI `check` job, and block force pushes and deletion.

**Why:** You asked for development rigor. `main` always equals what's released, `dev` always builds, and CI checks
every change before it lands. Details are in [CONTRIBUTING.md](../CONTRIBUTING.md).

---

## R5 — Public-repo hygiene
*2026-11-25*

**Decision:**
- No personal or network details in files, docs or commit messages: home IPs and subnets, time zones, local paths,
  names beyond the GitHub identity, photos of homes, tokens.
- Tools default to the bar's USB address. Real addresses and passwords live in the git-ignored `.env`.
- Before the repo went public, its history was squashed to a single clean commit to remove earlier home-network
  details. The PR checklist repeats the rule.

**Why:** The repo is public and git history is permanent.

---

## R6 — CI
*2026-11-25*

**Decision:** `.github/workflows/ci.yml` runs on every PR and every push to `dev` and `main`:
1. It installs pinned Pillow and Node 24.
2. It runs `tools/check.sh`, which regenerates assets, typechecks, builds and runs each app's tests.
3. It reports, without failing, any regenerated assets that differ from the commit.
4. It builds again from the committed assets, which is what a release ships.

**Why:** Generators, TypeScript and packaging are all tested on every change. The difference report flags forgotten
asset commits without failing builds over cross-platform pixel noise.

---

## R7 — AGENTS.md is the single source for AI agents; CLAUDE.md imports it
*2026-11-25*

**Decision:**
- A vendor-neutral `AGENTS.md` at the root holds the instructions for AI coding agents: commands, repo map, workflow
  rules, definition of done, privacy, platform pitfalls and code style.
- `CLAUDE.md` imports it (`@AGENTS.md`) and adds only Claude Code specifics: plan first, look at LED previews, treat
  the device as a shared physical screen, and git and commit-message rules.
- Apps can have their own pair. Wizarding Thanksgiving's covers renderer invariants, clock parity and pixel-art rules.
  `tools/new-app.sh` generates stubs for new apps.

**Why:**
- One source means the two instruction sets can't drift apart. `AGENTS.md` is read by most coding agents, and
  Claude Code loads `CLAUDE.md`, which pulls it in.
- The rules come from this project's real failures: `src/*.ts` entry points, installing over a running app, black as
  unlit, and the wrong `npx busy-cli` package. They also draw on the BUSY scaffold's own guidance about conserving
  device resources.
- One rule was added after a near-miss while writing these guides: generate files with real file tools or
  uniquely named heredoc delimiters, never a nested `<<EOF` inside another `<<EOF`. That mistake made a shell run
  documentation text as commands. Nothing was harmed, but backticks in prose became command substitutions.
