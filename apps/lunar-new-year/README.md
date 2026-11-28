# Lunar New Year

Festival scenes for the BUSY Bar: red lanterns, a dragon dance, a lion dance, red envelopes, dumplings,
firecrackers and fireworks, plus the zodiac animal of the year. A clock card and a countdown card play between
scenes. Before the new year, the countdown card counts the days. From New Year's Day through the Lantern Festival
(the 15th day), it shows `YEAR OF THE` / `GOAT` and the greetings, and the fireworks finale joins the loop as a
festival-only treat.

Open [`mockup/index.html`](mockup/index.html) in a browser to watch the show in an LED simulator. You can pick any
date there and try holiday mode.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Red Lanterns Rising | 12 s | Sky lanterns drift up from behind curled rooftops under a full moon. Then three red palace lanterns are lowered into the sky. |
| 2 | Dragon Dance | 16 s | A long red-and-gold dragon on poles chases a pearl down a lantern-lit street. Every hoop has its own dancer, and a big wave runs down its back. |
| 3 | Lion Dance | 14 s | A two-dancer lion prances in to a drum, blinks and shakes, rears up to pluck the greens and a red envelope, scatters lettuce for luck, and bows. |
| 4 | Red Envelopes | 12 s | A child bows to a grandparent and gets a red envelope, jumps for joy, and envelopes and gold coins shower down. |
| 5 | Dumplings Steaming | 12 s | The steamer lid lifts in a cloud of steam. Chopsticks dip a dumpling in sauce, then lift another, and out pops the lucky coin. |
| 6 | Firecrackers | 12 s | The Nian sneaks up the street and flees when the fuse is lit. The string pops end to end, leaving a carpet of red paper. The Nian peeks back in and ducks away. |
| 7 | Fireworks Finale | 15 s | Red and gold fireworks over a pagoda and rooftops build to a volley. Then `HAPPY` / `NEW YEAR` shines in gold. **Plays only during the festival** (and in holiday mode). |
| Z | Year of the … | 6 s | One per zodiac animal: Rat, Ox, Tiger, Rabbit, Dragon, Snake, Horse, Goat, Monkey, Rooster, Dog, Pig. The animal arrives and does its own move, and `YEAR OF THE` / `<ANIMAL>` wipes in. The app plays the animal of the current or upcoming lunar year. |

## Cards

Each card plays live text over a looping backdrop: a wine-red wall with two glowing lanterns and plum blossoms.

| When | Count card |
|---|---|
| Before New Year's Day | `72 DAYS` / `TO LUNAR NEW YEAR` (`1 DAY` the day before) |
| New Year's Day to day 14 | `YEAR OF THE` / `GOAT`, then `HAPPY` / `NEW YEAR`, then the wish in the chosen language (see Settings) |
| Day 15 (the Lantern Festival) | `YEAR OF THE` / `GOAT`, then `LANTERN` / `FESTIVAL`, then the wish |
| Outside the date table (2036 onward) | `HAPPY` / `NEW YEAR` only, with no countdown |

The **clock card** shows the bar's local time (24-hour `HH:MM`), then the date (`SAT 6 FEB`).

The animal comes from the kit's zodiac (`2027 = GOAT`). In January, before the new year, it's the upcoming
year's animal. Dates come from the shared kit's Lunar New Year table (`lib/ts/busybar/holidays.ts`, 2025–2036).

**Playlists.**
- **Before the holiday** (and outside the date table): Lanterns, clock, the zodiac scene, count, Dragon Dance,
  clock, Red Envelopes, count, Lion Dance, clock, Dumplings, count, Firecrackers, count. About 2 m 15 s; no finale.
- **During the festival:** the zodiac scene and the greeting card open the loop, then all seven scenes, the
  Fireworks Finale included, alternating with the clock and count cards. About 2 m 55 s.

## Settings

On the bar: **Apps → Lunar New Year → Setup**. Changes apply the next time the app starts.

| Setting | Options | Default |
|---|---|---|
| Greeting | the festival's wish page: **Mandarin** `GONG XI` / `FA CAI`, **Cantonese** `GUNG HEI` / `FAT CHOI`, **Vietnamese** `CHUC MUNG` / `NAM MOI`, **Korean** `SAEHAE BOK` / `MANI BADEUSEYO`, or **None** (no wish page) | Mandarin |

The romanizations are written without diacritics because the bar's fonts are ASCII. If the settings can't be read,
the app uses the default.

## Controls

| Button | Action |
|---|---|
| OK | Next step |
| Encoder | Next or previous step |
| START | Holiday mode: the festival playlist and cards on any date. Each further press steps to the next zodiac animal (Goat, Monkey, Rooster, …). After all twelve, the next press returns to the real date. |
| Back | Quit |

## How to change it

Run these from `apps/lunar-new-year/`. The repo-level `tools/check.sh lunar-new-year` runs the build and the tests.

```bash
python3 renderer/build.py                                    # render everything (+ GIFs in previews/)
python3 renderer/review.py all previews/                     # LED-style strips of every scene, the zodiac and the cards
python3 renderer/review.py scene lion_dance previews/ 0.2 6 9  # every 0.2 s between 6 s and 9 s
python3 renderer/review.py sprites previews/sprites.png      # the sprite contact sheet
bash tests/check.sh                                          # logic tests and live-text parity
```

| Change | Where |
|---|---|
| A scene's art or timing | `renderer/scenes/<scene>.py` |
| A zodiac animal | its sprite in `renderer/sprites.py`, its move in `renderer/scenes/zodiac.py` |
| Playlist order | `PLAYLISTS` in `renderer/scenes/__init__.py` |
| Card colors, positions and page lengths | `renderer/textstyle.py` |
| Card texts, greetings and date rules | `app/shared/lny.ts`, and the mirror in `mockup/template.html` (a test checks they agree) |
| Settings fields | `app/src/appmeta/settings.json` and `SETTINGS_VERSION` in `app/shared/lny.ts` (bump both together) |
| Buttons | `app/src/main.ts` |

Design notes and decisions are in [docs/DECISIONS.md](docs/DECISIONS.md).

## Install

Download `io.github.mertzjames.lunar-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh lunar-new-year     # build + typecheck + tests
tools/deploy.sh lunar-new-year    # install and launch on the bar in .env
tools/release.sh lunar-new-year   # (maintainers, on main) tag a release; CI publishes it
```
