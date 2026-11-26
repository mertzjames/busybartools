# AGENTS.md — Valentine's Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## Tone (D2)

Sweet and family-friendly, not romantic-explicit: hearts, a cherub, birds, chocolates, a rose, candy hearts. Words
on screen are short, generic and original (`FOR YOU`, `BE MINE`, `XOXO`, `HUG ME`, `LOVE YOU`, `BE TRUE`,
`SO SWEET`). The cherub is a generic winged baby; no licensed characters or brand candy designs.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 backdrops
                                    app/shared/generated/show.ts  scenes, backdrops, text LAYOUT, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             simulator (template.html + inlined valentine.ts)
renderer/vfx.py      hearts of any size, rising-heart drifts, a heart-shaped firework, caption helpers
renderer/sprites.py  the cherub, the two birds, the rose's bloom stages
app/shared/valentine.ts  card texts and the playlist, pure functions of the bar's time (app, mockup, tests share it)
app/src/main.ts      configuration for the kit's createShow(); START toggles holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh valentines-day` runs all of it):

```bash
python3 renderer/build.py                                   # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene cupid previews/ 0.2 5 7    # every 0.2 s between 5 s and 7 s
python3 renderer/review_zoom.py cupid previews/z.png 0 36 4.6,5.4   # zoomed columns, for small sprites
python3 tests/text_parity.py                                # app TS vs renderer: identical card pixels
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Each scene's `render()` returns exactly `SECONDS * FPS` RGBA frames of
  72×16. Seed every RNG; CI re-renders and expects byte-identical `.anim` files.
- **Scene module contract:** `NAME`, `TITLE`, `SECONDS`, `KEYFRAMES`, `render()`, registered in `PLAYLIST`.
- **Seven scenes, three count slots.** The playlist is scene, clock, scene, count… On the day, the count slots show
  `day0`–`day2` in order. Changing the number of scenes changes how many day cards are shown (`playlist()` wraps).
- **Dates come only from the kit** (`HOLIDAYS.valentinesDay`, `nextOccurrence`, `daysLabel`). Never hard-code a year.
- **The candy-heart frame.** `count_bg` draws its candy hearts in columns 1–9 and 62–70, rows 1–9. Big lines on it
  (`head`, `candy`) must be at most 47 px wide; the tiny line (rows 10–15) may use the full width.
  `TO VALENTINE'S DAY` is 67 px. Tests check all of this.
- **Live-text parity.** Card pixels come from three implementations that must agree: `LAYOUT` in
  `renderer/scenes/text.py` (drawn by `build.draw_live`), the app (`xpmtext.ts` with the generated `LAYOUT`), and the
  mockup. `tests/text_parity.py` checks them, and that `DAY_TEXT` (review copy) matches the app's `DAY_CARDS`.
- **Generated files are outputs.** Never hand-edit `.anim` files, `app/shared/generated/show.ts`, the icons or
  `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** Keep total `.anim` data under about 3 MB. It is about 0.6 MB now. Keep glows steady: halos that flicker
  every frame make files several times larger.

## Pixel-art rules

- **Small features are lit.** The cherub's eye is a lit blue (`#4A50B4`) on peach skin, and the gold bird's eye is a
  lit plum. Black is an unlit LED.
- **Separate overlapping shapes.** Rising hearts get a 1 px dark halo, so neighbors never merge into blobs; the big
  hearts get one too.
- **Pinks need a dark background.** Pale pinks blended at low alpha turn grey-mauve; dim hearts behind text use
  saturated reds instead.
- **Fonts:** `big` 5×7 (A–Z, 0–9, `!',-.:?`, about 12 characters across), `tiny` 3×5 (no comma), `clock` 7×12.
  Missing characters are skipped silently; `tests/logic.test.mts` checks every card text.
