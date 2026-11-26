# AGENTS.md

Instructions for AI coding agents (and humans in a hurry) contributing to **busybartools**: a public collection of
apps, animations and tools for the BUSY Bar, a 72×16 RGB LED display that runs JavaScript apps on the device.

Read this first. For depth, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) (platform and toolchain) and
[CONTRIBUTING.md](CONTRIBUTING.md) (branches, PRs, releases). An app folder may have its own `AGENTS.md` with
app-specific rules. The closest one to the file you're editing wins.

## Commands

Run everything from the repo root.

```bash
python3 -m pip install -r requirements.txt   # once: Pillow (pinned, for reproducible renders)
tools/check.sh                               # build + typecheck + test EVERY app. Must pass before any PR
tools/check.sh <app>                         # just one app, e.g. wizard-thanksgiving
tools/check.sh --no-prebuild <app>           # build from committed assets only (what releases ship)
tools/deploy.sh <app>                        # install + launch on a real bar (needs .env); only when asked
python3 tools/screens.py --count 8 --every 2 # capture the bar's screen to screens/strip.png
tools/new-app.sh <folder> --id <id> --name "<Name>" --description "<one line>"   # scaffold a new app
```

- **Node:** the BUSY CLI needs **Node 24**. The tools use local `node` if it's v24, otherwise
  `npx -y -p node@24`. Don't change engines or try to make Node 26 work.
- **No device?** `tools/check.sh` needs none. Never guess a device address. The bar's address comes only from the
  git-ignored `.env` (`BUSYBAR_ADDR`, plus `BUSYBAR_TOKEN` if a password is set). Without `.env`, the tools default to
  USB `10.0.4.20`.

## Repository map

```
apps/<folder>/            one self-contained app (see "App convention")
lib/python/busybar/       shared render kit (Python): canvas, fx, party, font, sprite, showbuild, anim, preview
lib/ts/busybar/           shared TypeScript: xpmtext, walltime, drawqueue, holidays (date rules), showrunner (playback)
lib/tests/                kit tests; tools/check.sh runs them first
tools/                    shared scripts: check, deploy, release, new-app, screens, lib.sh
docs/                     INSTALLING.md (users), DEVELOPMENT.md (devs), DECISIONS.md (repo-level R1…)
.github/workflows/        ci.yml (PR checks, job "check"), release.yml (tag -> GitHub Release)
```

### App convention (the tools depend on it)

```
apps/<folder>/
  app/                    REQUIRED  BUSY JS app (TypeScript). src/main.ts entry; src/appmeta/manifest.json
  app/shared/             modules + generated data, imported as @shared/*  (NOT in app/src/; see below)
  app/src/animations/     .anim files packaged with the app
  prebuild.sh             optional  generates assets before the JS build
  tests/check.sh          optional  app tests, run by tools/check.sh
  README.md               REQUIRED  what it does, controls, how to change it
  docs/DECISIONS.md       REQUIRED  decision log (D1, D2, …): what was decided, why, alternatives
  AGENTS.md               optional  app-specific agent notes
```

## Workflow rules

1. **Never commit to `main` or `dev` directly.** Both are protected. Branch from `dev` as
   `<github-username>/<topic>`, with a topic prefix: `feat-`, `fix-`, `new-app-`, `tool-`, `docs-` or `hotfix-`.
   Open a PR into `dev`. Only maintainers promote `dev` → `main` and cut releases.
2. **One topic per PR.** Don't mix a new app with unrelated refactors.
3. **Never** force-push shared branches, rewrite published history, move or delete tags, or create releases unless a
   maintainer explicitly asks.
4. **Releases** come from version tags (`<app-folder>-v<version>`) pushed by `tools/release.sh` on `main`. CI
   publishes them. To release an app, bump `"version"` (semver) in its manifest **in a PR**. Never commit `.tgz`
   packages.
5. **Don't touch the device unless asked.** `tools/deploy.sh`, `curl` POSTs to the bar and `/api/input` change what
   a real person's display shows.

## Definition of done

- [ ] `tools/check.sh` passes (this is exactly what CI's required `check` job runs).
- [ ] Generated assets are regenerated and **committed** (`.anim` files, `app/shared/generated/*`, mockups).
      Releases build from committed files.
- [ ] Visual changes are reviewed as LED-style renders (`busybar.preview.led`, or the app's review tool) and, when a
      device is available and the user asked, on the bar with `tools/screens.py`.
- [ ] The app's `README.md` reflects the change, and its `docs/DECISIONS.md` has a new entry for any meaningful
      choice. Repo-wide choices go in `docs/DECISIONS.md` (R-numbers).
- [ ] No personal or network details anywhere (see Privacy).
- [ ] The commit summary is imperative and 72 characters or fewer.

## Privacy (this repo is public)

Never write any of these into files, docs, test fixtures, commit messages or PR text:
- real IP addresses or subnets (use `<bar-ip>`; `10.0.4.20` is the bar's public USB default, and `192.168.1.50` is
  the documented example);
- time-zone offsets or locations;
- local paths like `/Users/...` or home directories;
- people's names, beyond a contributor's own GitHub identity;
- photos of homes;
- passwords or tokens.

`.env` is git-ignored. Keep it that way, and never print its contents into the repo.

## BUSY Bar platform: what agents get wrong

**The runtime is JerryScript, not Node or a browser.**
- There's no `fs`, `process`, `window` or `document`, and no Node built-ins.
- Available: `fetch`, `setTimeout`/`setInterval`, `console`, `Date`, `JSON`, `localStorage`.
- `main()` runs **once**. The app stays alive only while a `listen("input", …)` handler, a timer or a pending
  `fetch` exists. Quit by clearing every timer and unbinding. Call `setTimeout(unbind, 0)`, never `unbind()` inside
  its own handler.
- Use `short` for button taps, not `press`. The encoder sends `delta` ±1.

**Every `.ts` file under `app/src/` becomes its own script entry.** `main.js` then begins with an ES `import` and the
firmware can't run it. Put helpers and generated data in `app/shared/` and import them as `@shared/...`. After
`npm run build`, the build output must show `scripts: main.js` only.

**Smooth motion means `.anim` files.**
- Timer-driven redraws manage about 3 fps. The firmware plays `.anim` at the file's fps with no requests.
- Write them with `lib/python/busybar/anim.py` (`write_anim`, then verify with `read_anim`).
- Width and height are at most 255. Use one section per file, and bake colors in.

**Draw API.**
- `device.DisplayDraw({ application_name: manifest.id, priority: 50, elements })`. Elements are keyed by `id`;
  re-sending an id replaces it.
- Colors are `#RRGGBBAA`.
- Built-in fonts are ASCII-only (`tiny`, `small`, `normal`, `bold`, `large`, `extra_large`). For styled or custom
  text, render an `xpmbitmap` (at most 32 colors, within 72×16).

**Black is an unlit LED.** Near-black details (eyes, outlines) render as holes. A row of dark pixels once read as
"three eyes". Use lit colors for small features.

**Conserve the device.** The app shares CPU and RAM with the bar's web server.
- Keep one draw request in flight, send only changed elements, and use human-scale timers.
- Keep the default 128 KiB heap unless measured otherwise.
- Don't log in tight loops.

**Time.**
- `device.TimeGet()` returns the bar's local ISO timestamp with offset. Read the wall-clock fields directly; don't
  use JS `Date` local-time methods.
- In Python, round halves up (`floor(v + 0.5)`) in anything compared with JS `Math.round`.

**Installing over a running app fails (HTTP 400) and uninstalls it.** Quit first. `tools/deploy.sh` does this.

**npm.**
- Use `npx -p @busy-app/cli busy-cli …` or the project's `node_modules/.bin/busy-cli`. **Never** run
  `npx busy-cli`: that's an unrelated package.
- A nested `npx` inside `npx -c` fails, so pass every package with `-p`.

**Shell.**
- Scripts must run on macOS's bash 3.2. With `set -u`, expand possibly-empty arrays as `${arr[@]+"${arr[@]}"}`.
- When generating files from the shell, never nest heredocs that share a delimiter (`<<EOF` inside `<<EOF`). The
  inner terminator ends the outer heredoc, and the shell then runs the rest as commands. Backticks in prose become
  command substitutions. Use unique delimiters (`<<AGENTS_EOF`), or write files with an editor or file tool.

## Code style

- **Python:** 3.10+, standard library plus Pillow only. Type hints where helpful. Output must be deterministic
  (seeded RNG), so CI's re-render matches the commit byte-for-byte.
- **TypeScript:** strict (the scaffold's `tsconfig`). Handle every promise (`void p.catch(report)`), and keep one
  failed request from stopping timers.
- **Art:** original only. No copyrighted characters, logos or fonts (see `NOTICE.md`).
- **Edits:** keep them minimal and focused. Match surrounding style. Don't reformat unrelated code.
- **Generated files:** don't hand-edit them (`app/shared/generated/*`, `mockup/index.html`, `.anim`). Change the
  generator and rebuild.
