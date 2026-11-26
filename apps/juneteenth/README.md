# Juneteenth

A show for the BUSY Bar that opens solemn and becomes joyful, the way Juneteenth is observed. On June 19, 1865,
Union troops arrived in Galveston, Texas, and announced General Order No. 3: the enslaved people there learned they
were free, more than two years after the Emancipation Proclamation. Juneteenth has been a federal holiday since 2021.

Seven pre-rendered scenes play in turn, with a clock card and a countdown to June 19 between them. On the day, the
countdown becomes `JUNETEENTH` and `FREEDOM DAY`.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Dawn over Galveston Bay | 14 s | The night lightens over the bay; a lighthouse sweeps its beam, a sailing ship drifts across, gulls cross and the sun's rim rises |
| 2 | The News Arrives | 16 s | A rider gallops into town and posts a notice; people gather and raise their arms; then `JUNE 19, 1865` / `GALVESTON TEXAS` |
| 3 | The Juneteenth Flag | 14 s | The flag (a white star in a nova, blue over red, split by an arc) goes up and waves; people cheer and wave small flags |
| 4 | Family Cookout | 16 s | A shade tree, bunting, a grill with smoke, a picnic table; family arrives with a dish, kids play catch, everyone lifts a red cup |
| 5 | Red Drinks and Red Foods | 14 s | Strawberry soda poured, a watermelon cut into wedges, red velvet cake, strawberries; then `RED FOR` / `RESILIENCE` |
| 6 | Music in the Park | 14 s | A band under string lights at sunset (drums, saxophone, bass), notes floating up, neighbors dancing on the beat |
| 7 | Freedom Day Fireworks | 16 s | Red, white, blue and gold fireworks over the bay, a crowd seen from behind, `HAPPY` / `JUNETEENTH`, then `FREEDOM DAY` |

No likenesses of real people and no images of suffering: the solemn part is about dawn, news and hope. People are
simple faceless figures with a range of warm skin tones. All art is original.

## Cards

Between the scenes, alternating:

| Card | Text |
|---|---|
| Clock | the time (`18:05`), then the date (`THU 26 NOV`) |
| Countdown, before and after June 19 | `205 DAYS` / `TO JUNETEENTH` (`1 DAY` the day before; after the day it counts to next year's) |
| On June 19 (two cards, taking turns) | `JUNETEENTH`, then `FREEDOM DAY` / `JUNE 19`; `HAPPY` / `JUNETEENTH`, then `CELEBRATE` / `FREEDOM` |

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next or previous step |
| START | holiday mode: preview the June 19 cards and playlist on any date (press again to go back) |
| Back | quit |

## Install

Download `busybartools.juneteenth-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh juneteenth     # render, typecheck, build and run the tests
tools/deploy.sh juneteenth    # install and launch on the bar in .env
tools/release.sh juneteenth   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                                   # render everything (+ GIF previews in previews/)
python3 renderer/review.py all previews/                    # LED-style strips of every scene and the cards
python3 renderer/review.py scene news previews/ 0.2 4 7     # every 0.2 s between 4 s and 7 s
python3 renderer/review.py zoom flag previews/ 3,6 0 40     # close-ups of columns 0-40
open mockup/index.html                                      # the simulator and storyboards
```

## How to change it

| Change | Where |
|---|---|
| A scene | `renderer/scenes/<name>.py`, registered in `PLAYLIST` (`renderer/scenes/__init__.py`) |
| The flag | `NOVA_11`, `flag_cell` and `draw_flag` in `renderer/jfx.py` |
| Card words or timing | `app/shared/juneteenth.ts` (and `DAY_TEXT` in `renderer/scenes/text.py`, which the tests compare) |
| Card colors | `LAYOUT` in `renderer/scenes/text.py` |
| Words in the scenes | the constants in `renderer/scenes/text.py` |
| Buttons | `app/src/main.ts` |

Generated files (`app/src/animations/*.anim`, `app/shared/generated/show.ts`, the icons, `mockup/index.html`) come
from `renderer/build.py`: change the generator, rebuild and commit them.

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
