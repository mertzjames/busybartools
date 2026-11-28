# Labor Day

A tribute to working people that opens into the last long weekend of summer, for Labor Day (the first Monday of
September) on the BUSY Bar's 72×16 display. Six scenes play from sunrise to fireworks: three about the work, then
the day off. Between them, live cards show the clock and a countdown to the day, and on the day itself a greeting.

Warm and non-partisan: generic workers in a range of skin tones, plain faces, no real people, and no union or
company logos ([docs/DECISIONS.md](docs/DECISIONS.md) D2).

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Topping Out | 14 s | At sunrise a yellow tower crane lifts the last beam (white, with a flag and an evergreen) into a steel frame; two ironworkers guide it home, one welds it in a shower of sparks |
| 2 | Parade of Trades | 14 s | A nurse, a teacher, a farmer, a builder, a mechanic and a chef march down Main Street, raise their tools in turn and wave as streamers fall |
| 3 | Harvest Time | 14 s | In the golden hour a red tractor pulls a baler across a field, dropping round hay bales; a red barn and a silo on the horizon, swallows overhead |
| 4 | Backyard Cookout | 14 s | Burgers flip on a red kettle grill, friends at a gingham-covered table raise their cups, string lights come on and fireflies blink at dusk |
| 5 | Last Swim of Summer | 14 s | The sun sinks into the sea, waves foam up the sand past an umbrella and a sandcastle; a swimmer runs in, splashes and waves; a gull glides by |
| 6 | Thank You, Workers | 14 s | Fireworks over the finished tower; a crowd of workers in hard hats and caps cheers from below; bunting drops in, then THANK YOU and WORKERS |

The show alternates `scene, clock, scene, count, …` and takes about 2 minutes per loop.

## Cards

| Card | Before the day | On the day |
|---|---|---|
| clock | the time (`18:05`), then the date (`MON 6 SEP`) | same |
| count | `284 DAYS` / `TO LABOR DAY` | `HAPPY` / `LABOR DAY`, then `THANK YOU` / `WORKERS`, `ENJOY` / `THE DAY` or `SO LONG` / `SUMMER` (one per count slot) |

After the day, the countdown counts to next year's. Every card is two lines of the big font, which fill the 16 rows
exactly (D7).

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: preview the on-the-day cards and playlist on any date (press again to go back) |
| Back | quit |

## Install

Download `io.github.mertzjames.laborday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh labor-day     # build + typecheck + tests
tools/deploy.sh labor-day    # install and launch on the bar in .env
tools/release.sh labor-day   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                    # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                     # LED-style strips of every scene and card
python3 renderer/review.py scene steel previews/ 0.2 8 9     # every 0.2 s between 8 s and 9 s
python3 renderer/review.py zoom parade previews/ 0 40 8.4    # big crops of columns 0-40 at 8.4 s
bash tests/check.sh                                          # date logic + live-text parity
```

Open `mockup/index.html` in a browser for the simulator and storyboards (START toggles holiday mode there too).

### How to change it

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py` (shared helpers in `renderer/lfx.py`), then `python3 renderer/build.py` and review strips |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` (update this README and the playlist test) |
| Card words or timings | `app/shared/laborday.ts` and `DAY_TEXT` in `renderer/scenes/text.py` (the parity test checks they agree) |
| Card colors or rows | `LAYOUT` in `renderer/scenes/text.py`, then rebuild |
| Buttons | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
