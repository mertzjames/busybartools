# MLK Day

A quiet tribute for Martin Luther King Jr. Day (the third Monday of January) for the BUSY Bar. Slow scenes of
dawn play in turn: a march of people of every age, a dove over the city, joined hands, ringing bells, a day of
service, and dawn on a mountaintop. Between them come a clock and a countdown to MLK Day. On the day itself, the
countdown becomes `MLK DAY` and a word.

There are no likenesses of real people and no quotations (see [docs/DECISIONS.md](docs/DECISIONS.md) D2). Figures
are small and faceless, the colors are deep blues and dawn golds, and each scene ends with a single word.

Open [mockup/index.html](mockup/index.html) in a browser to watch the whole show, cards included, with a holiday-mode
toggle.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | The March at Dawn | 16 s | A long line of people of every age and skin tone walks toward the sunrise: families hand in hand, a child on a parent's shoulders, an elder with a cane. `TOGETHER` |
| 2 | A Dove over the City | 14 s | A white dove with an olive sprig crosses a sleeping city as its windows go dark, circles back and settles on a rooftop. `PEACE` |
| 3 | Many Hands | 15 s | People seen from behind, facing the dawn, raise their arms one by one and join hands; a warm light runs along the chain. `UNITY` |
| 4 | Freedom Bells | 15 s | Three bells in a stone frame begin to ring at first light; rings of sound spread and a flock of birds lifts off. `FREEDOM` |
| 5 | A Day of Service | 18 s | Neighbors plant a tree, volunteers fill a crate at a food drive, and two painters roll out a community mural that reads `SERVICE`. |
| 6 | Dawn on the Mountaintop | 16 s | The closing scene: the sun rises behind the highest peak and its light runs down the ridges. `DREAM` |

## Cards

Cards are live text drawn by the app from the bar's clock, over a looping backdrop.

| Card | When | Text |
|---|---|---|
| clock | after scenes 1, 3, 5 | the time (`18:05`), then the date (`MON 18 JAN`) |
| count | after scenes 2, 4, 6, before and after the day | `53 DAYS` / `TO MLK DAY` (`1 DAY` the day before; after the day it counts to next year's) |
| day0, day1, day2 | in the count slots, on MLK Day | `MLK DAY`, then `DREAM`; `MLK DAY`, then `EQUALITY`; `MLK DAY`, then `SERVICE`, then `A DAY ON` / `NOT A DAY OFF` |

`A DAY ON, NOT A DAY OFF` is the motto of the MLK Day of Service.

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview MLK Day's cards and playlist on any date. Press again to go back. The new cycle starts on a card, so the change shows at once. |
| Back | quit |

## How to change it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` and `PLAYLIST` in `renderer/scenes/__init__.py` | `python3 renderer/build.py`, then review strips |
| Card words, timing or the playlist | `app/shared/mlk.ts` (and `DAY_TEXT` in `renderer/scenes/text.py` for review strips) | `tools/check.sh mlk-day` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `python3 renderer/build.py`, `python3 tests/text_parity.py` |
| Card backdrops | `renderer/scenes/clock_bg.py`, `count_bg.py` | `python3 renderer/build.py` |

Review the art as LED-style strips (tone-mapped like the bar):

```bash
python3 renderer/review.py all previews/                  # every scene and both backdrops, plus every card page
python3 renderer/review.py scene march previews/ 0.2 9 11  # every 0.2 s between 9 s and 11 s
```

## Install

Download `io.github.mertzjames.mlkday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh mlk-day     # build + typecheck + tests (dates, card texts, live-text parity)
tools/deploy.sh mlk-day    # install and launch on the bar in .env
tools/release.sh mlk-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
