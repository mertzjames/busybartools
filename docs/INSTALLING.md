# Installing apps on your BUSY Bar

This guide works for every app in this repo. Each app's own README covers what it does and its controls.

- [What you need](#what-you-need)
- [Install from a release (recommended)](#install-from-a-release-recommended)
- [Enable the HTTP API over Wi-Fi](#enable-the-http-api-over-wi-fi)
- [Install from source](#install-from-source)
- [Starting, stopping and removing apps](#starting-stopping-and-removing-apps)
- [Troubleshooting](#troubleshooting)

## What you need

- A **BUSY Bar** with current firmware. JS apps need firmware **1.3.1 or later**. Each release lists the minimum HTTP
  API version it needs. Apps here were tested on API 27.16.0.
- A computer with a browser, and either the bar's **USB cable** or the bar on the **same network** as the computer.

To check your bar's API version, open `http://10.0.4.20/api/version` over USB, or `http://<bar-ip>/api/version`
over Wi-Fi. You'll get back something like `{"api_semver":"27.16.0"}`.

## Install from a release (recommended)

1. Open the [Releases page](https://github.com/mertzjames/busybartools/releases) and pick the app. Download the
   `.tgz` file listed under **Assets**, for example `wizard.thanksgiving-1.0.0.tgz`. Don't unpack it.
2. Open your bar's web page:
   - **USB:** connect the bar to your computer and open **http://10.0.4.20**. USB needs no password.
   - **Wi-Fi:** open `http://<bar-ip>`. You'll find the IP on the bar's **Network** tab (over USB) or in your
     router's device list.
3. Go to the **Apps** tab, click **+ Add app** and select the `.tgz`.
4. Click **Install app**.
5. On the bar, open the **Apps** menu and choose the app.

To update an app, quit it on the bar first (short-press **Back**), then install the newer `.tgz` the same way.
Installing over a running app fails and can leave it uninstalled; if that happens, just install it again.

## Enable the HTTP API over Wi-Fi

You don't need this to install from a release. You need it to use `tools/deploy.sh`, `busy-cli` or
`tools/screens.py` over Wi-Fi, or to control the bar with `curl`. By default the bar refuses API requests over
Wi-Fi.

1. Connect the bar by **USB** and open **http://10.0.4.20**.
2. Go to the **Network** tab and find the **HTTP API** section, under **Over Wi-Fi**.
3. Turn on **HTTP API access**.
4. *(Optional, recommended on shared networks)* Turn on **Password protection** and set a password. Requests then
   need an `X-API-Token: <password>` header, and this repo's tools read it from `BUSYBAR_TOKEN`.
5. Note the bar's **IP address**, from the same page or from your router.
6. Test it from your computer:
   ```bash
   curl http://<bar-ip>/api/version   # {"api_semver":"..."}: the bar is reachable
   curl http://<bar-ip>/api/time      # {"timestamp":"..."}: API access works
   curl -H "X-API-Token: <password>" http://<bar-ip>/api/time    # if you set a password
   ```

> **Security:** With access on and no password, anyone on your network can control the bar while it's powered.
> Set a password if you share the network, or turn access off again after installing. Installed apps keep running
> either way.

## Install from source

Use this to try unreleased changes or your own edits. You need Python 3 (3.10+) and npm. The tools fetch Node 24
automatically if your Node is a different version.

```bash
git clone https://github.com/mertzjames/busybartools.git
cd busybartools
python3 -m pip install -r requirements.txt
cp .env.example .env          # set BUSYBAR_ADDR to your bar's IP; leave unset for USB (10.0.4.20)
tools/deploy.sh wizard-thanksgiving
```

`tools/deploy.sh <app>` checks that the bar answers, regenerates the app's assets, builds it, quits whatever app is
running, then installs and launches it. `.env` is git-ignored, so your address and password stay on your machine.

## Starting, stopping and removing apps

| To | Do |
|---|---|
| Start an app | On the bar: **Apps** menu → the app. Or over the API: `curl -X POST "http://<bar-ip>/api/apps/launch?app_id=<app-id>"` |
| Quit the running app | Short-press **Back** on the bar, or `curl -X POST http://<bar-ip>/api/apps/quit` |
| Remove an app | Bar web page → **Apps** tab → remove it. Or `curl -X DELETE "http://<bar-ip>/api/apps?app_id=<app-id>"` |
| See installed apps | `curl http://<bar-ip>/api/apps/list` |

App ids are listed in each release's notes and in each app's `app/src/appmeta/manifest.json`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| Everything times out over Wi-Fi (ping, web page, API) | Your computer can't reach the bar. If the bar is on a separate guest or smart-device network (VLAN), allow your computer to reach the bar's IP on TCP port 80, join the same network, or use USB. |
| `/api/version` works but other calls return `403 Forbidden` | Wi-Fi HTTP API access is off, or a password is required. See [Enable the HTTP API over Wi-Fi](#enable-the-http-api-over-wi-fi). |
| Install fails with `400`, and the app then vanishes from the Apps list | It was running during the install. Quit it (short-press **Back**) and install again. `tools/deploy.sh` does this for you. |
| The app shows the wrong time | Apps use the bar's clock. Set the bar's time zone and time in its settings. |
| `Unsupported engine` or other Node errors when building | The BUSY CLI needs Node 24. Use the `tools/` scripts, which run it with Node 24 for you. |
