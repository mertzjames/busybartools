# Veterans Day

A tribute for Veterans Day (November 11), which honors everyone who served in the U.S. armed forces, living and dead.
Six calm scenes play on the 72×16 display: flags along a small-town Main Street, a parade, a salute at sunrise, a
field of poppies, a child's thank-you and a closing flag. A clock card and a countdown card play between them. On the
day the countdown becomes a few words of thanks, and at 11:00 on November 11, the 11th hour of the 11th day of the
11th month, a quiet card marks the armistice of 1918 before the show resumes.

Open [mockup/index.html](mockup/index.html) in a browser for an LED simulator and storyboards of every scene and card.

## Scenes

| # | Scene | Length | What happens |
|---|---|---|---|
| 1 | Flags on Main Street | 14 s | Storefronts brighten at sunrise. The town puts a flag out on each lamppost in turn, then they all wave against the sky while autumn leaves drift down. |
| 2 | The Parade | 16 s | A flag bearer in a plain dress uniform, three veterans of different ages marching in step, an open car with two older veterans waving, and an older veteran walking behind. Neighbours seen from behind wave small flags at the curb. |
| 3 | The Salute | 14 s | At sunrise a service member in a plain dress uniform and an older veteran in a red cap salute as the flag goes up the pole. They hold the salute until it flies at the top, then lower their hands. |
| 4 | A Field of Poppies | 14 s | Red poppies open across a green field under a warm afternoon sky, then sway in a slow breeze. A few petals drift. |
| 5 | A Thank You | 14 s | An older veteran rests on a bench by a lit café window. A child brings a handmade card, the veteran opens it to a red heart, and the two wave. Then `THANK YOU` appears. |
| 6 | Thank You, Veterans | 16 s | The flag fills the display, its thirteen stripes rippling, then dims behind `THANK YOU` / `VETERANS`. |

No insignia, seals, branch emblems or medals (uniforms are plain colors with no patches), no likenesses of real
people, and nothing that depicts combat or weapons. Veterans of different ages, skin tones and genders.

## Cards

Live text, drawn by the app from the bar's clock (`/api/time`), in warm ivory and soft rose:

| Card | When | Pages |
|---|---|---|
| Clock | every other step | the time (`09:05`), then the date (`WED 11 NOV`) |
| Countdown | before and after the day | `350 DAYS` (or `1 DAY`) / `TO VETERANS DAY` |
| On the day | Nov 11, in the countdown's three slots | `VETERANS DAY`, then `THANK YOU` / `VETERANS`; `VETERANS DAY`, then `HONOR ALL` / `WHO SERVED`; `VETERANS DAY`, then `THANK YOU` / `FOR YOUR SERVICE` |
| The 11th hour | a cycle that starts from 11:00:00 to 11:00:59 on Nov 11 | `11TH HOUR`; `11TH DAY` / `11TH MONTH`; `ARMISTICE` / `NOV 11 1918`; `THANK YOU` / `VETERANS` (5 s each) |

**How the 11:00 moment works:** at the start of every cycle the app checks the bar's clock. If it is Nov 11 and 11:00
is less than 10 minutes away, it arms one timer for 11:00:02. When the timer fires, the app starts a new cycle. A
cycle that starts in the minute 11:00 opens with the moment card and then plays the day's usual show, so the moment
plays once and the show resumes. At 10:59 or 11:01 a cycle has no moment card. See
[docs/DECISIONS.md](docs/DECISIONS.md) D6.

## Controls

| Button | Action |
|---|---|
| OK | next step |
| Encoder | next / previous step |
| START | holiday mode: the 1st press previews Veterans Day (the day cards) on any date, the 2nd opens every cycle with the 11:00 moment card, the 3rd goes back to the calendar |
| Back | quit |

## How to change it

Run these from this folder (`tools/check.sh veterans-day` from the repo root runs the build and all the tests):

```bash
python3 renderer/build.py                              # render every scene; writes .anim, show.ts, icons, mockup
python3 renderer/review.py all previews/               # LED-style strips of every scene and card
python3 renderer/review.py grid salute previews/ 0.2 1.4 3.4   # a labeled grid every 0.2 s
python3 renderer/review.py zoom thank_you previews/ 6.0 10 40  # one frame, large, columns 10-40
bash tests/check.sh                                    # Node logic tests + live-text parity
```

- **Scenes** live in `renderer/scenes/` (one module each, registered in `scenes/__init__.py`). Shared drawing
  helpers (flags, poppies, people, storefronts) are in `renderer/vfx.py`.
- **Card words and timing** are in `app/shared/veterans.ts` (the source of truth for the app, the mockup and the
  tests). `renderer/scenes/text.py` holds the text styles and review copies of the words; the parity test checks
  they agree.
- **Generated files** (`app/src/animations/*.anim`, `app/shared/generated/show.ts`, the icons and
  `mockup/index.html`) come from `renderer/build.py`. Don't edit them by hand.

## Install

Download `busybartools.veteransday-<version>.tgz` from this app's GitHub Release and upload it to your bar.
See [Installing apps](../../docs/INSTALLING.md).

## Develop

```bash
tools/check.sh veterans-day     # build + typecheck + tests
tools/deploy.sh veterans-day    # install and launch on the bar in .env
tools/release.sh veterans-day   # (maintainers, on main) tag a release; CI publishes it
```

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
