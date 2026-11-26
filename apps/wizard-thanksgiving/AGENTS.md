# AGENTS.md — Wizarding Thanksgiving

App-specific rules. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background on every choice is in
[docs/DECISIONS.md](docs/DECISIONS.md) (D1–D26): read the relevant entries before changing something deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + clock_bg
                                    app/shared/generated/show.ts  playlist, durations, fonts, clock layout
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/src/main.ts (TS) plays the scenes in order; after each one it draws a clock card from /api/time
```

Commands, run from this folder (the repo-level `tools/check.sh wizard-thanksgiving` runs all of it):

```bash
python3 renderer/build.py                               # render everything (~2 s); verifies every .anim round-trips
python3 renderer/review.py scene <scene> <out_dir> 1.5  # LED-style keyframe strip; LOOK at it before committing
python3 renderer/review.py sprites <out.png>            # contact sheet of all sprites
python3 tests/clock_parity.py                           # app TS vs renderer: identical clock pixels
```

## Invariants: don't break these

- **15 fps, full screen.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of 72×16.
  `build.py` asserts this.
- **Deterministic.** Use seeded `random.Random(n)` and `fx.Particles(seed=…)`, never module-level `random`. CI
  re-renders on Linux and expects byte-identical output.
- **Scene module contract** (`renderer/scenes/<name>.py`): `NAME` (file-safe; becomes `<NAME>.anim`), `TITLE`,
  `SECONDS`, `KEYFRAMES = [(seconds, caption), …]` (used by the mockup storyboards) and `render()`. Register it in
  `PLAYLIST` in `renderer/scenes/__init__.py`. Order matters: a clock card follows every scene.
- **Tone curve.** `GAMMA` in `build.py` (currently 0.8) is applied to every output frame **and** to the clock colors.
  Scenes draw in "linear" colors; don't pre-brighten inside scenes.
- **Clock parity.** The clock text is drawn by three implementations that must agree pixel-for-pixel:
  - `renderer/font.py` with `LAYOUT` in `renderer/scenes/clock_bg.py`;
  - `app/shared/clocktext.ts`;
  - the mockup template.

  If you change glyphs, layout, colors or rounding, update all three and keep `tests/clock_parity.py` passing.
- **Generated files are outputs.** Never hand-edit `app/shared/generated/show.ts`, `mockup/index.html` or `.anim`
  files. Edit the generator, run `build.py`, and commit the results.
- **App code placement.** Helpers go in `app/shared/`, never extra `.ts` files in `app/src/` (see the repo AGENTS.md).

## Pixel-art rules learned the hard way

- **Lit colors for small features.** Black and near-black are unlit LEDs. The wizard's glasses are silver frames
  around green eyes for this reason (D18).
- **Fonts only have** `A–Z 0–9 space ! ' , - . : ?` (the `big` 5×7 font; `tiny` 3×5 has no comma). The clock
  font has digits and `:` only. Missing characters are silently skipped. The `big` font fits about 12 characters across
  72 px, and `tiny` about 18.
- **Sprites are text grids** in `renderer/sprites.py`: `.` is transparent, and every other character maps to a
  palette entry. Sprites face right; use `img(i, flip=True)` for left. Change colors with `Sprite.recolor()` instead
  of copying a sprite. Students' scarves use palette keys `R` and `Y`, and each student wears a different house
  (D19).
- **Original art only.** Keep the theme to genre references. No official characters, names, logos or fonts.
- **Test readability at LED scale.** A sprite that reads in the grid can blur on the panel. Render it with
  `review.py` and look at it.

## Changing the show

| Change | Where | Then |
|---|---|---|
| Add or replace a scene | new `renderer/scenes/<name>.py` + `PLAYLIST` | `build.py`, review the strip, update `README.md`'s scene table |
| Scene length | `SECONDS` in the scene (and its timeline) | `build.py` (durations flow into `show.ts` and the mockup) |
| Clock timing or colors | `LAYOUT` in `renderer/scenes/clock_bg.py` | `build.py` + `tests/clock_parity.py` |
| Overall brightness | `GAMMA` in `renderer/build.py` | `build.py`, check on the real panel if possible |
| Playback logic or buttons | `app/src/main.ts` | `tools/check.sh wizard-thanksgiving` |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers promote and run `tools/release.sh wizard-thanksgiving` |

Add a `docs/DECISIONS.md` entry for anything a future contributor would wonder about.
