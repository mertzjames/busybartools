# Decision log — Independence Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, and cards and a `steps(t)` playlist from `app/shared/july4.ts`. The date comes
only from the kit (`nextOccurrence(t, HOLIDAYS.independenceDay)`); no year is hard-coded.

**Why:** The round-2 common spec. The structure follows Presidents' Day, the closest finished app (a flag, an eagle,
fireworks), and some of its helpers are copied app-locally (D5).

## D2 — Festive, family-friendly and non-partisan
*2026-11-26*

**Decision:**
- No likenesses of real people: the people on screen are generic (band members, kids, a cook) with plain faces and
  no eyes, or are seen from behind (the sparkler kids).
- No official seals, emblems or logos. The Liberty Bell is original pixel art (D8); the brick hall behind it is a
  generic hall with a steeple, not a drawing of a real building.
- The words on screen are civic and shared: `USA` (written with a sparkler), `LIBERTY`, the greeting, the countdowns
  and `ENJOY THE FIREWORKS!`. Nothing partisan.

**Why:** The brief's tone for this app. The Fourth is a celebration, so the show is a party from morning to night.

## D3 — Seven scenes, one Fourth of July from morning to night
*2026-11-26*

**Decision:** Hometown Parade (15 s), The Liberty Bell, Backyard Cookout, Eagle and Flag, Sparklers at Dusk (14 s
each), Fireworks over the City (16 s), Happy 4th! (14 s): 101 s of scenes. The order follows the day's light: a
morning parade, the bell, an afternoon cookout, the flag in the breeze, sparklers at dusk, then the fireworks and the
finale.

**Alternatives:** Ending on the fireworks over the city without a text finale; the brief asks for a "Happy 4th"
finale, and it gives the loop a clear end. Seven scenes give three count slots, so on the day the fireworks countdown
comes round three times a loop (D7).

## D4 — Tone curve, steady glows, small files
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors. Large soft areas hold
still: the sun's glow is steady, the smoke haze after the finale volley moves in 20 quantized steps, and the flag's
wave shading is quantized to steps of 1/16. Total `.anim` data is about 0.9 MB.

**Why:** The value approved on real hardware for Wizarding Thanksgiving; and the round-2 lesson that per-frame changes
over big areas bloat the files.

## D5 — The flag: thirteen one-row stripes, a dense checker of stars
*2026-11-26*

**Decision:** In Eagle and Flag the flag is 13 rows tall, one row per stripe: 7 red and 6 white, red at the top and
bottom. The canton covers the top 7 stripes and 12 of the 30 columns (the real flag's 40% of the fly), navy with
white dots in a dense checkerboard inside a one-pixel navy border. The wave moves each column by a whole row and
shades it by the wave's slope (`jfx.draw_flag`, copied from Presidents' Day's `pfx.draw_flag`). The small hand flags
the kids wave are 4×3: a blue corner, then red and white rows.

**Why:** Fractional row offsets blur one-row stripes into pink; whole-row steps keep every stripe red or white. A
sparse dot canton read as eyes in another app; a dense checker reads as stars. The fly is a little longer than the
real 1.9:1 so the wave has room to show.

The eagle (seen from below, wings spread, a lit brown with a white head and tail) is Presidents' Day's design,
copied app-locally, and banks with the same per-column shear.

## D6 — Cards: two big lines, rows 0 and 8
*2026-11-26*

**Decision:** Every count and greeting line fits the `big` font, so the cards use two big lines (y 0 and y 8: each 7
rows plus a 1-row shadow, filling the 16 rows exactly) instead of a big line over a `tiny` one. The longest line is
`FIREWORKS IN`, 65 px plus the shadow. Styles (`renderer/scenes/text.py`, exported to `show.ts`):

| Style | Font, row | Color | Used for |
|---|---|---|---|
| time | clock, 2 | gold | `18:05` |
| date | big, 4 | gold | `SUN 4 JUL` |
| head | big, 0 | gold | `220 DAYS`, `HAPPY` |
| sub | big, 8 | pale red | `TO JULY 4TH`, `4TH OF JULY` |
| lead | big, 0 | pale blue | `FIREWORKS IN`, `ENJOY THE` |
| num | big, 8 | gold | `02:15`, `FIREWORKS!` |

The countdown says `TO JULY 4TH` (61 px): it reads well and fits. The backdrops are a night-blue clock card (stars, a
drifting stripe ribbon on the bottom row, tiny bursts in the far corners, clear of the widest date) and a darker
count card, since its two lines cover all 16 rows.

## D7 — On the Fourth, count down to the fireworks at dusk (21:00)
*2026-11-26*

**Decision:** On July 4 the count slots show a day card of two pages: `HAPPY` / `4TH OF JULY`, then `FIREWORKS IN` /
`HH:MM` (hours and minutes until 21:00 bar-local time, rounded up to the minute, so `00:01` during the last minute and
`21:00` at midnight). From 21:00 the second page says `ENJOY THE` / `FIREWORKS!`. Before the day it's `N DAYS` /
`TO JULY 4TH`; from July 5 it counts to next year's (up to 365 days).

- **Pages computed from t.** Each line is a function of the time it is drawn at, and the day card always has the same
  two pages of two lines, so when the minute rolls over during the card (the runner recomputes each line at second
  0) the count steps down, and at 21:00 it changes straight to the after-dusk words. A runner test covers 20:59:55.
- **HH:MM, not MM:SS in the last hour.** The runner redraws a line when the minute rolls over. Seconds would need
  one-second pages, and each changed line fades in again, so the digits would blink every second and send three
  draw requests a second. Minutes are calmer and kinder to the bar.
- **A fixed 21:00.** Fireworks usually start around dusk, roughly 21:00-21:30 across the US in early July. The kit has
  no sunset estimate yet (`lib/ts/busybar/sun.ts` was not on `dev` when this was built), so dusk is a constant
  (`DUSK_HOUR`, `DUSK_MINUTE` in `app/shared/july4.ts`). **Candidates for later:** a settings option for the hour, or
  sunset + 30 minutes from the bar's time zone once the kit has it.

## D8 — The Liberty Bell: original art, the crack as a stepped line
*2026-11-26*

**Decision:** A 15×13 bronze bell drawn from scratch: a domed crown, straight waist, flared lip, two raised bands,
light from the left. The crack runs up from the lip, right of center, as a stepped line (two pixels down, one across)
in a darker but lit brown. The bell hangs from a wooden yoke on a frame and swings by shifting each row a whole
number of pixels (rotating pixel art mangles it). Each time the swing turns, rings of sound (additive gold arcs)
spread out. `LIBERTY` appears beside it from 8.6 s, over a darkened patch of sky.

**What was tried:**
- The first bell was too triangular to read as a bell; the dome and straight waist fixed it.
- The ring waves were invisible as blended gold on a pale sky. The sky is now a deeper summer blue and the arcs are
  added light.

**Note:** The real bell is no longer rung (it's struck gently on anniversaries). Here it swings as a symbol, the way
it's usually pictured.

## D9 — START cycles: normal, holiday mode, dusk demo
*2026-11-26*

**Decision:** START (short press) cycles three modes, each restarting the show on a count slot so the change shows at
once:
1. **normal**: the real date.
2. **holiday mode**: the Fourth's cards and playlist on any date, at today's real time of day (so before 21:00 it
   counts down to 21:00 today).
3. **dusk demo**: the cards show July 4 at 20:58 (keeping the bar's seconds), and the day card follows every scene
   (no clock), so the countdown runs `00:02`, `00:01`, then `ENJOY THE FIREWORKS!` within two minutes.

The demo shifts the bar's time by a whole number of minutes (`demoShift`), fixed at the first cycle after the press,
so the shifted clock's minute rollovers land on the bar's own, which is when the runner redraws the lines. The mockup
has the same three-step button (and the S key).

**Why:** The countdown's best moment is its last minute, which otherwise needs waiting until 20:59 on July 4. New
Year's Eve's demo (a jump to T-15 s) set the pattern.

## D10 — The parade: a muted street, a bright parade
*2026-11-26*

**Decision:** The shopfronts, sidewalk and street are muted greys and dusty colors with warm windows and one string of
tiny pennants; the marching band wears white shakos with red plumes, red jackets and white trousers, with gold horns.
Five kids on the far sidewalk wave 4×3 hand flags. The float has a pleated red and white skirt under a blue band of
gold stars, a big gold star on a post against the sky, and two kids waving from the deck. The parade crosses at
8 px/s; the float is still rolling across as the scene ends.

**What was tried:** Brick shops with striped awnings and big bunting swags: with the red jackets and the kids' flags
everything ran together into stripes. Navy shakos vanished against the shops; white ones read.

**Open:** It's still the busiest scene. A simpler version would drop the far-sidewalk kids (the kids on the float
would remain).

## D11 — Other art notes
*2026-11-26*

- **Cookout:** a white picket fence drowned out the apron, the tablecloth and the food; a green hedge replaced it.
  Watermelon slices are 7 px wide (smaller ones vanished), seeds a lit brown. The flipped burger arcs up and lands
  browner.
- **Fireworks over the City:** a dark skyline on a dark sky disappeared; a purple glow along the horizon now sits
  behind lower, darker buildings with lit windows and red beacons. Bursts are drawn only above each column's roof,
  and the river glints with the brightest burst above it.
- **Sparklers:** three kids seen from behind (hair, no faces) in lit mid-tone shirts against a three-stop dusk sky
  (navy, purple, a narrow orange band). Trails are additive and about 0.8 s long; the middle kid writes `USA` in pen
  strokes, which hang in the air and fade.
- **Finale:** the greeting is revealed outward from the center of a big gold ring burst, over a darkened sky, with
  red, white and blue confetti behind it and glints across the words.

## D12 — A shorter flag in Eagle and Flag
*2026-11-26*

**Decision:** the Eagle and Flag scene's flag is 26 px wide (was 30) with a 10 px canton (was 12), still 13 stripes
tall.

**Why:** review feedback said the flag looked slightly too long. At 30 × 13 it was about 2.3 : 1; the real flag is
1.9 : 1. 26 × 13 is 2 : 1, a small change that keeps the waving fly clear of the eagle's path. The canton stays at
two fifths of the fly, as on the real flag.

**Alternatives:** 25 px would be closer to 1.9 : 1, but the review asked for only a little shorter.
