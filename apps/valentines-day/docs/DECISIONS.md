# Decision log — Valentine's Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/valentine.ts`. The structure
(build, review, text parity, logic tests, mockup) follows MLK Day, the first round-2 app on the runner.

**Why:** It is the round-2 common spec, and the runner already handles one request in flight, card pages, fades and
the minute rollover.

## D2 — Sweet and family-friendly; original words only
*2026-11-26*

**Decision:** Hearts, a cherub, a love letter, birds, chocolates, a rose and candy hearts. Nothing romantic-explicit:
no kissing figures, no couples. The words on screen are `FOR YOU`, `BE MINE`, `XOXO`, `HUG ME`, `LOVE YOU`, `BE TRUE`,
`SO SWEET`, the greeting and the countdown. They are short common phrases, not any brand's candy-heart list, and the
candy hearts carry ink dashes rather than a brand's printed words or shapes.

**Judgment call for review:** `XOXO` and `LOVE YOU` are the warmest phrases; both are common on classroom
valentines. Swap them in `DAY_CARDS` (and `DAY_TEXT`) if the user prefers milder ones, such as `BE MY PAL` (49 px:
too wide, so it would need a shorter word) or `SMILE`.

## D3 — Seven scenes, ending on the candy-heart finale
*2026-11-26*

**Decision:** Hearts Afloat, Cupid's Arrow, Special Delivery, Lovebirds, A Box of Chocolates, A Rose Blooms, Candy
Hearts (101 s of scenes). Hearts Afloat opens because it is the simplest statement of the theme. Each scene ends on
a heart or a word, and the finale ends on heart fireworks.

**Why seven:** The brief offered seven ideas, and all of them read at 72×16. With seven scenes the cycle is scene,
clock, scene, count… with four clock and three count slots, which matches the three on-the-day cards (D8).

**Alternatives:** Dropping the chocolates or the rose to get six scenes. Both read clearly and add variety
(an object being emptied, a plant growing), so they stayed.

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — Original sprites; lit features; separated shapes
*2026-11-26*

**Decision:**
- **The cherub** is a generic winged baby, 17×12: gold curls, peach skin, a pink sash, white wings with blue shade
  (two flap frames). Its eye is a lit blue (`#4A50B4`), which reads on peach skin where a dark rose disappeared. The
  bow is orange-gold (`#FF9628`), so it doesn't merge with the pale gold hair. The arrow has a sideways-heart tip.
- **The lovebirds** are generic songbirds (7×5): one rose-red, one gold. Real lovebirds are green, but green would
  break the palette and turn muddy on a dusk sky.
- **The rose** has five bloom stages (11×8): bud, half open, open, full. A crown of pale petal tips on top made it
  read as a rose rather than a red blob.
- **Hearts** are hand-drawn at widths 3, 5, 7 and 9 and come from the implicit heart curve above that
  (`vfx.heart_rows`). Rising hearts get a 1 px dark halo so neighbors never merge into blobs; the big hearts get one
  too, to separate them from what passes behind.

**What was tried:** The first cherub (13×10) read as a peach-and-gold blob with no face. A bigger round head, a lit
blue eye and a bow in a different gold fixed it. The first chocolates (4×4) were too small: the heart-shaped piece
vanished on red satin. 5×5 pieces in gold cups on a dark satin read clearly. Hearts at random columns piled up into
blobs; shuffled column slots plus the halo fixed it.

## D6 — Words in clear space
*2026-11-26*

**Decision:** Only three scenes carry words, all in the big font over a dimmed band: `FOR YOU` (to the right of the
opened letter), and `BE MINE` then `XOXO` (between the candy-heart stacks of the finale, which stay within columns
0–15 and 56–71).

## D7 — Candy-heart cards
*2026-11-26*

**Decision:** Styles (`renderer/scenes/text.py`): `time` (clock font, y 2), `date` and `candy` (big, y 4), `head`
(big, y 1) and `sub` (tiny, y 10). Card text is warm white into rose pink over a deep berry shadow; the small line is
gold; candy phrases are blush pink with a crimson shadow, like printed candy. Backdrops: the clock card is a plum
night with small hearts rising (dim saturated reds behind the text, because pale pinks at low alpha turned grey);
the countdown and day cards have two pastel candy hearts at the ends (columns 1–9 and 62–70, rows 1–9) that beat
twice per loop.

**The countdown layout:** `N DAYS` in big (at most `365 DAYS`, 45 px, so it fits between the candy hearts) over
`TO VALENTINE'S DAY` in tiny. That is 67 px, which fits the full width under the candy hearts with the shadow. The
tiny font has the apostrophe. `TO VALENTINE'S` alone was considered; the full name reads better and fits.

**On the day:** `HAPPY` (big) over `VALENTINE'S DAY` (tiny, 56 px). `VALENTINE'S DAY` in big would be 89 px.

## D8 — Card logic in one pure module, shared by app, mockup and tests
*2026-11-26*

**Decision:** `app/shared/valentine.ts` returns every card's pages as styles and strings (`cardPages(name, t)`) and
the playlist (`playlist(scenes, t, holiday, fromCard)`). `main.ts` maps styles to `LAYOUT` specs. Every line is
recomputed from the time it is drawn at, so the clock rolls over and the countdown changes at midnight. The mockup
runs the same file: `build.py` type-strips it with Node 24 (with the kit's `walltime.ts` and `holidays.ts`) and
inlines it. The date comes only from `HOLIDAYS.valentinesDay` (`nextOccurrence`, `daysLabel`).

**On the day:** the three count slots become `day0`, `day1` and `day2`, each the greeting followed by two candy
phrases (`BE MINE`, `XOXO`; `HUG ME`, `LOVE YOU`; `BE TRUE`, `SO SWEET`). All three share the candy-heart backdrop.

**After the day:** the countdown counts to next year's (`364 DAYS` on Feb 15, 2027; `365 DAYS` on Feb 15, 2028,
because Feb 29 falls in between).

## D9 — START previews the day, starting on a card
*2026-11-26*

**Decision:** START toggles holiday mode (the on-the-day cards and playlist on any date). It restarts the cycle with
the playlist rotated to begin at the first count slot, so the change is visible at once (`HAPPY VALENTINE'S DAY`, or
`N DAYS` when switching back). The runner reports START as "ignored", and the app handles it there. This works with
or without the kit's planned `show.start(from)`.

## D10 — Size
*2026-11-26*

**Decision:** About 0.6 MB of `.anim` data for seven scenes and two backdrops, well under the 3 MB budget. Glows
are steady (drawn once into the background, or constant per frame); only a few core pixels twinkle.
