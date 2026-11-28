# Easter

A springtime Easter show for the BUSY Bar. Seven cheerful scenes play in turn: a bunny hiding eggs in a sunny
garden, two kids on an egg hunt, chicks hatching, eggs being painted, spring flowers opening, an Easter basket, and
an Easter sunrise. Between them come a clock and a countdown to Easter Sunday. On the day itself, the countdown
becomes `HAPPY` / `EASTER` and a cheerful extra page.

Easter here is Western Easter Sunday, which moves every year between March 22 and April 25 (Mar 28, 2027; Apr 16,
2028; Apr 1, 2029). The date comes from the kit's computus (`HOLIDAYS.easter`), so it never needs updating.

Open [mockup/index.html](mockup/index.html) in a browser to watch the whole show, cards included, with a holiday-mode
toggle.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | The Bunny's Garden | 16 s | On a sunny morning the bunny hops in, stops three times to sniff the grass and leave a decorated egg behind it (by a bush, among the tulips, by a bush), then hops away; the hidden eggs twinkle. |
| 2 | The Egg Hunt | 16 s | Two kids walk through the garden. One finds the eggs peeking out from the bushes and the tulips and tosses each into the other's basket, which fills up egg by egg. Four found: they jump and cheer. |
| 3 | Chicks Hatching | 15 s | Three pastel eggs in a straw nest wobble, crack along a zigzag and pop their tops one by one; a fluffy chick pokes out of each, and at the end all three cheep together. |
| 4 | Painting Eggs | 16 s | Three white eggs in egg cups. The brush dips into a paint pot, sweeps each egg in a pastel, then paints its pattern: a pink zigzag, blue dots, yellow stripes. |
| 5 | Spring Flowers | 15 s | Shoots push up across a bare, sunny garden bed and open into tulips and daffodils; two butterflies flutter in and one settles on a tulip. |
| 6 | The Easter Basket | 14 s | Decorated eggs drop into a wicker basket lined with paper grass, a chocolate bunny pops up in the middle, a pink bow lands on the handle, and the basket glitters. |
| 7 | Easter Sunrise | 16 s | The finale: a violet dawn warms into a spring morning as the sun rises between the hills, Easter lilies and daffodils open, and `HAPPY EASTER` is spelled out across the sky. |

## Cards

Cards are live text drawn by the app from the bar's clock, over a looping backdrop.

| Card | When | Text | Backdrop |
|---|---|---|---|
| clock | after scenes 1, 3, 5, 7 | the time (`18:05`), then the date (`SUN 28 MAR`) | a spring evening: soft stars, grass, two tiny eggs |
| count | after scenes 2, 4, 6, before and after the day | `122 DAYS` / `TO EASTER` (`1 DAY` the day before; after the day it counts to next year's) | two big decorated eggs with a sliding glint |
| day0, day1, day2 | in the count slots, on Easter Sunday | `HAPPY` / `EASTER`, then `EGG HUNT` / `TIME!`; `HAPPY` / `EASTER`, then `HOPPY` / `EASTER!`; `HAPPY` / `EASTER`, then `SPRING IS` / `HERE!` | pastel confetti drifting down both edges |

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview Easter Sunday's cards and playlist on any date. Press again to go back. The new cycle starts on a card, so the change shows at once. |
| Back | quit |

## How to change it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` and `PLAYLIST` in `renderer/scenes/__init__.py` | `python3 renderer/build.py`, then review strips |
| Props (eggs, flowers, kids, basket) or sprites (bunny, chick) | `renderer/efx.py`, `renderer/sprites.py` | rebuild and review every scene that uses them |
| Card words, timing or the playlist | `app/shared/easter.ts` (and `DAY_TEXT` in `renderer/scenes/text.py` for review strips) | `tools/check.sh easter` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `python3 renderer/build.py`, `python3 tests/text_parity.py` |
| Card backdrops | `renderer/scenes/clock_bg.py`, `count_bg.py`, `day_bg.py` (each declares the free `TEXT_GAP` its text must fit) | `python3 renderer/build.py`, `python3 tests/text_parity.py` |

Review the art as LED-style strips (tone-mapped like the bar):

```bash
python3 renderer/review.py all previews/                        # every scene and backdrop, plus every card page
python3 renderer/review.py scene hatching previews/ 0.2 1.4 3.2 # every 0.2 s between 1.4 s and 3.2 s
```

## Install

Download `io.github.mertzjames.easter-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh easter     # build + typecheck + tests (dates, card texts, mockup logic, live-text parity)
tools/deploy.sh easter    # install and launch on the bar in .env
tools/release.sh easter   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
