# Development guide

How this repo is put together, how to build and test apps, and what we've learned about the BUSY Bar platform.
For the branch model, pull requests and releases, see [CONTRIBUTING.md](../CONTRIBUTING.md). If you work with an
AI coding agent, point it at [AGENTS.md](../AGENTS.md). Claude Code loads it automatically through
[CLAUDE.md](../CLAUDE.md).

- [Setup](#setup)
- [Repository layout](#repository-layout)
- [Everyday workflow](#everyday-workflow)
- [Anatomy of an app](#anatomy-of-an-app)
- [Adding a new app](#adding-a-new-app)
- [Making animations (`.anim`)](#making-animations-anim)
- [BUSY Bar platform notes](#busy-bar-platform-notes)
- [Testing on the device](#testing-on-the-device)
- [HTTP API cheat sheet](#http-api-cheat-sheet)
- [Gotchas we hit](#gotchas-we-hit)

## Setup

| Need | Why | Notes |
|---|---|---|
| Python 3.10+ | Asset generators, shared `busybar` library, tests | `python3 -m pip install -r requirements.txt` (Pillow is pinned for reproducible renders) |
| npm | BUSY JS app toolchain | The BUSY CLI requires **Node 24**. `tools/` uses your `node` if it's v24, otherwise runs Node 24 through `npx -p node@24`. |
| A BUSY Bar | Deploying and testing | USB (`10.0.4.20`, no password) or Wi-Fi with the HTTP API enabled ([guide](INSTALLING.md#enable-the-http-api-over-wi-fi)) |
| `gh` (optional) | Opening PRs, watching CI and releases | |

Copy `.env.example` to `.env` (git-ignored) and set `BUSYBAR_ADDR` (and `BUSYBAR_TOKEN` if you use a password).
Every tool reads it.

## Repository layout

```
apps/
  wizard-thanksgiving/      an app (see "Anatomy of an app")
lib/python/busybar/
  anim.py                   .anim writer + reader (round-trip verification)
  preview.py                LED-style renders of frames: led(), strip()
tools/
  check.sh                  build + typecheck + test apps; CI runs this
  deploy.sh                 build one app and install/launch it on the bar from .env
  release.sh                tag a release of one app from main (CI publishes it)
  new-app.sh                scaffold a new app in this layout
  screens.py                capture what the bar is showing, as LED-style PNGs
  lib.sh                    shared shell helpers (app resolution, Node 24, API auth)
docs/
  INSTALLING.md             end-user install guide
  DEVELOPMENT.md            this file
  DECISIONS.md              repo-level decisions (apps keep their own logs)
.github/workflows/          ci.yml (PR checks), release.yml (tag → GitHub Release)
```

## Everyday workflow

```bash
git switch dev && git pull
git switch -c <your-github-username>/<topic>     # e.g. alice/snow-scene (see CONTRIBUTING.md)

# edit...
tools/check.sh <app>                  # regenerate assets, typecheck, build, run the app's tests
tools/deploy.sh <app>                 # install and launch on your bar
python3 tools/screens.py --count 8 --every 2  # grab what the bar shows -> screens/strip.png

git commit -am "Describe the change"   # commit regenerated assets too (see below)
git push -u origin HEAD && gh pr create --base dev
```

**Commit generated assets.** Apps commit what their generators produce (for example `.anim` files and generated
TypeScript), so anyone can build and release from a clean clone. Releases are built from these committed,
device-tested files (`tools/check.sh --no-prebuild`). CI regenerates them too, and reports any difference without
failing the build, because renders can differ by a pixel between platforms.

## Anatomy of an app

Every app lives in `apps/<folder>/` (lowercase, dashes) and follows this convention, which the `tools/` scripts rely
on:

```
apps/<folder>/
  app/                     REQUIRED. A BUSY JS app project (scaffolded by @busy-app/create-app)
    package.json             scripts: typecheck, build (busy-cli build)
    src/main.ts              entry point (becomes scripts/main.js)
    src/appmeta/manifest.json  id, name, version (semver), api_version, description, author
    src/appmeta/icon_front_8x8.png, icon_back_11x11.png   optional menu icons
    src/animations/*.anim    animations packaged with the app
    shared/                  helpers + generated data imported as @shared/* (bundled into main.js)
  prebuild.sh              OPTIONAL. Generates assets before the JS build (run by check/deploy/release)
  tests/check.sh           OPTIONAL. App tests, run by tools/check.sh after the build
  README.md                REQUIRED. What it does, controls, how to change it
  docs/DECISIONS.md        REQUIRED. Decision log: what was decided, why, what else was considered
  AGENTS.md, CLAUDE.md     OPTIONAL. App-specific notes for AI coding agents (CLAUDE.md imports AGENTS.md)
```

The package for upload is `app/dist/<app-id>.tgz`. A release names it `<app-id>-<version>.tgz`.

Wizarding Thanksgiving is the reference example. It has a Python renderer (`renderer/`) that draws the pixel art,
writes the `.anim` files, generates `app/shared/generated/show.ts`, and builds a browser mockup (`mockup/`). Its
`tests/clock_parity.py` runs the app's real TypeScript under Node and compares it pixel-for-pixel with the renderer.

## Adding a new app

```bash
tools/new-app.sh fireplace --id busybartools.fireplace --name "Fireplace" --description "A crackling fire loop"
```

This runs the official scaffolder into `apps/fireplace/app` with no prompts and installs dependencies. It also
creates `README.md`, `docs/DECISIONS.md`, `AGENTS.md` and `CLAUDE.md` stubs. The author defaults to "busybartools contributors"; pass
`--author` to change it. Then:

1. Write `app/src/main.ts`. The scaffold draws "Hello" every second. The smallest useful app draws one element:
   ```ts
   import { device } from "@shared/device";
   import manifest from "./appmeta/manifest.json";
   const APP = manifest.id;

   function main(): void {
     void device.DisplayDraw({
       application_name: APP, priority: 50,
       elements: [{ id: "fire", type: "animation", path: "animations/fire.anim", x: 0, y: 0, loop: true }],
     }).catch((e) => console.error(`${APP}: ${e}`));
     const unbind = listen("input", (ev) => {          // keeps the app alive; Back quits
       if (ev.key === "back" && ev.action === "short") setTimeout(unbind, 0);
     });
   }
   main();
   ```
2. Add assets under `app/src/animations` or `app/src/images`. If you generate them, add a `prebuild.sh`.
3. Keep extra TypeScript modules and generated data in `app/shared/`, **not** `app/src/` (see
   [Gotchas](#gotchas-we-hit)).
4. `tools/check.sh fireplace`, then `tools/deploy.sh fireplace`.
5. Add a row to the **Apps** table in the root `README.md`, and open a PR into `dev`.

## Making animations (`.anim`)

Smooth motion on the bar comes from `.anim` files that the firmware plays by itself at the file's fps, with zero
HTTP requests. Timer-driven redraws from an app top out around 3 visible frames per second.

`lib/python/busybar/anim.py` writes them (BGRA8888, the first frame whole, later frames as changed pixels only) and
reads them back for verification:

```python
import sys; sys.path.insert(0, "lib/python")
from PIL import Image
from busybar.anim import image_to_bgra, write_anim, read_anim
from busybar.preview import led

frames = []
for i in range(30):                                   # 2 s at 15 fps
    img = Image.new("RGB", (72, 16), (0, 0, 0))       # draw your frame here
    img.putpixel((i * 2 % 72, 8), (255, 160, 40))
    frames.append(img)

size = write_anim("app/src/animations/demo.anim", [image_to_bgra(f) for f in frames], 72, 16, fps=15)
back = read_anim("app/src/animations/demo.anim")      # assert it round-trips
assert back["frames"] == [image_to_bgra(f) for f in frames]
led(frames[10], cell=10).save("preview.png")         # LED-style preview for review
```

Guidelines from building the first app:
- **Width and height are at most 255**, and an animation should be no bigger than the display it targets
  (72×16 front).
- **Use one section per file.** Single-section output matches a production generator. Multi-section output hasn't been
  verified on a device.
- **Colors are baked in.** Make one file per color variant.
- **Small changes compress well.** Unchanged pixels between frames cost almost nothing, so static backgrounds are
  cheap. Eight 15 to 18 s full-screen scenes came to about 1.1 MB.
- **Draw from an element:** `{"type":"animation","path":"animations/x.anim","loop":true}`. The path is relative
  to the app package.
- **With `loop:false`, schedule what comes next with a timer** of the animation's length.

## BUSY Bar platform notes

**Display and drawing.**
- The front panel is 72×16 RGB and the back is 160×80 greyscale. Colors are `#RRGGBBAA`.
- **Black is an unlit LED,** so near-black details read as holes. Use lit colors for eyes and outlines.
- Apps draw with `device.DisplayDraw({ application_name, priority, elements })`.
- Elements are keyed by `id`: re-sending an id replaces it, and `DisplayClear` removes ids.
- Element types: `text`, `image`, `animation`, `countdown`, `rectangle` and `xpmbitmap`.
- `z_index` orders layers, and `timeout` or `display_until` auto-expire elements.
- `priority` runs 1–100. Use 50. Built-in apps use about 10, and an active BUSY session uses 90.

**Text.**
- Built-in fonts are ASCII-only bitmaps: `tiny` (6 px line), `small` (9), `normal` / `bold` / `condensed` (11),
  `large` (13), `extra_large` (14).
- For styled text (gradients, shadows, custom glyphs), render it as an `xpmbitmap`: XPM2 text, at most 32 colors,
  no larger than the display. See `apps/wizard-thanksgiving/app/shared/clocktext.ts`.

**JS runtime.**
- Apps run on JerryScript (roughly ES2020): not Node, not a browser.
- Available: `fetch`, timers, `console`, `Date`, `JSON`, `localStorage`.
- `main()` runs once. The app stays alive only while a `listen("input", …)` handler, a timer or a pending `fetch`
  exists.
- To quit, clear timers and unbind the listener. Call `setTimeout(unbind, 0)`, not `unbind()` inside the handler.
- Input: `ok`, `start` and `back` with `short`, `long`, `press`, `release` or `repeat` (use `short` for taps), plus
  `encoder` with `delta` ±1.
- The heap defaults to 128 KiB (`heap_size_kib` in the manifest, max 512).

**Time.**
- `device.TimeGet()` returns the bar's local time as ISO 8601 with its offset, e.g. `2026-11-26T18:05:42-05:00`.
- Read the wall-clock fields directly. Don't use JS `Date` local-time methods, which don't know the bar's time zone.

**Requests.**
- Every draw is an HTTP request to the bar's own web server, handled one at a time.
- Keep one request in flight, send only what changed, and work on human time scales.

## Testing on the device

| Tool | Use |
|---|---|
| `tools/deploy.sh <app>` | Build, quit the running app, install, launch |
| `python3 tools/screens.py --count N --every S` | Capture the front display from `GET /api/screen` into `screens/`. This is the framebuffer, not how the LEDs look in a room |
| `curl -X POST "http://<bar>/api/input?key=ok"` | Press a button remotely (`ok`, `back`, `start`). Handy to skip to a scene before capturing it |
| `http://<bar>/docs` | The bar's own API reference for its exact firmware |

Colors and brightness still need a human looking at the real panel. LEDs are brighter and more saturated than a
monitor.

## HTTP API cheat sheet

Base: `http://<bar>/api`. Over Wi-Fi with a password, add the header `X-API-Token: <password>`.

| Method | Path | Notes |
|---|---|---|
| GET | `/version` | `{"api_semver":"27.16.0"}`. Answers even when Wi-Fi access is off |
| GET | `/time` | Local ISO timestamp |
| POST | `/display/draw` | `{application_name, priority, elements[]}` |
| DELETE | `/display/draw` | Clear: `?application_name=` or body `{application_name, element_ids}` |
| GET | `/screen?display=0` | Front framebuffer, base64 of BGR bytes (72×16×3) |
| GET/POST | `/display/brightness` | `{"value":"auto"}`. Set with a query parameter `?value=0..100\|auto` |
| POST | `/input?key=ok` | Simulate a button |
| GET | `/apps/list` | Installed apps |
| POST | `/apps/stage` | Body: the `.tgz`. Returns `install_key` |
| POST | `/apps/install?install_key=` | `400` if the app is running (and it ends up uninstalled) |
| POST | `/apps/launch?app_id=` | `404` if not installed |
| POST | `/apps/quit` | `409` if nothing is running |
| DELETE | `/apps?app_id=` | Uninstall |

## Gotchas we hit

- **Every `.ts` file under `app/src/` becomes its own script.** `busy-cli build` makes each one an entry point, and
  `main.js` then starts with an ES `import`, which the firmware's script runner won't load. Put modules and generated
  data in `app/shared/`. Check `scripts:` in the build output: it should list only `main.js`.
- **Installing over a running app fails with 400 and uninstalls it.** Always quit first. `tools/deploy.sh` does.
- **Use `npx -p @busy-app/cli busy-cli …`, never `npx busy-cli`.** The unscoped name is a different npm package.
- **Nested `npx` inside `npx -c` fails with `EUSAGE`.** Pass every package with `-p` in a single `npx` call.
- **macOS ships bash 3.2:** `"${arr[@]}"` on an empty array is an error under `set -u`. Use `${arr[@]+"${arr[@]}"}`.
- **Python and JS round halves differently** (banker's rounding vs half-up). Shared color math must use
  `floor(v + 0.5)` in Python to match `Math.round`.
- **`.gif`, `.jpg`, `.wav` and `.mp3` in an app aren't playable.** The bar reads `.png`, `.anim` and `.snd`.
