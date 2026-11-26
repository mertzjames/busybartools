# AGENTS.md — Mother's Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/mothersday.ts           card texts and the playlist: pure functions of the bar's time
app/src/main.ts (TS)               configuration for the kit's show runner (lib/ts/busybar/showrunner.ts)
```

Commands, run from this folder (the repo-level `tools/check.sh mothers-day` runs all of it):

```bash
python3 renderer/build.py                                     # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                      # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene card previews/ 0.2 3 5       # every 0.2 s between 3 s and 5 s
python3 renderer/review_zoom.py hug previews/zoom.png 10 50 6,8.5   # zoom into columns 10-49
bash tests/check.sh                                           # date logic (node --test) + live-text parity
```

## Invariants: don't break these

- **Tone (D2):** warm, sweet and inclusive. Generic figures with plain faces (no eyes), a range of skin tones and hair;
  moms, grandmothers and parents. No gendered stereotypes beyond the warmth of the day, no real people, no logos.
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA frames of 72×16. Seed
  every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`,
  registered in `PLAYLIST` (`renderer/scenes/__init__.py`).
- **Dates come from the kit** (`HOLIDAYS.mothersDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from `LAYOUT` in `renderer/scenes/text.py` (Python), the kit's
  `xpmtext.ts` (the app) and the mockup, which all draw the same. `tests/text_parity.py` checks them and that
  `DAY_CARDS` (`app/shared/mothersday.ts`) matches `DAY_TEXT` (`renderer/scenes/text.py`).
- **Every text fits.** `LOVE YOU MOM` in `big` is 71 px plus the shadow, edge to edge, so `count_bg` keeps bright art
  out of its edges; `tests/logic.test.mts` asserts every card text fits in 72 px and uses glyphs the fonts have.
- **Steady glows (D5).** Flicker only a few pixels; large per-frame changes bloat the `.anim` files. About 0.5 MB now.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Black is an unlit LED.** Hair is a lit brown or silver, never near-black; faces are plain skin.
- **Lit backdrops behind people (D4).** A pillow behind Mom, a mid-blue sky in the garden, a sunset glow behind the hug.
  Medium and dark skin vanished against a mauve wall and a purple sky until the backgrounds changed.
- **Small objects need contrast (D6).** The white cup sits against the dark wall, not the bright window; the ribbon is
  red on cream.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters), `tiny` 3×5 (no comma, about 18 characters),
  `clock` 7×12. Missing characters are skipped silently.
