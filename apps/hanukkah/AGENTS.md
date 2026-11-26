# AGENTS.md — Hanukkah

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     23 scenes (menorah_0-8, window_0-8, 5 more) + 2 card backdrops
                                    app/shared/generated/show.ts  scenes, durations, card backdrops, fonts, text layout
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/hanukkah.ts   pure date logic: tonight's candles, card texts, the playlist, holiday mode
app/src/main.ts          configuration for the kit's createShow() (lib/ts/busybar/showrunner.ts)
```

Commands, run from this folder (the repo-level `tools/check.sh hanukkah` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene, card and night; LOOK
python3 renderer/review.py scene menorah_8 previews/ 0.2 2 6  # every 0.2 s between 2 s and 6 s
bash tests/check.sh                                         # logic + mockup mirror tests, live-text parity
```

## Invariants: don't break these

- **Candle rules (D3, D11).** The new candle appears at candle time: sunset at the location setting, or estimated
  from the bar's UTC offset, unless the Candle time setting fixes an hour (fallback 17:00). Night n uses the
  rightmost n cups; the shamash lights them from left to right. The count stays 8 through the ninth calendar day.
  `tests/logic.test.mts` pins the 2026 boundaries.
- **Settings** live in `app/src/appmeta/settings.json`. Bump its `version` and `SETTINGS_VERSION` in `main.ts`
  together; keep `SUNDOWN_OPTIONS` in `hanukkah.ts` and the mockup's selector in step with the enum.
- **Dates come only from the kit** (`HOLIDAYS.hanukkah`, `nextOccurrence(t, …, 9)`, `daysLabel`). Never hard-code
  a year.
- **Three copies of the date logic agree:** `app/shared/hanukkah.ts`, the `<logic>` block in
  `mockup/template.html` (which also mirrors the kit's `sun.ts`), and the tests. Change them together.
- **Scene names are an interface.** The app finds scenes by name (`menorah_<n>`, `window_<n>`, `dreidel`, `latkes`,
  `sufganiyot`, `gelt`, `finale`). Renaming one means changing `hanukkah.ts` and the mockup too.
- **15 fps, full screen, deterministic.** Each `render()` returns exactly `SECONDS * FPS` RGBA 72×16 frames. Seed
  every RNG; use `hash01` for flicker. CI re-renders and expects identical bytes.
- **Keep glows steady.** Flame and room glows don't flicker per frame; flickering them across many pixels tripled
  the `.anim` size. Total is about 1.6 MB; keep it under about 3 MB.
- **Live-text parity.** `LAYOUT` in `renderer/scenes/cards.py`, the app's `xpmtext` bitmaps and the mockup must draw
  identical pixels (`tests/text_parity.py`).
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.

## Pixel-art rules

- **Lit colors only for details.** Wicks are grey-brown, the night is lit navy. Black is an unlit LED.
- **Flames sit above a wick row,** so they don't merge into a white candle.
- **Fonts:** `big` 5×7 (about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12. `HAPPY HANUKKAH` only
  fits in `tiny`.
- **Respect:** traditional symbols used correctly (candle count and order, the shamash, dreidel letters). Warm and
  celebratory, no caricature. Original art only.
