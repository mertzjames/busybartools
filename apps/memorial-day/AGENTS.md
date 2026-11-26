# AGENTS.md — Memorial Day

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

## How this app is built

```
renderer/ (Python)  ──build.py──►  app/src/animations/*.anim     one full-screen 72×16 .anim per scene + 2 backdrops
                                    app/shared/generated/show.ts  scenes, durations, backdrops, text layout, fonts
                                    app/src/appmeta/icon_*.png    menu icons
                                    mockup/index.html             browser simulator (template.html + memorial.ts)
app/shared/memorial.ts   dates, the half-staff rule, card texts, the playlist (pure functions of the bar's time)
app/src/main.ts          configuration for the kit's createShow(); START cycles the holiday mode
```

Commands, run from this folder (the repo-level `tools/check.sh memorial-day` runs all of it):

```bash
python3 renderer/build.py                                    # render everything; verifies every .anim round-trips
python3 renderer/review.py all previews/                     # LED-style strips of every scene and card; LOOK at them
python3 renderer/review.py scene flyover previews/ 0.2 5 8   # every 0.2 s between 5 s and 8 s
bash tests/check.sh                                          # Node logic tests + live-text parity
```

## Invariants: don't break these

- **Tribute tone (D2, D3).** Slow, muted, no party effects, jokes, cookouts or sales; no insignia, seals or branch
  emblems; no likenesses; no combat. No "Happy Memorial Day".
- **The flag custom (D5).** Half-staff on Memorial Day before 12:00 local, full staff from 12:00 and on every other
  day. `halfStaff()` is the one source of truth; tests cover 11:59 and 12:00.
- **15 fps, full screen, deterministic.** Each scene returns `SECONDS * FPS` RGBA frames; seed every RNG.
- **Scene registry.** `ALL` in `renderer/scenes/__init__.py` lists every shipped scene in show order; the two flag
  variants (`flag_half`, `flag_full`) come first. `playlist()` finds them by name.
- **Words in two places.** `app/shared/memorial.ts` is the source of truth; `renderer/scenes/text.py` keeps a review
  copy. `tests/text_parity.py` checks they agree and that the pixels match; `tests/logic.test.mts` checks every text
  fits and that the mockup's inlined logic matches the app.
- **Generated files are outputs.** Never hand-edit `.anim`, `show.ts`, the icons or `mockup/index.html`.
- **One script.** Helpers live in `app/shared/`. The build output must say `scripts: main.js` only.
- **Size.** About 1 MB of `.anim` data; keep it under 3 MB.

## Pixel-art rules

- Black is an unlit LED: the poppy eye is lit violet, the bugler silhouette is a lit plum and reads only against a
  bright sky behind him.
- Flags shift by whole rows (fractional offsets blur red and white into pink).
- Fonts: `big` 5×7 (about 12 characters), `tiny` 3×5 (about 18), `clock` 7×12. Missing characters are skipped.
