# Decision log — Advent Calendar

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — The loop: door, vignette, countdown card
*2026-11-25*

**Decision:** Each pass of the show is three steps: a 3 s door intro that reveals the date, the day's vignette
(8 s; 9 s on Dec 24, 10 s for the finale), and a 5.5 s countdown card. Then it repeats.

**Why:** It reads like opening an Advent calendar every time someone looks up, keeps the day's animation coming back
every ~16 s, and always ends on useful information (how long until Christmas).

**Alternatives:** Play all opened days in sequence (today's vignette would be rare by late December); a clock card
like Wizarding Thanksgiving's (the countdown matters more here than the time).

## D2 — 25 vignettes that build toward Christmas
*2026-11-25*

**Decision:** One original vignette per day, Dec 1–24, plus a Dec 25 finale. The first week is quiet objects
(snowflake, mittens, cocoa, candy cane, bells, ornaments, candles), the second animals and treats, the third
characters (snowman, toy soldier, sledding, carolers, nutcracker, presents, reindeer), and the last days tell one
story: the North Pole, the tree is decorated (22), the sleigh flies (23), the star goes on top (24), and everything
comes together on Christmas morning (25).

**Why:** Escalation gives a reason to come back each day and makes the last week feel like an event.

## D3 — One shared door animation, with the date drawn live
*2026-11-25*

**Decision:** `door.anim` is the same for every day: a ribboned door swings open onto a starry night, and the app
writes `DEC N` into the opening at 1.4 s (`SHOW.door.text_ms`).

**Why:** 25 baked doors would add about 1 MB for almost no visible difference. With live text the door also works
for any browsed day.

**Alternatives:** A number painted on each door (needs 25 files, or a live overlay that would have to vanish exactly
as the door starts to swing, which network latency makes unreliable).

## D4 — Live text: xpmbitmaps in the shared fonts, with a parity test
*2026-11-25*

**Decision:** Every date and countdown is an `xpmbitmap` from the shared kit's `textBitmap`, using the `big` and
`tiny` fonts and the styles in `renderer/scenes/text.py`: `date` (intro), `head` + `sub` (number over caption), and
`top` + `bot` (two big lines, for `MERRY / CHRISTMAS` and `SEE YOU / NEXT YEAR!`). `tests/text_parity.py` runs the
app's TypeScript and compares its bitmaps with `font.draw_text`, pixel for pixel. Text fades in with three opacity
steps, like Wizarding Thanksgiving.

**Why:** Matches the mockup and the rest of the collection, with gold and ice gradients and shadows.

**Alternatives:** The firmware's `countdown` element: it would tick by itself, but only in a built-in font, and it
counts to a Unix timestamp while every rule here is about the bar's local calendar date.

## D5 — Seasons follow the bar's local date
*2026-11-25*

**Decision:** Jan 1–Nov 30 shows the Winter Night scene and `N DAYS / TO ADVENT` (no door: nothing has opened yet).
Dec 1–23 counts days to Christmas; Dec 24 counts time; Dec 25 is the finale with its door and `MERRY / CHRISTMAS`;
Dec 26–31 loops the finale with `SEE YOU / NEXT YEAR!`. Day counts are calendar days (`walltime.daysUntil`), so
"1 DAY" means tomorrow, with a singular. Only `device.TimeGet()`'s wall-clock fields are used.

**Why:** Families think in calendar days, and the bar's local date is the only one that matters to the person
looking at it. JS `Date` local methods don't know the bar's time zone.

## D6 — Christmas Eve counts hours and minutes, rounded up
*2026-11-25*

**Decision:** On Dec 24 the card shows the time left until local midnight as `HH:MM`, with minutes rounded up (at
17:18:30 it shows `06:42`; in the last minute, `00:01`). If the minute changes while the card is up, the app redraws
the text in place at the boundary (`msUntilCardChange`) without another request. At 00:00:00 on Dec 24 it shows
`24:00`.

**Why:** Rounding up never shows `00:00` before Christmas has arrived. The 7×12 clock font can't fit a caption
under it, so the 5×7 `big` font carries the time.

## D7 — The encoder browses opened doors, clamped
*2026-11-25*

**Decision:** The encoder steps through days 1..today (all 25 after Christmas, none before Advent) and stops at
both ends rather than wrapping. A browsed day plays door, vignette and card; landing back on today resumes following
the real date. OK returns to today. The countdown card always describes the real today, even while browsing.

**Why:** It's an Advent calendar: you can reopen old doors but not peek ahead. Clamping makes "turn left a lot" a
reliable way back to Dec 1.

## D8 — Logic is pure TypeScript, and the mockup mirror is tested against it
*2026-11-25*

**Decision:** Season, countdown text, the show sequence and browsing live in `app/shared/advent.ts` as pure
functions of a `LocalTime`. The mockup can't import TypeScript, so `mockup/template.html` carries a JavaScript
mirror in a marked `<logic>` block. `tests/advent.test.mts` extracts it and checks that it agrees with the app at
four times on every day of 2026–2028 (including a leap year), and that its text drawing is pixel-identical.

**Why:** A reviewer can trust that the mockup's date slider shows what the bar will show on that date.

## D9 — Same tone curve as the rest of the collection (GAMMA 0.8)
*2026-11-25*

**Decision:** `GAMMA = 0.8` in `renderer/build.py`, applied to every frame and every live-text color.

**Why:** This is the value approved on real hardware for Wizarding Thanksgiving. One tone curve keeps the
collection consistent on the same panel.

## D10 — LED readability fixes found in review
*2026-11-25*

**Decision:** These changes came from reviewing every scene as LED-style strips:
- Mittens and the cocoa mug lost their white dot patterns. Two light dots on a red shape read as a face. They now
  use a solid band and a single heart.
- The penguin stands on a daylight sky. A navy body against a night sky read as a hole.
- The sled rider's coat is blue. With a red hat on a green coat, the rider read as a tiny Christmas tree.
- The snowman's top hat is a lit slate blue with a red band. Near-black disappeared against the sky.
- The wreath's bulbs are warm white, gold and red at full opacity. Cool colors and blended bulbs vanished into the
  green.
- The finale dims the scene before `HO HO HO!` so the text reads (a tip from the Wizarding Thanksgiving work).

**Why:** Black is an unlit LED, and small light details on a dark sprite turn into eyes.

## D11 — Sprites live next to their scene; final-week props are shared
*2026-11-25*

**Decision:** Each scene defines its own sprites. The tree, star, sleigh team and gifts are in `renderer/props.py`
because days 22–25 reuse them. `review.py sprites` collects every sprite for a contact sheet.

**Why:** Most sprites appear exactly once. Sharing only the story props keeps the last week visually continuous.

## D12 — Time is read once per pass and once per card
*2026-11-25*

**Decision:** The app calls `TimeGet` at the start of every pass (to choose the door and scene) and again when a
card appears (for an accurate countdown). Midnight needs no special handling: the next pass picks up the new day.

**Why:** Two requests per ~16 s pass is light on the bar's web server, and the card is never more than a few
seconds stale.

---

## D13 — First catalog screenshots show the pre-Advent loop
*2026-11-27*

**Decision:** Version 1.1.0, the first one in the BUSY Apps Catalog, ships with two screenshots captured on a bar
before December 1: the Winter Night cabin (the cover) and the "4 DAYS / TO ADVENT" card. After December 1, capture
several real doors on the bar and publish 1.1.1 with them, since catalog screenshots only change with a new version.

**Why:** The catalog asks for screenshots captured on a bar or in the official emulator, and before Advent the app
shows only this loop. Submitting now lets review start before the first door opens.

**Alternatives:** Setting the bar's clock to December, or adding a preview mode that opens any door on any date.
Both would have delayed submission past December 1.
