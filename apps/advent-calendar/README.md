# Advent Calendar

A unique animation for every day of Advent, with a countdown to Christmas.

Every loop, a door on the calendar swings open onto the date (`DEC 7`), that day's vignette plays, and a card
counts down to Christmas from the bar's own clock (`18 DAYS` / `TO CHRISTMAS`). On Christmas Eve the card counts
hours and minutes to midnight (`06:42` / `TO GO`). On Christmas Day the finale plays, followed by `MERRY` /
`CHRISTMAS`. Turn the encoder to revisit any door you have already opened.

- 25 original vignettes, Dec 1 to the Dec 25 finale, that grow busier toward Christmas
- 72×16 full-screen animations at 15 fps, played by the firmware (1.6 MB of `.anim` data)
- All dates and countdowns are drawn live from the bar's local time, in the collection's pixel fonts
- A browser mockup with a date slider: [mockup/index.html](mockup/index.html)

## The loop

| Step | Length | What you see |
|---|---|---|
| Door | 3 s | A wrapped door opens onto a starry night, and the date appears in it (`DEC 7`) |
| Vignette | 8 s (Dec 24: 9 s, Dec 25: 10 s) | That day's animation |
| Countdown card | 5.5 s | Two lines of live text over holly and snow |

| Bar date | Door | Vignette | Card |
|---|---|---|---|
| Jan 1 – Nov 30 | none | Winter Night | `N DAYS` / `TO ADVENT` |
| Dec 1 – Dec 23 | `DEC N` | day N | `N DAYS` / `TO CHRISTMAS` |
| Dec 24 | `DEC 24` | The Star | `HH:MM` / `TO GO` (time left until midnight, updated each minute) |
| Dec 25 | `DEC 25` | Christmas Morning | `MERRY` / `CHRISTMAS` |
| Dec 26 – Dec 31 | none | Christmas Morning | `SEE YOU` / `NEXT YEAR!` |

## Behind every door

| Day | Vignette | What happens |
|---|---|---|
| 1 | First Snow | A big snowflake crystal drifts down and sparkles, then the first snow whitens the hills |
| 2 | Mittens | A pair of knitted mittens swing on a yarn line; a gust sends them flying sideways |
| 3 | Hot Cocoa | Marshmallows plop into a steaming mug by a frosty window; the steam curls into a heart |
| 4 | Candy Cane | A giant candy cane swings in, its stripes spin like a barber pole, peppermints roll by |
| 5 | Jingle Bells | Two golden bells under a bow swing together and ring out in sparkles |
| 6 | Ornaments | Three glass baubles sway on a pine bough as a glint runs across each |
| 7 | Advent Candles | Four candles on an evergreen wreath light one by one, and the room warms |
| 8 | Penguin | A penguin waddles onto the ice, belly-slides across, and flaps happily |
| 9 | Gingerbread | Two gingerbread friends run in, leap for a high-five, and dance in falling sprinkles |
| 10 | Cookies and Milk | Cookies land on a plate, milk pours, and a note slides up: `FOR SANTA` |
| 11 | Polar Bear | A polar bear pads across the ice under the northern lights and looks up at a shooting star |
| 12 | Wreath | A wreath on a red front door; its lights switch on, chase around and twinkle |
| 13 | Stockings | Stockings by a crackling fire; a candy cane, a teddy and a star pop into them |
| 14 | Snowman | A snowball rolls in and grows, the head drops on, then a hat, a carrot nose, and a wave |
| 15 | Toy Soldier | A wind-up toy drummer marches in, beats a drum roll, salutes and marches on |
| 16 | Sledding | A kid on a red sled races down a moonlit hill and flies off two bumps |
| 17 | Carolers | Three carolers sing under a street lamp as music notes float into the snow |
| 18 | Nutcracker | A wooden nutcracker cracks two walnuts, then grins proudly |
| 19 | Presents | Wrapped gifts tumble into a wobbly pile, then confetti bursts |
| 20 | Reindeer | A reindeer prances across a moonlit field, takes a run-up and lifts off |
| 21 | North Pole | Under a purple-green aurora, the letters on a candy-striped signpost light up: `NORTH POLE` |
| 22 | The Tree | A bare tree gets its lights, ornaments and tinsel, then everything twinkles |
| 23 | Sleigh Ride | A sleigh and two reindeer swoop across a huge moon over sleeping rooftops |
| 24 | The Star | On Christmas Eve a star spirals up and lands on top of the tree |
| 25 | Christmas Morning | The finale: the tree glows over presents, the sleigh flies past, stardust fireworks burst, `HO HO HO!` |
| – | Winter Night | Before Advent: a cabin among snowy pines, chimney smoke and falling snow |

## Controls

| Control | Action |
|---|---|
| Encoder | Browse the doors already opened (1 to today; all 25 after Christmas). Turning back onto today follows today again |
| OK | Back to today |
| Back (short press) | Quit |

## Install

Download `busybartools.advent-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md). The calendar follows the bar's own date and time, so set the bar's
clock and time zone first.

## Develop

```bash
tools/check.sh advent-calendar      # render, typecheck, build, and run tests/check.sh
tools/deploy.sh advent-calendar     # install and launch on the bar in .env
```

From this folder:

```bash
python3 renderer/build.py                         # render every scene (~5 s), write show.ts, icons and the mockup
python3 renderer/review.py scene day07            # LED-style keyframe strip -> previews/review_day07.png
python3 renderer/review.py all                    # strips for every scene
python3 renderer/review.py cards                  # the door and every countdown card with live text
node --experimental-strip-types --test tests/advent.test.mts   # logic tests (Node 24)
python3 tests/text_parity.py                      # app text bitmaps == renderer text, pixel for pixel
```

| Path | What it is |
|---|---|
| `renderer/scenes/dayNN_*.py` | One vignette per day (`NAME = "dayNN"`) |
| `renderer/scenes/door.py`, `card_bg.py`, `winter.py` | The intro, the countdown backdrop, the out-of-season scene |
| `renderer/scenes/text.py` | Live-text styles (font, row, colors) shared by the app, mockup and tests |
| `renderer/common.py`, `renderer/props.py` | App-local helpers: snow, ground, pines, aurora; the tree, star, sleigh and gifts |
| `app/shared/advent.ts` | Pure logic: seasons, countdown text, the show sequence, browsing |
| `app/src/main.ts` | Plays the show on the bar |
| `mockup/template.html` | The mockup; its `<logic>` block mirrors `advent.ts` and is tested against it |

To preview a date in the mockup, use its slider or open `mockup/index.html?date=12-24&time=17:18`.

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
