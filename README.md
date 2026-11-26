# busybartools

Custom apps, animations and developer tools for the [BUSY Bar](https://busy.app), the desk and wall display with a
72×16 RGB LED front panel.

<p>
  <img src="apps/wizard-thanksgiving/docs/media/dragon_roast.gif" alt="A winged serpent dragon torches a turkey" width="49%">
  <img src="apps/wizard-thanksgiving/docs/media/owl_post.gif" alt="A snowy owl delivers a Happy Thanksgiving letter" width="49%">
</p>

## Apps

| App | What it does | Get it |
|---|---|---|
| [Wizarding Thanksgiving](apps/wizard-thanksgiving/) | Eight wizard-themed Thanksgiving scenes (owls, broomsticks, a talking hat, a winged serpent dragon) with a 24-hour clock and the date between them | [Latest release](https://github.com/mertzjames/busybartools/releases?q=wizard-thanksgiving) |

More apps and tools will be added over time. Want to build one? See [Adding a new app](docs/DEVELOPMENT.md#adding-a-new-app).

## Install an app

Each app ships as a single `.tgz` file on the [Releases page](https://github.com/mertzjames/busybartools/releases):

1. Download the app's `.tgz` from its release. Don't unpack it.
2. Open your bar's web page: **http://10.0.4.20** over USB, or `http://<bar-ip>` on Wi-Fi.
3. Go to **Apps → + Add app**, choose the file, and click **Install app**.
4. On the bar, open the **Apps** menu and start it.

The full guide, including how to enable the HTTP API over Wi-Fi and fix common problems, is in
[docs/INSTALLING.md](docs/INSTALLING.md).

## Repository layout

```
apps/<app>/          one folder per app: the BUSY JS app (app/), its generators, docs and tests
lib/python/busybar/  shared Python: .anim writer/reader, LED-style previews
tools/               shared scripts: check, deploy, release, new-app, screen capture
docs/                installing, development guide, repo-level decisions
.github/             CI, release automation, PR template
```

## For developers

```bash
python3 -m pip install -r requirements.txt   # Pillow (pinned)
tools/check.sh                               # build, typecheck and test every app (no device needed)
cp .env.example .env                         # set BUSYBAR_ADDR to your bar's IP (or leave unset for USB)
tools/deploy.sh wizard-thanksgiving          # install and launch on your bar
```

- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md): toolchain, app anatomy, adding an app, making `.anim` animations,
  BUSY Bar platform notes and testing on the device.
- [CONTRIBUTING.md](CONTRIBUTING.md): branch model (`main` for releases, `dev` for integration,
  `<you>/<topic>` for work), pull requests and how releases are cut.

## License

[MIT](LICENSE). This is an unofficial community project, not affiliated with BUSY / Flipper Devices. Themed apps are
fan projects with original art. See [NOTICE.md](NOTICE.md).
