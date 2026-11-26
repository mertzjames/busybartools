# Wizarding Thanksgiving for the BUSY Bar

A wizard-themed Thanksgiving show for the [BUSY Bar](https://busy.app)'s 72×16 LED front display. Eight short
animated scenes loop all evening: owls, broomsticks, a talking hat, a winged serpent dragon and plenty of turkey.
A gold 24-hour clock and the date appear between scenes.

<p>
  <img src="docs/media/dragon_roast.gif" alt="A winged serpent dragon torches a turkey on a spit" width="49%">
  <img src="docs/media/sorting.gif" alt="A talking hat sorts a turkey: GOBBLEDOR!" width="49%">
</p>

| # | Scene | Length |
|---|---|---|
| 1 | **Owl Post:** a snowy owl delivers HAPPY / THANKSGIVING | 18 s |
| 2 | **The Gravy Express:** a steam train hauls the feast | 14 s |
| 3 | **Broom Chase:** a young wizard chases a winged golden pie | 16 s |
| 4 | **Cauldron Bake-Off:** a young witch brews a pumpkin pie | 16 s |
| 5 | **Great Hall Feast:** floating candles, and the turkey levitates | 18 s |
| 6 | **Sorting the Turkey:** the talking hat decides… GOBBLEDOR! | 17 s |
| 7 | **Dragon Roast:** a winged serpent torches the turkey. WELL DONE! | 16 s |
| 8 | **Pumpkin Patronus:** EXPECTO PIE! | 15 s |

After each scene, a clock card shows the time (`HH:MM`, 24-hour) for 4.5 s, then the date (`THU 26 NOV`) for 3.5 s.
The time comes from the bar's own clock. One full loop takes about 3 minutes 14 seconds.

To preview everything in a browser before installing, download and open [`mockup/index.html`](mockup/index.html).

---

## Contents

- [What you need](#what-you-need)
- [Option A: Install the ready-made app (no tools needed)](#option-a-install-the-ready-made-app-no-tools-needed)
- [Enable the HTTP API over Wi-Fi](#enable-the-http-api-over-wi-fi)
- [Option B: Build and install from source](#option-b-build-and-install-from-source)
- [Using it](#using-it)
- [Uninstalling](#uninstalling)
- [Customizing](#customizing)
- [Troubleshooting](#troubleshooting)
- [How it works](#how-it-works)
- [License and credits](#license-and-credits)

## What you need

- A **BUSY Bar** with current firmware (version 1.3.1 or later, which runs JS apps). The app needs HTTP API
  **27.12.0 or newer**. It was tested on 27.16.0.
- A computer with a browser, and either the bar's **USB cable** or the bar on the **same network** as the computer.
- For Option B only: **Python 3** with Pillow, and **npm** (the build script fetches Node 24 automatically).

To check your firmware's API version, open `http://10.0.4.20/api/version` over USB, or `http://<bar-ip>/api/version`
over Wi-Fi.

## Option A: Install the ready-made app (no tools needed)

The repo includes a prebuilt package: [`release/wizard.thanksgiving.tgz`](release/wizard.thanksgiving.tgz).

1. **Download** `release/wizard.thanksgiving.tgz`. Keep it as a `.tgz` and don't unpack it.
2. **Open the bar's web page:**
   - **USB:** connect the bar to your computer and open **http://10.0.4.20**. USB needs no password.
   - **Wi-Fi:** open `http://<bar-ip>`. You can find the IP on the bar's **Network** tab (over USB) or in your
     router's list of devices.
3. Go to the **Apps** tab, click **+ Add app** and select `wizard.thanksgiving.tgz`.
4. Click **Install app**.
5. On the bar, open the **Apps** menu and choose **Wizard Thanksgiving**. The show starts right away and loops until
   you quit.

## Enable the HTTP API over Wi-Fi

Skip this if you install by USB or with Option A. You need it for `scripts/deploy.sh` over Wi-Fi, the `busy-cli`
tools and `scripts/screens.py`. By default, the BUSY Bar refuses API requests over Wi-Fi.

1. Connect the bar by **USB** and open **http://10.0.4.20**.
2. Go to the **Network** tab and find the **HTTP API** section, under **Over Wi-Fi**.
3. Turn on **HTTP API access**.
4. *(Optional, recommended on shared networks)* Turn on **Password protection** and set a password. Requests must
   then send it as an `X-API-Token` header, and this repo's scripts read it from `BUSYBAR_TOKEN`.
5. Note the bar's **IP address**, from the same page or from your router.
6. Test it from your computer:
   ```bash
   curl http://<bar-ip>/api/version   # -> {"api_semver":"27.16.0"}  (this endpoint never needs a password)
   curl http://<bar-ip>/api/time      # -> {"timestamp":"..."}  means you're in
   # with a password:
   curl -H "X-API-Token: <password>" http://<bar-ip>/api/time
   ```
   - `403 Forbidden` on `/api/time`: Wi-Fi access is still off, or a password is required.
   - A timeout on everything: your computer can't reach the bar. See [Troubleshooting](#troubleshooting).

> **Security note:** With access on and no password, anyone on your network can control the bar while it's
> powered. Use a password if other people share your network, or turn access off again after installing. The app
> keeps running without it.

## Option B: Build and install from source

```bash
git clone <this repo>
cd busybartools
python3 -m pip install -r renderer/requirements.txt   # Pillow

cp .env.example .env    # then edit: set BUSYBAR_ADDR to your bar's IP (and BUSYBAR_TOKEN if you set a password)
scripts/deploy.sh
```

Leave `BUSYBAR_ADDR` unset to deploy over USB (`10.0.4.20`). `.env` is git-ignored, so your address and password stay
local.

`scripts/deploy.sh`:
1. Checks the bar answers on `/api/version`.
2. Renders the scenes (`python3 renderer/build.py`, about 2 s). Pass `--no-render` to use the committed animations.
3. Builds the app under Node 24 (`npx -p node@24`, so your system Node is untouched) into
   `app/dist/wizard.thanksgiving.tgz`.
4. Quits any running app, then installs and launches. Installing over a running copy fails and removes the app.
   If `busy-cli` fails, it falls back to the raw API: `apps/stage` → `apps/install` → `apps/launch`.

To build the package without a bar connected:
```bash
python3 renderer/build.py
cd app && npx -y -p node@24 -c 'npm ci && npm run build'    # -> app/dist/wizard.thanksgiving.tgz
```

## Using it

| On the bar | Does |
|---|---|
| **OK** (short press) | Skip to the next scene or clock card |
| **Encoder** (turn) | Step forward or back through the show |
| **Back** (short press) | Quit and give the screen back to the bar |

- **The time is wrong or in the wrong timezone:** set the timezone and time in the bar's own settings. The app
  displays the bar's local time.
- **The colors look too dim or too bright:** the bar's brightness is left on auto. Change it on the bar, or see
  `GAMMA` under [Customizing](#customizing).
- **To run it without touching the bar:** `curl -X POST http://<bar-ip>/api/apps/launch?app_id=wizard.thanksgiving`
  (needs the Wi-Fi API enabled).

## Uninstalling

- **Web page:** open `http://10.0.4.20` (USB) or `http://<bar-ip>` and remove **Wizard Thanksgiving** on the
  **Apps** tab.
- **Command line:** `cd app && npx -y -p node@24 -c 'npx busy-cli app uninstall --addr <bar-ip>'`.

## Customizing

Everything visual is generated from Python, so edits are small.

| Change | Where |
|---|---|
| Characters, colors, scarves | `renderer/sprites.py`: sprites are text grids, one letter per pixel, with a palette |
| A scene's choreography, captions, length | `renderer/scenes/<scene>.py` (`SECONDS`, `KEYFRAMES`, `render()`) |
| Scene order | `PLAYLIST` in `renderer/scenes/__init__.py` |
| Clock and date colors and timing | `LAYOUT` in `renderer/scenes/clock_bg.py` |
| Overall brightness | `GAMMA` in `renderer/build.py` (1.0 = original, lower = brighter darks) |
| Pixel fonts | `renderer/font.py` |

Then run `python3 renderer/build.py`, check `mockup/index.html` in a browser, and run `scripts/deploy.sh`. To see
what the bar is showing, run `python3 scripts/screens.py --count 10 --every 2`, which writes LED-style PNGs to
`screens/`.

To refresh the prebuilt package after changes, copy `app/dist/wizard.thanksgiving.tgz` to `release/`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Everything times out (ping, web page, API) over Wi-Fi | Your computer can't reach the bar. If it's on a separate guest or smart-device network (VLAN), allow your computer to reach the bar's IP on TCP port 80, connect to the same network, or use USB. |
| `/api/version` works but other calls return `403 Forbidden` | Wi-Fi HTTP API access is off, or a password is needed. See [Enable the HTTP API over Wi-Fi](#enable-the-http-api-over-wi-fi). |
| Install returns `400` and the app then disappears from the Apps list | It was running during the install. Short-press **Back** on the bar (or `POST /api/apps/quit`) and install again. `scripts/deploy.sh` does this for you. |
| `Unsupported engine` or Node errors during the build | The BUSY CLI needs Node 24. Run builds through `npx -y -p node@24 -c '…'`, as the script does. |
| A `.gif`, `.jpg` or `.wav` you added doesn't show up | The bar only reads `.png`, `.anim` and `.snd`. Generate animations with `renderer/`. |

## How it works

1. **Sprites as text.** Each character is a small grid of letters in Python (`renderer/sprites.py`).
2. **A renderer** choreographs every frame of each scene at 15 fps: paths, particles, fire, text. Output is
   deterministic.
3. **`.anim` files.** Frames are packed into the bar's native animation format (`renderer/anim_writer.py`), which the
   firmware plays without any network traffic. Every file is decoded again and checked pixel-for-pixel.
4. **The app** (`app/src/main.ts`, TypeScript) loops the scenes and draws the clock from the bar's `/api/time` in a
   custom gold pixel font. The clock is sent as small bitmaps, and only a few requests go out per card.
5. **The mockup** (`mockup/index.html`) plays the same frames and fonts in a browser.

The reasoning behind each choice, including what didn't work, is in [`docs/DECISIONS.md`](docs/DECISIONS.md). The
original plan is in [`docs/PLAN.md`](docs/PLAN.md).

## License and credits

- Code and art: [MIT](LICENSE).
- The `.anim` writer is adapted from [devrsw/busybar-skill](https://github.com/devrsw/busybar-skill) (MIT).
- This is an unofficial fan project, not affiliated with the Wizarding World franchise or with BUSY / Flipper
  Devices. All art is original. See [NOTICE.md](NOTICE.md).
