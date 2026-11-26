# Wizarding Thanksgiving — BUSY Bar party screen

## Context
You're hosting a Harry Potter–themed Thanksgiving (Thu 26 Nov 2026) and want the BUSY Bar's front display (72×16 RGB LED) to run on its own during the party. It should cycle through animated scenes where characters walk, fly or interact, and every so often show the time (24-hour) and date in the same style. The repo (`busybartools`) is empty, so everything is new.

All characters will be **original pixel art that hints at the theme** (a boy wizard with round glasses, a snowy owl, a pointed sorting hat, floating candles). Nothing is copied from official artwork, logos or fonts.

## What the research found (and how it shapes the design)
- **Display:** the front is 72×16 RGB. Colors are `#RRGGBBAA`. Built-in ASCII fonts: `tiny` (6px), `small` (9px), `normal`/`bold` (11px), `large` (13px), `extra_large` (14px).
- **Drawing:** you send `POST /api/display/draw` with `application_name`, `priority` and `elements[]`. Element types are `text`, `image`, `animation`, `countdown`, `rectangle` and `xpmbitmap`. Each element has an id, and drawing the same id again replaces it.
- **Smooth motion:** animation needs `.anim` files, which the firmware plays itself at about 20 fps without further requests. Moving things by redrawing from a timer tops out at about 3 fps and looks choppy. So every scene is **pre-rendered into a full-screen 72×16 `.anim`**.
- **On-device JS apps** ([docs](https://docs.busy.app/bar/dev/js-apps)) need firmware 1.3.1 or later.
  - The app is scaffolded with `npm create @busy-app/app`. It is written in TypeScript, uses `@busy-app/busy-lib`, and builds to `dist/<id>.tgz`.
  - It supports `setTimeout`/`setInterval`, and `device.TimeGet()` returns the timestamp with its `±HH:MM` timezone offset.
  - It installs over USB (`npm run app:install`) or through the bar's web UI (Apps → Add app).
  - Result: the bar runs the show by itself, with no laptop needed during the party.
- **`.anim` format:** this is the firmware's own binary format: header `"bicycle1"`, sections, and delta-encoded BGRA frames. There are two ways to write it:
  - the community writer `templates/make_anim.py` in `devrsw/busybar-skill`, which is MIT-licensed and has no dependencies;
  - the firmware's `scripts/seq2anim.py`, which takes a zip of numbered PNGs plus `meta.json`.
- **Local toolchain:** Python 3.15 and Pillow 13 are installed. Node is **v26**, but the BUSY CLI needs **Node 24**, so builds will run under Node 24 (`npx -p node@24` or `brew install node@24`) without changing your default Node.

## Approach
A Python **scene renderer** builds pixel-art frames from sprite definitions. It writes three things for each scene: a `.anim` for the bar, a GIF preview, and frame data for the browser mockup. A small **JS app** plays the scenes in a loop and drops in a clock/date screen between them.

### Proposed scenes (each about 15–25 s; to be refined after the mockups)
1. **Owl Post:** a snowy owl flaps across a starry purple sky carrying a letter. It drops the letter and "HAPPY THANKSGIVING" scrolls in gold.
2. **Broom Chase:** a wizard on a broomstick chases a winged golden pumpkin pie. They loop up and down and zip across the screen, and the wizard finally catches it.
3. **Great Hall Feast:** floating candles flicker above a long table with a roast turkey. A wizard walks in and waves a wand, sparkles fly, and the turkey floats up ("LEVIOSA!").
4. **Sorting the Turkey:** a turkey waddles in and an oversized pointed hat drops onto it. The hat wiggles and "thinks", then announces "…GOBBLEDOR!" in house colors.
5. **Pumpkin Patronus:** a silver-blue glowing turkey patronus bursts from a wand tip and gallops across the screen, leaving a trail of mist.
6. **The Gravy Express:** a red steam locomotive puffs across a night landscape, pulling cars loaded with a gravy boat, a pumpkin and a turkey. Puffs of steam drift up and fade, and the wheels turn.
7. **Cauldron Bake-Off:** a bubbling green cauldron sits over a fire. A witch drops in ingredients (an apple, a pumpkin, a sparkle) one at a time, the colors swirl, and with a poof a steaming pumpkin pie rises out.
8. **Dragon Roast:** a small green dragon walks up to a raw turkey on a spit and sneezes a puff of fire. The turkey turns golden brown, and the dragon licks its lips ("DONE!").

**Clock/date screen**, shown after every scene for about 8 s. It's styled as a map with a magical reveal: ink footprints walk across, then the time `HH:MM` (24-hour, `large` font, gold on parchment-brown) sparkles in. Next, the date (for example `THU 26 NOV`) slides in, or the two alternate. The background (candle flicker or footprints) is a looping `.anim`, and the time and date are live `text` elements computed from `TimeGet()` (UTC plus the offset), redrawn on each minute boundary.

### Planned files
```
busybartools/
├── renderer/                   # Python 3, Pillow
│   ├── sprites.py              # pixel-art sprites as ASCII grids + palettes (owl, wizard, broom, turkey, hat, pie, candle, patronus)
│   ├── scenes/                 # one module per scene: frame-by-frame choreography (positions, poses, effects)
│   ├── canvas.py               # 72x16 RGBA compositor, text-in-pixel-font helper, sparkle/particle helpers
│   ├── anim_writer.py          # .anim writer (port/vendor of busybar-skill make_anim.py, MIT, with attribution)
│   └── build.py                # renders all scenes -> app/src/animations/*.anim, previews/*.gif, mockup/frames.js
├── mockup/index.html           # browser LED-matrix simulator (72x16 round "LEDs"), cycles scenes + clock exactly like the device
├── app/                        # scaffolded with `npm create @busy-app/app` (Node 24)
│   └── src/
│       ├── main.ts             # playlist loop, clock scene, Back = quit, OK = skip scene
│       ├── appmeta/manifest.json  (id e.g. "local.wizard.thanksgiving", heap_size_kib 256)
│       ├── appmeta/icon_front_8x8.png
│       └── animations/*.anim   # generated
├── docs/DECISIONS.md           # running decision log (ADR-style: date, decision, why, alternatives)
├── .gitignore                  # node_modules, dist, __pycache__, previews/*.gif (optional), .env
└── README.md                   # how to build, install, run at party time
```

### Device and repo setup
- **BusyBar:** `<bar-ip>` over Wi-Fi, running the latest firmware. The local API is `http://<bar-ip>/api` with an `X-API-Token: <HTTP API password>` header. Wi-Fi API access has to be turned on in the bar's web UI (Network tab → HTTP API access).
  - During planning, ping and HTTP to the bar **timed out** from this Mac. It may be on another network or VLAN, asleep, or have API access off. All the non-device work goes first, and I'll ask for the API password and recheck connectivity when I reach the device step.
  - The password is never committed. It's read from the `BUSYBAR_TOKEN` environment variable or a git-ignored `.env`.
- **Git:** `origin` is the project's GitHub repo and has no commits yet. Work goes on `main`, the first push sets upstream, and I'll commit and push after each milestone below.
- **Decision log:** every meaningful decision is recorded in `docs/DECISIONS.md`. That covers the JS app vs a laptop-driven player, baked `.anim` vs timer redraws, full-screen scenes, the fps choice, the 24-hour time source (`TimeGet` + offset), the original-art policy, the scene list, the playlist order and timing, and anything you change at the mockup checkpoints.

### JS app logic (`app/src/main.ts`)
- The playlist is the 8 scenes with CLOCK after each one (owl, train, broom, cauldron, feast, sorting, dragon, patronus), repeating forever. A full cycle takes about 4 minutes.
- **Scene step:** draw one `animation` element (`id:"scene"`, full screen, `loop:false`, `path:"animations/<scene>.anim"`), then call `setTimeout` for that scene's length, which the build script writes into a generated `scenes.ts`.
- **Clock step:** draw a looping background `.anim` plus `text` elements for time and date. Time comes from `device.TimeGet()` and is formatted by hand as `HH:MM`, without relying on `Date` local-time methods. The clock ticks on the second boundary, not with a drifting `setInterval`.
- Clear `application_name` when switching scenes. Resend the whole frame at the start of each step, in case a notification took over the screen.
- `priority: 50`. Input: `back` (short press) quits cleanly by clearing timers, unbinding input and clearing the display. `ok` skips to the next scene.

## Execution order, with your review checkpoints (commit and push after each step)
0. Repo skeleton: README, `.gitignore`, `docs/DECISIONS.md` with the decisions made so far, and this plan copied to `docs/PLAN.md`. Push the first commit.
1. **Sprite and scene prototyping:** write `sprites.py`, `canvas.py` and the first versions of all 8 scenes plus the clock.
2. **Mockup checkpoint 1 (static storyboards):** render 3–4 key frames per scene and the clock screen, scaled up as LED-dot images. Publish them as an artifact page so you can comment on characters, colors, wording and which scenes to keep or drop.
3. **Mockup checkpoint 2 (animated simulator):** `mockup/index.html` plays the full rotation in your browser with LED-matrix rendering at real timing, including the live 24-hour clock and date. Publish it as an artifact so you can check motion, pacing and timing before anything goes on the device.
4. Write the `.anim` files and check them by decoding them back to PNG frames and comparing with the renderer output.
5. Scaffold and implement the JS app, build under Node 24, and install over USB.
6. Test on the bar, adjust brightness and colors (LEDs look different from a screen), and write the README run steps.

## Verification
- `python3 renderer/build.py` produces every `.anim`, GIF and `mockup/frames.js` without errors. A round-trip decode of each `.anim` matches the source frames pixel-for-pixel.
- The mockup page runs the whole rotation, the clock shows the correct 24-hour local time, and the date matches today.
- On the device:
  - `npm run build && npm run app:install && npm run app:run` succeeds (fallback: the curl `apps/stage` → `apps/install` → `apps/launch` sequence).
  - `GET /api/screen?display=0` screenshots confirm each scene and the clock render.
  - Let it run 30+ minutes to confirm it loops without heap or reboot problems. Short Back press quits; OK skips.
- Check the time against your phone across a minute rollover.

## Risks / unknowns
- The firmware version needs to be 1.3.1 or later for JS apps. I'll check with `GET /api/version` when the bar is connected. If it's older, the fallback is a laptop script that uploads the `.anim` assets and draws them over HTTP.
- The `.anim` writer for multi-section files hasn't been tested on a device, so each scene will be a single section, which is the tested path.
- If `.anim` sizes or the heap become a problem, lower the fps to about 12 and keep delta frames small by leaving transparent pixels at zero.
