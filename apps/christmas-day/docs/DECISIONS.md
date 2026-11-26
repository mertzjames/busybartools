# Decision log — Christmas Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Mirror Wizarding Thanksgiving on the shared render kit
*2026-11-25*

**Decision:** Full-screen 72×16 `.anim` scenes at 15 fps rendered by a Python `renderer/`, played in order by an
on-device TypeScript app, with a live clock card after each scene. The build pipeline, fonts, sprite class and
TypeScript helpers come from the shared render kit (`lib/python/busybar`, `lib/ts/busybar`).

**Why:** It's the proven pattern from Wizarding Thanksgiving: the firmware plays `.anim` files smoothly with no
requests, and one renderer feeds the bar, the mockup and the storyboards. Reusing the kit keeps this app to its
scenes and art.

**Alternatives:** Sprite animations layered over bitmaps (harder to choreograph), or timer-driven redraws (about
3 fps).

---

## D2 — Eight scenes ordered from Christmas Eve to Christmas night
*2026-11-25*

**Decision:** Playlist: Trimming the Tree, Carolers, Sleigh Across the Moon (Eve); Stockings, Present Surprise,
Toy Train, Snowman (the Day); Merry Christmas fireworks (night). 15–18 s each, about 3 m 16 s per loop with the
clock cards.

**Why:** The loop reads as one story of the holiday rather than a shuffle, and the finale's big `MERRY CHRISTMAS`
lands right before the loop restarts. Each scene has characters that move and interact and ends on a short
punchline caption.

**Alternatives:** Opening with the sleigh (the most iconic image), but a quiet tree trimming that builds to a star
is a better first scene, and the sleigh then reads as the Eve's climax.

---

## D3 — Sprites as text grids; props and effects procedural
*2026-11-25*

**Decision:** Characters (children, elf, Santa's sleigh, reindeer, cat, puppy, dog, carolers, train) are text-grid
sprites in `renderer/sprites.py`. Trees, houses, presents, snowballs, the moon, snow, light strings, fire and
fireworks are drawn procedurally in `renderer/xfx.py`.

**Why:** Grids are easy to review and tweak. Procedural props scale freely (a 6-row pine on the clock card, a
12-row tree indoors) and stay consistent across scenes.

---

## D4 — Tone curve GAMMA = 0.8
*2026-11-25*

**Decision:** Use the tone curve approved on real hardware for Wizarding Thanksgiving, applied by `build_scenes` to
every frame and by `tone_rgb` to the live clock colors.

**Why:** It lifts dark skies and dim snow without touching unlit pixels, and the bar, the mockup and the review
strips stay identical. Re-tuning without a device would be guesswork.

---

## D5 — App-local effects module instead of new kit code
*2026-11-25*

**Decision:** `renderer/xfx.py` holds `Snow` (seamless, loop-periodic snowfall with wind drift), `light_string`
(twinkling swags), `draw_tree`/`tree_spots`/`garland_path`, `house`, `present`, `full_moon`, `fire`, `snow_ground`
and `Fireworks`.

**Why:** The shared kit is frozen while the holiday apps are built in parallel (playbook). These are candidates to
promote under R2 if another app needs them. Advent Calendar and New Year's Eve likely will, for snow and
fireworks.

---

## D6 — Lit colors for every small feature
*2026-11-25*

**Decision:** Eyes are a lit brown (`#7A4A3A`), the snowman's coal is a grey-blue (`#5A648C`), and noses and mouths
are lit reds and oranges. Backgrounds are dark but never pure black where characters stand.

**Why:** Black is an unlit LED, and near-black details read as holes. Review strips also showed contrast problems:
the orange cat vanished against red brick, so the stocking it bats hangs at the end of the mantel and the cat sits
against the dark wall. A striped wallpaper lit the whole background and made it busy, so it was removed.

---

## D7 — Candy-cane clock card
*2026-11-25*

**Decision:** The time is white fading to ice blue with a red shadow, in the `clock` font at y=2. The date is gold
with a holly-green shadow, in the `big` font at y=4. Timing is 4.5 s of time and 3.5 s of date. The 4 s backdrop
loop has a scalloped light string on rows 0–1, two snowy pines with twinkling bulbs in the corners, a snowbank on
row 15, and snow kept faint in the text band.

**Why:** The card needs its own Christmas palette, distinct from the wizard's gold on purple. The red shadow makes
the digits read as candy canes. Decorations stay outside the text's rows and columns, so the live text never
fights the backdrop. The widest possible date (55 px) is checked by the parity test.

---

## D8 — Shared TypeScript through `app/shared/clocktext.ts`
*2026-11-25*

**Decision:** The app imports `textBitmap`, `parseWallClock`, `nextMinute` and `createDrawQueue` through one
re-export module in `app/shared/`, using relative paths with `.ts` extensions. `tests/clock_parity.py` runs that
module and the generated `show.ts` under Node 24 and compares the XPM output pixel for pixel with
`busybar.font.draw_text`. It also checks the playlist and that every `.anim` exists.

**Why:** Files under `app/src/` become separate script entries and break the firmware. The parity test is what
guarantees the bar, the mockup and the renderer draw the same clock. Only the `big` and `clock` fonts are exported
to keep `main.js` small.

---

## D9 — Captions placed where the action isn't
*2026-11-25*

**Decision:** Punchlines use the `tiny` font in an empty part of the sky or wall (usually top right), or the `big`
font where there is room (TA-DA!, HO HO HO!). The finale dims the village to about 28% under MERRY / CHRISTMAS, and
the fireworks stay bright on top and keep to the screen edges once the words are up.

**Why:** At 16 px tall, a 7-row caption over 10-row characters hides them. Dimming the frame under the big
two-line title keeps the green CHRISTMAS readable over the green trees.

---

## D10 — Review tooling with time windows
*2026-11-25*

**Decision:** `renderer/review.py` renders tone-mapped LED strips at keyframes, every N seconds, or every N seconds
within a start–end window. The clock card strip includes the live text drawn exactly as the app draws it.

**Why:** Fast moments (Santa's gift toss, the cat's pounce) fall between keyframes. The window mode caught a gift
hidden behind the sleigh and a pounce that crossed the whole screen, and both were fixed by retiming.
