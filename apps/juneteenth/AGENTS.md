# AGENTS.md — Juneteenth

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     7 full-screen 72×16 scenes + clock_bg, count_bg, day_bg
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text layout, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator + storyboards (inlines app/shared/juneteenth.ts)
app/src/main.ts      configures the kit's show runner; card text and the playlist come from app/shared/juneteenth.ts
```

Commands, run from this folder (the repo-level `tools/check.sh juneteenth` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene <scene> previews/ 0.2 6 8  # every 0.2 s between 6 s and 8 s
python3 renderer/review.py zoom <scene> previews/ 3,6 0 40  # cell-18 close-ups of columns 0-40
bash tests/check.sh                                         # logic tests + live-text parity
```

## Invariants: don't break these

- **Tone and respect (D3, D4).** The show opens solemn (dawn, the news) and becomes joyful. No chains, violence or
  suffering imagery, no likenesses of real people, no long quotations. Keep the first two scenes calm: no confetti
  or party effects.
- **The flag is the official design (D5):** a white five-point star inside a white outlined nova, centered, on a
  field split by an arc, blue above and red below. Waving shifts columns by whole rows and moves the emblem as one
  piece.
- **People are faceless (D6):** lit skin tones, no dark pixels for features, light or saturated clothes. Check
  contrast against the background (horses on streets, shirts on walls, hats on trim).
- **15 fps, full screen, deterministic.** Seed every RNG; CI re-renders and expects identical files.
- **One source for words (D11).** Card text in `app/shared/juneteenth.ts`; styles, `DAY_TEXT` and the baked scene
  words in `renderer/scenes/text.py`. The parity test checks they agree, fit and clear each backdrop's `TEXT_GAP`.
- **No top-level name in `juneteenth.ts` may repeat one in `walltime.ts` or `holidays.ts`:** the mockup inlines all
  three into one scope.
- **Dates come from the kit** (`HOLIDAYS.juneteenth`, `nextOccurrence`, `daysLabel`); never hard-code a year.
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`; the build must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB (about 1.3 MB now).

## Fonts

`big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma, about 18 characters), `clock`
7×12. Missing characters are skipped silently, which is why the parity test checks every glyph.
