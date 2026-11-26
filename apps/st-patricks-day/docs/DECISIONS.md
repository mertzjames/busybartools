# Decision log — St. Patrick's Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/stpatricks.ts`. The structure
follows MLK Day's (round 2), which was the first app on the runner.

**Why:** It is the round-2 common spec, and the runner already handles one request in flight, card pages, fades and
the minute rollover.

## D2 — Festive and family-friendly: folklore and heritage, no drinking, no caricature
*2026-11-26*

**Decision:**
- The show celebrates the day through folklore (a leprechaun, a rainbow, a pot of gold, shamrocks, a four-leaf
  clover) and heritage (the Irish tricolor, a piper in a saffron kilt, a drummer, Celtic knotwork, the green river).
- Nothing about drinking: no beer, pints, toasts or drunkenness in the art or the words.
- No "fighting Irish" figure and no stage-Irish clichés. The leprechaun is cheerful and dances; he doesn't brawl
  or guard his gold.

**Why:** The brief: a warm, family-friendly celebration of Irish heritage without stereotypes.

**Considered and left out:** "TOP O' THE MORNING" as a caption (a stage-Irish phrase rarely used in Ireland), and
`SLAINTE` (a toast; see D8).

## D3 — Seven scenes, the jig first and fireworks last
*2026-11-26*

**Decision:** The Leprechaun's Jig, Rainbow's End, The Shamrock Field, The Parade, The Green River, The Celtic Knot,
The Finale (104 s of scenes; about 2 m 34 s per loop with cards). All seven proposed scenes made it.

**Why:** The jig introduces the main character; the rainbow brings him back at the pot of gold; the quieter field
and the busier parade alternate; the knot carries the greeting; the finale ends loud. Seven scenes give four clock
and three count slots.

**Alternatives:** Dropping the river or the knot for a six-scene show. Both were kept: the river is the most
recognizable modern custom, and the knot is the most "Irish design" scene without any figure.

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — An original leprechaun, and keeping green off green
*2026-11-26*

**Decision:**
- The leprechaun (`renderer/pfx.py`, `leprechaun()`) is 11 × 14, front view: a tall green hat with a lit dark-green
  band and a gold buckle, ginger hair and beard, rosy nose, **lit blue eyes**, a green coat with a gold button and a
  brown belt, green breeches, white stockings and brown shoes. Arms (`hips`, `up`, `out`, …) and legs (`stand`,
  `kick_l`, `kick_r`, `click`, `tuck`) are separate poses, so the jig is built from them.
- No black anywhere: eyes, hat band, shoes and the iron pot are lit colors.
- Green figures never stand on green of the same brightness. The jig's far hills are a dim teal, the near hill is
  only the bottom rows; the shamrock field sits on near-black soil-green; the parade street is dark slate under a
  lighter dusk sky.

**What was tried:** The first jig background had bright green rolling hills: the coat and legs dissolved into
them. The first parade had colorful shopfronts with lit windows and a crowd in front: the marchers were lost in the
clutter. Both were simplified.

## D6 — An original knot: a two-cord plait
*2026-11-26*

**Decision:** The Celtic Knot scene is an original pattern, not a copy of a historical or published knot: two cords
(gold and green) swing either side of a rounded-rectangle path around the display edge and cross every half period
(16 periods per lap). At each crossing the cord underneath breaks for a pixel either side, and which cord is on top
alternates, so the cords go over, under, over… like real knotwork. The cords are laid progressively, with a sparkle
at each pen tip, and close into an unbroken border.

**Why:** Over-under alternation is what makes interlace read as Celtic; a closed border leaves the middle free for
`ERIN GO BRAGH` in the `tiny` font (49 px).

## D7 — Cards: gold and shamrock green on deep green, three backdrops
*2026-11-26*

**Decision:**
- Text: gold (warm white into gold) for the main line and shamrock green for the second line, both over a deep-green
  shadow. Styles: `time` (clock font), `date`, `head`, `word`, `top` and `bottom` (`big`), and `sub` (`tiny`).
- `ST. PATRICK'S` is 65 px in `big` and `TO ST. PATRICK'S` 57 px in `tiny`, so the countdown is `N DAYS` (`big`) over
  `TO ST. PATRICK'S` (`tiny`), and the name of the day is two `big` lines (`top` at row 0, `bottom` at row 8).
- Three backdrops: `clock_bg` (deep green, a shamrock in each top corner, grass, gold glints at the edges),
  `count_bg` (a small rainbow from the top-left corner, a shamrock top right, coins in the bottom corners, all clear of
  the text), and `day_bg` (deep green with faint gold glitter and a dim rainbow chase on the bottom row) for the day
  cards, whose two big lines use the whole display.

**Why:** Dark backdrops keep live text legible; decoration stays in the corners the text never reaches.

## D8 — The greeting: ERIN GO BRAGH
*2026-11-26*

**Decision:** The on-the-day cards are `HAPPY` → `ST. PATRICK'S` / `DAY`, and `ERIN GO` / `BRAGH` → `HAPPY` /
`ST. PATRICK'S DAY`. They take turns in the count slots (`day0`, `day1`, `day0`). The Celtic Knot scene also shows
`ERIN GO BRAGH`.

**Why:** "Erin go bragh" (from the Irish *Éire go brách*, "Ireland forever") is a heritage motto with a long
history on banners and in parades. It celebrates Ireland itself, which suits the brief best.

**Alternatives:**
- `SLAINTE`: a toast ("health"), so drink-centric; ruled out by D2. It also needs an accent the ASCII fonts lack.
- `LUCK O' THE IRISH`: fits in `tiny` (62 px), and is widely used fondly, but its origin is debated (it may have
  begun as a backhanded remark about Irish miners' "luck"). The four-leaf clover scene says `LUCKY!` instead.
- Accented Irish spellings: the fonts are ASCII-only.

**Judgment call for review:** the user may prefer `LUCK O' THE IRISH` as the greeting; it is a one-line change in
`DAY_CARDS` and `DAY_TEXT`.

## D9 — START previews the day; dates only from the kit
*2026-11-26*

**Decision:** `HOLIDAYS.stPatricksDay` with `nextOccurrence` gives the days to the next March 17 (0 on the day, then
next year's). START toggles holiday mode, which shows the on-the-day cards on any date; it calls `show.start()`
again with the playlist rotated to begin at the first count slot, so the change shows at once. The logic lives in
`app/shared/stpatricks.ts`, which the app, the mockup (type-stripped and inlined) and the tests share.

**Why:** The round-2 spec, and MLK Day's proven pattern. The mockup check in `tests/logic.test.mts` compares the
mockup's inlined logic with the app's on every day of 2026–2029.

## D10 — Scene details worth knowing
*2026-11-26*

- **The parade's piper wears a saffron kilt**, the traditional color of Irish pipe bands, which sets him apart from
  a Scottish tartan. The flag is the Irish tricolor, green at the hoist, trailing behind its pole.
- **The green river** shows orange powder turning the water green, which is how the real dye behaves; the city is
  generic, not a particular one.
- **The four-leaf clover** is the 13 × 13 `size=2` shamrock: heart-shaped leaves with a lit rim and a darker cross
  between them. Without the rim and cross, the leaves merged into one blob.
- **The rainbow** is an ellipse (`rx` 25, `ry` 16) whose right foot ends behind the pot, so it reads as landing in it.
