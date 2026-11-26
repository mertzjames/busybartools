# Kwanzaa

A Kwanzaa show for the BUSY Bar's 72×16 LED front display. Each day of Kwanzaa (December 26 to January 1) the
kinara lights that day's candles. A card asks `HABARI GANI?` and answers with the principle of the day, in Swahili
and English. Between them play scenes of the harvest, the unity cup, drums and dance, a woven cloth and the karamu
feast. Before Kwanzaa, the candles wait unlit and a card counts the days to December 26.

| # | Scene | Length |
|---|---|---|
| 1 | **Lighting the Kinara:** the Kwanzaa table (mkeka, mazao, muhindi, unity cup). A taper lights the day's candles in the official order, and `DAY 3` appears. Before Kwanzaa, the candles are unlit and the caption says `DEC 26`. | 14 s |
| 2 | **The Harvest:** fruit and vegetables arc into a basket in a cornfield at sunset, then ears of corn drop in. `MAZAO` / `THE HARVEST` | 14 s |
| 3 | **The Unity Cup:** the elder pours a libation, the cup passes hand to hand, and all pull together. `HARAMBEE!` | 16 s |
| 4 | **Drums and Dance:** two drummers under a baobab at dusk and three dancers on the beat. The drums roll, everyone leaps, and confetti flies. | 15 s |
| 5 | **The Kente Weave:** a shuttle weaves an original kente-inspired cloth row by row; it glides past glinting. `HAPPY` / `KWANZAA` | 14 s |
| 6 | **The Karamu Feast:** `KARAMU` / `DEC 31` over the table; the family sits down, the dishes arrive, everyone cheers. | 16 s |

The kinara scene is rendered once unlit and once for each day, in each of the two candle orders (see
[Settings](#settings)). The app picks the variant from the bar's date and the setting.

### Cards

Between the scenes, cards alternate in this order: clock, count, clock, count, clock, count.

| Card | Shows |
|---|---|
| **Clock** | The time (`18:05`, 24-hour) for 4.5 s, then the date (`SAT 26 DEC`) for 3.5 s |
| **Count**, before Kwanzaa | `30 DAYS` / `TO KWANZAA`, then `KWANZAA` / `DEC 26 - JAN 1` |
| **Count**, during Kwanzaa | `HABARI GANI?` / `WHAT'S THE NEWS?`; then the answer, the day's principle (`UJIMA` / `COLLECTIVE WORK`, `UJIMA` / `AND RESPONSIBILITY`); then `KWANZAA` / `DAY 3 OF 7`, or `KARAMU` / `DAY 6: THE FEAST` on December 31 |

The seven principles (Nguzo Saba), one per day:

| Day | Date | Principle | New candle: official site (default) | New candle: from the center |
|---|---|---|---|---|
| 1 | Dec 26 | Umoja (Unity) | black, center | black, center |
| 2 | Dec 27 | Kujichagulia (Self-Determination) | red, far left | red, next to the black |
| 3 | Dec 28 | Ujima (Collective Work and Responsibility) | green, next to the black | green, next to the black |
| 4 | Dec 29 | Ujamaa (Cooperative Economics) | red, middle | red, middle |
| 5 | Dec 30 | Nia (Purpose) | green, middle | green, middle |
| 6 | Dec 31 | Kuumba (Creativity), the karamu | red, next to the black | red, far left |
| 7 | Jan 1 | Imani (Faith) | green, far right | green, far right |

Each day lights all the candles up to that day. The default order follows the official Kwanzaa website: see
[docs/DECISIONS.md](docs/DECISIONS.md) D3 and D14. One full loop takes about 2 minutes 17 seconds.

To preview everything in a browser, download and open [`mockup/index.html`](mockup/index.html). It is a
self-contained LED simulator with storyboards and a holiday-mode control.

## Install

1. Download `busybartools.kwanzaa-<version>.tgz` from the
   [latest Kwanzaa release](https://github.com/mertzjames/busybartools/releases?q=kwanzaa).
2. In your bar's web page (**http://10.0.4.20** over USB, or `http://<bar-ip>`), go to **Apps → + Add app**, choose the
   file, and click **Install app**.
3. On the bar, open the **Apps** menu and choose **Kwanzaa**.

The full guide, with Wi-Fi API setup and troubleshooting, is in [docs/INSTALLING.md](../../docs/INSTALLING.md).

| | |
|---|---|
| App id | `busybartools.kwanzaa` |
| Needs | BUSY Bar HTTP API 27.12.0+ |

## Controls

| On the bar | Does |
|---|---|
| **OK** (short press) | Skip to the next scene or card |
| **Encoder** (turn) | Step forward or back through the show |
| **START** (short press) | **Holiday mode:** the first press previews day 1 of Kwanzaa, and each later press moves to the next day. After day 7, the next press returns to today's date. |
| **Back** (short press) | Quit |

Dates and the clock come from the bar's local time, so set the time zone in the bar's settings.

## Settings

On the bar, open **Apps → Kwanzaa → Setup**. The same setting is also in the bar's web interface.

| Setting | Options | Default |
|---|---|---|
| **Candle order** | **Official site:** the black candle, then red and green alternately, each side lit from left to right. **From the center:** the black candle, then red and green alternately, moving outward from the center. | Official site |

Families light the candles in different orders, so both are offered. The setting applies the next time the app
starts. If it can't be read, the app uses the default. The mockup has a matching candle-order menu.

## Develop

From the repo root:

```bash
python3 -m pip install -r requirements.txt
tools/check.sh kwanzaa     # render scenes, typecheck, build, run the logic and parity tests
tools/deploy.sh kwanzaa    # install and launch on the bar from .env
```

From this folder:

```bash
python3 renderer/build.py                                  # ~4 s: .anim files, show.ts, icons, mockup, GIF previews
python3 renderer/review.py all previews/                   # LED-style strips of every scene, kinara variant and card
python3 renderer/review.py kinara 3 previews/ 0.2 2 5      # one kinara variant, a frame every 0.2 s from 2 s to 5 s
python3 renderer/review.py center 3 previews/              # a center-out kinara variant (days 2-7)
python3 renderer/review.py scene harvest previews/ 0.5     # one scene, a frame every 0.5 s
python3 renderer/review.py cards previews/                 # every card page, drawn as the app draws it
```

### Layout

| Path | What |
|---|---|
| `renderer/kfx.py` | App-local props: the kinara and candle flames, the two `LIGHT_ORDERS`, mkeka, corn, unity cup, basket, fruit, the kente motifs, simple figures |
| `renderer/scenes/` | One file per scene (`SECONDS`, `KEYFRAMES`, `render()`); `kinara.py` makes the kinara variants for both orders; `PLAYLIST` in `__init__.py` |
| `renderer/scenes/text.py` | Card text styles, timings and the Nguzo Saba: the single source for the app, the mockup and the review strips |
| `renderer/scenes/card_bg.py` | The card backdrop: a kente border and a warm glow |
| `renderer/build.py` | Renders everything through the shared kit (`lib/python/busybar/showbuild.py`); `GAMMA` tone curve |
| `app/src/main.ts` | The on-device app: configuration for the shared show runner (`lib/ts/busybar/showrunner.ts`), plus holiday mode |
| `app/shared/kwanzaa.ts` | The date logic: the day of Kwanzaa, the count card's pages, the playlist, the candle-order setting |
| `app/src/appmeta/settings.json` | The app's Setup page on the bar: the candle order |
| `app/shared/kit.ts` | Re-exports the shared TypeScript kit |
| `app/shared/generated/show.ts` | Generated scenes, durations, styles, timings, principles and fonts |
| `mockup/template.html` | The browser simulator; `build.py` fills it into `mockup/index.html` |
| `tests/logic.test.mts` | Day of Kwanzaa across the new year, card texts, the playlist for both candle orders, the setting and its fallbacks, holiday mode |
| `tests/text_parity.py` | The app's TypeScript vs the renderer: identical text pixels and identical card pages |

### Changing it

| Change | Where | Then |
|---|---|---|
| A scene | `renderer/scenes/<name>.py` (+ `PLAYLIST`) | `build.py`, review strips, the scene table above |
| A lighting order or the candle art | `LIGHT_ORDERS` and `Kinara` in `renderer/kfx.py` (and `settings.json`, `ORDERS` in `kwanzaa.ts` for a new order) | review every `kinara` variant |
| Principle texts or card timing | `renderer/scenes/text.py` and `countPages` in `app/shared/kwanzaa.ts` (keep them identical) | `tools/check.sh kwanzaa` |
| Card colors or layout | `STYLES` in `renderer/scenes/text.py` | `build.py`, `review.py cards`, the parity test |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md). All art is original (see
[NOTICE.md](../../NOTICE.md)).
