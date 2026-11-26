# Memorial Day

A quiet tribute for Memorial Day, which honors those who died in military service. Slow scenes of the flag (at
half-staff until noon on the day, as the custom asks), the six armed services, a field of poppies, rows of white
headstones at dusk, a lone bugler at sunset, a missing-man flyover, the Tomb of the Unknown Soldier and a memorial
wall, with a clock and a countdown between them.

Open [mockup/index.html](mockup/index.html) in a browser for a simulator of the bar and storyboards of every scene.

## The show

One cycle is scene, clock, scene, countdown, and so on (about 3 min):

| # | Scene | Seconds | What happens |
|---|---|---|---|
| 1 | The Flag at Half-Staff | 14 | The morning of Memorial Day: the flag is at the peak, then lowered slowly to half-staff against a calm morning sky |
| 1 | The Flag at Full Staff | 14 | From noon on Memorial Day, and every other day: the flag flies at the peak against a clear afternoon sky |
| 2 | The Armed Services | 17 | The six services in order of precedence, each for about 2.8 s with its name across the top, sliding one into the next: `ARMY` (a column marching along a road), `MARINE CORPS` (three figures in dress blues salute), `NAVY` (a grey ship at sea), `AIR FORCE` (jets in echelon trailing smoke), `SPACE FORCE` (a satellite over the curve of the Earth), `COAST GUARD` (an orange rescue helicopter hovering over the waves) |
| 3 | A Field of Poppies | 14 | Red poppies run to the hills; a slow breeze passes through them and a single petal drifts |
| 4 | Rows of Honor | 16 | Straight rows of plain white headstones, small flags before the nearest; sunset fades to twilight and stars |
| 5 | The Lone Bugler | 14 | A silhouetted bugler on a hill raises the bugle as the sun goes down (taps is implied), then stands at attention |
| 6 | The Missing Man | 14 | Four plain aircraft fly over in formation; the third pulls up and climbs away alone, and the others fly on |
| 7 | The Tomb of the Unknown Soldier | 16 | A sentinel in dress blues walks 21 steps across the mat before a white marble tomb, turns to face it, turns again and walks back, while the day turns to rain, then snow, then night |
| 8 | At the Memorial Wall | 16 | A wreath between two candles at a stone wall; `WE REMEMBER` fades in |

Only one flag scene plays per cycle. The app picks it from the bar's clock at the start of each cycle, so at noon
the flag goes to full staff within one cycle.

## Cards

Live text drawn by the app from the bar's clock, over a calm looping backdrop:

| Card | When | Text |
|---|---|---|
| Clock | after scenes 1, 3, 5, 7 | the time (`09:05`), then the date (`MON 31 MAY`) |
| Countdown | after scenes 2, 4, 6, 8, before and after the day | `186 DAYS` / `TO MEMORIAL DAY` |
| Day 1 | on the day, after scenes 2 and 8 | `MEMORIAL DAY`, then `HONOR AND` / `REMEMBER` |
| Day 2 | on the day, after scene 4 | `MEMORIAL DAY`, then `WE REMEMBER` |
| Day 3 | on the day, after scene 6 | `MEMORIAL DAY`, then `HALF-STAFF` / `UNTIL NOON` (morning) or `FULL STAFF` / `RAISED AT NOON` (afternoon) |

Memorial Day is the last Monday of May (May 31, 2027; May 29, 2028), from the kit's `HOLIDAYS.memorialDay`.

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: the first press previews the morning of Memorial Day (half-staff flag, day cards), the second the afternoon (full staff), the third goes back to the calendar. Each press restarts the cycle at the flag |
| Back | quit |

## Install

Download `busybartools.memorialday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh memorial-day                              # build + typecheck + tests
python3 apps/memorial-day/renderer/build.py              # (from the repo root) re-render the scenes
python3 apps/memorial-day/renderer/review.py all apps/memorial-day/previews/   # LED-style review strips
python3 apps/memorial-day/renderer/review.py grid tomb apps/memorial-day/previews/ 0.5   # a labeled grid
tools/deploy.sh memorial-day                             # install and launch on the bar in .env
```

How to change it:
- **A scene:** edit or add `renderer/scenes/<name>.py`, register it in `ALL` (`renderer/scenes/__init__.py`), run
  `build.py` and look at the review strips.
- **The words:** `app/shared/memorial.ts` (the app and mockup) and `renderer/scenes/text.py` (review copy; the parity
  test checks they agree).
- **Text colors and positions:** `LAYOUT` in `renderer/scenes/text.py`.
- **The noon switch:** `NOON_HOUR` and `halfStaff()` in `app/shared/memorial.ts`.

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
