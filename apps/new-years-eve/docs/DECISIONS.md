# Decision log — New Year's Eve

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — Follow the Wizarding Thanksgiving pattern on the shared render kit
*2026-11-25*

**Decision:** A Python renderer bakes every scene and backdrop into full-screen 72×16 `.anim` files at 15 fps; a small
TypeScript app sequences them and draws live text as xpmbitmaps. Built on `lib/python/busybar` and `lib/ts/busybar`.

**Why:** Firmware playback is smooth with zero requests; the pattern is proven on the bar. The shared kit gives
identical fonts, tone curve and `.anim` encoding across the holiday apps.

## D2 — The manifest name is "New Years Eve"
*2026-11-25*

**Decision:** `manifest.json` says `New Years Eve`, without the apostrophe; docs and the mockup say New Year's Eve.

**Why:** `tools/new-app.sh` passes the name inside single quotes, so an apostrophe breaks the scaffold. It's unknown
whether the bar's menu renders `'` well. Easy to change later in one line.

## D3 — Everything is a pure function of the bar's local wall-clock time
*2026-11-25*

**Decision:** Phases, the year, card text, the demo offset and the step planner live in `app/shared/nye.ts` and take a
`LocalTime` from `walltime.parseLocal(device.TimeGet())`. No JS `Date` local-time methods.

**Why:** The bar knows its own time zone; the JS runtime doesn't. Pure functions can be tested across midnight and the
year boundary in Node, and the mockup runs the very same code (D10).

## D4 — Phases and the year
*2026-11-25*

**Decision:** Dec 31: party until T−61 s, final minute T−60…T−11, final ten T−10…T−1. Jan 1: celebration for the first
60 s, then "after midnight" until 06:00. Everything else is off-season. The year counted to is the year of the date
reached at midnight (on Dec 31, next year); on Jan 1 it's the year that just began; off-season it's the next new year.

**Why:** Matches the spec. The midnight countdown only happens on the real New Year's Eve; a countdown to every
midnight labelled with a year would be wrong eleven months a year.

**Alternatives:** Count down to every midnight (with `TO MIDNIGHT`). Rejected for the reason above; demo mode (D6)
covers testing any day.

## D5 — Scenes never overrun midnight
*2026-11-25*

**Decision:** In the party phase a scene starts only if it ends by T−60 s. A card is cut to end at T−60 s, or skipped if
less than 2 s would be left. Otherwise the final-minute screen starts straight away and counts `1:08`, `1:07` … until
the plain seconds take over at 59. Time-locked steps end exactly on the bar's second boundaries.

**Why:** The spec's rule ("go straight to the final minute"). The longest scene is 15 s, so the early start is at
most ~15 s, and the M:SS count keeps it honest.

## D6 — Demo mode is a clock offset to Dec 31 23:59:45
*2026-11-25*

**Decision:** START sets an offset (seconds) so the app's clock reads 15 s before the next Jan 1, carried across the year
with `addSeconds`. The offset clears itself once the effective time leaves Dec 31 / the celebration, i.e. after the
60 s celebration, and the app returns to real time. START again replays it.

**Why:** Every phase then sees a real NYE date, so the demo shows exactly what the night will (including the right
year), with no special cases in the logic. Auto-expiry means nobody is left with a bar stuck on Jan 1.

**Alternatives:** A "force NYE" flag; a toggle on START. Both add branches the tests would need to cover twice.

## D7 — Seconds are aligned to the bar's tick
*2026-11-25*

**Decision:** On start, and on cards when needed, the app polls `/api/time` (40 ms apart, at most ~30 times) until the
second changes and anchors `Date.now()` to that boundary. Between syncs it computes the time from the anchor. A card
does a single cheap read and re-measures the edge only when the clock drifted by more than a second, every 10 min,
or every 2 min in the last 15 min before midnight. Live ticks are scheduled 30 ms after each predicted boundary.

**Why:** "Aligned to the bar clock" for the final ten. `TimeGet` has whole-second resolution, so one read leaves up to
a second of phase error; the edge poll brings it to roughly one request's latency. The polling bursts are rare and
never happen during the final minute (it would delay the digits).

## D8 — One xpmbitmap per update; backdrops are `.anim` loops
*2026-11-25*

**Decision:** Each live screen is a list of layers (text, clipped text, rectangles) composed into a single xpmbitmap
(at most 32 colors, cropped to what's drawn), redrawn only when it changes: at most one request per second for the
countdowns, every 4 s for the celebration. The backdrops are seamless loops (card 4 s, final minute 2 s, last 30 s
1 s, final ten exactly 1 s so its flash lands on every beat, fireworks 6 s) plus a 3 s one-shot burst at midnight.

**Why:** The bar handles one HTTP request at a time; draws faster than about 1/s would starve it. Composing card text
(clock font) and labels (tiny font) into one bitmap halves the requests.

## D9 — An app-local "huge" font for the final ten and the year
*2026-11-25*

**Decision:** 10×15 digits with 3 px strokes, registered with `busybar.font.register_font("huge", …)` in
`renderer/live.py` and exported with the other fonts. `tests/live_parity.py` checks the app's composed bitmaps against
`draw_text`, pixel for pixel, including this font, clipping and the progress bar.

**Why:** The 7×12 clock font isn't dramatic enough for the last ten seconds; 15 px plus the shadow fills the display.
App-local because `lib/` is frozen during parallel work.

## D10 — The mockup runs the app's own TypeScript
*2026-11-25*

**Decision:** `build.py` type-strips `walltime.ts`, `xpmtext.ts`, `nye.ts` and `screens.ts` with Node 24's
`module.stripTypeScriptTypes`, drops the import lines and inlines them into `mockup/index.html` as `NYE.*`. The
simulator runs the same planner loop as `main.ts` on a virtual clock.

**Why:** A hand-written JS copy of the phase logic would drift. This keeps the mockup honest by construction.

**Cost:** The prebuild needs Node 24 (already required by the toolchain and tests). Shared files keep single-line
imports and avoid enums and namespaces. `stripTypeScriptTypes` is marked experimental; if it changes, swap in
`typescript.transpileModule` from the app's devDependencies.

## D11 — Party palette: golds, silvers and neon on midnight ink
*2026-11-25*

**Decision:** Gold and silver gradients for live text, neon pink, cyan, lime and violet for lights, confetti and
fireworks, on deep navy-to-purple skies. The mockup uses Limelight (art deco) with champagne gold.

**Why:** Reads as New Year's at a glance and stays distinct from Wizarding Thanksgiving's candle gold on plum.

## D12 — Tone curve GAMMA = 0.8
*2026-11-25*

**Decision:** Same tone curve as Wizarding Thanksgiving, applied by `build_scenes` to every frame and with `tone_rgb` to
every live-text color.

**Why:** Approved on the real hardware. Dark skies and dim glitter stay visible; unlit pixels stay off.

## D13 — Eight scenes, ordered for variety
*2026-11-25*

**Decision:** Disco Fever, Champagne Pop, The Clock Tower, Confetti Poppers, Year Odometer, Conga Line, Ball Drop
Rehearsal, Fireworks Finale (12–15 s each). Party hats and noisemakers live in the conga line rather than a scene of
their own. After the countdown and the celebration the party resumes with a scene, not a card.

**Why:** Alternates calm and busy scenes, and close-ups with wide shots. The ball drop "rehearses" (stops halfway and
goes back up) so it never pretends midnight has come.

## D14 — The odometer's digits are live
*2026-11-25*

**Decision:** The scene bakes the gold frame, the drum shading, the glint and the confetti. The app draws the four
digits at 0.9 s, mid-roll at 6.0 s and rolled over at 6.4 s (`OVERLAY` in the scene module, exported to `show.ts`).

**Why:** A baked year would be wrong next year. Only the digits that change roll, so 2029 → 2030 rolls two.

## D15 — Readable at LED scale
*2026-11-25*

**Decision:** Lit colors for small features (guests have no dark eyes; the bottle is a lit green; clock hands are gold
and white on a dark face). Captions that sit over busy art get a darker band baked into the backdrop (the fireworks
loop dims its middle to 35 % where `HAPPY NEW YEAR` goes). The final-ten backdrop throws its sparks outside the digit.

**Why:** Reviewed every scene and live screen as LED strips: a cream clock face with dark hands, and a ring crossing
the huge digits, both read poorly and were changed.
