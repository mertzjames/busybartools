# Decision log — Presidents' Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, and cards and a `steps(t)` playlist from `app/shared/presidents.ts`. The date
comes only from the kit (`nextOccurrence(t, HOLIDAYS.presidentsDay)`); no year is hard-coded.

**Why:** The round-2 common spec. The structure follows MLK Day, the other single-day, floating-Monday holiday app.

## D2 — Light, warm and non-partisan: symbols, objects and places
*2026-11-26*

**Decision:**
- No faces or likenesses of any president: no portraits, busts, statues or silhouettes of real people. The day is
  told with a flag, a cherry tree, an eagle, a quill, monuments, a log cabin and a stovepipe hat.
- No official seals, emblems or logos (no presidential seal). The wax seal in "We the People" is a plain red disc.
- The monuments are generic: an obelisk, a columned memorial and a domed hall. The memorial's lit interior is empty.
- No president is named and nothing partisan is said. The words on screen are `WE THE PEOPLE` (the opening of the
  U.S. Constitution, a public-domain text that belongs to everyone), the greeting, the countdown, and three civic
  words on the day (`LIBERTY`, `UNION`, `FREEDOM`).

**Why:** The brief's tone rules. Presidents' Day honors the office and all who held it, so the show celebrates shared
symbols rather than any person.

## D3 — Seven scenes, morning to night
*2026-11-26*

**Decision:** Old Glory, The Cherry Tree, Eagle over the Mountains, We the People, Monuments at Sunset, The Log Cabin,
Fireworks Finale (14 s each, 98 s of scenes). The order follows one day's light: a bright winter morning, a spring-like
afternoon, candlelight, sunset, dusk, then night fireworks.

**Alternatives:** A chronological order (Washington, the Constitution, Lincoln, the monuments). The time-of-day order
reads better on a loop and ends on the party. Seven scenes give three count slots, one for each on-the-day card (D7);
the seventh scene is followed by a clock card.

## D4 — The flag: thirteen one-row stripes, stars as dots
*2026-11-26*

**Decision:** The flag is 13 rows tall, one row per stripe: 7 red and 6 white, red at the top and bottom. The canton
covers the top 7 stripes and about 40% of the fly (16 of 40 columns), navy with white dots in a checkerboard inside a
one-pixel navy border. The wave moves each column by a whole row and shades it by the wave's slope.

**Why:** Fractional row offsets blur one-row stripes into pink. Whole-row steps keep every stripe red or white, and
the shading carries the ripple. The real 50 stars can't fit in 16×7 pixels, so the dots suggest them (the brief
allows it).

**What was tried:** A deep-blue morning sky: the navy canton vanished into it. The sky is now a pale winter blue, and
the pole is brass rather than silver so it shows against it.

## D5 — Folklore nods, told gently
*2026-11-26*

**Decision:**
- **The cherry tree** (Washington folklore): the tree is in full blossom and unharmed, a hatchet rests against the
  trunk, and a cherry pie (a Washington's Birthday tradition) cools on a stump. A robin and drifting petals keep it
  light.
- **The log cabin** (Lincoln's birthplace): a tall stovepipe hat stands in the cabin's open, lit doorway, with a stack
  of books by the door (a nod to reading by firelight) and a lantern on the step. No person appears.

**What was tried:**
- The hatchet's grey head against the pale sky disappeared. It now overlaps the brown trunk in bright silver with a
  white edge.
- The hat in front of the log wall (charcoal on brown) didn't read as a hat, and at first it was as tall as the door.
  It now stands in the warm doorway, smaller than the door, so its silhouette is clear. It's a lit charcoal with a
  sheen (black is an unlit LED), rim-lit by the lantern once it's lit.

## D6 — Tone curve, steady glows
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors. Glows (the sun, the
moon, the candle, the lantern) are steady; only a few core pixels flicker. Slow light changes (the sunset, the
memorial's lights, the lantern) move in small quantized steps.

**Why:** The value approved on real hardware for Wizarding Thanksgiving. Per-frame flicker on large glows bloated
another app's `.anim` files about threefold. Total `.anim` data is about 0.9 MB.

## D7 — Cards: two lines, the holiday's name in the small font
*2026-11-26*

**Decision:**
- Before the day: `81 DAYS` (big, rows 1–8) over `TO PRESIDENTS' DAY` (tiny, rows 10–15; 67 px plus the shadow, so
  it fits the 72 px width with 2 px to spare).
- On the day, each count slot shows `HAPPY` (big) over `PRESIDENTS' DAY` (tiny) for 5 s, then one word for 3.5 s:
  `LIBERTY`, `UNION`, then `FREEDOM`.
- The clock card shows the time, then the date.
- Colors: cream into gold over a dark-red shadow for the big lines, and a pale red-white for the small line, over
  navy backdrops. The clock backdrop has stars along the top and a stripe ribbon along the bottom row. The count
  backdrop is a dim starry navy with a red glow at the bottom.

**Alternatives:** `PRESIDENTS' DAY` in the big font is 81 px, too wide. `PRESIDENTS'` / `DAY` as two big lines leaves
no room for the count. A brighter red shadow muddied the gold letters on the panel, so it was darkened.

## D8 — START previews the day
*2026-11-26*

**Decision:** START toggles holiday mode: the playlist is picked as if it were Presidents' Day, and the cycle restarts
rotated to begin at the first count slot (`playlist(..., fromCard)`), so the greeting shows at once. Press it again
to go back. The mockup has the same toggle. The handler calls `show.start()` again, which works with the current
runner and with the runner's planned `start(from)`.

**Why:** It lets the day be reviewed on any date, as the playbook requires.

## D9 — The finale's caption is baked into the scene
*2026-11-26*

**Decision:** The finale draws `HAPPY` (big) over `PRESIDENTS' DAY` (tiny) into its frames, after the bunting drops
in. A dark box behind the words keeps the late, smaller bursts from crossing them, and those bursts stay at the
edges. The confetti falls behind the words.

**Why:** The finale is a scene, so it plays all year. A baked greeting is the scene's ending, while the live cards
handle the date.
