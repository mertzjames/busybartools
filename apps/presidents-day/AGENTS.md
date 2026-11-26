# AGENTS.md — Presidents' Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/presidents.ts           card texts and the playlist: pure functions of the bar's time
app/src/main.ts (TS)               configuration for the kit's show runner (lib/ts/busybar/showrunner.ts)
```

Commands, run from this folder (the repo-level `tools/check.sh presidents-day` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene flag previews/ 0.2 0 5     # every 0.2 s between 0 s and 5 s
bash tests/check.sh                                         # date logic (node --test) + live-text parity
```

## Invariants: don't break these

- **Tone (D2):** light, warm and non-partisan. No faces or likenesses of any president or real person, no official
  seals or logos, no president named. Symbols, objects and places only.
- **The flag (D4):** 13 one-row stripes, red at the top and bottom; the canton covers the top 7. Whole-row wave steps.
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA frames of 72×16. Seed
  every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`,
  registered in `PLAYLIST` (`renderer/scenes/__init__.py`).
- **Dates come from the kit** (`HOLIDAYS.presidentsDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from `LAYOUT` in `renderer/scenes/text.py` (Python), the kit's
  `xpmtext.ts` (the app) and the mockup, which all draw the same. `tests/text_parity.py` checks them and that
  `DAY_CARDS` (`app/shared/presidents.ts`) matches `DAY_TEXT` (`renderer/scenes/text.py`).
- **Every text fits.** `TO PRESIDENTS' DAY` in `tiny` is 67 px plus the shadow; `tests/logic.test.mts` asserts every
  card text fits in 72 px and uses glyphs the fonts have.
- **Steady glows (D6).** Flicker only a few core pixels; large per-frame changes bloat the `.anim` files. About 0.9 MB now.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Black is an unlit LED.** The stovepipe hat is a lit charcoal with a sheen, the eagle's wings are a lit brown, the
  night skylines are a lit navy-grey.
- **Check contrast against the background (D4, D5).** The navy canton vanished in a deep-blue sky, a grey hatchet in
  a pale sky, and a charcoal hat against brown logs. Change the background behind the detail.
- **Rotating pixel art mangles it.** The eagle banks with a per-column shear (`banked()` in `scenes/eagle.py`).
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters), `tiny` 3×5 (no comma, about 18 characters),
  `clock` 7×12. Missing characters are skipped silently.
