# Mother's Day

Flowers, hugs and breakfast in bed for Mother's Day (the second Sunday of May) on the BUSY Bar's 72×16 display.
Seven warm scenes play in turn. Between them, live cards show the clock and a countdown to the day, and on the day
itself a greeting and a few sweet words.

Moms come in many forms, so the figures are generic: plain faces, a range of skin tones and hair, a mom, a
grandmother, a parent and child ([docs/DECISIONS.md](docs/DECISIONS.md) D2).

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | A Bouquet for Mom | 14 s | Tulips, roses, daisies and lavender swing in stem by stem from both sides and gather into a bunch; a paper wrap rises and a red ribbon bow ties it |
| 2 | Breakfast in Bed | 15 s | A child carries a tray (pancakes with butter and syrup, orange juice, a tulip in a vase) into a sunny bedroom and slides it onto Mom's lap; she lifts her arms and hearts float up |
| 3 | Growing Together | 16 s | A parent and child work along a garden bed: seeds, a watering can, and sprouts that shoot up behind them and open into flowers; a butterfly visits |
| 4 | A Handmade Card | 12 s | A crayon card on a wooden table among crayons slides over and opens like a book: a big red heart and MOM; the heart beats |
| 5 | A Hug Under the Blossoms | 15 s | A cherry tree blooms at dusk while a child runs in and a grandmother walks in; they meet in a hug, a heart rises and petals drift over them |
| 6 | Tea in the Sunny Window | 12 s | A teacup steams on a sunny windowsill by a geranium and tulips; clouds drift, a butterfly visits, and the steam curls into a heart |
| 7 | Happy Mother's Day | 14 s | A border of flowers blooms, hearts float up, HAPPY, then MOTHER'S DAY with a shower of petals |

The show alternates `scene, clock, scene, count, …` and takes about 2½ minutes per loop.

## Cards

| Card | Before the day | On the day |
|---|---|---|
| clock | the time (`18:05`), then the date (`SUN 9 MAY`) | same |
| count | `164 DAYS` / `TO MOTHER'S DAY` | `HAPPY` / `MOTHER'S DAY`, then `LOVE YOU MOM`, `THANK YOU` / `FOR ALL YOU DO` or `BIG HUGS` / `TODAY AND ALWAYS` (one per count slot) |

After the day, the countdown counts to next year's. `MOTHER'S DAY` fits the big font only edge to edge, so the cards
draw it in the small one under a big first line (D7).

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: preview the on-the-day cards and playlist on any date (press again to go back) |
| Back | quit |

## Install

Download `io.github.mertzjames.mothersday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh mothers-day     # build + typecheck + tests
tools/deploy.sh mothers-day    # install and launch on the bar in .env
tools/release.sh mothers-day   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                     # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                      # LED-style strips of every scene and card
python3 renderer/review.py scene card previews/ 0.2 3 5       # every 0.2 s between 3 s and 5 s
python3 renderer/review_zoom.py hug previews/zoom.png 10 50 6,8.5   # zoomed columns 10-49 at 6 s and 8.5 s
bash tests/check.sh                                           # date logic + live-text parity
```

Open `mockup/index.html` in a browser for the simulator and storyboards (START toggles holiday mode there too).

### How to change it

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py`, then `python3 renderer/build.py` and review strips |
| Shared art (palette, flowers, hearts, figures) | `renderer/mfx.py` |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` (update this README) |
| Card words or timings | `app/shared/mothersday.ts` and `DAY_TEXT` in `renderer/scenes/text.py` (the parity test checks they agree) |
| Card colors or rows | `LAYOUT` in `renderer/scenes/text.py`, then rebuild |
| Buttons | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
