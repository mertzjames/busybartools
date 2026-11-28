# Christmas Day

A Christmas show for the BUSY Bar's 72×16 LED front display. Eight short animated scenes follow the holiday from
Christmas Eve to Christmas night: an elf trims the tree, Santa's sleigh crosses the moon, a cat raids the stockings,
a puppy pops out of a present, and the night ends with fireworks. A candy-cane 24-hour clock and the date appear
between scenes.

| # | Scene | Length |
|---|---|---|
| 1 | **Trimming the Tree:** an elf hangs ornaments, the lights spiral on, and the star is tossed to the top. TA-DA! | 17 s |
| 2 | **Carolers in the Snow:** three carolers sing under a street lamp; a dog howls along. FA LA LA! | 16 s |
| 3 | **Sleigh Across the Moon:** Santa tosses a present down a chimney on his way past the full moon. HO HO HO! | 16 s |
| 4 | **Stockings by the Fire:** a cat bats a stocking off the mantel, dives in and peeks out. STUFFED! | 16 s |
| 5 | **Present Surprise:** a jack-in-the-box, then a wiggling box with a puppy inside. BEST GIFT! | 17 s |
| 6 | **The Toy Train:** a train circles the tree; the cat hops over it, then rides away on the last car. ALL ABOARD! | 15 s |
| 7 | **Building a Snowman:** the wind steals the snowman's hat; the girl brings it back wearing it. MUCH BETTER! | 17 s |
| 8 | **Merry Christmas:** fireworks over the village, then MERRY / CHRISTMAS | 18 s |

After each scene, a clock card shows the time (`HH:MM`, 24-hour, white with a red candy-cane shadow) for 4.5 s,
then the date (`FRI 25 DEC`, gold with a holly-green shadow) for 3.5 s, over a twinkling light string and gentle
snowfall. The time comes from the bar's own clock. One full loop takes about 3 minutes 16 seconds.

To preview everything in a browser, download and open [`mockup/index.html`](mockup/index.html), a self-contained
LED simulator with storyboards.

## Install

1. Download `io.github.mertzjames.christmas-<version>.tgz` from the
   [latest Christmas Day release](https://github.com/mertzjames/busybartools/releases?q=christmas-day).
2. In your bar's web page (**http://10.0.4.20** over USB, or `http://<bar-ip>`), go to **Apps → + Add app**, choose the
   file, and click **Install app**.
3. On the bar, open the **Apps** menu and choose **Christmas Day**.

The full guide, with Wi-Fi API setup and troubleshooting, is in [docs/INSTALLING.md](../../docs/INSTALLING.md).

| | |
|---|---|
| App id | `io.github.mertzjames.christmas` |
| Needs | BUSY Bar HTTP API 27.12.0+ |

## Controls

| On the bar | Does |
|---|---|
| **OK** (short press) | Skip to the next scene or clock card |
| **Encoder** (turn) | Step forward or back through the show |
| **Back** (short press) | Quit |

The clock shows the bar's local time, so set the time zone in the bar's settings. Brightness follows the bar's own
setting.

## Develop

From the repo root:

```bash
python3 -m pip install -r requirements.txt
tools/check.sh christmas-day     # render scenes, typecheck, build, run the live-text parity test
tools/deploy.sh christmas-day    # install and launch on the bar from .env
```

From this folder:

```bash
python3 renderer/build.py                                  # ~2 s: .anim files, show.ts, icons, mockup, GIF previews
python3 renderer/review.py all previews/                   # LED-style keyframe strips of every scene + the clock card
python3 renderer/review.py scene sleigh_ride previews/ 0.5 # one scene, a frame every 0.5 s (optional start end)
python3 renderer/review.py sprites previews/sprites.png    # contact sheet of every sprite
python3 tests/clock_parity.py                              # app vs renderer clock pixels, timestamp parsing
```

### Layout

| Path | What |
|---|---|
| `renderer/sprites.py` | Original pixel-art sprites as text grids, one letter per pixel, with a palette |
| `renderer/xfx.py` | App-local effects and props: snowfall, light strings, trees, houses, presents, fire, fireworks |
| `renderer/scenes/` | One file per scene (`SECONDS`, `KEYFRAMES`, `render()`); `PLAYLIST` order in `__init__.py` |
| `renderer/scenes/clock_bg.py` | Clock backdrop, plus `LAYOUT` (clock and date colors and timing) |
| `renderer/build.py` | Renders everything through the shared kit (`lib/python/busybar/showbuild.py`); `GAMMA` tone curve |
| `app/src/main.ts` | The on-device app: plays scenes, draws the clock card, handles buttons |
| `app/shared/clocktext.ts` | Re-exports the shared TypeScript kit (`xpmtext`, `walltime`, `drawqueue`) |
| `app/shared/generated/show.ts` | Generated playlist, durations, fonts and clock layout |
| `mockup/template.html` | The browser simulator; `build.py` fills it into `mockup/index.html` |
| `tests/clock_parity.py` | Runs the app's TypeScript under Node 24 and compares its clock pixels with the renderer |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md). All art is original (see
[NOTICE.md](../../NOTICE.md)).
