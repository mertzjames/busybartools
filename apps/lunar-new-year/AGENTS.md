# AGENTS.md — Lunar New Year

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     7 festival scenes, 12 zodiac scenes, card_bg
                                    app/shared/generated/show.ts  scenes, playlists, text styles + timing, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (from mockup/template.html)
app/shared/lny.ts (TS)   the date logic: season, zodiac animal, card texts, greetings, playlist, holiday mode
app/src/main.ts (TS)     loads the settings once, then configures the kit's show runner (createShow)
app/src/appmeta/settings.json   the Greeting setting (enum), editable on the bar under Setup
```

Commands, run from this folder (the repo-level `tools/check.sh lunar-new-year` runs all of it):

```bash
python3 renderer/build.py                                    # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                     # LED-style strips of every scene, the zodiac, the cards
python3 renderer/review.py scene dragon_dance previews/ 0.2 8 11  # every 0.2 s between 8 s and 11 s
bash tests/check.sh                                          # logic tests, mockup mirror, live-text parity
```

## Invariants: don't break these

- **15 fps, full screen.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of 72×16.
- **Deterministic.** Seed every RNG. Never use module-level `random` or iterate sets.
- **Scene contract** (`NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`). Festival scenes go in `PLAYLIST` and are
  named in `PLAYLISTS` (`renderer/scenes/__init__.py`). Zodiac scenes are `zodiac.ZodiacScene` instances named
  `zodiac_<animal>`, in the kit's `ZODIAC` order.
- **Dates come only from the kit** (`HOLIDAYS.lunarNewYear`, `zodiac`, `nextOccurrence`). Never hard-code a year.
  The festival span is 15 days. Outside the table, there's a generic greeting and no countdown (D11).
- **Three copies of the card logic must agree:**
  - `app/shared/lny.ts`;
  - the `// <logic>` block in `mockup/template.html`;
  - the styles in `renderer/textstyle.py`.

  `tests/logic.test.mts` and `tests/text_parity.py` check them.
- **Card backdrop stays calm.** Lanterns keep to rows 0–7 and the outer 5 columns, and blossoms to the outer 2
  columns. Text boxes:
  - time: rows 2–14, x 19–53;
  - `TO LUNAR NEW YEAR`: rows 10–15, x 4–68;
  - two big lines: rows 0–15, x 12–60.
- **Settings:** `settings.json` "version" equals `SETTINGS_VERSION` in `lny.ts`, and its greeting options equal
  `GREETINGS`; the tests check both. Load settings once at start with the kit's `loadSettings` (never throws).
- **The finale is festival-only** (D16): keep it out of the countdown playlist.
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** The build output must say `scripts: main.js` only.
- **Size.** Total `.anim` data is about 1.1 MB. Keep it under about 3 MB.

## Pixel-art rules

- **Lit colors for small features.** Black is an unlit LED: eyes are dark-but-lit browns or light glints, and the
  tiger's stripes are a lit brown.
- **Contrast.** Red envelopes and lanterns sit on dark wine or night backgrounds, never on bright red. Dim the
  scene behind captions (D13).
- **People are simple figures**, with no drawn faces or caricature (D12). Original art only: no licensed
  characters.
- **Fonts:**
  - `big` 5×7, about 12 characters across;
  - `tiny` 3×5, no comma;
  - `clock` 7×12, digits and `:` only.

  Missing characters are skipped silently.

## Changing the show

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` (+ `PLAYLIST`, `PLAYLISTS`) | `build.py`, review strips, README table |
| A zodiac animal | `renderer/sprites.py` + `ANIMALS` in `renderer/scenes/zodiac.py` | `review.py zodiac previews/` |
| Card text or rules | `app/shared/lny.ts` **and** the mockup `<logic>` block | `bash tests/check.sh` |
| Card colors or timing | `renderer/textstyle.py` | `build.py` + `tests/text_parity.py` |
| Buttons | `app/src/main.ts` | `tools/check.sh lunar-new-year` |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers release |
