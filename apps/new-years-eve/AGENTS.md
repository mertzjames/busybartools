# AGENTS.md — New Year's Eve

App-specific rules for AI coding agents. The repo-wide rules in [/AGENTS.md](../../AGENTS.md) still apply. Background
on every choice is in [docs/DECISIONS.md](docs/DECISIONS.md): read the relevant entries before changing something
deliberate.

- **What it does:** party scenes with a countdown card to the bar's midnight on Dec 31, a final-minute screen, huge
  digits for the last ten seconds, then fireworks with `HAPPY NEW YEAR` and the year. START is a demo (T−15 s).
- **Entry point:** `app/src/main.ts`. Put helpers and generated data in `app/shared/`, never in `app/src/`.
- **Build and test:** `tools/check.sh new-years-eve` from the repo root.

## How this app is built

```
renderer/ (Python) ──build.py──► app/src/animations/*.anim      8 scenes + 6 live-screen backdrops
                                  app/shared/generated/show.ts   playlist, backdrops, LAYOUT (toned), FONTS (+ huge)
                                  app/src/appmeta/icon_*.png
                                  mockup/index.html              template + data + the app's TS logic, type-stripped
app/shared/nye.ts       pure time logic: phaseAt, newYear, cardText, demoOffset, settleDemo, planStep, celebrateState
app/shared/screens.ts   pure live-screen layouts -> layers -> one xpmbitmap (composeBitmap)
app/src/main.ts         clock sync (edge polling), timers, draws through one drawqueue
```

## Invariants: don't break these

- **15 fps, full screen, deterministic.** Every scene's `render()` returns `SECONDS * FPS` 72×16 frames. Seed every RNG
  (`random.Random(n)`, `Particles(seed=…)`, or the `party.hash01` flicker); never module-level `random`. CI re-renders
  and expects byte-identical files.
- **Backdrop loops are seamless.** `final10_bg` is exactly 1 s (one beat). Time-based effects in loops go through
  `party.draw_looped` or are periodic in the frame count.
- **No baked dates or years.** Anything that depends on the time is drawn live by the app (cards, counts, the year,
  the odometer digits).
- **Pure logic stays pure and inlinable.** `nye.ts` and `screens.ts` take time as an argument (no `Date.now()`, no
  device calls, no JS `Date` local-time methods), use single-line imports, and no enums or namespaces, because
  `build.py` type-strips and inlines them into the mockup. New exports must be `export function` or `export const`.
- **Scenes never overrun midnight.** Keep `planStep` the only place that decides what plays; the tests simulate whole
  evenings and assert no scene or card ends after T−60 s. Every scene must stay shorter than about 20 s.
- **Requests.** At most one live-text draw per second (one composed xpmbitmap, at most 32 colors) and one request in
  flight. No edge sync during the final minute.
- **Live-text parity.** `tests/live_parity.py` must pass: the app's bitmaps equal `busybar.font.draw_text` with the
  exported `LAYOUT`. Change colors and positions in `renderer/live.py` only; `GAMMA` (0.8) tones them in `build.py`.
- **Generated files are outputs:** `show.ts`, `.anim`, icons and `mockup/index.html`. Edit the generator, rebuild,
  commit the results.
- **Keep `.anim` data under about 4 MB** (it's about 1.1 MB). Static backgrounds compress well; full-screen flashes
  don't.

## Changing the show

| Change | Where | Then |
|---|---|---|
| Add or replace a scene | `renderer/scenes/<name>.py` + `PLAYLIST` in `scenes/__init__.py` | `build.py`, `review.py scene <name>`, look at it, update README |
| A live screen's look | `renderer/live.py` (layout, colors, huge font) or `app/shared/screens.ts` (placement) | `tools/check.sh new-years-eve` (parity), `review.py live` |
| Phase timings | constants at the top of `app/shared/nye.ts` | update tests and README |
| Backdrops | `renderer/scenes/backdrops.py` | `review.py all`, `review.py live` |
| Release | bump `"version"` in `app/src/appmeta/manifest.json` in a PR to `dev` | maintainers run `tools/release.sh new-years-eve` |

Always look at LED-style strips (`python3 renderer/review.py all` and `live`) before committing art.
