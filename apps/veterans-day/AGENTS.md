# AGENTS.md — Veterans Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 3 backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text layout, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (template.html + veterans.ts)
app/shared/veterans.ts   dates, card texts, the 11:00 moment, the playlist (pure functions of the bar's time)
app/src/main.ts          configuration for the kit's createShow(); the 11:00 timer; START cycles the holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh veterans-day` runs all of it):

```bash
python3 renderer/build.py                                    # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                     # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py grid salute previews/ 0.2 1.4 3.4 # a labeled grid every 0.2 s between 1.4 s and 3.4 s
bash tests/check.sh                                          # Node logic tests + live-text parity
```

## Invariants: don't break these

- **Tribute tone (D2, D3).** Calm and warm; no party effects or jokes; no insignia, seals, branch emblems, medals or
  patches; no likenesses; no combat or weapons. No "Happy Veterans Day".
- **The 11:00 moment (D6).** `inMoment()` is the one source of truth: 11:00:00–11:00:59 on Nov 11 by the bar's
  wall clock. `msToMoment()` arms the timer only within 10 minutes; Back must clear it. Tests cover 10:59, 11:00 and
  11:01.
- **15 fps, full screen, deterministic.** Each scene returns `SECONDS * FPS` RGBA frames; seed every RNG.
- **Scene registry.** `ALL` in `renderer/scenes/__init__.py` lists every shipped scene in show order; `BACKDROPS`
  the three card backdrops, each with `ART` boxes that live text must stay clear of.
- **Words in two places.** `app/shared/veterans.ts` is the source of truth; `renderer/scenes/text.py` keeps a review
  copy and the scene captions. `tests/text_parity.py` checks they agree, that the pixels match and that text clears
  the edge art; `tests/logic.test.mts` checks every text fits and that the mockup's inlined logic matches the app.
- **Mockup scope.** The mockup pastes walltime.ts, holidays.ts and veterans.ts into one scope: don't add a top-level
  name to veterans.ts that repeats a kit name (`DAY_MS`, `pad2`, ...).
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** About 0.8 MB of `.anim` data; keep it under 3 MB.

## Pixel-art rules

- Black is an unlit LED: the poppy eye is a lit violet; trousers and cap bands are a lit dark blue.
- People need contrast behind them: a lit window, a warm horizon or a plain muted wall. Faces are plain skin.
- Flags shift by whole rows (fractional offsets blur red and white into pink).
- Fonts: `big` 5×7 (about 12 characters), `tiny` 3×5 (about 18), `clock` 7×12. Missing characters are skipped.
