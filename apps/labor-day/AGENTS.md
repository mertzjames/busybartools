# AGENTS.md — Labor Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/laborday.ts             card texts and the playlist: pure functions of the bar's time
app/src/main.ts (TS)               configuration for the kit's show runner (lib/ts/busybar/showrunner.ts)
```

Commands, run from this folder (the repo-level `tools/check.sh labor-day` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene steel previews/ 0.2 8 10   # every 0.2 s between 8 s and 10 s
bash tests/check.sh                                         # date logic (node --test) + live-text parity
```

## Invariants: don't break these

- **Tone (D2):** a warm tribute to working people, then the day off. Generic workers with plain faces and a range of
  skin tones; no real people, no union or company logos, no brand trade dress, nothing partisan. No red cross on the
  nurse (a protected emblem).
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA frames of 72×16. Seed
  every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`,
  registered in `PLAYLIST` (`renderer/scenes/__init__.py`). Six scenes give three count slots, one per day card.
- **Dates come from the kit** (`HOLIDAYS.laborDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from `LAYOUT` in `renderer/scenes/text.py` (Python), the kit's
  `xpmtext.ts` (the app) and the mockup, which all draw the same. `tests/text_parity.py` checks them and that
  `DAY_CARDS` (`app/shared/laborday.ts`) matches `DAY_TEXT` (`renderer/scenes/text.py`).
- **Every text fits (D7).** Two big lines at y 0 and y 8; `TO LABOR DAY` is 67 px plus the shadow.
  `tests/logic.test.mts` asserts every card text fits and uses glyphs the fonts have.
- **The mockup runs the app's logic (D11).** A test checks the inlined block against the app for 2026–2029.
- **Steady glows, quantized light (D9).** Flicker only a few pixels; quantize slow light changes. About 0.9 MB now.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Black is an unlit LED.** Tires are a lit charcoal, the night skyline a lit navy-grey, the crane silhouette on
  the clock card a dark gold.
- **Check contrast against the background (D4, D10).** Rust steel vanished in the sunrise, gold bales in a gold
  field, a white fence in a peach sky, a sandcastle in the sand. Change the background behind the detail.
- **People:** heads against the sky, bodies against a mid-tone; faces are plain skin (a 3x3 head has no room for
  lit eyes). Use silver hair or a hat on dark skin. Seen from behind, they need no face at all (`lfx.back_view`).
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters), `tiny` 3×5 (no comma, about 18 characters),
  `clock` 7×12. Missing characters are skipped silently.
