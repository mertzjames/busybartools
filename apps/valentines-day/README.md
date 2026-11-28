# Valentine's Day

A sweet, family-friendly Valentine's show for the BUSY Bar. Seven scenes play in turn: rising hearts, a little
cherub whose arrow turns into a heart, a winged love letter, two lovebirds on a wire, a box of chocolates opened one
piece at a time, a rose in bloom, and a candy-heart finale with heart fireworks. Between them come a clock and a
countdown to February 14. On the day itself, the countdown becomes `HAPPY` / `VALENTINE'S DAY` and candy-heart
phrases such as `BE MINE` and `XOXO`.

The colors are reds, pinks and warm whites with gold accents, over deep plum so the pinks stay bright. All art is
original (see [docs/DECISIONS.md](docs/DECISIONS.md) D2 and D5).

Open [mockup/index.html](mockup/index.html) in a browser to watch the whole show, cards included, with a holiday-mode
toggle.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Hearts Afloat | 14 s | Hearts of every pink and red rise and sway through a plum night until one grows in the middle into a big heart that beats, ringed by gold twinkles. |
| 2 | Cupid's Arrow | 15 s | A winged cherub with gold curls flutters in, draws its bow and lets fly. The heart-tipped arrow streaks across the sky and bursts into a big beating heart; the cherub flutters away. |
| 3 | Special Delivery | 14 s | A love letter with little wings flutters across the evening sky and lands. The heart seal pops, the flap opens, a letter rises with a red heart, and `FOR YOU` appears. |
| 4 | Lovebirds | 14 s | A rosy bird and a golden bird land on a wire over the rooftops at dusk and hop closer until their beaks meet and a heart pops up above them. |
| 5 | A Box of Chocolates | 14 s | A red box tied with a gold ribbon opens on twelve chocolates in gold cups. They are picked one at a time until a single heart-shaped chocolate is left. |
| 6 | A Rose Blooms | 14 s | A stem grows, puts out leaves and a bud, and the bud opens into a red rose. Two smaller roses open beside it, and petals drift down. |
| 7 | Candy Hearts | 16 s | The finale: pastel candy hearts tumble down and stack up at both ends, `BE MINE` and then `XOXO` stamp in between them, and heart-shaped fireworks end the show. |

## Cards

Cards are live text drawn by the app from the bar's clock, over a looping backdrop. The countdown and day cards sit
between two pastel candy hearts.

| Card | When | Text |
|---|---|---|
| clock | after scenes 1, 3, 5 and 7 | the time (`18:05`), then the date (`SUN 14 FEB`) |
| count | after scenes 2, 4 and 6, before and after the day | `80 DAYS` / `TO VALENTINE'S DAY` (`1 DAY` the day before; after the day it counts to next year's) |
| day0, day1, day2 | in the count slots, on February 14 | `HAPPY` / `VALENTINE'S DAY`, then two candy phrases: `BE MINE`, `XOXO`; `HUG ME`, `LOVE YOU`; `BE TRUE`, `SO SWEET` |

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview Valentine's Day's cards and playlist on any date. Press again to go back. The new cycle starts on a card, so the change shows at once. |
| Back | quit |

## How to change it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` and `PLAYLIST` in `renderer/scenes/__init__.py` | `python3 renderer/build.py`, then review strips |
| Sprites (cherub, birds, rose) | `renderer/sprites.py`; hearts and effects in `renderer/vfx.py` | `python3 renderer/build.py` |
| Card words, timing or the playlist | `app/shared/valentine.ts` (and `DAY_TEXT` in `renderer/scenes/text.py` for review strips) | `tools/check.sh valentines-day` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `python3 renderer/build.py`, `python3 tests/text_parity.py` |
| Card backdrops | `renderer/scenes/clock_bg.py`, `count_bg.py` | `python3 renderer/build.py` |

Candy phrases must be at most 47 px wide in the `big` font (about 8 characters), so they fit between the candy
hearts; the tests check it.

Review the art as LED-style strips (tone-mapped like the bar):

```bash
python3 renderer/review.py all previews/                     # every scene and both backdrops, plus every card page
python3 renderer/review.py scene cupid previews/ 0.2 5 7       # every 0.2 s between 5 s and 7 s
python3 renderer/review_zoom.py cupid previews/z.png 0 36 4.6  # a big view of columns 0-35 at 4.6 s
```

## Install

Download `io.github.mertzjames.valentines-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh valentines-day     # build + typecheck + tests (dates, card texts, live-text parity)
tools/deploy.sh valentines-day    # install and launch on the bar in .env
tools/release.sh valentines-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
