# Decision log — Father's Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, and cards and a `steps(t)` playlist from `app/shared/fathers.ts`. The date comes
only from the kit (`nextOccurrence(t, HOLIDAYS.fathersDay)`, the third Sunday of June); no year is hard-coded.

**Why:** The round-2 common spec. The structure follows Presidents' Day, the other single-day, nth-weekday holiday
app, so the two read the same to a maintainer.

## D2 — Warm, lighthearted and inclusive
*2026-11-26*

**Decision:**
- The cast is dads, a granddad and father figures with five skin tones (deep to light) and different hair: a fishing
  cap and beard, a red ball cap, a buzz cut, short dark hair, and grey hair under a straw hat. Kids include a
  daughter with a ponytail and a son in a bike helmet. Nobody is named or labeled, so any father figure fits.
- Humor is gentle and about the day's own clichés, never at anyone's expense: a necktie that can't pick a pattern, a
  nap interrupted by a leaf, a showy burger flip, and one fishing pun on the day cards (`REEL COOL` / `DAD`, D9).
- No stereotypes that put anyone down (no clueless-dad gags), no brands, no copyrighted characters.

**Why:** The brief's tone. Father's Day is celebrated by many kinds of families.

## D3 — Seven scenes, dawn to night
*2026-11-26*

**Decision:** Fishing at Dawn, Playing Catch, The First Ride, Backyard Grill, The Wild Tie, Hammock Nap, Fireworks for
Dad (14 s each, 98 s of scenes). The order follows one summer day's light: sunrise on the lake, a bright morning,
midday, afternoon, indoors, sunset, night.

**Why:** The order reads well on a loop and ends on the celebration. Seven scenes give three count slots, one for
each on-the-day card (D7); the seventh scene is followed by a clock card.

**Alternatives:** The brief also suggested "a gift unwrapped" and "a hammock with a falling leaf" as options; all
six suggested scenes made the cut, plus the finale.

## D4 — People that read on 16 rows
*2026-11-26*

**Decision:** One procedural figure, `ffx.figure()` (adapted from Kwanzaa's `person()`): an adult is 13 rows, a child
9, 5 px wide with arms at any angle, plus seated (on a dock edge, on a bike saddle) and kneeling poses. Faces are
plain skin: a 3 px head has no room for lit eyes. Hair is a lit dark brown, never near-black. Lying down (the hammock)
is drawn by hand along the hammock's curve.

**What was tried (and fixed):**
- Fishing: a pink-violet dawn sky behind the parent's dark head made it vanish. The upper sky is now a deep blue, so
  the heads read against it, and the rod is a pale cane that shows against both.
- Catch: a white ball disappeared against the pale sky and a white fence. The ball is a 2×2 yellow softball, and the
  fence is gone.
- Bike: grey tires vanished in the pale sky, and a filled diamond frame read as a red blob. The tires are a lit
  charcoal over a lawn strip, and the frame is an open step-through.
- Grill: a brown fence swallowed the brown burgers and the dad's tan skin. A low dark hedge sits behind instead, so
  the burgers sit against the sky. White smoke vanished in the pale sky; it's a light grey.
- Hammock: the napper dissolved into the bright sunset, and striped fabric made him unreadable. Dark far hills now
  sit behind the hammock (rim-lit along the ridge), the hammock is one calm blue, and the leaf is lime because an
  orange leaf disappeared on his orange shirt.

## D5 — `#1 DAD`, with an app-local `#` glyph
*2026-11-26*

**Decision:** The shared big font has no `#`, so `renderer/scenes/text.py` registers one with
`font.register_font("big", {...}, extend=True)`, never editing `lib/`. The finale bakes `#1 DAD` into its frames. The
glyph is exported with the live fonts as well, so the parity test also checks it, but no live card uses it.

**Alternatives:** `BEST DAD` in the finale. The trophy with `#1 DAD` is the classic Father's Day image, and the glyph
costs one table entry. `BEST DAD` / `EVER` is used on a day card instead.

## D6 — Tone curve, steady glows, small files
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors. Glows (the sun, the
lamp, the trophy) are steady; the coals, the fireflies and the water glints flicker only a few pixels. The sunrise and
the sunset move the sun in whole-row steps (five and three steps), and the backgrounds are cached per step.

**Why:** The value approved on real hardware for Wizarding Thanksgiving, and the round-2 lesson that per-frame glow
flicker bloats `.anim` files. Total `.anim` data is about 0.44 MB.

## D7 — Cards: big words on the day, the name in the small font under the count
*2026-11-26*

**Decision:**
- Before the day: `206 DAYS` (big, rows 1–8) over `TO FATHER'S DAY` (tiny, rows 10–15). After the day it counts to
  next year's; the longest possible count is `370 DAYS`.
- On the day, each count slot shows `HAPPY` over `FATHER'S DAY` as two big lines (rows 0–7 and 8–15; `FATHER'S DAY`
  is 65 px) for 5 s, then a phrase for 4 s: `BEST DAD` / `EVER` (one line would be 73 px), `THANKS DAD`, then
  `REEL COOL` / `DAD`.
- The clock card shows the time, then the date.
- Colors: cream into a sunset orange over a deep-navy shadow for the big lines, and a pale sky blue for the small
  line. The clock backdrop is a summer night with fireflies blinking at the edges; the count backdrop is a dusk sky
  over a lake's far shore.

**Why:** Big text reads from across a room, and the greeting fits it. `TO FATHER'S DAY` doesn't (81 px).

## D8 — START previews the day
*2026-11-26*

**Decision:** START toggles holiday mode: the playlist is picked as if it were Father's Day, and the cycle restarts
rotated to begin at the first count slot (`playlist(..., fromCard)`), so the greeting shows at once. Press it again to
go back. The mockup has the same toggle. The handler calls `show.start()` again (no step index), so it works with the
runner before and after `start(from)` was added.

**Why:** It lets the day be reviewed on any date, as the playbook requires.

## D9 — One pun, clean and on theme
*2026-11-26*

**Decision:** The third day card is `REEL COOL` / `DAD`, a fishing pun that ties back to the opening scene. The
other cards are sincere (`BEST DAD EVER`, `THANKS DAD`).

**Why:** The brief allows a clean, original dad-joke card. One is enough to make people smile without turning the
day into a joke.

## D10 — One source of truth for card logic
*2026-11-26*

**Decision:** Card texts, page lengths and the playlist live in `app/shared/fathers.ts`. The build type-strips it
(with the kit's `walltime.ts` and `holidays.ts`) into the mockup, and a Node test evaluates the mockup's copy and
compares it with the app's for every day of 2026–2029. `DAY_TEXT` in `renderer/scenes/text.py` is a review copy that
the parity test checks against `DAY_CARDS`.

**Why:** The mockup and the bar can't drift apart, and the review strips show exactly what the bar shows.
