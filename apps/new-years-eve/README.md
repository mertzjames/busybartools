# New Year's Eve

Party scenes, a countdown to midnight, and a celebration when the new year rings in, for the BUSY Bar's 72×16 LED
display. Everything follows the bar's own local clock, and the year is read from the bar's date.

Open [`mockup/index.html`](mockup/index.html) in a browser for a simulator that runs the app's own phase logic, with
buttons to jump the clock to T−90 s, T−30 s, T−12 s or after midnight, plus storyboards of every scene and screen.

## How the night runs

| Phase | When (bar time) | On screen |
|---|---|---|
| **Party** | Dec 31, more than 60 s to midnight | The eight scenes below, each followed by a 6 s **countdown card**: `HH:MM:SS` (or `MM:SS` in the last hour) and `TO 2027`, ticking every second. A scene only starts if it ends by T−60 s; otherwise the final minute starts early. |
| **Final minute** | T−60 … T−11 s | The seconds left, big, over chasing marquee lights and two spinning beacons, with a bar along the bottom that fills toward T−10. The lights double their speed for the last 30 s. |
| **Final ten** | T−10 … T−1 s | One huge digit per second, on the bar's tick, each in a new color (gold, silver, pink, cyan), with a flash and sparks on every beat. |
| **Midnight** | 00:00:00, for 60 s | A huge `0` with a flash, a burst of rings and rockets, then `HAPPY NEW YEAR` and the year, alternating with the year in huge digits, over a looping fireworks backdrop. |
| **After midnight** | Jan 1 until 06:00 | The party loop again, with a clock card: the time and `HAPPY 2027`. |
| **Off-season** | any other time | The party loop, with a clock card: the time and `37 DAYS` / `TO 2027`. |

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Disco Fever | 14 s | A mirror ball drops in on its chain, spins, and throws colored spots around the room; two guests dance on a lit floor. |
| 2 | Champagne Pop | 14 s | The bottle shakes in its ice bucket, the cork pops and flies across the room in a foam fountain, two flutes rise and clink. `CHEERS!` |
| 3 | The Clock Tower | 14 s | Snow over a sleeping town; the view climbs an old stone tower to its glowing clock, where the minute hand ticks from 11:55 toward twelve. `TICK` … `TOCK` … `ALMOST TIME!` |
| 4 | Confetti Poppers | 12 s | Two party poppers fire confetti and curly streamers from the corners, then both at once. `WOOHOO!` |
| 5 | Year Odometer | 12 s | A gold counter shows the old year, then the changing digits roll over to the new one with a glint and confetti. The digits are drawn live by the app, so the years are always right. |
| 6 | Conga Line | 15 s | Four guests in party hats conga in, dance with their hands up, blow their noisemakers, and conga off. |
| 7 | Ball Drop Rehearsal | 13 s | A glittering ball starts down its pole above the city under searchlights, stops halfway (`NOT YET!`) and zips back up. `SOON!` |
| 8 | Fireworks Finale | 15 s | Rockets over the skyline: peonies, rings, palms and gold willows, then a big finale. |

All art is original pixel art of generic party imagery: no real landmarks, logos or characters.

## Install

Download `io.github.mertzjames.newyear-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md). Make sure the bar's clock and time zone are right: the countdown
uses the bar's local time.

## Controls

| Button | Action |
|---|---|
| **START** (short press) | **Demo mode:** jumps the app's clock to 15 s before the next new year, so you can watch the final seconds and the celebration any day. Real time comes back by itself after the celebration. Press again to replay. |
| **OK** | Skip the current scene or card. The countdown and the celebration follow the clock and can't be skipped. |
| **Back** | Quit. |

## Develop

```bash
tools/check.sh new-years-eve     # render, typecheck, build, Node tests + live-text parity test
tools/deploy.sh new-years-eve    # install and launch on the bar in .env
tools/release.sh new-years-eve   # (maintainers, on main) tag a release; CI publishes it
```

From this folder:

```bash
python3 renderer/build.py                          # render everything (~3 s), write show.ts, icons and the mockup
python3 renderer/review.py all                     # LED-style keyframe strips of every scene and backdrop -> previews/
python3 renderer/review.py live                    # the live screens as the bar shows them (runs the app's TS)
python3 renderer/review.py scene disco_ball previews 1   # one scene, a frame every second
node --experimental-strip-types --test tests/logic.test.mts   # Node 24
python3 tests/live_parity.py
```

| Path | What it is |
|---|---|
| `renderer/scenes/*.py` | One module per scene, plus `backdrops.py` for the live screens' backdrops |
| `renderer/live.py` | The app-local `huge` digit font and the layout and colors of every live screen |
| `renderer/party.py`, `sprites.py` | Fireworks, confetti, string lights, skyline; the guests, bottle and cork |
| `app/shared/nye.ts` | Pure logic: phases, year, countdown text, demo offset, the step planner |
| `app/shared/screens.ts` | Pure layouts of the live screens, composed into one xpmbitmap per update |
| `app/src/main.ts` | Clock sync, timers and draws on the bar |
| `app/shared/generated/show.ts`, `app/src/animations/*.anim`, `mockup/index.html` | Generated by `renderer/build.py`; don't edit by hand |

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md). Rules for coding agents: [AGENTS.md](AGENTS.md).
