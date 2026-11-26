# Decision log — Hanukkah

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — The shared render kit and show runner, Christmas Day's shape
*2026-11-26*

**Decision:** Full-screen 72×16 `.anim` scenes at 15 fps rendered by a Python `renderer/` (GAMMA 0.8), played by
the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `app/src/main.ts` is configuration: scenes from the
generated `show.ts`, a `clock` card and a `count` card, and `steps(t)` from `app/shared/hanukkah.ts`. Dates come
only from `lib/ts/busybar/holidays.ts` (`HOLIDAYS.hanukkah`, `nextOccurrence` with a 9-day span, `daysLabel`).

**Why:** The round-2 playbook's common spec. This is the first app on the shared runner, so it has no playback
loop of its own.

**Alternatives:** Copying Christmas Day's own loop (now superseded by the kit).

---

## D2 — Nine pre-rendered variants of the menorah and of the window
*2026-11-26*

**Decision:** `menorah_0` … `menorah_8` and `window_0` … `window_8` are separate `.anim` files; `steps(t)` picks
tonight's count for both. Variant 0 is the resting menorah: no candles, the shamash unlit.

**Why:** The firmware plays `.anim` files on its own, so the candle count can't be drawn live over a scene. The
window scene shows a menorah too, and a full menorah on night 2 would contradict the menorah scene that just played,
so it follows the count as well. Steady glows keep each variant small (about 50–80 KiB); all 23 scenes and two card
backdrops come to about 1.6 MB.

**Alternatives:** A fully lit window menorah every night (cheaper but inconsistent); drawing candles as live
`xpmbitmap` overlays (no smooth flames, more requests).

---

## D3 — 17:00 is sundown; placed right to left, lit left to right
*2026-11-26*

**Decision:**
- The first candle is lit on the evening of `HOLIDAYS.hanukkah` (the day before 25 Kislev). On that date the
  count is 0 before 17:00 and 1 from 17:00. Each later date adds one at 17:00, and the count stays at 8 through
  the last (ninth calendar) day. The day after, the count is 0 and the countdown to next year starts.
- On night n the candles stand in the rightmost n of the eight cups (positions 9−n … 8, from the viewer's left).
  The shamash, raised 2 px in the middle, is lit first, lifted out, and lights them from left to right: the newest
  candle first. Then it goes back to its holder.

**Why:** The bar has no location or sunset table. Early-December sunsets across most of the US fall between about
16:00 and 17:30, so a fixed 17:00 is a simple, predictable stand-in.
The candle order follows the common custom (add from the right, light the newest first).
Tested at the 2026 boundaries (Dec 4 16:59 → 0, 17:00 → 1, Dec 11 17:00 → 8, Dec 12 23:00 → 8, Dec 13 → 0) and
across the 2027 new year.

**Alternatives:** Sunset by latitude (needs a location the bar doesn't have); switching at midnight (would show the
new candle a whole evening late).

---

## D4 — Card texts
*2026-11-26*

**Decision:** The count card is a `big` headline over a `tiny` line:
- before: `18 DAYS` / `TO HANUKKAH` (`daysLabel`, so `2 DAYS`);
- the day before: `TOMORROW` / `HANUKKAH BEGINS`;
- the first evening's date before 17:00: `TONIGHT` / `HANUKKAH BEGINS`;
- during: `NIGHT 3` / `HAPPY HANUKKAH`, then a second page `NIGHT 3` / `CHAG SAMEACH`;
- after: the count to next year's Hanukkah.

The night number is the candle count, so during the day on Dec 5 it still says `NIGHT 1`. The clock card shows the
time (`clock` font) and then the date (`big`).

**Why:** `HAPPY HANUKKAH` is 83 px in `big`, too wide for one line, but 55 px in `tiny`. Two pages show both
greetings. `TOMORROW` and `TONIGHT` read warmer than `1 DAY` and `0 DAYS`.

**Alternatives:** Scrolling `HAPPY HANUKKAH` in `big` (live text can't scroll smoothly); `DAY 1` during daylight
(the candle count is what the menorah shows).

---

## D5 — Blue, silver and gold; lit flames; no black details
*2026-11-26*

**Decision:** Night-blue backgrounds, a gold menorah, blue and white candles, silver for the shamash, the dreidel's
handle and the snow, gold for gelt and the card's small line. Flames are a yellow base, a near-white core and an
orange tip that sways, above a lit grey-brown wick. The sky behind the menorah is lit navy, never black.

**Why:** The traditional Hanukkah palette, and black is an unlit LED. The flame sits above a wick row so it doesn't
merge into a white candle.

---

## D6 — The dreidel as a turning prism with simplified Hebrew letters
*2026-11-26*

**Decision:** The dreidel is drawn column by column as a square prism: each column shows whichever face is in front
there, with that face's 5×5 letter squeezed by perspective, so the letters slide across as it turns. Letters are
simplified nun, gimel, hei and shin (the diaspora set). Spinning fast, the letters blur out; it stops face-on with
gimel, then `GIMEL!` and `TAKE ALL` while the pot of gelt hops over.

**Why:** A recognizable spin at 16 px, and the letters stay readable when it slows. Gimel is the happy ending.

**Alternatives:** Toppling onto its side (the letter would be unreadable at this size).

---

## D7 — START cycles through the nights
*2026-11-26*

**Decision:** Holiday mode: each START press previews the next night (1, 2, … 8) on any date and restarts the cycle
with that night's menorah, window, count card and the finale. A ninth press goes back to following the date. The
mockup's START button does the same.

**Why:** It lets a reviewer (or anyone, in July) see every night's menorah and both greeting pages without waiting,
with one button.

**Alternatives:** Always previewing night 8 (hides the nights that need checking most).

---

## D8 — Card backdrops and live-text parity
*2026-11-26*

**Decision:** Two 4 s looping backdrops: `clock_bg` (a starry night with a silver shimmer at the edges) and
`count_bg` (the same night with a lit candle at each end). `LAYOUT` in `renderer/scenes/cards.py` holds the four
text styles (`time`, `date`, `head`, `sub`), tone-mapped by `build.py` into `show.ts` and the mockup.
`tests/text_parity.py` checks that the app's `xpmtext` bitmaps and the renderer draw identical pixels.

**Why:** The text band stays calm; candles at the ends fit the 7 px margins that `HAPPY HANUKKAH` leaves.

---

## D9 — The playlist, and the finale only during Hanukkah
*2026-11-26*

**Decision:** A cycle opens with the count card, then alternates scenes with the clock and count cards: menorah,
dreidel, latkes, sufganiyot, gelt, window, and (only while candles are lit, or in holiday mode) the finale. About
2 m 14 s outside Hanukkah and 2 m 52 s during it.

**Why:** Opening on the count card says at once how far off Hanukkah is, or which night it is. `HAPPY HANUKKAH`
fireworks in July would be odd, so outside the holiday the show is a calm countdown.

---

## D10 — The mockup mirrors the app's date logic
*2026-11-26*

**Decision:** `mockup/template.html` has a `<logic>` block that mirrors `app/shared/hanukkah.ts` (and the kit's
Hebrew-calendar rule). `tests/logic.test.mts` runs it against the app's code on every day of 2026–2032 at 00:00,
16:59, 17:00 and 23:59.

**Why:** The simulator then picks the same playlist and card texts as the bar, for the viewer's own date and time.
