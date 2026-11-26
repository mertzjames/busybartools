# AGENTS.md — Easter

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## Tone (D2, D3)

- Cheerful, family-friendly, springtime: bunny, eggs, chicks, flowers. Original art only (no licensed characters).
- The only traditional note is the finale's sunrise with Easter lilies. No cross or other explicitly religious
  symbol; ask the user before adding one.
- Kids are small faceless profiles (no eyes or mouths).

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 3 backdrops
                                    app/shared/generated/show.ts  scenes, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator (template.html + inlined easter.ts logic)
renderer/efx.py      eggs, flowers, grass, sky, sun, basket, nest, kids, the bunny's hop
renderer/sprites.py  the bunny, the chick, the butterfly, the chocolate bunny
app/shared/easter.ts card texts, backdrops and the playlist, pure functions of the bar's time (app, mockup, tests)
app/src/main.ts      configuration for the kit's createShow(); START toggles holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh easter` runs all of it):

```bash
python3 renderer/build.py                                      # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                       # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene hatching previews/ 0.2 1.4 3.2 # every 0.2 s between 1.4 s and 3.2 s
python3 tests/text_parity.py                                   # app TS vs renderer: identical card pixels, text gaps
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of
  72×16. Seed every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract:** `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`, registered in `PLAYLIST`.
- **Seven scenes, three count slots.** The playlist is scene, clock, scene, count… On Easter Sunday, the count slots
  show `day0`–`day2` in order. Changing the number of scenes changes how many day cards are shown (`playlist()`
  wraps), and `tests/logic.test.mts` expects seven.
- **Dates come only from the kit** (`HOLIDAYS.easter`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from three implementations that must agree: `LAYOUT` in
  `renderer/scenes/text.py` (drawn by `build.draw_live`), the app (`xpmtext.ts` with the generated `LAYOUT`), and the
  mockup. `tests/text_parity.py` checks them, that `DAY_TEXT` (review copy) matches the app's `DAY_CARDS`, and that
  every text stays inside its backdrop's `TEXT_GAP`.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB. It is about 0.45 MB now.

## Pixel-art rules

- **Pastels stay lit and saturated** (D4). No blue egg on the blue sky; check every new color in a review strip.
- **Small features are lit colors** (D5): the bunny's eye is deep violet, the chick's lit brown, the crack plum.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12.
  Missing characters are skipped silently; `tests/logic.test.mts` checks every card text.
