# Wizarding Thanksgiving

A wizard-themed Thanksgiving show for the BUSY Bar's 72×16 LED front display. Nine short animated scenes loop all
evening: owls, broomsticks, a talking hat, a winged serpent dragon, four students, a very old wizard and plenty of turkey. A gold 24-hour
clock and the date appear between scenes.

<p>
  <img src="docs/media/dragon_roast.gif" alt="A winged serpent dragon torches a turkey on a spit" width="49%">
  <img src="docs/media/sorting.gif" alt="A talking hat sorts a turkey: GOBBLEDOR!" width="49%">
</p>

| # | Scene | Length |
|---|---|---|
| 1 | **Owl Post:** a snowy owl delivers HAPPY / THANKSGIVING | 18 s |
| 2 | **The Gravy Express:** a steam train hauls the feast | 14 s |
| 3 | **Broom Chase:** the scarlet-and-gold wizard chases a winged golden pie | 16 s |
| 4 | **Cauldron Bake-Off:** the blue-and-bronze witch brews a pumpkin pie | 16 s |
| 5 | **Great Hall Feast:** floating candles, and the yellow-and-black witch levitates the turkey | 18 s |
| 6 | **Sorting the Turkey:** the talking hat decides… GOBBLEDOR! | 17 s |
| 7 | **Dragon Roast:** a winged serpent torches the turkey. WELL DONE! | 16 s |
| 8 | **Pumpkin Patronus:** the green-and-silver wizard casts a silver turkey. EXPECTO PIE! | 15 s |
| 9 | **The Feast Appears:** the four students gather, and a very old wizard says NITWIT! BLUBBER! ODDMENT! TWEAK! and conjures the feast, dish by dish | 18 s |

After each scene, a clock card shows the time (`HH:MM`, 24-hour) for 4.5 s, then the date (`THU 26 NOV`) for 3.5 s.
The time comes from the bar's own clock. One full loop takes about 3 minutes 40 seconds.

To preview everything in a browser, download and open [`mockup/index.html`](mockup/index.html), a self-contained
LED simulator with storyboards.

## Install

1. Download `wizard.thanksgiving-<version>.tgz` from the
   [latest Wizarding Thanksgiving release](https://github.com/mertzjames/busybartools/releases?q=wizard-thanksgiving).
2. In your bar's web page (**http://10.0.4.20** over USB, or `http://<bar-ip>`), go to **Apps → + Add app**, choose the
   file, and click **Install app**.
3. On the bar, open the **Apps** menu and choose **Wizard Thanksgiving**.

The full guide, with Wi-Fi API setup and troubleshooting, is in [docs/INSTALLING.md](../../docs/INSTALLING.md).

| | |
|---|---|
| App id | `wizard.thanksgiving` |
| Needs | BUSY Bar HTTP API 27.12.0+ (tested on 27.16.0) |

## Controls

| On the bar | Does |
|---|---|
| **OK** (short press) | Skip to the next scene or clock card |
| **Encoder** (turn) | Step forward or back through the show |
| **Back** (short press) | Quit |

The clock shows the bar's local time, so set the time zone in the bar's settings. Brightness follows the bar's own
setting, which is auto by default.

## Develop

From the repo root:

```bash
python3 -m pip install -r requirements.txt
tools/check.sh wizard-thanksgiving     # render scenes, typecheck, build, run the clock parity test
tools/deploy.sh wizard-thanksgiving    # install and launch on the bar from .env
```

From this folder:

```bash
python3 renderer/build.py                                # ~2 s: .anim files, generated show.ts, icons, mockup, GIF previews
python3 renderer/review.py scene dragon_roast /tmp 1.5   # LED-style keyframe strip of one scene
python3 renderer/review.py sprites /tmp/sprites.png      # contact sheet of every sprite
python3 renderer/review.py cast /tmp/cast.png            # the students and the old wizard: every frame + a lineup
python3 tests/clock_parity.py                            # app vs renderer clock pixels, timestamp parsing
```

### Layout

| Path | What |
|---|---|
| `renderer/sprites.py` | Original pixel-art sprites as text grids, one letter per pixel, with a palette |
| `renderer/cast.py` | The four students (2 wizards, 2 witches: look, house, frames, wand tip) and the old wizard |
| `renderer/scenes/` | One file per scene (`SECONDS`, `KEYFRAMES`, `render()`); `PLAYLIST` order in `__init__.py` |
| `renderer/scenes/clock_bg.py` | Clock backdrop, plus `LAYOUT` (clock and date colors and timing) |
| `lib/python/busybar/` (repo root) | Shared render kit: fonts, 72×16 canvas, effects, `Sprite` and the build pipeline (`showbuild`) |
| `renderer/build.py` | Renders everything. `GAMMA` sets overall brightness (1.0 = original, lower = brighter darks) |
| `app/src/main.ts` | Playlist, clock card, input handling |
| `app/shared/clocktext.ts` | Re-exports the shared XPM text and bar-time helpers from `lib/ts/busybar/` |
| `app/shared/generated/show.ts` | Generated playlist, durations, fonts and clock layout (don't edit by hand) |
| `app/src/animations/` | Generated `.anim` files (committed) |
| `mockup/` | `template.html` → generated `index.html` |
| `prebuild.sh`, `tests/check.sh` | Hooks used by `tools/check.sh`, `deploy.sh` and `release.sh` |
| `docs/DECISIONS.md` | Why everything is the way it is (D1–D32) |
| `docs/PLAN.md` | The original plan |

## How it works

1. Sprites are text grids, and a Python renderer choreographs every frame at 15 fps.
2. Frames are packed into the bar's native `.anim` format, which the firmware plays with no network traffic. Every
   file is decoded again and checked pixel-for-pixel.
3. The app loops the scenes. Between them it draws the clock from the bar's `/api/time` as small XPM bitmaps in a
   custom gold pixel font.
4. The mockup plays the same frames and fonts, and a test confirms the app and renderer draw identical clock pixels.

All art is original; see [NOTICE.md](../../NOTICE.md).
