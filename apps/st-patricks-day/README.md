# St. Patrick's Day

A festive St. Patrick's Day show (March 17) for the BUSY Bar, drawn from Irish folklore: a leprechaun dancing a jig,
a rainbow ending at a pot of gold, a meadow of shamrocks with one lucky four-leaf clover, a parade with a piper and a
drummer, a river dyed green, a Celtic knot that weaves itself, and green, white and orange fireworks. Between scenes
come a clock and a countdown to St. Patrick's Day. On the day itself, the countdown becomes `HAPPY ST. PATRICK'S DAY`
and `ERIN GO BRAGH`.

It is family-friendly: folklore and heritage, with no drinking jokes and no caricatures (see
[docs/DECISIONS.md](docs/DECISIONS.md) D2). The leprechaun and the knot pattern are original designs.

Open [mockup/index.html](mockup/index.html) in a browser to watch the whole show, cards included, with a holiday-mode
toggle.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | The Leprechaun's Jig | 14 s | On a hilltop at sunrise, a leprechaun (green coat, buckled hat, ginger beard) taps his foot, dances a jig as notes float by, leaps for a heel click and tips his hat; gold sparkles and tiny shamrocks rise. |
| 2 | Rainbow's End | 15 s | A spring shower clears, a rainbow arcs across the sky to an old iron pot, a glint slides down it, and the pot overflows with tumbling, glittering gold. The leprechaun peeks out from behind it. |
| 3 | The Shamrock Field | 15 s | The view drifts over shamrocks nodding in the breeze until one catches the light: it has four leaves. It rises up, big and glowing. `LUCKY!` |
| 4 | The Parade | 16 s | Under green, white and orange bunting, the parade marches past: the tricolor, a piper in a saffron kilt with notes rising from the pipes, a drummer with a shamrock on the bass drum, and two children skipping. Confetti. |
| 5 | The Green River | 14 s | A work boat crosses a city river puffing orange powder; where it lands, the water turns green until the whole river glows emerald. A little shamrock sailboat drifts in. |
| 6 | The Celtic Knot | 14 s | A gold cord and a green cord weave over and under each other around the edge of the display into a closed knotwork border, around `ERIN GO BRAGH`. A gleam runs around the knot. |
| 7 | The Finale | 16 s | Fireworks in green, white and orange, with gold willows, over the night hills. `HAPPY`, then `ST. PATRICK'S`, then a last volley. |

## Cards

Cards are live text drawn by the app from the bar's clock, over a looping backdrop.

| Card | When | Text |
|---|---|---|
| clock | after scenes 1, 3, 5, 7 | the time (`18:05`), then the date (`WED 17 MAR`) |
| count | after scenes 2, 4, 6, before and after the day | `111 DAYS` / `TO ST. PATRICK'S` (`1 DAY` the day before; after the day it counts to next year's) |
| day0, day1 | in the count slots on March 17, taking turns | `HAPPY`, then `ST. PATRICK'S` / `DAY`; `ERIN GO` / `BRAGH`, then `HAPPY` / `ST. PATRICK'S DAY` |

`ERIN GO BRAGH` is an anglicized Irish motto meaning "Ireland forever" (D8).

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview St. Patrick's Day's cards and playlist on any date. Press again to go back. The new cycle starts on a card, so the change shows at once. |
| Back | quit |

## How to change it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` and `PLAYLIST` in `renderer/scenes/__init__.py` | `python3 renderer/build.py`, then review strips |
| Shared art (leprechaun, shamrocks, pot, rainbow) | `renderer/pfx.py` | rebuild and review every scene that uses it |
| Card words, timing or the playlist | `app/shared/stpatricks.ts` (and `DAY_TEXT` in `renderer/scenes/text.py` for review strips) | `tools/check.sh st-patricks-day` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `python3 renderer/build.py`, `python3 tests/text_parity.py` |
| Card backdrops | `renderer/scenes/clock_bg.py`, `count_bg.py`, `day_bg.py` | `python3 renderer/build.py` |

Review the art as LED-style strips (tone-mapped like the bar):

```bash
python3 renderer/review.py all previews/                 # every scene and backdrop, plus every card page
python3 renderer/review.py scene jig previews/ 0.2 9 11  # every 0.2 s between 9 s and 11 s
```

## Install

Download `busybartools.stpatricks-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh st-patricks-day     # build + typecheck + tests (dates, card texts, mockup logic, live-text parity)
tools/deploy.sh st-patricks-day    # install and launch on the bar in .env
tools/release.sh st-patricks-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
