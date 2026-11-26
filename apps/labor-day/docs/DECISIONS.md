# Decision log — Labor Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, and cards and a `steps(t)` playlist from `app/shared/laborday.ts`. The date
comes only from the kit (`nextOccurrence(t, HOLIDAYS.laborDay)`); no year is hard-coded.

**Why:** The round-2 common spec. The structure follows Presidents' Day, the other single-day, floating-Monday
holiday app, so the two read the same to maintainers.

## D2 — A tribute to workers, then the day off; generic, inclusive and non-partisan
*2026-11-26*

**Decision:**
- The first half honors work (building, the trades, farming); the second half is how the day is spent (a cookout,
  the beach, fireworks). The finale thanks workers in words.
- Workers are generic: plain skin-tone faces with no features, a range of skin tones, men and women, told apart by
  hats and tools. No real people and no likenesses.
- No union or company logos, no brand trade dress (the tractor is a plain red, not a maker's color scheme), and no
  slogans. Nothing partisan: the words on screen are `THANK YOU`, `WORKERS`, the greeting, the countdown and three
  short phrases on the day.
- The nurse wears teal scrubs and a plain white cap with **no red cross**: the Red Cross emblem is legally protected.

**Why:** The brief: a tribute to American workers that opens into the relaxed end of summer, non-partisan, with no
logos and no real people.

## D3 — Six scenes, sunrise to fireworks
*2026-11-26*

**Decision:** Topping Out, Parade of Trades, Harvest Time, Backyard Cookout, Last Swim of Summer, Thank You,
Workers (14 s each, 84 s of scenes). The order follows one day's light: sunrise, midday, golden hour, dusk, sunset,
night.

**Alternatives:** A seventh scene, a lineworker restoring power at dusk as a town's windows light up. It didn't fit
the time-of-day order (it would fall between the sunset and the fireworks and slow the ending), and six scenes give
exactly three count slots, one for each on-the-day card (D7). It's a good candidate if the show is extended.

## D4 — Topping out: the last beam goes up white, with a flag and an evergreen
*2026-11-26*

**Decision:** The first scene shows the ironworkers' topping-out tradition: the final beam of a building is painted
white and raised with a small US flag and an evergreen tree on it. A yellow tower crane lifts it into a steel frame
at sunrise, two ironworkers in hard hats guide it, and one welds it in a shower of sparks.

**What was tried:**
- Rust-red steel against the sunrise vanished (same hue). The frame is a lit slate silhouette with a faint warm rim
  on its top edges, so it reads against the orange sky; the crane is hard-hat yellow, which reads against the blue
  top of the sky.
- A sun behind the frame, with a big glow, saturated into a pale blob. The sun is now left of the frame with a
  smaller glow, and the sky is quantized to 40 steps as it brightens.
- Orange-vested workers on the pink-orange sky vanished; they wear bright blue shirts, with yellow and white hats.

## D5 — A parade of trades you can read at 3 pixels wide
*2026-11-26*

**Decision:** Six front-facing workers, 12 rows tall, each told by a hat and a tool:

| Trade | Hat | Clothes | Tool |
|---|---|---|---|
| Nurse | small white cap | teal scrubs | a clipboard |
| Teacher | silver hair in a bun | purple cardigan | an apple and a book |
| Farmer | wide straw hat | red shirt, denim overalls | a pitchfork |
| Builder | yellow hard hat | hi-vis orange vest with a silver stripe | a hammer |
| Mechanic | red ball cap | blue-grey coveralls | a wrench |
| Chef | tall white toque | whites | a spatula |

Heads sit against the sky and bodies against a mid-green tree line, so every skin tone, the whites and the hi-vis
colors stand out. The teacher has dark skin and silver hair (dark hair on dark skin reads as one blob).

## D6 — The finale: a crowd of workers watches the fireworks over the finished tower
*2026-11-26*

**Decision:** The tower from "Topping Out" stands finished, windows lit and its flag on the roof. Workers in hard
hats, caps and hair seen from behind (no faces) cheer along the bottom. Bunting drops in at 8.6 s, then one big word
at a time over a dimmed panel: `THANK YOU`, then `WORKERS`.

**Why:** People seen from behind read clearly and need no faces. The crowd (rows 11–15), the bunting (rows 0–2) and
one big line of text (rows 3–10) share the screen without overlapping; two lines wouldn't leave room for the crowd.

## D7 — Cards: two big lines; dark backdrops
*2026-11-26*

**Decision:**
- Every countdown and day card is two lines of the `big` font at y 0 and y 8, which fill the 16 rows exactly. The
  widest text, `TO LABOR DAY`, is 67 px; the longest count, `370 DAYS` (the day after Labor Day 2025), is 45 px.
- First line: hard-hat gold over a dark brown shadow. Second line: a summer-sky blue over a navy shadow.
- On the day the count slots become `HAPPY` / `LABOR DAY`, then a phrase: `THANK YOU` / `WORKERS`, `ENJOY` /
  `THE DAY`, `SO LONG` / `SUMMER`. The brief's "ENJOY THE DAY" is 73 px in `big`, so it's split over two lines.
- The clock backdrop is a night over a dim skyline with a crane at the right edge whose red light blinks; its jib
  was shortened to columns 66–71 so the widest date (columns 8–64) never touches it. The countdown backdrop is a
  dim indigo night with an ember glow along the bottom, because the text covers all 16 rows.

**Alternatives:** `tiny` for the second line (as Presidents' Day does). The big font is far easier to read on LEDs,
and here it fits.

## D8 — START previews the day; the cycle restarts on a card
*2026-11-26*

**Decision:** START (short press) toggles holiday mode: the playlist uses the on-the-day cards on any date. It calls
`show.start()` again with a playlist rotated to begin at the first count slot, so the change shows at once. The
playlist logic is a pure function in `app/shared/laborday.ts`, tested against 2027-09-06, 2028-09-04 and
2029-09-03, the days before and after, and holiday mode.

## D9 — Tone curve and size
*2026-11-26*

**Decision:** `GAMMA = 0.8` (the curve approved on real hardware for Wizarding Thanksgiving), applied to frames and
live-text colors alike. Slow light changes (the sunrise, the dusk at the cookout, the sunset) are quantized to 32–40
steps and glows stay steady between steps. Total `.anim` data is about 0.9 MB.

## D10 — Contrast fixes found in review
*2026-11-26*

**What was tried, and what changed:**
- **Harvest:** golden bales on a golden field vanished. The stubble is now a browner ochre, the windrow a bright
  straw line ahead of the baler, and the bales pale straw with a darker spiral. A two-stop sky went grey in the
  middle; it now has three stops (blue, lavender-rose, peach, then an orange band at the horizon).
- **Cookout:** a white picket fence and the bodies in front of it merged into the peach sky. The fence is now a lit
  wooden privacy fence; an orange shirt on it became pink.
- **Beach:** a sandcastle the color of the sand vanished; it's now darker wet sand with a red pennant.
- **Birds** drawn as five-pixel wings read as a dark cloud; they're three pixels, flapping.

## D11 — The mockup runs the app's own logic
*2026-11-26*

**Decision:** `renderer/build.py` type-strips `walltime.ts`, `holidays.ts` and `app/shared/laborday.ts` with Node 24
and inlines them into the mockup (as Presidents' Day does). A Node test extracts that block from
`mockup/index.html` and checks it gives the same countdown, playlist and card pages as the app for every day of
2026–2029, with and without holiday mode.
