# AGENTS.md — Christmas Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + clock_bg
                                    app/shared/generated/show.ts  playlist, durations, fonts, clock layout
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/src/main.ts (TS) plays the scenes in order; after each one it draws a clock card from the bar's time
```

Commands, run from this folder (the repo-level `tools/check.sh christmas-day` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene; LOOK at them
python3 renderer/review.py scene <scene> previews/ 0.2 6 8  # every 0.2 s between 6 s and 8 s
python3 tests/clock_parity.py                               # app TS vs renderer: identical clock pixels
```

## Invariants: don't break these

- **15 fps, full screen.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of 72×16. The kit's
  `build_scenes` asserts this.
- **Deterministic.** Seed every RNG (`random.Random(n)`, `Particles(seed=…)`, `Snow(seed=…)`). Never use
  module-level `random` or iterate sets. CI re-renders on Linux and expects byte-identical `.anim` files.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES` and `render()`.
  Register the module in `PLAYLIST` (`renderer/scenes/__init__.py`). A clock card follows every scene.
- **Tone curve.** `GAMMA = 0.8` in `build.py` applies to every frame and to the clock colors. Scenes draw in linear
  colors; don't pre-brighten.
- **Live-text parity.** Clock and date pixels come from three implementations that must agree:
  - `LAYOUT` in `renderer/scenes/clock_bg.py`, drawn with `busybar.font`;
  - `app/shared/clocktext.ts`, which re-exports the shared `xpmtext.ts`;
  - `mockup/template.html`.

  `tests/clock_parity.py` checks them, plus the widest date and the playlist.
- **Clock backdrop stays calm.** Decorations keep to rows 0–1 and 14–15 and the outer columns. The time occupies
  rows 2–14, x 19–53, and the date occupies rows 4–11.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`. Change the generator, rebuild and commit.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 4 MB. It is about 0.8 MB now.

## Pixel-art rules

- **Lit colors for small features.** Eyes are `#7A4A3A`, coal is grey-blue, noses are orange. Black is an unlit LED.
- **Check contrast against the background.** An orange cat on red brick vanished, and green text over green trees
  muddled. Move the action or dim the background (D6, D9).
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma, about 18
  characters), `clock` 7×12 (digits and `:`). Missing characters are skipped silently.
- **Sprites face right**; use `img(i, flip=True)` for left. Use `Sprite.recolor()` for color variants.
- **Original art only:** generic Christmas folklore (Santa, reindeer, elves, snowmen). No licensed characters.
  For example, no glowing-nosed reindeer.

## Changing the show

| Change | Where | Then |
|---|---|---|
| Add or replace a scene | new `renderer/scenes/<name>.py` + `PLAYLIST` | `build.py`, review strips, README scene table |
| Scene length | `SECONDS` (and its timeline) | `build.py` |
| Clock timing or colors | `LAYOUT` in `renderer/scenes/clock_bg.py` | `build.py` + `tests/clock_parity.py` |
| Brightness | `GAMMA` in `renderer/build.py` | check on the real panel if possible |
| Buttons or playback | `app/src/main.ts` | `tools/check.sh christmas-day` |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers release |
