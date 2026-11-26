# AGENTS.md — Advent Calendar

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md) (D1–D12): read the relevant entries before changing
something deliberate.

- **What it does:** A unique animation for every day of Advent, with a countdown to Christmas.
- **Entry point:** `app/src/main.ts`. Put helpers and generated data in `app/shared/`, never in `app/src/`.
- **Build and test:** `tools/check.sh advent-calendar` from the repo root.

## How this app is built

```
renderer/ (Python) ──build.py──►  app/src/animations/*.anim     day01..day25, door, winter, card_bg
                                   app/shared/generated/show.ts  days, durations, text styles, fonts
                                   app/src/appmeta/icon_*.png    menu icons
                                   mockup/index.html             simulator (from mockup/template.html)
app/shared/advent.ts   pure logic: season, card text, show sequence, browsing (tested)
app/src/main.ts        plays door -> vignette -> card from the bar's /api/time
```

## Invariants: don't break these

- **25 days, in order.** `DAY_MODULES` in `renderer/scenes/__init__.py` lists `day01`…`day25`; `SHOW.days[i]` is
  December `i + 1`, and day 25 is the finale. The tests check there are exactly 25.
- **15 fps, full screen, deterministic.** Each scene's `render()` returns `SECONDS * FPS` RGBA 72×16 frames. Seed
  every RNG (`random.Random(n)`, `Particles(seed=…)`, `Snow(seed=…)`). Two builds must be byte-identical.
- **Scene module contract:** `NAME` (file-safe; becomes `<NAME>.anim`), `TITLE`, `SECONDS`,
  `KEYFRAMES = [(seconds, caption), …]` and `render()`. Vignettes run 7–10 s (a test enforces it).
- **Tone curve.** `GAMMA = 0.8` in `build.py` applies to frames and live-text colors. Scenes draw in linear colors.
- **Live-text parity.** Text styles live in `renderer/scenes/text.py`. Three implementations must agree pixel for
  pixel: `busybar.font.draw_text`, the kit's `xpmtext.ts` (via `app/shared/kit.ts`), and the mockup's `<logic>`
  block. `tests/text_parity.py` and `tests/advent.test.mts` check this.
- **Logic mirror.** `mockup/template.html`'s `<logic>` block mirrors `app/shared/advent.ts`. Change both together;
  `tests/advent.test.mts` compares them on every day of three years.
- **Live text must use real glyphs and fit.** `big` has A–Z 0–9 and `!',-.:?`; `tiny` has no comma. A test renders
  every card text the logic can produce and checks the glyphs exist and the bitmap fits 72×16.
- **Size budget:** keep total `.anim` data under about 4 MB (currently 1.6 MB; `build.py` prints the total).
- **Generated files are outputs.** Never hand-edit `.anim`, `app/shared/generated/show.ts` or `mockup/index.html`.
- **Bar time only.** Use `parseLocal(device.TimeGet().timestamp)`, never JS `Date` local methods.

## Pixel-art rules learned here

- **No light dot pairs on dark or red shapes** unless they are meant to be eyes: they read as faces (D10).
- **Dark sprites need a light background** (the penguin), and **near-black details vanish** (use lit slate).
- **Blend nothing small into a busy color:** draw bulbs and sparkles at full opacity and dim them by scaling their
  own color.
- **Captions over a busy scene:** dim the frame first, then draw the text (see `day25_finale.py`).
- **Look at it.** `python3 renderer/review.py scene dayNN` writes an LED-style strip to `previews/`. View it before
  committing. `review.py cards` shows the door and every countdown card with live text.

## Changing the show

| Change | Where | Then |
|---|---|---|
| Replace a day's vignette | `renderer/scenes/dayNN_*.py` (keep `NAME = "dayNN"`) | `build.py`, review the strip, update the README table |
| Card wording or rules | `app/shared/advent.ts` **and** the mockup `<logic>` block | update `tests/advent.test.mts`, `tools/check.sh advent-calendar` |
| Text colors or rows | `renderer/scenes/text.py` | `build.py`, `tests/text_parity.py` |
| Step timing | scene `SECONDS`, `door.TEXT_MS`, `text.CARD_MS` | `build.py` (flows into show.ts and the mockup) |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers run `tools/release.sh advent-calendar` |
