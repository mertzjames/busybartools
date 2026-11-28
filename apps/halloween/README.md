# Halloween

A spooky-fun, family-friendly Halloween show for the BUSY Bar. Eight scenes play in turn: jack-o'-lanterns carved
and lit one by one, a haunted house on a hill, trick-or-treaters in costume, bats across the moon, a friendly ghost
in a graveyard, a black cat on a fence, a witch on her broom and a skeleton dance. Between them come a clock and a
countdown in nights to October 31. On the night itself, the countdown becomes `HAPPY` / `HALLOWEEN` and phrases such
as `TRICK OR TREAT!` and `BOO!`.

The colors are glowing pumpkin orange, slime green and purple over a deep violet night. All art is original: generic
costumes, no licensed characters (see [docs/DECISIONS.md](docs/DECISIONS.md) D2 and D5).

Open [mockup/index.html](mockup/index.html) in a browser to watch the whole show, cards included, with a holiday-mode
toggle.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Carving Night | 16 s | Four plain pumpkins sit on a porch rail. One at a time, a glinting knife carves each a different face (classic, surprised, winking, goofy) and a candle lights it, until all four glow. A bat flits past. |
| 2 | The Haunted House | 16 s | A crooked house with a tower and a steep gable stands on a hill under a full moon. Lightning strikes in the sky behind it four times: before the windows light, again while they light up one by one (yellow, one green, one purple), again as a shadowy figure glides past the green attic window, and once more, distant, behind the bare tree after the door creaks open and three bats flutter out. |
| 3 | Trick or Treat! | 16 s | A sheet ghost, a little witch, a pumpkin and a caped hero walk up to a house with a jack-o'-lantern on the step. `TRICK OR TREAT!` The door opens, candy flies into each bucket (each kid hops), and they hurry off. |
| 4 | Bats Across the Moon | 14 s | Bats pour out of a bare tree's hollow and stream across a big full moon, a big bat swoops close past it, and three bats circle the moon. |
| 5 | A Friendly Ghost | 15 s | Green mist drifts through a graveyard of cartoon tombstones (one says `RIP`). A ghost rises from behind the big stone, blinks, waves and says `BOO!`; two little ghosts join it, and they float away. |
| 6 | The Black Cat | 14 s | A black cat (violet-grey with a moonlit rim and yellow-green eyes) pads along a fence and stops in front of the moon. A bat flits by: it arches its back and puffs its tail, then sits and slowly blinks. |
| 7 | The Witch's Flight | 14 s | A witch on her broom (green face, violet hat and dress, orange hair) swoops over the rooftops trailing sparkles, crosses the moon, and comes back the other way far off. |
| 8 | Skeleton Dance | 15 s | The finale: spotlights come up on three skeletons dancing to a beat (arm pumps, a can-can ripple, the middle skull hopping off its neck and back), the floor flashes, and Halloween confetti rains down. |

## Cards

Cards are live text drawn by the app from the bar's clock, over a looping backdrop. Both backdrops have cobwebs in
the top corners; the clock card has a flickering candle and a dangling spider, the countdown card two small
jack-o'-lanterns.

| Card | When | Text |
|---|---|---|
| clock | after scenes 1, 3, 5 and 7 | the time (`18:05`), then the date (`SAT 31 OCT`) |
| count | after scenes 2, 4, 6 and 8, before and after the day | `339 NIGHTS` / `TO HALLOWEEN` (`1 NIGHT` the night before; after the day it counts to next year's) |
| day0 … day3 | in the count slots, on October 31 | `HAPPY` / `HALLOWEEN`, then `TRICK OR` / `TREAT!`; `BOO!`; `SPOOKY` / `SEASON`; `HAPPY` / `HAUNTING` |

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview Halloween's cards and playlist on any date. Press again to go back. The new cycle starts on a card, so the change shows at once. |
| Back | quit |

## How to change it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` and `PLAYLIST` in `renderer/scenes/__init__.py` | `python3 renderer/build.py`, then review strips |
| Sprites (bats, house, kids, witch, ghosts, cat) | `renderer/sprites.py`; pumpkins, moon, cobwebs, candles and stones in `renderer/hfx.py` | `python3 renderer/build.py` |
| Card words, timing or the playlist | `app/shared/halloween.ts` (and `DAY_TEXT` in `renderer/scenes/text.py` for review strips) | `tools/check.sh halloween` |
| Card colors or positions | `LAYOUT` in `renderer/scenes/text.py` | `python3 renderer/build.py`, `python3 tests/text_parity.py` |
| Card backdrops | `renderer/scenes/clock_bg.py`, `count_bg.py` | `python3 renderer/build.py` |

Every card line, shadow included, must fit in the 56 px between the backdrops' corner art (columns 8–63, about 11
characters in the `big` font); the tests check it.

Review the art as LED-style strips (tone-mapped like the bar):

```bash
python3 renderer/review.py all previews/                       # every scene and both backdrops, plus every card page
python3 renderer/review.py scene cat previews/ 0.2 5.6 7         # every 0.2 s between 5.6 s and 7 s
python3 renderer/review_zoom.py cat previews/z.png 30 72 6.2     # a big view of columns 30-71 at 6.2 s
```

## Install

Download `io.github.mertzjames.halloween-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh halloween     # build + typecheck + tests (dates, card texts, live-text parity)
tools/deploy.sh halloween    # install and launch on the bar in .env
tools/release.sh halloween   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
