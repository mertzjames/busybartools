# AGENTS.md — St. Patrick's Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## Tone (D2)

- Festive and family-friendly. Celebrate the day through folklore (leprechauns, rainbows, pots of gold, shamrocks)
  and heritage (the tricolor, pipers, knotwork).
- **No drinking.** No beer, pints, toasts (that rules out `SLAINTE`) or drunkenness, in art or words.
- **No caricatures.** No "fighting Irish" figures, no stage-Irish clichés. Any new on-screen word needs the user's
  approval.
- Original art only: the leprechaun and the knot pattern are this app's own designs.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 3 backdrops
                                    app/shared/generated/show.ts  scenes, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator (template.html + inlined stpatricks.ts)
renderer/pfx.py      app-local art: the leprechaun, shamrocks, rainbow, pot of gold, coins, captions
app/shared/stpatricks.ts  card texts and the playlist, pure functions of the bar's time (app, mockup, tests share it)
app/src/main.ts      configuration for the kit's createShow(); START toggles holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh st-patricks-day` runs all of it):

```bash
python3 renderer/build.py                                # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                 # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene jig previews/ 0.2 9 11  # every 0.2 s between 9 s and 11 s
python3 tests/text_parity.py                             # app TS vs renderer: identical card pixels
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of
  72×16. Seed every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract:** `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`, registered in `PLAYLIST`.
- **Seven scenes, three count slots.** The playlist is scene, clock, scene, count… On the day, the count slots show
  `day0`, `day1`, `day0`. Changing the number of scenes changes the slots (`playlist()` wraps).
- **Dates come only from the kit** (`HOLIDAYS.stPatricksDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **Live-text parity.** Card pixels come from three implementations that must agree: `LAYOUT` in
  `renderer/scenes/text.py` (drawn by `build.draw_live`), the app (`xpmtext.ts` with the generated `LAYOUT`), and the
  mockup. `tests/text_parity.py` checks them, and that `DAY_TEXT` (review copy) matches the app's `DAY_CARDS`.
  `tests/logic.test.mts` runs the mockup's inlined logic against the app's for every day of 2026–2029.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB. It is about 1.0 MB now.

## Pixel-art rules

- **Black is an unlit LED.** The leprechaun's eyes are a lit blue, his hat band a lit dark green, his shoes a lit
  brown; the pot is a lit blue-grey iron.
- **Green on green vanishes.** Keep backgrounds behind green figures a different hue or much darker: the jig's far
  hills are a dim teal, the shamrock field's soil is near-black green, the parade street is dark slate (D5).
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12.
  Missing characters are skipped silently; `tests/logic.test.mts` checks every card text fits.

## Changing the show

| Change | Where | Then |
|---|---|---|
| Add or replace a scene | new `renderer/scenes/<name>.py` + `PLAYLIST` | `build.py`, review strips, README scene table |
| Card words or timing | `app/shared/stpatricks.ts` + `DAY_TEXT` in `renderer/scenes/text.py` | `tools/check.sh st-patricks-day` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `build.py` + `tests/text_parity.py` |
| Buttons or playback | `app/src/main.ts` | `tools/check.sh st-patricks-day` |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers release |
