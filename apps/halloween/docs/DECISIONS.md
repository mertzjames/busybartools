# Decision log — Halloween

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/halloween.ts`. The structure
(build, review, text parity, logic tests, mockup) follows Valentine's Day.

**Why:** It is the round-2 common spec, and the runner already handles one request in flight, card pages, fades and
the minute rollover.

## D2 — Spooky-fun, never frightening; original characters only
*2026-11-26*

**Decision:**
- Every character is friendly: the jack-o'-lanterns grin or look surprised, the ghost has pink cheeks and waves, the
  skeletons dance, the cat ends with a smug blink. Nothing jumps at the viewer, and there is no gore.
- Costumes are generic (a sheet ghost, a witch hat and dress, a pumpkin suit, a blue suit with a red cape and a plain
  gold emblem dot). The witch, the ghosts, the skeletons and the cat are original designs; no movie monsters and no
  franchise's pumpkin king.
- Tombstones carry `RIP` at most (one stone), never names or dates.
- The words on screen are short, common Halloween phrases: `TRICK OR TREAT!`, `BOO!`, `SPOOKY SEASON`,
  `HAPPY HAUNTING`, the greeting and the countdown.

**Judgment calls for review:**
- The skull that hops off its neck in the Skeleton Dance is a classic cartoon gag, kept at a two-pixel hop with the
  other two skeletons clapping. If it feels too macabre, the middle skeleton can clap instead (`pose_at` in
  `renderer/scenes/skeletons.py`).
- The shadowy figure passing the haunted house's green window is a plain head-and-shoulders shape, not a monster.

## D3 — Eight scenes, opening on the lanterns and closing on the dance
*2026-11-26*

**Decision:** Carving Night, The Haunted House, Trick or Treat!, Bats Across the Moon, A Friendly Ghost, The Black
Cat, The Witch's Flight, Skeleton Dance (120 s of scenes, a 2 min 56 s loop with the cards).
- Carving Night opens because the jack-o'-lantern is the holiday's signature image.
- Skeleton Dance closes because it is the most festive: a beat, a flashing floor and confetti.
- The three moonlit night-sky scenes (bats, cat, witch) are spread out so the full moon doesn't repeat back to back.

**Why eight:** The brief listed eight ideas and every one reads at 72×16. Eight scenes give four clock and four count
slots, which fit four on-the-day cards.

**Alternatives:** Merging the bats and the witch into one moon scene (to get seven). They stayed separate because
each has its own payoff: the ribbon of bats and the big bat swooping close, versus the witch's sparkle trail.

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — Black is an unlit LED: lit violet-greys, rim light and lit eyes
*2026-11-26*

**Decision:**
- **The black cat** (16×9, five frames: two walk steps, arched back, sitting, a blink) is a deep violet-grey
  (`#3E3256`) with a lavender rim (`#9C86CC`) along its back, head and ears, lit yellow-green eyes (`#C8FF46`) and
  a pink nose. The arched frame puffs the tail with rim-colored bristles.
- **Silhouettes sit on the moon.** The cat stops in front of the full moon, and the witch and the bats cross it,
  so their dark shapes have a bright source right behind them (the round-2 silhouette lesson).
- **Bats** are lit violet-greys with orange-red eye pairs; on the moon they read as darker shapes, on the sky as
  lighter ones.
- **The witch** (16×11) has a violet hat with a slime-green band, a green face with a long nose and a lit-violet
  eye, orange hair, a violet dress and a wooden broom with straw bristles. Her far-away return uses a separate 9×6
  sprite rather than a downscale (downscaling small pixel art mangles it).
- **The haunted house** is built in code (a 45° gable two pixels thick, a tower with a spire, a chimney) in lit
  violet-greys with a moonlit edge on the side facing the moon.
- **Skeletons** are procedural: a skull with lit green sockets (black sockets would be holes), an oval rib cage, a
  pelvis and two-bone limbs posed per beat. Arms never go straight out at shoulder height: with the ribs, that read
  as a cross, so the can-can uses hands on hips.
- **Ghosts** are white with lit-violet eyes, pink cheeks and a rippling hem (two frames, plus a blink and a wave).

## D6 — Jack-o'-lanterns: hand-drawn bodies, four carved faces, a three-stop light ramp
*2026-11-26*

**Decision:** Pumpkins use hand-drawn bodies (15×11 and 7×6) with darker ridges between the lobes and a highlight.
The four 11×7 faces are different and original (classic triangles with a toothy grin, surprised O, a wink with a
crooked smile, goofy slanted eyes with a stepped zigzag grin). A 1 px alternating zigzag disappears on LEDs, so the
goofy grin steps two up, two down.

When lit, the skin darkens a little and the face ramps from the carved hole through a deep amber to candle yellow.
A straight blend from brown to yellow passed through olive; a ramp through orange made the face vanish into the skin
for a moment. Only a few face pixels flicker; the halo is steady.

## D7 — Cards: nights, cobwebs and candlelight; a 56 px text gap
*2026-11-26*

**Decision:**
- **The countdown counts nights:** `339 NIGHTS` / `TO HALLOWEEN`, `1 NIGHT` the night before, since Halloween is a
  night. The kit has `daysLabel` only, so the app has its own `nightsLabel` (reported as a kit idea). The number is
  the kit's day count (`nextOccurrence(t, HOLIDAYS.halloween).days`), so it changes at midnight.
- **Styles** (`renderer/scenes/text.py`): pumpkin orange (pale gold into orange) for the big lines, slime green for
  the small line and the second line of two-line phrases, ghost white into mint for `BOO!`, all over a deep violet
  shadow (a dark shadow, not a same-hue one). Two big lines at rows 0 and 8 fill the display exactly.
- **Backdrops:** cobwebs in both top corners on both cards. The clock card adds a candle (with a wick row between the
  flame and the wax) in the bottom-left, a small jack-o'-lantern in the bottom-right and a little spider bobbing on
  its thread. The count card has two small jack-o'-lanterns in the bottom corners. Glows are static; only flame and
  face pixels flicker.
- **The text gap:** all corner art stays in columns 0–7 and 64–71, so every line (shadow included) must fit columns
  8–63 (`TEXT_GAP`). The longest countdown is `365 NIGHTS` (55 px, from Nov 1 of a year before a leap day), and the
  widest date is 55 px; both fit exactly. The tests decode every card bitmap and check it.

## D8 — One source of truth for the card logic
*2026-11-26*

**Decision:** `app/shared/halloween.ts` holds the card texts, page lengths and the playlist as pure functions of the
bar's local time. The app imports it, the mockup inlines it (type-stripped by Node 24, together with the kit's
`walltime.ts` and `holidays.ts`), and the tests run it against real dates. A test also extracts the mockup's logic
block and compares it with the app's for every day of three years.

App-level constants carry an `HW_` prefix, because the mockup pastes the three files into one scope and a repeated
top-level name would be a SyntaxError.

## D9 — START previews the night
*2026-11-26*

**Decision:** START (a short press, when the runner ignores it) toggles holiday mode: the playlist switches to the
on-the-day cards on any date, and the new cycle is rotated to start on the first count slot, so the change shows at
once. Pressing it again goes back. The mockup has the same toggle.

## D10 — Quantized fades and steady glows keep the files small
*2026-11-26*

**Decision:** Slow light changes (windows lighting up, the lantern light ramp, the stage lights, the door's glow) are
quantized to a few steps, glows are drawn on static backgrounds, and the graveyard mist moves every third frame. The
eight scenes and two backdrops total about 0.7 MB of `.anim` data, well under the 3 MB budget.
