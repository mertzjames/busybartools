# Decision log — Memorial Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()`. `main.ts` is configuration: scenes from the generated
`show.ts`, and cards and a `steps(t)` playlist from `app/shared/memorial.ts`.

**Why:** The round-2 common spec. The runner already handles one request in flight, card pages, fades and the minute
rollover, and `steps(t)` is exactly what the flag custom needs (D5).

## D2 — A tribute: slow, muted, nothing festive
*2026-11-26*

**Decision:** 14–16 s scenes with slow changes, muted colors (a calm flag, pale stone, poppy red, dusk blues), no
confetti, fireworks, party effects or jokes, and no cookout or sale imagery. Words are few and plain; there is no
"Happy Memorial Day" (a test checks no card says HAPPY).

**Why:** Memorial Day honors those who died in military service; the playbook's tone rules for tributes.

## D3 — No insignia, no likenesses, no combat; six scenes
*2026-11-26*

**Decision:** The flag, poppies, plain headstones (no names or inscriptions, all the same), a bugler as a silhouette
with a generic peaked cap, plain grey aircraft with no markings, and a memorial wall whose engraving is abstract
marks. No service-branch seals or emblems (they are protected), no faces, no weapons and nothing that depicts
combat. Show order: the flag, poppies, headstones, bugler, flyover, the wall. The flag opens because it carries the
day's custom (D5); the wall closes with `WE REMEMBER`.

**Alternatives:** A candle scene on its own: folded into the wall, which has two candles. A rifle salute or a folded
flag: left out, since weapons and funerals edge toward the depiction the tone rules rule out.

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — Half-staff until noon on the day, as two flag scenes
*2026-11-26*

**Decision:** The flag scene has two variants, rendered from one file (`renderer/scenes/flag.py`, as
`SimpleNamespace` modules): `flag_half` and `flag_full`. `halfStaff(t)` is true on Memorial Day before 12:00 local
time (`t.hour < 12`, so 11:59 is half-staff and 12:00 is full staff). `playlist()` puts the matching variant in the
first slot and skips the other. The day card's last page follows the same rule: `HALF-STAFF` / `UNTIL NOON`, then
`FULL STAFF` / `RAISED AT NOON`.
- The half-staff scene follows the custom of first raising the flag to the peak and then lowering it slowly to
  half-staff: it opens at the peak and lowers it one row at a time over 6 s.
- The flag has seven stripes (one row each) and a canton of lit dots: a 16-row panel can't show thirteen stripes
  at half-staff. Dots in two sparse rows read as a pair of eyes, so the canton is a dense checker.

**Timing:** `steps(t)` runs at the start of each cycle (about 2 min), so at noon the flag goes to full staff within
one cycle; a card that is showing at 12:00 updates its line at the minute rollover. The noon switch uses the bar's
local wall clock, never JS `Date` local time.

**Why:** The flag custom for Memorial Day (half-staff from sunrise until noon, then full staff). Sunrise varies by
place and season and the bar has no location, so the half-staff period starts at midnight; before sunrise most
people aren't looking at it.

## D6 — Full staff on every other day
*2026-11-26*

**Decision:** Before and after Memorial Day the flag scene shows full staff.

**Why:** Full staff is the flag's normal position. Showing half-staff all year would suggest a mourning period that
isn't happening (flags are also lowered by proclamation on other days, which an offline app can't know).

**Judgment call for review:** this means the app's half-staff scene is seen only on the morning of the day or in
holiday mode.

## D7 — The words on screen
*2026-11-26*

**Decision:** Every word the app shows: the countdown `N DAYS` (or `1 DAY`) / `TO MEMORIAL DAY`; on the day
`MEMORIAL DAY`, `WE REMEMBER`, `HONOR AND` / `REMEMBER`, `HALF-STAFF` / `UNTIL NOON` and `FULL STAFF` /
`RAISED AT NOON`; the clock's time and date; and `WE REMEMBER` in the closing scene. The other scenes have no
captions.
- `MEMORIAL DAY` in the big font is 67 px (it fits 72 with its shadow). `HONOR AND REMEMBER` is too wide for one big
  line and cramped in tiny, so it is two big lines (`upper` y 0, `lower` y 8, which just fit 16 rows with shadows).
- In the closing scene the caption sits across the top of the wall in the big font, with the wreath and candles
  below it; the tiny font's `M` reads like an `N` at that size.

**Out of scope:** a "National Moment of Remembrance" card at 15:00 (per the brief).

## D8 — Calm cards
*2026-11-26*

**Decision:** Card text is warm white into pale silver over a deep-navy shadow, with a muted poppy rose for the
small line. Styles (`renderer/scenes/text.py`): `time` (clock font, y 2), `date` and `word` (big, y 4), `head` (big,
y 1), `sub` (tiny, y 10), `upper` (big, y 0) and `lower` (big, y 8). Backdrops: the clock card is a night sky with
faint stars and a few poppies in the bottom corners; the countdown and day cards are a quiet dusk with a low rose
horizon and a poppy in each bottom corner. The corner poppies sit low (rows 12–15, the outer 4 columns) so they clear
`TO MEMORIAL DAY` and `MEMORIAL DAY`.

## D9 — START previews the day: morning, afternoon, back
*2026-11-26*

**Decision:** START cycles a holiday mode: `off` (the calendar), `morning` (Memorial Day before noon: half-staff flag,
day cards), `afternoon` (after noon: full staff), then `off` again. Each press calls `show.start()`, which begins a new
cycle at the flag scene, so the change shows at once. The mockup's START button does the same.

**Why:** The brief asks for both halves of the day to be reviewable on any date. Starting the cycle at the flag (not
at a card, as MLK Day does) shows the part that differs most between the modes first.

## D10 — Scene art notes
*2026-11-26*

- **Poppies:** the nearest row is 5 × 4 flowers with a lit violet eye (black would be a hole) and a 1 px dark ring,
  so neighbours don't merge into blobs; fewer mid-field flowers for the same reason.
- **Headstones:** a perspective grid converging on the horizon read as V-shaped scatter on 16 rows. Three straight,
  staggered rows (1 × 1, 1 × 2, 3 × 4 with rounded shoulders) read as a cemetery, and small flags stand only before the
  nearest row, flying away from the centre so the scene stays symmetrical.
- **Bugler:** a dark silhouette dissolved into a dark violet sky. It reads when the sun sits right behind his
  shoulders and the sky stays warm; the sun sets only partway (behind the hill), and the bugle is part of the
  silhouette with a single brass glint at the bell (gold on the gold sun vanished).
- **Flyover:** the evening sky is a deeper blue so the pale planes stand out; the missing man's trail starts above
  the formation, so it never joins the planes still flying level.
- **Size:** slow light changes are quantized (20–40 steps) and glows are steady; total `.anim` data is about 1 MB.

## D11 — A flag in proportion: 17 × 9 (review)
*2026-11-26*

**Review:** "The flag looks too long ... shorten it on the x-axis and slightly lengthen it on the y-axis", at both
half- and full-staff.

**Decision:** The scene flag is 17 wide and 9 tall (about 1.9 : 1, a real flag's proportions), down from 24 × 7. It
has nine one-row stripes (red at the top and bottom) and a 7 × 5 canton over the top five, about 40% of the fly, with
the dense checker of lit dots kept from D5. The pole moves to column 26 so the flag sits nearer the middle; its
finial is on row 0. Full staff puts the flag's top on row 1; half-staff on row 5, so its bottom stripe sits just
above the grass and five rows of bare pole show above it. The lowering now covers 4 rows over the same 6 s. This
supersedes the seven-stripe flag in D5; only the flag scenes use this flag (the headstones' small flags are
separate).

**Alternatives:** 11 rows (21 × 11) leaves no room below the peak for a visible half-staff; an even number of rows
would end on a white stripe.

## D12 — The Armed Services: one scene for all six (review)
*2026-11-26*

**Review:** "Let's add an animation for each of the armed services. It can be one animation for each one, or a single
animation that shows all of them."

**Decision:** One 17 s scene, `services`, after the flag. The six services appear in order of precedence, each for
2.8 s, with its name across the top in the big font over a softly darkened box and a small vignette of its domain in
rows 8–15 below. Each slides in from the right as the last slides away (0.6 s, eased).
- `ARMY`: a column of five soldiers in olive marching in step along a road, against a pale sky.
- `MARINE CORPS` (67 px, the widest name; it fits): three figures in dress blues (white cap, dark-blue coat, gold
  buttons, white belt and gloves, light-blue trousers with a red stripe) before a sandstone wall; they salute at 1 s.
- `NAVY`: a plain grey ship with a raked bow, a bridge and a mast, under way with a wake, against a warm horizon.
- `AIR FORCE`: three jets, seen from below, in echelon trailing white smoke across a deep-blue sky.
- `SPACE FORCE`: a satellite with solar panels and a blinking light over the curve of the Earth.
- `COAST GUARD`: a plain orange rescue helicopter hovering over the waves, its hoist line down to a life raft.

**Tone (D2, D3):** the services are shown only by domain, a plain silhouette, generic uniform colors and the name. No
emblems, seals, insignia, logos, markings or medals (the Coast Guard's diagonal stripe is left out on purpose), no
faces, no weapons and no combat. The names are new words on screen.

**Art notes:** at first the art vanished: olive soldiers on olive hills, a grey ship on a grey-blue sky and jets as
plus signs. What worked: a pale or warm band behind every figure, a darker sky only behind the caption, a ship darker
than the horizon, jets as swept arrows, and drawing the caption's dimmed box before figures that stand just below it.
The scene file uses only the shared kit, so Veterans Day can copy it.

## D13 — The Tomb of the Unknown Soldier: always guarded (review)
*2026-11-26*

**Review:** "Let's also add an animation of the unknown tomb and its guards, showing them guarding in any weather."

**Decision:** One 16 s scene, `tomb`, before the memorial wall. A plain white marble tomb (a cornice, faint corner
pilasters, a two-step plinth) stands on a plaza. A sentinel in dress blues (cap, dark-blue coat, white gloves,
light-blue trousers with a gold stripe) walks 21 steps across the mat (6.3 s), pauses, turns to face the tomb (seen
from behind), pauses, turns, pauses and walks back. The weather changes around him, a clear day, rain, snow (which
settles on the cornice) and night with stars and floodlights, each change a 1 s blend quantized to 20 steps.
- The real cadence is slower (about one step a second); 0.3 s steps fit the walk, the turns and the walk back in 16 s.
- The sentinel is 5 × 11 so he reads; at night he is lifted toward white (floodlit) and a warm haze lights the plaza,
  or his dark-blue coat vanished into the night sky.
- No caption, so no new words. `ALWAYS GUARDED` or `21 STEPS` would fit if wanted.

**Judgment calls for review:** the real sentinels carry a rifle; following D3 (no weapons) he carries none. The tomb
has no inscription and he has no face.

## D14 — Eight scenes: the count slots and the day cards
*2026-11-26*

**Decision:** Show order: flag, services, poppies, headstones, bugler, flyover, tomb, wall (about 3 min a cycle). With
eight scenes per cycle there are four clock slots and four count slots. On the day the count slots take the three day
cards in turn, so the fourth (after the wall) repeats the first. The first two day cards swap places, so the repeat is
`HONOR AND` / `REMEMBER` rather than an echo of the wall's own `WE REMEMBER`: services, then HONOR AND REMEMBER;
headstones, then WE REMEMBER; flyover, then the flag's position; the wall, then HONOR AND REMEMBER. No new words.

**Alternatives:** a fourth day card would need new words; a countdown of "0 DAYS" on the day reads wrong.
