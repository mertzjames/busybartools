# Decision log — Easter

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`, `GAMMA = 0.8`)
with live-text cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts`
is configuration: scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/easter.ts`.
The app's shape (renderer, `app/shared/` logic module, mockup with inlined logic, tests) follows MLK Day, the other
single-day app of this round.

**Why:** It is the round-2 common spec, and the runner already handles one request in flight, card pages, fades and
the minute rollover.

## D2 — The cheerful, secular side of Easter
*2026-11-26*

**Decision:** The show is about spring and the family traditions everyone shares: an original cartoon bunny, egg
hunts, chicks, painted eggs, flowers, a basket with a chocolate bunny. The bunny, chick and kids are original, generic
designs (no licensed characters).

**Why:** The brief asks for a family-friendly, cheerful show for every household, with any religious imagery kept
respectful and optional.

## D3 — One calm traditional note: a sunrise with Easter lilies, and no cross
*2026-11-26*

**Decision:** The finale, "Easter Sunrise", is the one calm scene: dawn over spring hills, the sun rising, white
Easter lilies opening. There is no cross or other explicitly religious symbol anywhere.

**Why:** The brief allows at most a gentle sunrise with a lily or a simple cross on a hill. The sunrise and the lily
honor the Christian tradition (sunrise services, the lily as a symbol of the resurrection) while still reading as
spring to everyone, so the scene fits a show that is otherwise secular. A cross would make the app explicitly
religious and is easy to get wrong at 16 px.

**Detail:** The first lily design (a 5-px tall white bar beside a stem) read as a small white cross on the LEDs. It
was redrawn as a sideways trumpet with petal tips curling out and gold stamens, so it reads as a flower.

**Alternatives:** a simple cross on a hill (left out, as above); no traditional note at all (the sunrise is a natural
finale and the lily is a widely loved Easter flower).

## D4 — Pastels that stay lit, and color contrast rules
*2026-11-26*

**Decision:**
- The six egg pastels (pink, blue, mint, lemon, lilac, peach) each keep one channel high and another well below it,
  so they read as colors on the LEDs, not as white. Each has a deeper accent of the same hue for patterns
  (`efx.ACCENT`).
- Pastels sit on deep backdrops where possible (the nest, the painting table, the basket and all three cards use a
  deep violet), which is where they read best.
- In the daytime garden, the sky is a clear mid blue (never so pale that cream or white reads as sky), and no blue egg
  sits against it: the first bunny scene's third egg was blue and vanished into the sky, so it became lilac.
- The middle egg in the nest is mint, not cream, so the yellow chick stands out from its shell.

**Why:** Round-1 and round-2 contrast traps (an orange cat on red brick, green on green). Checked in LED review
strips.

## D5 — Small features are lit; kids are faceless profiles
*2026-11-26*

**Decision:**
- The bunny's eye is a lit deep violet (`#40247A`), the chick's a lit brown (`#50280A`), and the egg crack a plum
  line. Nothing small is near-black.
- The crack is a stepped line (two pixels up, two down). An alternating one-pixel zigzag read as a checkerboard and
  disappeared.
- The kids in the egg hunt are 4 px wide and 10 rows tall, in profile, with a hair cap and plain lit skin: no eyes
  or mouth. They have two different skin tones, light shirts (mint, pink) that read against the sky, and lit white
  shoes against the grass.
- The bunny got a few shade pixels for its haunch and neck, so its head reads apart from its body.

**Why:** Black is an unlit LED (AGENTS.md). Faces at this size become dark holes or "three eyes".

## D6 — Seven scenes, morning to sunrise, about 108 s
*2026-11-26*

**Decision:** The Bunny's Garden, The Egg Hunt, Chicks Hatching, Painting Eggs, Spring Flowers, The Easter Basket,
Easter Sunrise. The bunny hides the eggs and the kids find them (a small story across scenes 1 and 2); the indoor
scenes (nest, table, basket) alternate with garden scenes; the sunrise closes with `HAPPY EASTER`.

**Why:** The brief's seven ideas all made distinct, readable scenes, and the whole show (with cards) is about
2 m 40 s per loop. The total `.anim` data is about 0.45 MB, far under the 3 MB budget.

**Finale text:** `HAPPY EASTER` (69 px in `big`) spans the sky. The sun rises at x = 32, exactly in the gap between
the two words, so the greeting never covers it, and the sky behind each word is softly darkened (`efx.dim_rect`).

## D7 — Card styles and backdrops
*2026-11-26*

**Decision:**
- Styles (`renderer/scenes/text.py`): `time` (clock font), `date`, `head` (big) in cream into sunny yellow; `sub`
  (tiny) in pastel pink; on the day, `top` (`HAPPY`, pink) and `bot` (`EASTER`, lemon), two `big` lines at rows 0
  and 8. Every shadow is a lit deep violet.
- Three backdrops: the clock's spring evening (grass, soft stars, two tiny eggs in the corners), the countdown's two
  big decorated eggs at the ends, and the holiday's pastel confetti drifting down both edges.
- Each backdrop declares the free columns its text must fit (`TEXT_GAP`), and `tests/text_parity.py` checks every
  card text (with its shadow) stays inside them.
- The backdrops are steady 4 s loops with only small moving parts (stars, a glint, confetti), which keeps them small.

**Why:** Pastel text on a deep backdrop is the clearest combination; the edge art makes the cards feel like Easter
without crossing the words.

## D8 — The on-the-day cards
*2026-11-26*

**Decision:** On Easter Sunday the three count slots become `day0`–`day2`: each opens with `HAPPY` / `EASTER`, then
a cheerful extra page: `EGG HUNT` / `TIME!`, `HOPPY` / `EASTER!`, `SPRING IS` / `HERE!`. The text lives in
`app/shared/easter.ts` (`DAY_CARDS`); `DAY_TEXT` in `renderer/scenes/text.py` is a review copy, and the parity test
checks they agree.

**Why:** The brief asks for HAPPY / EASTER plus a cheerful extra page. Three different extras keep the day from
repeating within one loop. "HOPPY EASTER" is a well-known pun; if it reads as a typo to reviewers, swap it.

**Countdown length:** after Easter the count is to next year's, which can be up to 399 days (a late Easter followed by
an early one: 384 days after Easter 2027). The tests check `399 DAYS` fits and that no day in 2026–2040 exceeds it.

## D9 — START previews the day; one source of date logic
*2026-11-26*

**Decision:**
- START toggles holiday mode (`show.input(e) === "ignored" && e.key === "start" && e.action === "short"`), then calls
  `show.start()` again. The new cycle is rotated to begin at the first count slot (`playlist(…, fromCard)`), so the
  greeting shows at once. This works with or without the runner's planned `show.start(from)`.
- Dates come only from the kit: `nextOccurrence(t, HOLIDAYS.easter)` and `daysLabel`. No year is hard-coded.
- The mockup runs the app's own logic: `build.py` type-strips `walltime.ts`, `holidays.ts` and `easter.ts` with
  Node 24 and inlines them. `tests/logic.test.mts` runs that inlined block with `new Function` and compares it with
  the app's TypeScript on every day of 2026–2030.

**Why:** The round-2 discoveries; it keeps the device, the mockup and the tests from drifting apart.

## D10 — Size and steadiness
*2026-11-26*

**Decision:** The sun in the garden scenes has no turning rays, the sunrise sky warms in 24 quantized steps, and
glows hold steady between frames. Total `.anim` data is about 450 KiB (the sunrise is the largest at about 165 KiB).

**Why:** Round-2 discovery: per-frame changes over large soft areas multiply the file size.

## D11 — The bunny's ears stay on when it bends down
*2026-11-26*

**Decision:** in the bunny's head-down frame (frame 3, used when it bends to hide an egg), the ears move down a row
with the head.

**Why:** the head dropped one row but the ears stayed where they were, which left a row of sky between them. Review
feedback caught it: on the panel the ears looked detached.

**Alternatives:** keeping the ears up and stretching them a pixel longer would also close the gap, but would make the
bunny look taller while it crouches.
