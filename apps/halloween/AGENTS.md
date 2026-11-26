# AGENTS.md — Halloween

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## Tone (D2)

Spooky-fun and family-friendly, never frightening: friendly faces, no gore, nothing that jumps out. Costumes are
generic (a sheet ghost, a witch hat, a pumpkin suit, a cape); the witch, ghosts, skeletons and cat are original. No
famous movie monsters or franchise characters. Tombstones say `RIP` at most, never a name. Words on screen are short
and generic (`TRICK OR TREAT!`, `BOO!`, `SPOOKY SEASON`, `HAPPY HAUNTING`).

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 backdrops
                                    app/shared/generated/show.ts  scenes, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator (template.html + inlined halloween.ts)
renderer/hfx.py      skies, the full moon, steady glows, jack-o'-lanterns and their faces, cobwebs, candles, stones
renderer/sprites.py  bats, the haunted house, the four trick-or-treaters, the witch, the ghosts, the black cat
app/shared/halloween.ts  card texts and the playlist, pure functions of the bar's time (app, mockup, tests share it)
app/src/main.ts      configuration for the kit's createShow(); START toggles holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh halloween` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene cat previews/ 0.2 5.6 7    # every 0.2 s between 5.6 s and 7 s
python3 renderer/review_zoom.py cat previews/z.png 30 72 6.2,9.0   # zoomed columns, for small sprites
python3 tests/text_parity.py                                # app TS vs renderer: identical card pixels
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of
  72×16. Seed every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract:** `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`, registered in `PLAYLIST`.
- **Eight scenes, four count slots.** The playlist is scene, clock, scene, count… On the day, the count slots show
  `day0`–`day3` in order. Changing the number of scenes changes how many day cards are shown (`playlist()` wraps).
- **Dates come only from the kit** (`HOLIDAYS.halloween`, `nextOccurrence`). The countdown counts nights with the
  app's own `nightsLabel` (D7). Never hard-code a year.
- **The text gap.** Both backdrops keep their corner art in columns 0–7 and 64–71. Every card line, its 1 px shadow
  included, must stay in columns 8–63 (`TEXT_GAP` in `renderer/scenes/text.py`): at most 55 px of text. `365 NIGHTS`
  is exactly 55. Tests decode every card bitmap and check it.
- **Live-text parity.** Card pixels come from three implementations that must agree: `LAYOUT` in
  `renderer/scenes/text.py` (drawn by `build.draw_live`), the app (`xpmtext.ts` with the generated `LAYOUT`), and the
  mockup. `tests/text_parity.py` checks them, and that `DAY_TEXT` (review copy) matches the app's `DAY_CARDS`.
- **Mockup names.** The mockup pastes `walltime.ts`, `holidays.ts` and `halloween.ts` into one scope, so app-level
  constants carry an `HW_` prefix (a repeated name like `DAY_MS` is a SyntaxError there). A test runs the mockup's
  logic block against the app's for every day of three years.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB. It is about 0.7 MB now. Keep glows steady: halos that flicker
  every frame make files several times larger; only a few flame and face pixels flicker.

## Pixel-art rules

- **Black is an unlit LED.** The cat, bats, witch's dress and house are lit violet-greys with a lighter rim on their
  moonlit edges. Eyes are lit: the cat's yellow-green, the skeletons' green sockets, the bats' orange-red.
- **Silhouettes need the moon.** The cat stops, and the witch and the bats fly, in front of the full moon, where the
  violet-grey reads as a crisp shape.
- **Faces glow against a darker skin.** A lit jack-o'-lantern's skin darkens a little; its face ramps from the carved
  hole through deep amber to candle yellow (a straight blend passes through olive, and through orange the face
  vanishes into the skin).
- **No accidental symbols.** Skeleton arms are never held straight out at shoulder height (with the ribs, that read
  as a cross); the can-can uses hands on hips.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12.
  Missing characters are skipped silently; the tests check every card text and the baked scene words (`SCENE_TEXT`).
