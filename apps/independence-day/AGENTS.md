# AGENTS.md — Independence Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/july4.ts                card texts, the dusk countdown, the playlist, the demo shift: pure functions of time
app/src/main.ts (TS)               configuration for the kit's show runner (lib/ts/busybar/showrunner.ts) + START modes
```

Commands, run from this folder (the repo-level `tools/check.sh independence-day` runs all of it):

```bash
python3 renderer/build.py                                       # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                        # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene parade previews/ 0.2 4 6       # every 0.2 s between 4 s and 6 s
python3 renderer/review_zoom.py cookout previews/z.png 4 40 3.6 # zoomed crop, for small sprites
bash tests/check.sh                                             # date logic (node --test) + live-text parity
```

## Invariants: don't break these

- **Tone (D2):** festive, family-friendly, non-partisan. No likenesses of real people, no official seals or logos.
  Generic figures have plain faces (no eyes) or are seen from behind.
- **The flag (D5):** 13 one-row stripes, red at the top and bottom; the canton covers the top 7, a dense checker of
  dots. Whole-row wave steps.
- **The fireworks countdown (D7):** on July 4, `FIREWORKS IN` / `HH:MM` to 21:00, rounded up; `ENJOY THE` /
  `FIREWORKS!` from 21:00. The day card always has two pages of two lines, so the runner's minute-rollover redraw
  (by page and line index) stays valid across 21:00.
- **Demo mode (D9):** the shift is a whole number of minutes, so the shifted clock rolls over with the bar's.
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA frames of 72×16. Seed
  every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`,
  registered in `PLAYLIST` (`renderer/scenes/__init__.py`). Seven scenes give three count slots.
- **Dates come from the kit** (`HOLIDAYS.independenceDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from `LAYOUT` in `renderer/scenes/text.py` (Python), the kit's
  `xpmtext.ts` (the app) and the mockup, which all draw the same. `tests/text_parity.py` checks them; the mockup
  inlines `july4.ts` (type-stripped) and `tests/logic.test.mts` checks it matches the app over four years.
- **Every text fits.** The widest line is `FIREWORKS IN` (65 px + shadow); the test walks every minute of July 4 and
  every day of two years.
- **Small files (D4).** About 0.9 MB of `.anim` now. Keep big soft areas still; quantize slow fades.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Black is an unlit LED.** Skylines are a lit navy, the eagle's wings a lit brown, watermelon seeds a lit brown,
  the bell's crack a darker but lit brown.
- **Contrast (D10, D11).** A white picket fence drowned out the cookout; brick and striped awnings swallowed the red
  band jackets; a dark skyline vanished on a dark sky until a glow went behind it.
- **Shapes:** rotate nothing. The bell swings by row shifts, the eagle banks by column shifts.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters), `tiny` 3×5, `clock` 7×12. Missing characters are
  skipped silently.
