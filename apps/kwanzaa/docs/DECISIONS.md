# Decision log — Kwanzaa

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Pre-rendered scenes on the shared show runner
*2026-11-26*

**Decision:** Full-screen 72×16 `.anim` scenes at 15 fps from a Python `renderer/`. They play on the kit's show
runner (`lib/ts/busybar/showrunner.ts`) with live-text cards between them. `app/src/main.ts` is configuration only:
the cards, `steps(t)` and holiday mode. The date logic lives in `app/shared/kwanzaa.ts`, where it can be tested.

**Why:** This is the round-2 common spec. The runner already handles one request in flight, page timing, minute
rollovers and the buttons. The firmware plays `.anim` files smoothly with no requests.

**Alternatives:** Copying Christmas Day's own playback loop (round 1, before the runner existed).

---

## D2 — Six scenes, with the kinara first in every cycle
*2026-11-26*

**Decision:** The cycle is: the day's kinara, clock, The Harvest, count, The Unity Cup, clock, Drums and Dance,
count, The Kente Weave, clock, The Karamu Feast, count. Scenes run 14–16 s, and a loop takes about 2 m 17 s.

**Why:** The kinara is the heart of the holiday and changes every day, so it opens each cycle. Each count card
(the principle of the day during Kwanzaa) follows a scene, three times per loop. The playbook suggested six scene
ideas, and all six fit: the kinara, the mazao and muhindi, the kikombe cha umoja, drums and dance, a kente-inspired
weave and the karamu. The karamu closes the loop because it is the feast near the end of Kwanzaa.

**Alternatives:** Playing the karamu scene only on December 31. Rejected because it is one of the strongest scenes,
and its own caption already says `DEC 31`. On December 31 the count card adds `KARAMU` / `DAY 6: THE FEAST`.

---

## D3 — Candle lighting order: the official Kwanzaa website
*2026-11-26*

**Decision:** Candle positions, left to right: red, red, red, black, green, green, green. Lighting order by day:
the black (center) on day 1, then far-left red, inner green, middle red, middle green, inner red, far-right green.
Each day relights all the candles lit so far (`LIGHT_ORDER` in `renderer/kfx.py`).

**Source:** officialkwanzaawebsite.org, "The Celebration" (Candle Lighting). It places the black candle in the center
for Umoja. The three red candles go to its left, for Kujichagulia, Ujamaa and Kuumba. The three green candles go to
its right, for Ujima, Nia and Imani. The page says: "The black candle is lit first on the first day of the
celebration." and "The remaining candles are lit afterwards from left to right on the following days."

**How we read it:** Each day lights its own principle's candle, so the colors alternate: red on day 2
(Kujichagulia), green on day 3 (Ujima), red on day 4, green on day 5, red on day 6, green on day 7. That matches the
brief ("alternately, starting with red"). Within each color, "from left to right" sets the position. The reds go
outer, middle, inner in the order the site lists them, and the greens go inner, middle, outer. So day 2 is the
far-left red, and day 7 is the far-right green.

**Alternatives:** Other sources light from the inside out (the red next to the black, then the green next to it), or
light strictly left to right. Both conflict with the official page.

---

## D4 — Eight kinara renders; the day changes at local midnight
*2026-11-26*

**Decision:** Render `kinara_0` (unlit, captioned `DEC 26`) and `kinara_1` … `kinara_7`. The app's `steps(t)` picks
scene index = day of Kwanzaa from the bar's local date. `kwanzaaDay` uses the kit's
`nextOccurrence(t, HOLIDAYS.kwanzaa, 7)`, which handles the span across the new year. The day changes at local
midnight.

**Why:** Each variant is a story: the taper lights the candles one by one, at most 1.4 s apart, so day 7 fits in the
lighting window. Most pixels are static, so the eight variants together take about 470 KiB. Families light the
candles in the evening, but the show runs all day, and showing the day's principle and candles from midnight matches
how the days are named. Unlike Hanukkah, no day starts at sundown here.

**Alternatives:** A single kinara with live-drawn flames (timer-driven redraws run at about 3 fps, too choppy for
flames). A sundown switch (no basis in Kwanzaa practice).

---

## D5 — The black candle is lit charcoal with a highlight
*2026-11-26*

**Decision:** The black candle is charcoal `#403E48` with a lighter left edge `#8A8896`, and a darker base pixel.
Wherever the weave and the borders use "black", they use the same charcoal.

**Why:** Black is an unlit LED (AGENTS.md). A true black candle would read as a gap in the kinara. Charcoal with a
highlight reads as a dark candle next to the red and green ones (checked in the review strips).

---

## D6 — Card texts: Habari gani? and the principle of the day
*2026-11-26*

**Decision:**
- Before Kwanzaa: `N DAYS` / `TO KWANZAA`, then `KWANZAA` / `DEC 26 - JAN 1`.
- During Kwanzaa: `HABARI GANI?` / `WHAT'S THE NEWS?`, then the answer. The answer is the Swahili principle in `big`
  over its English in `tiny`. Last comes `KWANZAA` / `DAY N OF 7`, or `KARAMU` / `DAY 6: THE FEAST` on December 31.
- The English that doesn't fit one tiny line (18 characters) takes a second page with the same Swahili word:
  `COLLECTIVE WORK` / `AND RESPONSIBILITY`, and `COOPERATIVE` / `ECONOMICS`.
- After January 1, the card counts to next year's Kwanzaa (`358 DAYS`). There is no separate "after" message.

**Source:** the names and translations come from officialkwanzaawebsite.org, whose "The Celebration" page lists each
principle with its English meaning. Its "The
Greetings" page gives the greeting: "Habari gani?", and the answer is the day's principle. "What's the news?" is
the usual English gloss of "Habari gani?".

**Why:** The greeting and its answer make a natural two-page card, and they teach the principle as it is used. The
English is never abbreviated, so it stays accurate.

**Note:** With the original runner, the repeated Swahili word faded in again on the second page. The runner update
in the kit (it keeps lines whose text and style don't change) fixed this, so the word now stays on screen.

---

## D7 — Holiday mode on START: preview day 1 to 7, then back
*2026-11-26*

**Decision:** The first START press previews day 1 of Kwanzaa (its kinara and its cards) on any date. Each later
press moves to the next day. After day 7, the next press returns to the real date. Each press restarts the cycle
from the kinara. The mockup has a START button with the same behavior, plus a day menu.

**Why:** Reviewing all seven days quickly, without waiting for December, is what holiday mode is for. Kwanzaa has
seven distinct days, so a simple on/off toggle would show only one of them.

**Alternatives:** An on/off toggle that shows day 1 only. A long press to leave the mode (the runner reports long
presses as ignored, but a single key with a clear cycle is easier to explain).

---

## D8 — People: simple figures with a range of warm skin tones
*2026-11-26*

**Decision:**
- Figures are drawn by `person()` in `renderer/kfx.py`: a 3×3 head, a 3 px garment with a gold band, and 1 px arms
  posed by angle.
- Five lit skin tones, from deep brown to light brown, are spread across every group.
- Headwear is varied and brightly colored: gele headwraps, kufi caps, and lit hair (the elder's is silver). The
  default hair color is a lit brown, never near-black.
- Faces have no eyes.

**Why:**
- Respectful and celebratory, with no caricature: features aren't drawn at all.
- A 3×3 face has no room for lit eyes, and dark pixels would read as holes.
- The garments carry the red, green and gold colors.
- Every figure stands against a warm wall light or a dusk sky, so deep skin tones stay visible.

---

## D9 — An original kente-inspired weave
*2026-11-26*

**Decision:** Three original 8×16 strip motifs (`KENTE_MOTIFS` in `renderer/kfx.py`) are set side by side. They use
only red, charcoal, green and gold:
- gold ground with bars;
- green ground with a gold zigzag and red diamonds;
- red ground with gold ladders.

The weave scene, the card borders, the mat stripes and the karamu table runner all use them.

**Why:** Kente's look comes from narrow woven strips sewn edge to edge. These motifs suggest it without copying
any named traditional cloth design. The colors are Kwanzaa's (black, red, green) plus gold.

---

## D10 — Tone curve GAMMA = 0.8
*2026-11-26*

**Decision:** Use the tone curve approved on hardware for Wizarding Thanksgiving. It applies to every frame and to
every live-text color.

**Why:** The bar, the mockup and the strips stay identical, and re-tuning without the device would be guesswork.

---

## D11 — Card layout and colors, checked by a parity test
*2026-11-26*

**Decision:**
- The card backdrop is a dark, lit plum-brown field with a slow warm glow. Kente borders glide along rows 0 and 15.
- `head` text is `big` on rows 1–7: gold with a red shadow. `sub` text is `tiny` on rows 9–13: pale green with a
  dark-green shadow.
- The clock is gold-white with a red shadow. The date is gold with a green shadow.
- The styles, timings and principles live only in `renderer/scenes/text.py` and are exported into `show.ts`.
- `tests/text_parity.py` checks two things: the app's pixels match the renderer's for every text the app can draw,
  and `countPages` in `kwanzaa.ts` matches `count_pages` in `text.py` for every day.

**Why:** Red, black (as the dark field), green and gold, with nothing on the text rows, so the widest words
(`KUJICHAGULIA`, 67 px; `SELF-DETERMINATION`, 71 px) stay readable edge to edge.

---

## D12 — Captions sit clear of the action
*2026-11-26*

**Decision:**
- Kinara: `DAY N` sits top left over the basket, and `DEC 26` top right over the cup. Asserts keep both clear of
  the candles.
- The harvest caption sits over a darkened left panel.
- `HARAMBEE!` appears only after the three pulls, over a dimmed top band.
- The karamu title shows over the empty table, before the family arrives.
- The scene's own `HAPPY KWANZAA` was dropped, because it covered the seated figures. The kente scene says
  `HAPPY` / `KWANZAA`.

**Why:** These are round-1 lessons: dim the art behind words, and don't let text cover the characters at their key
moment.

---

## D13 — The mockup runs the app's own date logic
*2026-11-26*

**Decision:** `build.py` strips the TypeScript types from `lib/ts/busybar/walltime.ts`, `lib/ts/busybar/holidays.ts`
and `app/shared/kwanzaa.ts` with Node 24's `stripTypeScriptTypes`, drops the imports, and inlines the result into
the mockup as a `KW` object. The approach comes from New Year's Eve. The mockup's day of Kwanzaa, count pages,
playlist and holiday-mode cycle all come from `KW`. `kwanzaa.ts` reads the global `SHOW`, which the mockup data
defines with the same fields as `show.ts`.

**Why:** It replaces a hand-written JavaScript mirror that could drift from the tested app code. The mockup now
shows exactly what the bar would.

---

## D14 — Both candle orders, chosen in the app's settings
*2026-11-26*

**Decision:** The app has a setting, `app/src/appmeta/settings.json`, field `lighting_order`, labeled "Candle order".
It can be edited on the bar under Apps → Kwanzaa → Setup.
- **Official site** (`official`, the default) is D3's order, which keeps D3's sourcing.
- **From the center** (`center_out`): the black candle first, then red and green alternately, moving outward. Day
  2 is the red next to the black, day 3 the green next to it, day 4 the middle red, day 5 the middle green, day 6
  the outer red, and day 7 the outer green.

How it works:
- `main.ts` reads the setting once at start with the kit's `loadSettings`, through `loadOrder` in
  `app/shared/kwanzaa.ts`. Any failure (no response, a different settings version, an unknown or mistyped value)
  gives the default.
- `cycleSteps(day, order)` picks the kinara through `SHOW.kinara[order][day]`.
- The renderer draws `kinara_center_2` … `kinara_center_7`. The unlit kinara and day 1 are the same in both orders,
  so they reuse `kinara_0` and `kinara_1`.

**Why:**
- The user asked for both orders, because families light the candles differently.
- Days 6 and 7 end with the same candles lit in both orders, but they are still rendered twice. The scene shows the
  taper lighting the candles one at a time, and on those days the order of lighting differs, which is the whole
  point of the setting. The extra cost is about 170 KiB.
- The karamu scene's small kinara shows day 6, and it lights the same six candles in both orders, so it needs no
  variant.
- The six extra renders take total `.anim` data from about 1.1 MB to about 1.5 MB.

**Alternatives:**
- Reusing day 6 and 7 from the official order. Rejected: the setting would then light those days in the wrong
  order.
- Drawing the flames live. Rejected: too slow on the device (D4).
- Picking the order with a button. Rejected: a setting persists, and START is already used for holiday mode.
