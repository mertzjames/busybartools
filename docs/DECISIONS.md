# Decision log

A running record of design decisions for the **Wizarding Thanksgiving** BUSY Bar party screen.
Each entry: what was decided, why, and what else was considered. Newest entries at the bottom.

---

## D1 — Run the show as an on-device JS app, not a laptop-driven player
*2026-11-25*

**Decision:** The scene playlist and clock run inside a BUSY Bar JS app (`app/`), installed on the bar.

**Why:** The bar has to run unattended for hours during the party. A JS app keeps running with no laptop,
no Wi-Fi dependency for drawing, and no risk of a sleeping computer freezing the screen. Firmware is the
latest release, which is past the 1.3.1 minimum for JS apps.

**Alternatives:** A Python script on a laptop calling `POST /api/display/draw` over Wi-Fi. That's easier to
iterate on, but fragile for a party. It stays the fallback if app install fails (see Risks in `PLAN.md`).

---

## D2 — Pre-render every scene as a full-screen 72×16 `.anim`
*2026-11-25*

**Decision:** Each scene is baked into one `.anim` file covering the whole front display, background
included. The app draws a single `animation` element per scene.

**Why:** `.anim` files are played by the firmware at their own fps with zero HTTP requests. Timer-driven
redraws top out around 3 visible fps, which is far too choppy for walking/flying characters. Baking the
background into the same file keeps layering trivial and guarantees what we preview is exactly what plays.

**Alternatives:** Separate sprite `.anim`s over `xpmbitmap` backgrounds. That gives smaller files, but
z-ordering, timing sync and colour-per-file limits make choreography much harder for little gain.

---

## D3 — Sprites are ASCII pixel grids in Python; one renderer feeds device *and* mockups
*2026-11-25*

**Decision:** `renderer/` (Python + Pillow) defines sprites as text grids with a palette and choreographs
scenes frame by frame. One build writes the `.anim` files, GIF previews, and the frame data that the
browser mockup plays.

**Why:** Text-grid sprites are easy to review in diffs and to tweak from feedback without an art tool. A single
source of truth means the mockup you approve is pixel-identical to what the bar shows.

---

## D4 — Vendor the community `.anim` writer (MIT) instead of the firmware converter
*2026-11-25*

**Decision:** `renderer/anim_writer.py` is adapted from `devrsw/busybar-skill` `templates/make_anim.py`
(MIT, attributed in the file). It writes raw BGRA8888 with a whole first frame and changed-pixel deltas after that.

**Why:** It has no dependencies, its single-section output is reported to match a generator used in production,
and it needs no firmware checkout. The firmware's `seq2anim.py` compresses better (QOI/RLE) but imports
firmware-repo helpers. We'll switch to it only if file size turns into a problem.

**Constraint adopted:** Single section per file (multi-section output hasn't been verified on a device).
Transparent and unchanged pixels stay byte-identical so deltas stay small.

---

## D5 — Original pixel art only
*2026-11-25*

**Decision:** Characters and props are original designs that *suggest* the wizarding theme (a boy wizard
with round glasses, a snowy owl, a pointed talking hat, floating candles, a steam train). Nothing is copied from
official artwork, logos or fonts, and no trademarked names appear on screen.

**Why:** It keeps the display ours, and the jokes work through references ("GOBBLEDOR!", "LEVIOSA!").

---

## D6 — Eight scenes, with a clock/date card after each
*2026-11-25*

**Decision:** Playlist order: Owl Post → Gravy Express → Broom Chase → Cauldron Bake-Off → Great Hall
Feast → Sorting the Turkey → Dragon Roast → Pumpkin Patronus, with a ~8 s clock/date card after every scene.
Scenes run ~15–25 s each, so a full cycle is about 4 minutes.

**Why:** You approved the original five and asked for 2–3 more. The Gravy Express, Cauldron Bake-Off and Dragon
Roast were added. Alternating busy and calm scenes, with the clock in between, gives guests a regular, predictable
moment to read the time.

---

## D7 — Time and date: live firmware text over a looping backdrop; 24-hour, from `TimeGet()`
*2026-11-25*

**Decision:**
- The clock card is a looping background `.anim` (candles/parchment) plus live `text` elements.
- The time `HH:MM` is 24-hour. The date is formatted like `THU 26 NOV`.
- Both are computed from `device.TimeGet()` (UTC timestamp + its `±HH:MM` offset), not from JS `Date`
  local-time methods, which don't know the bar's timezone.
- The minute is updated on the minute boundary.

**Why:** A baked `.anim` can't know the time, so the digits must be live elements. The firmware fonts
(`large` for time, `small` for date) are crisp at this size.

---

## D8 — Frame rate: 15 fps (provisional)
*2026-11-25*

**Decision:** Render scenes at 15 fps.

**Why:** It's smooth enough for 1-pixel-per-frame walking/flying at this resolution and keeps `.anim` files
about 25% smaller than 20 fps. We'll revisit after seeing it on the hardware.

---

## D9 — Secrets and tooling
*2026-11-25*

**Decision:**
- The bar's HTTP API password is never committed. Scripts read it from `BUSYBAR_TOKEN` or a git-ignored `.env`.
- The BUSY CLI needs Node 24 (this Mac has Node 26), so app builds run under Node 24 via `npx -p node@24` or a
  Homebrew `node@24` instead of changing the system Node.
- Target device: `<bar-ip>` (Wi-Fi), API header `X-API-Token`.

---

## D10 — The clock uses our own pixel fonts drawn as `xpmbitmap`, not firmware fonts
*2026-11-25*

**Decision:**
- The time uses a custom 7×12 digit font with 2 px strokes. The date uses our 5×7 headline font.
- Both are drawn in candle gold with a vertical gradient and a 1 px shadow.
- The app turns the glyph tables into `xpmbitmap` elements at runtime. The text fades in with three opacity steps, 150 ms apart.

**Why:**
- The firmware's built-in fonts can't do gradients or shadows, and the mockup couldn't match them exactly.
- Exporting one glyph table (`renderer/font.py` → `app/src/generated/show.ts` and the mockup) means the browser
  preview, the storyboards and the bar draw identical digits.
- The XPM palette stays well under the 32-color limit: 12 gradient rows plus a shadow.

**Supersedes:** the "firmware `large`/`small` text" part of D7. The time source and 24-hour format are unchanged.

---

## D11 — What's committed vs generated
*2026-11-25*

**Decision:**
- Commit the generated `app/src/animations/*.anim` (~1 MB total) and `app/src/generated/show.ts`. That way the app can be
  built and installed without running Python.
- Commit `mockup/index.html` (~0.8 MB, self-contained) so the review page opens straight from the repo.
- Do **not** commit `previews/*.gif` (~3 MB, regenerated on every build).

**Why:** It keeps the repo usable from a fresh clone without making every sprite tweak add megabytes of GIFs to the history.

---

## D12 — Storyboards and the animated simulator ship together as mockup 1
*2026-11-25*

**Decision:** The plan had two mockup checkpoints: static storyboards, then an animated simulator. They're combined into
one review page: the simulated bar plays the full show, and the storyboards for every scene sit below it.

**Why:** Both come from the same renderer output, so splitting them would only delay feedback. Feedback on either one
goes back into the renderer, and the page regenerates in about 2 seconds.

---

## D13 — Scene tuning from the first visual pass
*2026-11-25*

Changes made while checking renders at LED scale, before the mockup went out:
- The roast turkey now has a single bone tip. Two tips read as cat ears.
- The talking hat shrank from 14×10 to 10×8 so it sits on the turkey's head instead of hiding the whole bird.
- The cauldron is lighter grey, because dark grey disappears against the dungeon wall on LEDs.
- The train chimney and wheels are lighter grey for the same reason.
- The patronus halo is at 45% so the turkey silhouette stays readable.
- The owl scene's moon hides while HAPPY / THANKSGIVING is on screen, since the 67 px word needs the full width.

---

## D14 — Generated app data lives in `app/shared/`, not `app/src/`
*2026-11-25*

**Decision:** `renderer/build.py` writes the playlist and font tables to `app/shared/generated/show.ts`.

**Why:** `busy-cli build` treats every `.ts` file under `src/` as its own script. With the data in `src/generated/`,
the first build emitted `scripts/generated-show.js`, and `main.js` began with an ES `import`. The firmware runs
`main.js` as a plain script, so it would likely fail to start. Files under `shared/` are bundled into `main.js`.
The current package has one `main.js` with no imports or exports.

---

## D15 — Read local time straight from `/api/time`, and round halves up everywhere
*2026-11-25*

**Decision:**
- The app reads `HH:MM` and the date directly from the wall-clock fields of the `TimeGet()` timestamp
  (`2026-11-26T18:05:42-05:00`). The timestamp is already local to the bar's timezone, so no offset math is needed.
- The weekday comes from `Date.UTC(y, m, d)`.
- If the minute rolls over while the time is showing, the app updates it in place without another request.
- Color blending rounds halves up in Python (`floor(v + 0.5)`), matching JS `Math.round`.

**Why:** It refines D7. The rounding fix came from a parity test of the app's XPM output against the renderer: the
date differed by one color level on some rows because Python's `round()` rounds halves to even. After the fix, the app,
the mockup and the renderer produce identical clock pixels for `18:05`, `09:59` and `THU 26 NOV`.

---

## D16 — One-command deploy with a raw-API fallback
*2026-11-25*

**Decision:** `scripts/deploy.sh` does the whole deploy:
1. Checks `GET /api/version`.
2. Renders the scenes and builds the app under Node 24.
3. Installs and runs it with `busy-cli`.
4. If `busy-cli` fails, falls back to `POST /api/apps/stage` → `install` → `launch`.

The address and password come from the environment or a git-ignored `.env`.

**Why:** A community report says `busy-cli` 0.6 `app install` failed against one firmware version. The raw endpoints
are what the CLI calls anyway.

**Network note (2026-11-25):** The development computer and the bar (`<bar-ip>`) were on different subnets
reached through the router. Ping and HTTP both time out, which points to inter-VLAN filtering or Wi-Fi API access being
off. USB (`10.0.4.20`) avoids the problem entirely.

---

## D17 — The cauldron witch is a schoolgirl witch, not a Halloween witch
*2026-11-25 · from your mockup 1 feedback*

**Decision:**
- The witch sprite in scene 4 (Cauldron Bake-Off) was redrawn. The pointed purple hat and green skin are gone.
- She now has bushy brown hair, normal skin, a red-and-gold house scarf and the same school robe colors as the boy wizard.
- Her toss pose is now a wand flick: the wand tip sits where ingredients launch from (`HAND`).

**Why:** You said she read as a Halloween witch. The wizarding-school look comes from robes, a house scarf and a wand.
Matching the boy wizard's proportions and robe makes the two read as classmates across scenes.

---

## D18 — Wizard glasses: two green eyes in silver frames
*2026-11-26 · from your mockup comments on scenes 5 and 8*

**Decision:**
- The boy wizard's face row changed from three dark pixels (`SgSgSg`) to silver frames around two green eyes
  (`GeGGeG`). The broom rider got the same change (`GeGeG`).
- The raised-wand frame was redrawn so the hand, sleeve and wand meet the new face row. The wand tip stays at sprite
  column 8, row 0, so the sparkle positions in scenes 5 and 8 still line up.

**Why:** On LEDs, a black pixel is an unlit LED, so the dark glasses pixels showed up as holes in the face. Three holes
in a row read as three eyes. Lit colors survive: silver frames and green eyes read as glasses at 16 px tall.
**Rule adopted:** never use near-black for facial details. Use a lit color.

---

## D19 — Every student wears a different house's colors
*2026-11-26 · from your mockup comment on the storyboards*

**Decision:** Each wizard or witch who appears wears their own house scarf colors:

| Scene | Character | Scarf |
|---|---|---|
| 3 Broom Chase | wizard on the broom | scarlet and gold |
| 4 Cauldron Bake-Off | young witch | blue and bronze |
| 5 Great Hall Feast | wizard with the levitation spell | yellow and black |
| 8 Pumpkin Patronus | wizard casting the patronus | green and silver |

**How:** `Sprite.recolor()` swaps the scarf palette keys (`R` main stripe, `Y` accent) on the shared sprites, so the
pixel art stays in one place. "Black" is a lit dark grey (`#5A5A5A`), because true black is an unlit LED and the stripes
would disappear (same rule as D18).

**Why this pairing:** One house per appearance. Scarlet and gold goes to the broom chase, the most action-packed scene.
The cauldron (brewing) gets blue and bronze. The patronus, the last scene of the loop, gets green and silver so every
house is on screen once per cycle.

---

## D20 — Verified on the hardware
*2026-11-25*

**Status:** Installed and launched over Wi-Fi on the bar at `<bar-ip>`, which runs API 27.16.0.
`scripts/screens.py` captured 24 frames from `GET /api/screen` over 60 s. They show:
- Owl Post → clock → date → Gravy Express → clock → date → Broom Chase → clock → Cauldron;
- the scene `.anim`s playing on the firmware;
- the XPM clock text rendering;
- the date (`WED 25 NOV`) matching the bar's own clock and timezone;
- the time updating live from 19:30 to 19:31 across clock cards.

**Setup decisions:**
- The development computer needed network access to the bar, and Wi-Fi HTTP API access had to be turned on in the
  bar's web UI. See the README's install guide.
- Password protection is optional. With a password, the scripts read it from `BUSYBAR_TOKEN` in `.env`.

**Fixes found while deploying:**
- `scripts/deploy.sh` crashed on macOS's bash 3.2 when no password was set. Under `set -u`, an empty array counts as
  unset. Fixed with `${auth[@]+"${auth[@]}"}`.
- Added `scripts/screens.py` for screen captures. Frames come back as base64 BGR, 72×16×3.

**Limit:** `/api/screen` returns the framebuffer, not how the LEDs actually look in the room. Brightness and color
tuning still need someone looking at the bar.

---

## D21 — Brighten the content with a tone curve (gamma 0.8); leave the bar's brightness on auto
*2026-11-25 · you asked to "brighten it up a little"*

**Decision:**
- `renderer/build.py` applies `v' = 255 · (v/255)^0.8` to every output frame and to the clock colors.
- One knob controls it: `GAMMA`. `1.0` gives the original colors; lower values are brighter.
- The bar's hardware brightness stays on `auto` (that's how it was found: `GET /api/display/brightness` →
  `{"value":"auto"}`).

**Effect:** Dark backgrounds, dim stars and midtones lift the most. For example, a background value of 20 becomes 33,
128 becomes 147, and 200 becomes 210. Black stays an unlit LED and full brightness stays full, so colors don't wash out.

**Why not the hardware setting:** A fixed hardware brightness overrides the bar's light sensor for every app, and it
could end up dimmer than auto in a bright room. If the room still needs more at party time, the app can set
`display/brightness` when it launches and restore `auto` when it quits. That endpoint is on the app allowlist.

**Deploy note:** This time `busy-cli app install` failed while the previous build was still running. The raw-API
fallback in `deploy.sh` (stage → install → launch) installed and relaunched the app correctly. A screen capture
confirmed the new build was playing.

---

## D22 — The dragon becomes a menacing winged serpent that torches the turkey
*2026-11-25 · from your feedback after seeing the bar in person*

**Decision:** Scene 7 (Dragon Roast) was rebuilt:
- **Body.** A procedural serpent about 30 px long. Each segment sits 1 px of arc length behind the neck on the head's
  own flight path, so the body trails it like a snake. A traveling wave keeps it writhing while it hovers. The body
  tapers from 3 px (green back, gold belly) to a 1 px tail with a red spade, with red spines along the back.
- **Head.** Horned, brighter green than the body so it reads separately, with a glowing red eye that flares and fanged
  jaws that open.
- **Wings.** Dark crimson bat wings with green bones, set 12 px back along the body so they don't hide the head. They
  flap fast in flight and slow while hovering.
- **Action.** No more sneeze. The dragon swoops in, rears up with smoke curling from its nostrils, and torches the
  turkey with a sustained flame jet (about 3 s, flickering core plus flame fringe and impact flare). Then it flies up
  and off over the roast. The caption changed from "DONE!" to "WELL DONE!".

**Why:** You asked for something longer, snake-like with wings and more menacing, that torches the turkey instead of
sneezing. You also said brightness and colors look good on the bar, so D21's gamma 0.8 stays.

---

## D23 — Quit the running app before reinstalling
*2026-11-25*

**Finding:** Installing while the previous build is running fails. `POST /api/apps/install` returns 400, and the
firmware gives no reason. It also leaves the app **uninstalled**: launch then returns 404, and the app is gone from
`/api/apps/list`. That's why `busy-cli app install` failed on the last two deploys. The fallback in D16 only worked the
first time by luck of timing.

**Decision:** `scripts/deploy.sh` now sends `POST /api/apps/quit` (and ignores the 409 if nothing is running) before
installing. Sequence verified by hand: quit → stage → install → launch all returned 200.

**Testing tip:** `POST /api/input?key=ok` presses OK remotely, which skips to the next step. Twelve presses after a
launch jump to scene 7 (Dragon Roast), which is how the new dragon was captured on the bar with `scripts/screens.py`.

---

## D24 — The review page becomes a shareable showcase
*2026-11-25*

**Decision:** `mockup/template.html` (published as the "Wizarding Thanksgiving" artifact) was reframed from a feedback
page into a showcase for colleagues:
- the live simulator of what's on the bar;
- what the project is, and how it works in four steps;
- scene-by-scene storyboards;
- grouped highlights from this decision log;
- the plan and how it went;
- lessons from the hardware.

**Kept out on purpose:** personal details, such as the in-room photos (they show the inside of a home), names,
addresses and network specifics beyond what's needed to tell the story.

---

## D25 — Ready for a public repo
*2026-11-25 · you're making the repo public so others can use it*

**Decision:**
- **Install guide in the README.**
  - Option A: no tools, upload the prebuilt package in the bar's web UI.
  - Step-by-step instructions for enabling the HTTP API over Wi-Fi, with a `curl` test.
  - Option B: build from source with `scripts/deploy.sh`.
  - Also covers controls, uninstalling, customizing and troubleshooting.
- **Prebuilt package committed** at `release/wizard.thanksgiving.tgz` (~300 KB), so people without Python and Node can
  install from the bar's web page. Refresh it by copying `app/dist/wizard.thanksgiving.tgz` after a rebuild.
- **No personal defaults.** The scripts default to the USB address `10.0.4.20`, and your Wi-Fi address now lives in a
  git-ignored `.env`. `.env.example` documents `BUSYBAR_ADDR` and `BUSYBAR_TOKEN`. Home-network IPs and subnets in this
  log and in `PLAN.md` became `<bar-ip>` and "the development subnet".
- **MIT license** with the copyright held by "busybartools contributors", plus `NOTICE.md`. The notice credits the MIT
  `.anim` writer it's adapted from, and states this is an unofficial fan project with original art and no affiliation
  with the franchise or with BUSY.
- **Three small preview GIFs** in `docs/media/` (~200 KB each) for the README. That's an exception to D11's "no
  GIFs", kept small by halving the frame rate.

**Not changed:** git history. Earlier commits still contain the old home-network IP in a few files. Those are private
LAN addresses and low risk. Removing them would mean rewriting history before publishing, which is your call.
