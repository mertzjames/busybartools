# Independence Day

The Fourth of July on the BUSY Bar's 72×16 display. Seven scenes follow the day from a morning parade to fireworks
at night. Between them, live cards show the clock and a countdown to July 4th, and on the day itself the hours and
minutes until the fireworks at dusk.

Festive, family-friendly and non-partisan: no likenesses of real people and no official seals
([docs/DECISIONS.md](docs/DECISIONS.md) D2).

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Hometown Parade | 15 s | Down Main Street march a drum major twirling a baton, trumpets, a snare drum and a sousaphone, then a float with a gold star; kids wave little flags |
| 2 | The Liberty Bell | 14 s | A bronze bell, its crack running up from the lip, swings on its yoke; rings of sound spread out, then LIBERTY |
| 3 | Backyard Cookout | 14 s | Burgers and hot dogs on a red kettle grill, a burger flipped; watermelon and lemonade on a checked tablecloth, and a kid dashes off with a slice |
| 4 | Eagle and Flag | 14 s | The flag waves in a summer breeze (13 stripes, a dense checker of stars) as a bald eagle glides in, circles and climbs away |
| 5 | Sparklers at Dusk | 14 s | Three kids swing sparklers in loops and figure eights; the middle one writes USA in the air |
| 6 | Fireworks over the City | 16 s | Red, white, blue and gold bursts over a skyline on the river, then a dozen-shell finale volley and crackling gold |
| 7 | Happy 4th! | 14 s | Red, white and blue volleys, a big gold ring that spells out HAPPY 4TH OF JULY, confetti and glitter |

The show alternates `scene, clock, scene, count, …` and takes about 2½ minutes per loop.

## Cards

| Card | Before the Fourth | On the Fourth, before 21:00 | From 21:00 on the Fourth |
|---|---|---|---|
| clock | the time (`18:05`), then the date (`THU 26 NOV`) | same | same |
| count | `220 DAYS` / `TO JULY 4TH` | `HAPPY` / `4TH OF JULY`, then `FIREWORKS IN` / `02:15` | `HAPPY` / `4TH OF JULY`, then `ENJOY THE` / `FIREWORKS!` |

The fireworks countdown is hours and minutes until dusk, taken as 21:00 on the bar's clock and rounded up to the
minute (`00:01` in the last minute). It steps down as each minute rolls over. From July 5 the countdown counts to next
year's Fourth.

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | cycle: holiday mode (the Fourth's cards and playlist on any date) → dusk demo (the cards jump to 20:58 on the Fourth, so the countdown runs out within two minutes) → normal |
| Back | quit |

## Install

Download `io.github.mertzjames.july4-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh independence-day     # build + typecheck + tests
tools/deploy.sh independence-day    # install and launch on the bar in .env
tools/release.sh independence-day   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                         # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                          # LED-style strips of every scene and card
python3 renderer/review.py scene liberty_bell previews/ 0.2 4 6   # every 0.2 s between 4 s and 6 s
python3 renderer/review_zoom.py parade previews/zoom.png 0 40 5,10  # zoomed columns 0-40 at 5 s and 10 s
bash tests/check.sh                                               # date logic + live-text parity
```

Open `mockup/index.html` in a browser for the simulator and storyboards (START cycles the modes there too).

### How to change it

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py`, then `python3 renderer/build.py` and review strips |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` (update this README) |
| Dusk (the fireworks hour) | `DUSK_HOUR`, `DUSK_MINUTE` in `app/shared/july4.ts` (and the tests) |
| Card words or timings | `app/shared/july4.ts`, and `SAMPLE_PAGES` in `renderer/scenes/text.py` (the parity test checks they agree) |
| Card colors or rows | `LAYOUT` in `renderer/scenes/text.py`, then rebuild |
| Buttons and modes | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
