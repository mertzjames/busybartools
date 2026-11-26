# AGENTS.md — Father's Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
renderer/ffx.py                    palette, skies, glows, dim_rect, and figure(): the procedural people
app/shared/fathers.ts              card texts and the playlist: pure functions of the bar's time
app/src/main.ts (TS)               configuration for the kit's show runner (lib/ts/busybar/showrunner.ts)
```

Commands, run from this folder (the repo-level `tools/check.sh fathers-day` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py grid fishing previews/ 0.2 5 7   # a labeled grid every 0.2 s between 5 s and 7 s
python3 renderer/review_zoom.py hammock previews/z.png 14 50 1,8.8   # zoomed columns 14-50 at 1 s and 8.8 s
bash tests/check.sh                                         # date logic (node --test) + live-text parity
```

## Invariants: don't break these

- **Tone (D2):** warm, lighthearted and inclusive. A range of skin tones and father figures; gentle humor about the
  day, never at anyone's expense. No brands, no copyrighted characters.
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA frames of 72×16. Seed
  every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`,
  registered in `PLAYLIST` (`renderer/scenes/__init__.py`).
- **Dates come from the kit** (`HOLIDAYS.fathersDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from `LAYOUT` in `renderer/scenes/text.py` (Python), the kit's
  `xpmtext.ts` (the app) and the mockup, which all draw the same. `tests/text_parity.py` checks them, that every text
  fits in 72 px with its shadow, and that `DAY_CARDS` (`app/shared/fathers.ts`) matches `DAY_TEXT`.
- **The mockup runs the app's logic.** `tests/logic.test.mts` evaluates the mockup's inlined copy of
  `fathers.ts` and compares it with the app's for every day of 2026–2029. Rebuild after changing `fathers.ts`.
- **The `#` glyph (D5)** is registered app-locally in `renderer/scenes/text.py`. Never add glyphs to `lib/`.
- **Steady glows (D6).** Flicker only a few core pixels; large per-frame changes bloat the `.anim` files. About 0.44 MB.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Black is an unlit LED.** Hair, tires, the saddle and the night treeline are lit dark tones, never near-black.
- **Check contrast against the background (D4).** Heads vanished in a violet dawn, a white ball in a pale sky,
  burgers on a brown fence, a napper in a bright sunset. Change the background behind the detail: a darker sky, a
  hedge, far hills.
- **Same-hue traps:** an orange leaf on an orange shirt, tan skin on a tan fence. Pick a contrasting hue.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?` plus the app's `#`, about 12 characters), `tiny` 3×5 (no comma, about
  18 characters), `clock` 7×12. Missing characters are skipped silently.
