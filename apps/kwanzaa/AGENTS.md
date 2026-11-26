# AGENTS.md — Kwanzaa

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     kinara_0..7, kinara_center_2..7, scenes, card_bg
                                    app/shared/generated/show.ts  scenes, styles, timings, principles, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/src/main.ts (TS)  configures the kit's show runner: clock + count cards, steps(t) from app/shared/kwanzaa.ts
```

Commands, run from this folder (the repo-level `tools/check.sh kwanzaa` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py kinara 7 previews/ 0.2 2 11      # one kinara variant, every 0.2 s
python3 tests/text_parity.py                                # app TS vs renderer: identical text pixels and pages
```

## Invariants: don't break these

- **The candles are right.** Red ×3 left, black center, green ×3 right. Day 1 lights the black. Then the colors
  alternate red, green, … in one of two orders: `official` (each side from left to right, D3; the default) or
  `center_out` (outward from the center, D14), from `LIGHT_ORDERS`. Day N relights all N candles. Never change an
  order without a source and a D-note.
- **Scene indices come from `show.ts`.** `SHOW.kinara[order][day]` is the kinara scene index for each order, and
  `SHOW.playlist` lists the scenes that follow. `cycleSteps(day, order)` and the tests rely on this. Don't index
  `SHOW.scenes` by position.
- **The setting.** `app/src/appmeta/settings.json` (`lighting_order`, version 1) must match `ORDERS`,
  `DEFAULT_ORDER` and `SETTINGS_VERSION` in `app/shared/kwanzaa.ts` (tested). Bump the version on incompatible
  changes.
- **One source for card text.** `renderer/scenes/text.py` (styles, timings, principles) is exported into `show.ts`.
  `count_pages` (Python) and `countPages` (`app/shared/kwanzaa.ts`) must agree; `tests/text_parity.py` checks this.
  The mockup runs `kwanzaa.ts` itself (D13).
- **Dates come from the kit.** `nextOccurrence(t, HOLIDAYS.kwanzaa, 7)`; never hard-code a year. The day changes at
  local midnight (D4).
- **15 fps, full screen, deterministic.** Seed every RNG; use `hash01` or the frame number for flicker.
- **Tone curve.** `GAMMA = 0.8` in `build.py` applies to every frame and every text color.
- **Card rows.** The backdrop's border uses rows 0 and 15 only. `head` text uses rows 1–8 and `sub` rows 9–14.
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** About 1.5 MB of `.anim` data now. Keep it under about 3 MB.

## Pixel-art rules

- **Black is an unlit LED.** The black candle and the "black" in the weave are lit charcoal (D5). Hair defaults to a
  lit brown. Faces have no eyes (D8).
- **Respect.** Simple figures with a range of warm skin tones. No caricature, no exaggerated features, and no real
  people.
- **Contrast.** Figures stand against a warm wall glow or a dusk sky. Captions get a dimmed panel or band (D12).
- **Fonts:** `big` 5×7 (A–Z 0–9 `!',-.:?`, `KUJICHAGULIA` = 67 px), `tiny` 3×5 (18 characters max, no comma),
  `clock` 7×12.
- **Original art only.** The kente motifs are original (D9).

## Changing the show

| Change | Where | Then |
|---|---|---|
| Add or replace a scene | `renderer/scenes/<name>.py` + `PLAYLIST` | `build.py`, review strips, README table, the playlist test |
| Kinara art or timing | `Kinara` in `renderer/kfx.py`, `renderer/scenes/kinara.py` | review every variant (both orders) |
| Settings | `app/src/appmeta/settings.json`, `loadOrder` in `app/shared/kwanzaa.ts` | README settings, the settings tests |
| Card text or timing | `renderer/scenes/text.py` and `app/shared/kwanzaa.ts` | `tools/check.sh kwanzaa` |
| Buttons or holiday mode | `app/src/main.ts`, `nextPreview` in `app/shared/kwanzaa.ts` | README controls, D7 |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers release |
