# AGENTS.md — MLK Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## This is a tribute (D2)

- Slow, dignified pacing and calm colors (deep blues, dawn golds). No confetti, fireworks, jokes or party effects.
  Don't depict violence.
- **No likeness of Dr. King or any real person.** Figures stay small, generic and faceless.
- **No quotations** from his speeches or writings (the King estate enforces copyright). Only single common words, the
  holiday's name, the countdown and the MLK Day of Service motto `A DAY ON` / `NOT A DAY OFF`. Any new on-screen
  word needs the user's approval.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 backdrops
                                    app/shared/generated/show.ts  scenes, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator (template.html + inlined mlk.ts logic)
app/shared/mlk.ts    card texts and the playlist, pure functions of the bar's time (app, mockup and tests share it)
app/src/main.ts      configuration for the kit's createShow(); START toggles holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh mlk-day` runs all of it):

```bash
python3 renderer/build.py                                  # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                   # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene march previews/ 0.2 9 11  # every 0.2 s between 9 s and 11 s
python3 tests/text_parity.py                               # app TS vs renderer: identical card pixels
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of
  72×16. Seed every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract:** `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`, registered in `PLAYLIST`.
- **Six scenes, three count slots.** The playlist is scene, clock, scene, count… On the day, the count slots show
  `day0`–`day2` in order. Changing the number of scenes changes how many day cards are shown (`playlist()` wraps).
- **Dates come only from the kit** (`HOLIDAYS.mlkDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from three implementations that must agree: `LAYOUT` in
  `renderer/scenes/text.py` (drawn by `build.draw_live`), the app (`xpmtext.ts` with the generated `LAYOUT`), and the
  mockup. `tests/text_parity.py` checks them, and that `DAY_TEXT` (review copy) matches the app's `DAY_CARDS`.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB. It is about 2.0 MB now.

## Pixel-art rules

- **Every skin tone stays lit** (the deepest is `#764A32`). Check figures against the background: the horizon in
  the march sits behind the walkers' shoulders so clothes read against dark fields (D5).
- **Keep words in clear sky** (D6), and fade them in slowly.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12.
  Missing characters are skipped silently; `tests/logic.test.mts` checks every card text.
