# Father's Day

A summer day with Dad on the BUSY Bar's 72×16 display, for Father's Day (the third Sunday of June). Seven scenes play
from sunrise to fireworks. Between them, live cards show the clock and a countdown to the day, and on the day itself
a greeting.

Warm, lighthearted and for everyone: dads, granddads and father figures with a range of skin tones and hair, and
gentle humor that doesn't put anyone down ([docs/DECISIONS.md](docs/DECISIONS.md) D2).

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Fishing at Dawn | 14 s | A parent and child on the end of a dock at sunrise; the bobber dips, a little sunfish comes up, gets a cheer, and is let go with a splash |
| 2 | Playing Catch | 14 s | A yellow ball goes back and forth across a mowed lawn: a big lob, a bouncer, a high one the child backs up to catch, and a cheer |
| 3 | The First Ride | 14 s | A parent tightens a wobbly bike wheel with a wrench, gives it a spin, then jogs alongside holding the seat and lets go |
| 4 | Backyard Grill | 14 s | Burgers on a red kettle grill with smoke rising; three flips, a showy high flip, then onto a bun with cheese and the top bun |
| 5 | The Wild Tie | 14 s | A present tagged DAD shakes, unties and pops open; a necktie springs out, TA-DA!, and keeps changing its pattern |
| 6 | Hammock Nap | 14 s | A granddad naps under a straw hat at sunset; Z's drift up, the hammock sways, a leaf lands on his belly, a snort |
| 7 | Fireworks for Dad | 14 s | Summer-night fireworks; HAPPY / FATHER'S DAY, then a gold trophy rises beside #1 DAD with confetti |

The show alternates `scene, clock, scene, count, …` and takes about 2½ minutes per loop.

## Cards

| Card | Before the day | On the day |
|---|---|---|
| clock | the time (`18:05`), then the date (`SUN 20 JUN`) | same |
| count | `206 DAYS` / `TO FATHER'S DAY` | `HAPPY` / `FATHER'S DAY`, then `BEST DAD` / `EVER`, `THANKS DAD` or `REEL COOL` / `DAD` (one per count slot) |

After the day, the countdown counts to next year's. `FATHER'S DAY` fits the big font, so the greeting is two big
lines; under the countdown it goes in the small font (D7).

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: preview the on-the-day cards and playlist on any date (press again to go back) |
| Back | quit |

## Install

Download `io.github.mertzjames.fathersday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh fathers-day     # build + typecheck + tests
tools/deploy.sh fathers-day    # install and launch on the bar in .env
tools/release.sh fathers-day   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                   # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                    # LED-style strips of every scene and card
python3 renderer/review.py grid grill previews/ 0.5         # a labeled grid every 0.5 s (fine timing)
python3 renderer/review_zoom.py bike previews/z.png 14 52 1,2.4,4.6   # zoom on columns 14-52 at those times
bash tests/check.sh                                         # date logic + live-text parity
```

Open `mockup/index.html` in a browser for the simulator and storyboards (START toggles holiday mode there too).

### How to change it

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py`, then `python3 renderer/build.py` and review strips |
| The people (skin, hair, poses) | `ffx.figure()` in `renderer/ffx.py` and the palette there |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` (update this README) |
| Card words or timings | `app/shared/fathers.ts` and `DAY_TEXT` in `renderer/scenes/text.py` (the parity test checks they agree) |
| Card colors or rows | `LAYOUT` in `renderer/scenes/text.py`, then rebuild |
| Buttons | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
