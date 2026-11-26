# Decision log — Juneteenth

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with
live-text cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is
configuration: scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/juneteenth.ts`.
The shape (renderer, `app/shared/` logic module, mockup with the app's logic inlined, tests) follows Easter and MLK
Day from this round.

**Why:** It is the round-2 common spec. The runner already handles one request in flight, card pages, fades and the
minute rollover.

## D2 — Tone curve: GAMMA 0.8
*2026-11-26*

**Decision:** `GAMMA = 0.8` in `renderer/build.py`, applied to every frame and every live-text color.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every holiday app, so the apps
look alike on the bar.

## D3 — Opens solemn, becomes joyful
*2026-11-26*

**Decision:** Seven scenes in a fixed order: (1) dawn over Galveston Bay, (2) the news arriving and the date
`JUNE 19, 1865`, then (3) the Juneteenth flag, (4) a family cookout, (5) red drinks and red foods, (6) music and
dancing in the park, (7) a fireworks finale with `HAPPY` / `JUNETEENTH` and `FREEDOM DAY`. The first two scenes are
slow, quiet and calm in color, with no confetti or party effects; the celebration starts with the flag. Fireworks
use `busybar.party`.

**Why:** It is how the day is observed: remembrance of June 19, 1865, then a celebration of freedom. The round-2
playbook lists Juneteenth among the tributes and allows it to end in celebration.

**Alternatives:** A lighter show with fireworks throughout (rejected: it loses the history); an extra "reading the
order" close-up scene (rejected: it adds more text and the posted notice already carries the moment).

## D4 — The solemn part is about dawn, news and hope; no trauma imagery or likenesses
*2026-11-26*

**Decision:** No chains, no violence, no suffering imagery, and no likenesses of real people. The news scene shows
a rider in a blue coat posting a notice on a board, townspeople coming out to read it and raising their arms, then
the date over `GALVESTON TEXAS`. Nothing names or depicts General Granger. The text of General Order No. 3 is not
quoted.

**Why:** The brief, and respect: the day is about freedom arriving. A rider and a posted notice tell the story at 16
pixels without depicting anyone real or any suffering.

## D5 — The Juneteenth flag, drawn by hand and waved by whole rows
*2026-11-26*

**Decision:** The official design (2:3): a white five-point star inside a white outlined twelve-ray nova, centered
on the flag, on a field split by a broad arc spanning the width (a new horizon), blue above and red below. In the
flag scene it is 21 × 14 with an 11 × 11 hand-drawn nova and a 5 × 5 star (`NOVA_11` in `renderer/jfx.py`); small
hand-held flags (7 × 5) use a 3 × 3 star (`NOVA_3`). The arc runs from about 0.8 of the height at the edges to
0.56 at the middle, so it passes through the lower part of the nova.

The cloth waves Presidents' Day's way: each column shifts by a whole number of rows (fractional shifts blur white
into pink and blue) and is shaded by the wave's slope. **The star and nova move as one piece**, shifted by the wave
at the flag's center, so they never shear apart.

**Why:** A procedural twelve-ray outline at 11 px read as a blob or a scatter of dots; the hand-drawn ring with
tips at the corners reads as a burst around a star. Shifting the emblem per column broke the star into fragments on
every frame; moving it whole keeps it crisp while the field still ripples.

**Alternatives:** A ray burst instead of an outline (read as a sun, and the official nova is an outline); a
full-screen close-up of the flag (about 300 KiB more, and the whole flag is easier to recognize).

## D6 — People: faceless figures with a range of warm skin tones
*2026-11-26*

**Decision:** Every person is a simple figure (`jfx.person`, adapted from Kwanzaa's): a 3 × 3 head in one of six
lit warm skin tones, hair in lit dark browns (short, a rounded puff, two buns, long), or a headwrap, cap or
wide-brim hat, and clothes in light or saturated colors. No eyes or mouths. In the finale the crowd is seen from
behind (hair and shoulders) against a warm glow.

**Why:** A 3 × 3 head has no room for lit eyes, and dark pixels read as holes (AGENTS.md). Light, saturated clothes
keep small figures readable against grass, walls and dusk skies.

**Detail:** Review caught several contrast traps that were fixed: a bay horse and a brown-skinned rider vanished
on a tan street under a cream sky (now a blue sky, a grey-brown street and a darker horse); cream shirts vanished
on a whitewashed storefront (now painted blue-grey); hats merged with the storefront's brown roof trim (moved to the
top row); watermelon rinds disappeared against a green hedge (the hedge is gone, the food sits under a blue sky).

## D7 — App-local drawing helpers
*2026-11-26*

**Decision:** `renderer/jfx.py` holds the palette, skies, `qmix` (quantized light changes), glows, `dim_rect`, the
flag and `person()`. Sprites (a horse with two gallop frames, a two-masted ship, a lighthouse) are text grids in
`renderer/sprites.py`.

**Why:** `lib/` is frozen for app agents (playbook); these stay app-local until another app needs them (repo R2).

## D8 — Cards and their words
*2026-11-26*

**Decision:**
- **Clock** (every other step): the time (`clock` font), then the date.
- **Countdown**, before and after the day: `N DAYS` / `TO JUNETEENTH` (`1 DAY` the day before). After June 19 it
  counts to next year's; the longest is `365 DAYS`.
- **On June 19** the count slots become two day cards, taking turns: `JUNETEENTH`, then `FREEDOM DAY` / `JUNE 19`;
  and `HAPPY` / `JUNETEENTH`, then `CELEBRATE` / `FREEDOM`.
- Colors from the flag over a deep navy night: starlight white into gold for times and headlines, a lit coral red
  for small lines and `HAPPY`. Shadows are dark and of another hue (deep crimson under gold, deep navy under red).
- Backdrops: the clock's has a few stars and the flag's horizon (a red arc under a blue band) along the bottom; the
  countdown's has a small star-in-a-burst at each end; the day's has red, white, blue and gold glints in the edge
  bands. Each declares `TEXT_GAP`, and the parity test checks every text stays inside it.

**Why:** Celebratory and dignified. `FREEDOM DAY` and `JUNE 19` name the day and its history without quoting
anyone. "Freedom Day" and "Jubilee Day" are both traditional names; `FREEDOM DAY` is the clearer one.

## D9 — Red foods, and what the red means
*2026-11-26*

**Decision:** The red foods scene shows strawberry soda, watermelon, red velvet cake and strawberries, then dims
behind `RED FOR` / `RESILIENCE`.

**Why:** Red food and drink is a Juneteenth tradition, often explained as a symbol of resilience (other accounts
link it to West African traditions or to the sacrifices of ancestors). The brief chose resilience; the short caption
shares the meaning without a long explanation.

## D10 — START previews the day
*2026-11-26*

**Decision:** START toggles holiday mode: the on-the-day cards and playlist on any date. Pressing it restarts the
cycle at the first count slot (`show.start(firstCountStep(n))`, the runner's `start(from)`), so the change shows at
once. The mockup has the same toggle and calls the same functions.

**Why:** Reviewers can see June 19 without waiting for it (the common spec). Starting on the count slot instead of
the top means the press has a visible effect within a second.

## D11 — One source for every word, and tests against real dates
*2026-11-26*

**Decision:** Live-text styles, the day-card review copy and the words baked into scenes live in
`renderer/scenes/text.py`; the app's card text lives in `app/shared/juneteenth.ts`. `tests/text_parity.py` checks
the two agree, that the app's bitmaps match the renderer pixel for pixel, that every text clears the backdrops' edge
art, and that every baked caption fits with its shadow and has every glyph (the `big` font has a comma; `tiny` does
not, so `GALVESTON TEXAS` has none). `tests/logic.test.mts` tests the dates (2026–2040), the card texts before, on and
after the day, the playlist, START with the real runner, and runs the mockup's inlined logic against the app's on
every day of 2026–2030.

**Why:** The round-2 discoveries: width traps and drift between the app, mockup and renderer.

**Detail:** The mockup concatenates `walltime.ts`, `holidays.ts` and `juneteenth.ts` into one scope, so a top-level
name in the app module must not repeat one in the kit (`DAY_MS` collided with `holidays.ts`; it is `DAY_PAGE_MS`).

## D12 — Size: keep slow light changes quantized
*2026-11-26*

**Decision:** The dawn sky blends in 40 quantized steps (`jfx.qmix`) and caches each step; glows hold steady between
frames. Total `.anim` data is about 1.3 MB.

**Why:** The round-2 discoveries: per-frame changes over large areas bloat the files.
