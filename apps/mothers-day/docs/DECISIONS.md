# Decision log — Mother's Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Copy the round-2 shape: kit runner, Python scenes, shared card logic
*2026-11-26*

**Decision:** The app follows the holiday-app shape (docs/playbooks/holiday-apps-round2.md): a Python renderer writes
full-screen `.anim` scenes and two card backdrops; `app/src/main.ts` is configuration for the kit's show runner
(`lib/ts/busybar/showrunner.ts`); card texts and the playlist are pure functions in `app/shared/mothersday.ts`, shared
by the app, the mockup (type-stripped and inlined by `renderer/build.py`) and the tests. The layout is copied from
Presidents' Day, another single-day, nth-weekday holiday.

**Why:** one playback loop and one source of date logic for every holiday app; the mockup can't drift from the bar.

**Alternatives:** a custom playback loop (rejected by the playbook); hand-copying the logic into the mockup.

## D2 — Warm, sweet and inclusive; generic figures
*2026-11-26*

**Decision:** Every figure is generic: a 3×3 head with a plain skin face, simple hair and clothes. Across the show the
figures cover a range of skin tones (all five of `mfx.SKIN`'s lit tones appear) and hair (a curly puff, long hair, a
ponytail, short hair and a grandmother's silver bun). The people are "Mom" (breakfast), "a parent and child"
(garden) and "a child and a grandmother" (hug), so step-moms, adoptive moms and grandmothers can all see themselves.
There are no gendered props or chores; the warmth comes from flowers, food, a card, hugs and hearts. No text in the
scenes besides MOM and the finale's greeting.

**Why:** the brief: moms come in many forms, and no stereotypes beyond the warmth of the day.

**Alternatives:** faces with eyes (a 3×3 head has no room for lit eyes, and dark pixels read as holes); a fixed
"family" across all scenes (it would favor one kind of family).

## D3 — Seven scenes from morning to evening
*2026-11-26*

**Decision:** Bouquet (14 s), Breakfast in Bed (15 s), Growing Together (16 s), A Handmade Card (12 s), A Hug Under
the Blossoms (15 s), Tea in the Sunny Window (12 s), Happy Mother's Day finale (14 s): 98 s of scenes, about 2½
minutes per loop with the cards. The day moves from flowers and breakfast in the morning to a garden by day, a hug at
dusk and a quiet cup of tea, and ends on the greeting.

**Why:** all seven of the brief's ideas fit within the 5–8 scene budget and the size budget (about 0.5 MB in all),
and each has one clear action that reads at 72×16.

**Alternatives:** dropping the tea scene (the quietest) to shorten the loop; kept, because a calm moment between the
hug and the finale paces the show.

## D4 — Lit backdrops behind people
*2026-11-26*

**Decision:** Figures always stand in front of something lit: a big cream pillow behind Mom in bed, a mid-blue sky in
the garden, and a warm sunset glow right where the child and grandmother meet. The bedroom wall and the dusk sky are
kept dark, so pale clothes and the pillow pop.

**Why:** first renders lost Mom's medium-brown face against a mauve wall, and the child's head merged into a bright
purple sky (round-1 and round-2 discoveries: small people dissolve over busy or similar-valued backgrounds).

**Alternatives:** lighter skin tones only (rejected: D2); outlines around figures (too heavy at this size).

## D5 — Steady light, small motion
*2026-11-26*

**Decision:** Glows, sunbeams and the card backdrops' hearts hold still or step through a few quantized levels; only
small things move (petals, steam, butterflies, hearts, figures). The whole app's `.anim` data is about 0.5 MB.

**Why:** per-frame changes over large areas bloat `.anim` files (Hanukkah's discovery), and the bar shares memory
with its web server.

## D6 — Readable small objects
*2026-11-26*

**Decision:** The tea scene moved the cup out of the window onto the darker wall side of the sill, so the white cup
and its steam read; the window only frames sky, the sun and far hills. The bouquet's ribbon is rose red on a cream
wrap rather than lavender (it vanished among the lavender sprigs). On the card, MOM is drawn in saturated crayon colors
(rose, blue, violet) on a slightly dimmed pink paper.

**Why:** the first renders lost the cup against the bright sky and green treetops, the bow against the flowers, and
the dark-red M against the paper.

## D7 — Cards: two lines, sweet words on the day
*2026-11-26*

**Decision:** Text styles live in `renderer/scenes/text.py` (`LAYOUT`): cream into soft pink over a deep plum shadow
for the big lines, pale lavender for the small line. Before and after the day the count card is `N DAYS` (big) over
`TO MOTHER'S DAY` (tiny, 59 px). On the day the three count slots become `HAPPY` / `MOTHER'S DAY`, then one of
`LOVE YOU MOM` (big, 71 px: it fits edge to edge, so the count backdrop keeps its edges free of bright art),
`THANK YOU` / `FOR ALL YOU DO` or `BIG HUGS` / `TODAY AND ALWAYS`. Pages: clock 4.5 s + 3.5 s, count 6 s, greeting 5 s,
words 4 s. A test checks every text fits 72 px with its shadow and uses glyphs the fonts have.

**Why:** `MOTHER'S DAY` in `big` is 71 px wide, legal but cramped as a heading; the two-line layout matches the other
holiday apps. The words are short, warm and true for any kind of mom.

**Alternatives:** an app-local heart glyph (`I ♥ MOM`): fun, but it adds a font registration for one card.

## D8 — START previews the day; dates only from the kit
*2026-11-26*

**Decision:** START toggles holiday mode, which makes `playlist()` and the count slots behave as on Mother's Day, and
restarts the cycle at the first count slot (the playlist is rotated, not shortened) so the change shows at once. Press
START again to go back. The date is `nextOccurrence(t, HOLIDAYS.mothersDay)` (the second Sunday of May); no year is
hard-coded. Tests cover 9 May 2027, 14 May 2028 and 13 May 2029, the days before and after, and the first Sunday of
May.

**Why:** the playbook's holiday-mode spec, and the round-2 discovery that `show.start()` re-runs `steps(t)`.

## D9 — App-local helpers
*2026-11-26*

**Decision:** `renderer/mfx.py` holds the palette, flowers (tulip, rose, daisy, lavender, with a bud-to-open
`bloom()`), hearts (3, 5, 7 and 9 px, with an optional halo), petals, a butterfly and `person()` (adapted from
Kwanzaa's figure: adult or child, five hair styles, arm angles, a step, kneeling, seated, a skirt). `review_zoom.py`
(from Valentine's Day) zooms into columns for checking small sprites.

**Why:** `lib/` is frozen during the round; these are candidates for the kit if other apps want them.
