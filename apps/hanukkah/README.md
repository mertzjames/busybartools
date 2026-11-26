# Hanukkah

A Hanukkah show for the BUSY Bar's 72×16 LED front display. Its heart is a menorah that follows tonight's candle
count: the shamash is lit first, then it lights tonight's candles, newest first. Around it play a spinning dreidel,
latkes sizzling in a pan, sufganiyot under powdered sugar, a cascade of gelt, a menorah glowing in a snowy window,
and a blue-and-silver finale. Between scenes, a clock card and a countdown card appear; during Hanukkah the countdown
becomes the night's greeting.

| # | Scene | Length |
|---|---|---|
| 1 | **Tonight's Menorah:** the menorah in a window at night. Tonight's candles stand in the rightmost cups; the raised shamash is lit, lifted out, and lights them from left to right, then goes back to its place. Nine variants, 0–8 candles. | 16 s |
| 2 | **Spin the Dreidel:** a blue dreidel drops in spinning, slows until its letters (nun, gimel, hei, shin) pass by, and stops on gimel: TAKE ALL, and the pot of gelt hops over. | 15 s |
| 3 | **Latkes in the Pan:** three latkes sizzle over blue gas flames; a spatula flips each golden side up, and one goes onto a plate with applesauce and sour cream. | 15 s |
| 4 | **Sufganiyot:** a sifter dusts three jelly doughnuts with powdered sugar, then each gets its jelly. | 14 s |
| 5 | **A Cascade of Gelt:** gold and silver foil coins tumble, spin and pile into a glittering hill. | 14 s |
| 6 | **Window in the Snow:** from the street, tonight's candles glow in a window while snow falls; a gust blows through. Nine variants, 0–8 candles. | 14 s |
| 7 | **Happy Hanukkah:** blue, silver and white fireworks, a Star of David that glitters and bursts, then HAPPY / HANUKKAH. Only while candles are lit. | 16 s |

### Tonight's candles

The first candle is lit on the evening before 25 Kislev (computed from the Hebrew calendar, so no table needs
updating). The bar has no sunset table, so **17:00 local time stands in for sundown**:

| When (2026) | Candles | Count card |
|---|---|---|
| until Dec 2 | resting menorah | `N DAYS` / `TO HANUKKAH` |
| Dec 3 | resting menorah | `TOMORROW` / `HANUKKAH BEGINS` |
| Dec 4, before 17:00 | resting menorah | `TONIGHT` / `HANUKKAH BEGINS` |
| Dec 4, from 17:00 | 1 | `NIGHT 1` / `HAPPY HANUKKAH`, then `NIGHT 1` / `CHAG SAMEACH` |
| each later day, from 17:00 | one more | `NIGHT n` / … |
| Dec 11 from 17:00, through Dec 12 | 8 | `NIGHT 8` / … |
| from Dec 13 | resting menorah | the count to next year's Hanukkah |

The show picks its playlist again at the start of every cycle (about 2 to 3 minutes), so a new candle appears
within a few minutes of 17:00. Outside Hanukkah, the menorah and the window rest unlit and the finale is left out.

A cycle: count card, menorah, clock, dreidel, count, latkes, clock, sufganiyot, count, gelt, clock, window, then
(during Hanukkah) count, finale, and a last clock. The **clock card** shows the time (`HH:MM`, 24-hour, silver with
a blue shadow) for 4.5 s, then the date in gold for 3.5 s, over a starry night. The **count card** shows each page
for 4.5 s between two lit candles.

To preview everything in a browser, download and open [`mockup/index.html`](mockup/index.html), a self-contained
LED simulator with storyboards, the eight nights and a holiday-mode button.

## Install

1. Download `busybartools.hanukkah-<version>.tgz` from the
   [latest Hanukkah release](https://github.com/mertzjames/busybartools/releases?q=hanukkah).
2. In your bar's web page (**http://10.0.4.20** over USB, or `http://<bar-ip>`), go to **Apps → + Add app**, choose the
   file, and click **Install app**.
3. On the bar, open the **Apps** menu and choose **Hanukkah**.

The full guide is in [docs/INSTALLING.md](../../docs/INSTALLING.md).

| | |
|---|---|
| App id | `busybartools.hanukkah` |
| Needs | BUSY Bar HTTP API 27.12.0+ |

## Controls

| On the bar | Does |
|---|---|
| **OK** (short press) | Skip to the next scene or card |
| **Encoder** (turn) | Step forward or back through the show |
| **START** (short press) | Holiday mode: preview night 1, then 2, … 8 on any date; a ninth press goes back to today's show |
| **Back** (short press) | Quit |

The candles and the clock follow the bar's local time, so set the time zone in the bar's settings.

## Develop

From the repo root:

```bash
python3 -m pip install -r requirements.txt
tools/check.sh hanukkah     # render, typecheck, build, logic tests, live-text parity
tools/deploy.sh hanukkah    # install and launch on the bar from .env
```

From `apps/hanukkah/`:

```bash
python3 renderer/build.py                                # render everything (also GIFs in previews/)
python3 renderer/review.py all previews/                 # LED-style strips of every scene, card and night
python3 renderer/review.py scene menorah_3 previews/ 0.2 2 6   # every 0.2 s between 2 s and 6 s
```

| Change | Where |
|---|---|
| A scene | `renderer/scenes/<name>.py` (registered in `renderer/scenes/__init__.py`) |
| The menorah, flames, coins, dreidel letters | `renderer/hfx.py` |
| Card colors, fonts, timing | `LAYOUT` in `renderer/scenes/cards.py` |
| Sundown hour, card texts, playlist, holiday mode | `app/shared/hanukkah.ts`, mirrored in `mockup/template.html` (the tests check both) |
| Buttons | `app/src/main.ts` |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
