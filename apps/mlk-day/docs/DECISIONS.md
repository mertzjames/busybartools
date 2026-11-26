# Decision log — MLK Day

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Build on the shared show runner, like the other holiday apps
*2026-11-26*

**Decision:** Pre-rendered full-screen `.anim` scenes (Python renderer, 15 fps, the kit's `showbuild`) with live-text
cards between them, played by the kit's `createShow()` (`lib/ts/busybar/showrunner.ts`). `main.ts` is configuration:
scenes from the generated `show.ts`, cards and a `steps(t)` playlist from `app/shared/mlk.ts`.

**Why:** It is the round-2 common spec, and the runner already handles one request in flight, card pages, fades and
the minute rollover. Christmas Day's own playback loop is the older pattern.

## D2 — A tribute: calm, no likenesses, no quotations
*2026-11-26*

**Decision:**
- Slow pacing (14–18 s scenes, captions fade in over about 2 s) and calm color: deep blues and dawn golds. No
  confetti, fireworks, jokes or party effects. Nothing depicts violence.
- No likeness of Dr. King or any real person. People are small generic figures with no faces. In "Many Hands" they
  are seen from behind, so a head is just hair.
- No quotations from his speeches or writings: the King estate enforces copyright. On screen there are only single
  common words (`TOGETHER`, `PEACE`, `UNITY`, `FREEDOM`, `SERVICE`, `DREAM`, `EQUALITY`), the holiday's name, the
  countdown, and the MLK Day of Service motto `A DAY ON` / `NOT A DAY OFF`.

**Why:** The playbook's tone rules for tributes. Places and symbols (a march at sunrise, a dove, bells, a mountaintop)
carry the meaning without putting words in anyone's mouth.

**Judgment call for review:** "a mountaintop" and the word `DREAM` both evoke famous speeches without quoting them.
They are in the brief; the user should confirm they are comfortable with the pairing in the closing scene.

## D3 — Six scenes, night into morning
*2026-11-26*

**Decision:** March at Dawn, A Dove over the City, Many Hands, Freedom Bells, A Day of Service, Dawn on the
Mountaintop (94 s of scenes). The march opens the show because it is the strongest image of people walking
together; the mountaintop closes it, with `DREAM`.

**Alternatives:** A seventh, separate closing scene with a single word over a plain sunrise. The mountaintop already
does that job, and six scenes give three clock and three count slots, which matches the three on-the-day cards (D8).

## D4 — Tone curve
*2026-11-26*

**Decision:** `GAMMA = 0.8`, applied at build time to every frame and to the card text colors.

**Why:** The value approved on real hardware for Wizarding Thanksgiving and used by every scene app since.

## D5 — People of every age and skin tone, all lit
*2026-11-26*

**Decision:** Figures are drawn procedurally (`renderer/mfx.py`, `Person`) so skin tone, hair and clothes vary freely:
six skin tones from light to deep, adults, teens, children, an elder with a cane, and a parent carrying a child on
the shoulders. Families hold hands. The deepest skin tone is `#764A32`, which stays lit on the panel. The march adds
a faint warm rim light on each figure's sunward edge.

**What was tried:** A march over a warm dawn gradient: the clothes and legs dissolved into the orange horizon. Moving
the horizon behind the walkers' shoulders, with dark fields below and a blue-violet sky that keeps the warmth near
the sun, made every figure read. Shading the figures as backlit made them dull, so it was dropped. The first "Many
Hands" (a zigzag of arms rising from the bottom edge) read as a pattern, not people, so it became six people seen from
behind with heads and shoulders.

## D6 — One word per scene, placed in clear sky
*2026-11-26*

**Decision:** Each scene ends with one word that fades in slowly: big font where there is room (`PEACE`, `UNITY`,
`FREEDOM`, `DREAM`, the mural's `SERVICE`), tiny where people fill the frame (`TOGETHER`). Layouts keep the word clear
of the action: the dove's skyline is lower under `PEACE`, the joined hands lower to shoulder height before `UNITY`,
the far ridge sits below `DREAM`, and the sun moves out from under the captions.

## D7 — Calm cards
*2026-11-26*

**Decision:** Card text uses warm white into dawn gold over a deep-blue shadow, with a pale sky blue for the small
second line (`TO MLK DAY`, `NOT A DAY OFF`). Styles (`renderer/scenes/text.py`): `time` (clock font, y 2), `date` and
`word` (big, y 4), `head` (big, y 1) and `sub` (tiny, y 10). Backdrops: the clock card has a still pre-dawn sky over a
low skyline with a few warm windows; the countdown and day cards have a gold dawn band that breathes slowly, with faint
rays. The text band in the middle stays dark.

**Why:** The brief asks for calm colors and no rainbow gradients. The two backdrops tell the cards apart at a glance.

## D8 — Card logic in one pure module, shared by app, mockup and tests
*2026-11-26*

**Decision:** `app/shared/mlk.ts` returns every card's pages as styles and strings (`cardPages(name, t)`) and the
playlist (`playlist(scenes, t, holiday, fromCard)`). `main.ts` maps styles to `LAYOUT` specs. Every line is
recomputed from the time it is drawn at, so the clock rolls over and the countdown changes at midnight. The mockup
runs the same file: `build.py` type-strips it with Node 24 (with the kit's `walltime.ts` and `holidays.ts`) and
inlines it, as New Year's Eve does. The date comes only from `HOLIDAYS.mlkDay` (`nextOccurrence`, `daysLabel`).

**On the day:** the three count slots become `day0`, `day1` and `day2`: `MLK DAY` then `DREAM`; `MLK DAY` then
`EQUALITY`; and `MLK DAY`, then `SERVICE`, then the motto. Pairing `SERVICE` with the Day of Service motto keeps the
rotation to three cards, one per slot, with no state across cycles.

**After the day:** the countdown counts to next year's MLK Day (`363 DAYS` on the Tuesday after).

## D9 — START previews the day, starting on a card
*2026-11-26*

**Decision:** START toggles holiday mode (the on-the-day cards and playlist on any date). It restarts the cycle with
the playlist rotated to begin at the first count slot, so the change is visible at once (`MLK DAY`, or `N DAYS`
when switching back). The next cycle starts from the top as usual. The runner reports START as "ignored", and the
app handles it there.

**Alternatives:** Waiting for the next cycle (about 2 minutes) gave no feedback.

## D10 — Size
*2026-11-26*

**Decision:** About 2.0 MB of `.anim` data for six scenes and two backdrops, under the round's 3 MB budget. The
march, dove, bells and mountaintop are the largest (about 400 KiB each), because their skies change every frame.
