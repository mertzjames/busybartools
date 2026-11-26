# Presidents' Day

Stars, stripes and landmarks for Presidents' Day (the third Monday of February) on the BUSY Bar's 72×16 display.
Seven scenes play from a winter morning to fireworks at night. Between them, live cards show the clock and a
countdown to the day, and on the day itself a greeting.

Light, warm and non-partisan: no faces or likenesses of any president and no official seals. Symbols, objects and
places tell the story ([docs/DECISIONS.md](docs/DECISIONS.md) D2).

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Old Glory | 14 s | On a winter morning the flag goes up its pole and waves; a gust snaps it out. Thirteen stripes, stars as dots |
| 2 | The Cherry Tree | 14 s | A cherry tree in blossom with a hatchet resting on its trunk; a cherry pie cools on a stump, a robin drops in, a gust sends up petals |
| 3 | Eagle over the Mountains | 14 s | A bald eagle flies in, circles over snowy peaks banking into its turns, and climbs away toward the sun |
| 4 | We the People | 14 s | By candlelight a quill writes WE THE PEOPLE on a parchment, adds a flourish, and a plain red wax seal presses down |
| 5 | Monuments at Sunset | 14 s | An obelisk, a columned memorial and a domed hall at sunset over a reflecting pool; lights come on, stars come out |
| 6 | The Log Cabin | 14 s | A log cabin in the snow at dusk; a stovepipe hat stands in the warm doorway, books by the door, a lantern is lit |
| 7 | Fireworks Finale | 14 s | Red, white, blue and gold fireworks over the monuments, bunting drops in, HAPPY PRESIDENTS' DAY and confetti |

The show alternates `scene, clock, scene, count, …` and takes about 2½ minutes per loop.

## Cards

| Card | Before the day | On the day |
|---|---|---|
| clock | the time (`18:05`), then the date (`MON 15 FEB`) | same |
| count | `81 DAYS` / `TO PRESIDENTS' DAY` | `HAPPY` / `PRESIDENTS' DAY`, then `LIBERTY`, `UNION` or `FREEDOM` (one per count slot) |

After the day, the countdown counts to next year's. The holiday's name is too wide for the big font, so it's drawn in
the small one under a big first line (D7).

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: preview the on-the-day cards and playlist on any date (press again to go back) |
| Back | quit |

## Install

Download `busybartools.presidents-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh presidents-day     # build + typecheck + tests
tools/deploy.sh presidents-day    # install and launch on the bar in .env
tools/release.sh presidents-day   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                   # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card
python3 renderer/review.py scene quill previews/ 0.2 8 9    # every 0.2 s between 8 s and 9 s
bash tests/check.sh                                         # date logic + live-text parity
```

Open `mockup/index.html` in a browser for the simulator and storyboards (START toggles holiday mode there too).

### How to change it

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py`, then `python3 renderer/build.py` and review strips |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` (update this README) |
| Card words or timings | `app/shared/presidents.ts` and `DAY_TEXT` in `renderer/scenes/text.py` (the parity test checks they agree) |
| Card colors or rows | `LAYOUT` in `renderer/scenes/text.py`, then rebuild |
| Buttons | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
