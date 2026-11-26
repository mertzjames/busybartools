# Decision log — Veterans Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()`. `main.ts` is configuration: scenes from the generated
`show.ts`, and cards and a `steps(t)` playlist from `app/shared/veterans.ts`. The shape follows Memorial Day, the
closest sibling tribute.

**Why:** The round-2 common spec. The runner already handles one request in flight, card pages, fades and the minute
rollover, and `steps(t)` is what the 11:00 moment needs (D6).

## D2 — A tribute: calm and warm, grateful, never festive
*2026-11-26*

**Decision:** Slow scenes in warm, calm color (a morning street, a sunrise, an afternoon field, a lit café window).
No fireworks, confetti, party effects or jokes, and no "Happy Veterans Day" (a test checks no card says HAPPY).
The words are thanks: `THANK YOU`, `HONOR ALL WHO SERVED`, `THANK YOU FOR YOUR SERVICE`.

**Why:** Veterans Day honors all who served, living and dead. The brief asks for respect and gratitude, calm and
warm rather than somber, which sets it apart from Memorial Day (dusk, half-staff, `WE REMEMBER`).

## D3 — No insignia, no likenesses, no combat; a range of veterans; six scenes
*2026-11-26*

**Decision:**
- Uniforms are plain colors with no patches: a navy dress uniform with a white peaked cap, white gloves and a column
  of gold buttons; plain olive and tan uniforms with soft caps. Older veterans wear plain ball caps (navy, red) with
  no lettering. No service-branch seals, emblems, rank or medals (they are protected), no faces beyond plain skin, no
  weapons and nothing that depicts combat. The flag bearer carries only a flag.
- Veterans of different ages (silver and grey hair, younger marchers), skin tones (the five-tone palette) and
  genders (a marcher with a bun; at 3 × 3 px a head shows little more than hair and headwear).
- Show order: Main Street (the town at sunrise), the parade, the salute, the poppies, the thank-you, the finale. The
  places come first, then people, then remembrance and gratitude, and the flag closes with `THANK YOU VETERANS`.

**Alternatives:** A color guard with rifles (left out: weapons). A medal ceremony (medals copy real designs). A
wheelchair in the parade was considered for inclusion but is hard to read at 16 rows; left for a later version.

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — Dates and cards
*2026-11-26*

**Decision:** The date is `HOLIDAYS.veteransDay` (Nov 11) from the kit, through `nextOccurrence`; no year is
hard-coded. Before and after the day the countdown card reads `N DAYS` / `TO VETERANS DAY` (up to `365 DAYS` the day
after, when the next Nov 11 is in a leap year). On Nov 11 the three countdown slots become three day cards in turn,
each `VETERANS DAY` and then a pair of lines (D7). Veterans Day is always observed on Nov 11 itself, even when
federal offices close on a Friday or Monday, so the app never shifts the date.

## D6 — The 11th hour: a timer that starts a cycle, and a playlist that opens with the moment card
*2026-11-26*

**Decision:**
- `inMoment(t)` is true from 11:00:00 to 11:00:59 on Nov 11 by the bar's wall clock (`hour === 11 && minute === 0`),
  so 10:59 and 11:01 are outside it. `playlist(t)` puts the `moment` card first when the cycle starts inside it,
  then the day's usual playlist. The card is 20 s: `11TH HOUR`; `11TH DAY` / `11TH MONTH`; `ARMISTICE` /
  `NOV 11 1918`; `THANK YOU` / `VETERANS`, over a still, dark backdrop with one poppy in each corner.
- A cycle lasts about 2 min 35 s (D11), so cycles alone would rarely start in that minute. `main.ts` wraps `steps(t)`:
  at the start of every cycle it calls `msToMoment(t)`, which returns the time to 11:00:02 when it is Nov 11 and
  11:00 is less than 10 minutes away (otherwise null), and arms one `setTimeout` for it, replacing any earlier one.
  When it fires, `show.start()` begins a new cycle, whose playlist (picked by the bar's clock at about 11:00:02)
  opens with the moment. The 2 s margin makes a timer that fires a little early still land inside the minute.
- Back clears the timer, so it never keeps the app alive after quitting.
- Tests cover 10:59:59, 11:00:00, 11:00:59 and 11:01:00, the timer arithmetic, the mockup's copy of the logic, and
  a run of the real runner from 10:59:00 whose clock and timers advance together until the moment card plays.

**Why:** The armistice ending the First World War took effect at 11:00 on Nov 11, 1918, and Veterans Day began as
Armistice Day. The kit runner has no clock hook and the round rules forbid a new playback loop, so one human-scale
timer that calls `show.start()` is the least machinery that hits the minute. Re-arming at each cycle (and only within
10 minutes) avoids an hours-long timer drifting away from the bar's clock.

**Alternatives:** A card whose pages depend on t (it would only show if a card happened to start in the minute).
Interrupting a scene mid-way is what the timer does; it was judged fine for a once-a-year moment. A moment of
silence (a dark screen) was considered, but a dark bar looks broken.

## D7 — The words on screen
*2026-11-26*

**Decision:** Every word the app shows: the countdown `N DAYS` (or `1 DAY`) / `TO VETERANS DAY`; on the day
`VETERANS DAY`, `THANK YOU` / `VETERANS`, `HONOR ALL` / `WHO SERVED`, `THANK YOU` / `FOR YOUR SERVICE`; at 11:00
`11TH HOUR`, `11TH DAY` / `11TH MONTH`, `ARMISTICE` / `NOV 11 1918` and `THANK YOU` / `VETERANS`; the clock's time
and date; and two captions baked into scenes, `THANK YOU` (the thank-you scene) and `THANK YOU` / `VETERANS` (the
finale).
- `VETERANS DAY` in the big font is 69 px (70 with its shadow), so it fills the row. Pairs use two big lines (`upper`
  y 0, `lower` y 8). `FOR YOUR SERVICE` (16 characters) is too wide for the big font, so it is a tiny line under a
  big `THANK YOU`. The fonts have no `·` glyph, so the 11:00 card uses plain words on two lines.
- The third day card (`THANK YOU` / `FOR YOUR SERVICE`) and the `ARMISTICE` / `NOV 11 1918` page go beyond the
  brief's examples; they are judgment calls for review.
- The thank-you scene's caption is tiny, top right, so it doesn't cover the people.

## D8 — Calm cards, and edge art that clears the text
*2026-11-26*

**Decision:** Card text is warm ivory into a pale gold over a deep-navy shadow, with a soft poppy rose for the small
line (`renderer/scenes/text.py`). Backdrops: the clock card is an evening sky with faint stars on the top two rows and
a small flag on a pole in each bottom corner; the countdown and day cards are a warm dusk with a low amber horizon
and a small poppy in each bottom corner; the 11:00 card is darker and stiller still. Each backdrop declares the boxes
its edge art uses (`ART`), and the parity test decodes every card bitmap and checks the text and its shadow stay
clear of them (`VETERANS DAY` leaves only columns 0 and 71 free on rows 4-12, so the poppies sit on rows 13-15).

## D9 — START previews the day, then the 11:00 moment
*2026-11-26*

**Decision:** START cycles a holiday mode: `off` (the calendar), `day` (Veterans Day on any date: the day cards in
the countdown slots), `moment` (the day, with the moment card opening every cycle), then `off` again. Each press calls
`show.start()`, a new cycle from the top, so the change shows at once. The mockup's START button does the same.

**Why:** The brief asks for the on-the-day cards to be reviewable on any date, and suggests a second press for the
11:00 moment. Showing the moment at the start of every cycle in that mode (rather than once) keeps the logic a pure
function of the time and mode, and a reviewer sees it again every couple of minutes; the real moment plays once.

## D10 — Scene art notes
*2026-11-26*

- **Main Street:** the first version had a veteran and a grandchild walking past the shops; they dissolved into the
  shopfronts and lit windows. The scene became about the place: the town puts its flags out at sunrise, one lamppost
  after another, and the flags fly above the rooftops against the sky, where red and white read. Shop windows are a
  calm blue-grey glass with one warm display row; bright yellow windows took over the frame.
- **Parade:** behind the marchers the street is kept quiet (plain muted walls, a few warm windows, no flags), and the
  olive uniforms are a lit olive: the darker olive vanished. The flag bearer's flag flies ahead of him on the breeze:
  16 rows leave no room above his head, and flying back it hid him. Neighbours at the curb are seen from behind
  (hair and shoulders), each waving a hand flag, which avoids faces.
- **Salute:** the sky is warm at the horizon so the navy uniform reads against it; white gloves make the saluting
  hand visible on the navy sleeve. The older veteran's cap is red (blue vanished into the sky) and his jacket green
  (tan vanished into the peach horizon). The salute is four hand-drawn arm poses, not a rotated sprite. The flag
  starts gathered at the foot of the pole and unfurls as it climbs.
- **Poppies:** a warm afternoon, unlike Memorial Day's dusk field. The nearest flowers have a 1 px dark ring so they
  don't merge; the breeze moves in steps of 3 frames (calmer, and a smaller file).
- **Thank you:** the veteran sits in front of the lit window (dark skin and a navy cap read against it) and the child
  stands in front of the blue-grey wall. The bench is painted green: a wood-brown bench merged with the skin tones.
- **Finale:** a 13-stripe flag fills the display; the wave shifts whole rows with 3 shade steps, and it dims to 16 %
  so the ivory words read over it (at 28 % the white stripes competed with the letters).
- **Size:** total `.anim` data is about 0.8 MB (the finale's whole-cloth flag is the largest at about 220 KiB).

## D11 — The Armed Services, after the parade (review)
*2026-11-26*

**Review:** "Similar to Memorial Day (maybe even copy it over to here) add a set of animations or a single one that
shows each of the branches of service."

**Decision:** One 17 s scene, `services`, copied app-locally from Memorial Day's scene of the same name (apps can't
share code; it uses only the shared kit). The six services appear in order of precedence, each for 2.8 s, with its
name across the top in the big font and a small vignette of its domain below, sliding one into the next: `ARMY` (a
column marching along a road), `MARINE CORPS` (three figures in dress blues who salute), `NAVY` (a plain grey ship
at sea), `AIR FORCE` (three jets in echelon trailing smoke), `SPACE FORCE` (a satellite over the curve of the Earth)
and `COAST GUARD` (a plain orange rescue helicopter over the waves). The art is the same; the names take this app's
warm ivory-to-gold caption colors. The names live in `SCENE_CAPTIONS["services"]` (`scenes/text.py`), so the parity
test checks every glyph and width.
- It plays after the parade: the town's own veterans, then the services they served in, then the salute.
- Seven scenes give four clock slots and three count slots, so on the day each day card plays exactly once a cycle;
  the finale is now followed by a clock card. A cycle is about 2 min 35 s (D6's 10-minute timer window still covers
  it).

**Tone (D2, D3):** only domain, plain silhouettes, generic uniform colors and the names: no emblems, seals, insignia,
logos, markings (the Coast Guard's diagonal stripe is left out on purpose), medals, faces, weapons or combat.

**Not added:** a closing caption such as `THANK YOU` / `ALL WHO SERVED`; the finale already says `THANK YOU` /
`VETERANS`, and every new word needs review. The six names are new words on screen.
