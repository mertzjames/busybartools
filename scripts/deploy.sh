#!/usr/bin/env bash
# Build the scenes + app and install/launch it on the BUSY Bar.
#
#   scripts/deploy.sh            render, build, install, launch
#   scripts/deploy.sh --no-render  skip the Python render step (use committed .anim files)
#
# Config (env vars or a git-ignored .env in the repo root):
#   BUSYBAR_ADDR   bar IP/hostname (default 10.0.4.20 = USB; set your bar's Wi-Fi IP to deploy over Wi-Fi)
#   BUSYBAR_TOKEN  the bar's HTTP API password, only if "Password protection" is on (never commit it)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -f "$ROOT/.env" ] && set -a && . "$ROOT/.env" && set +a
ADDR="${BUSYBAR_ADDR:-10.0.4.20}"
TOKEN="${BUSYBAR_TOKEN:-}"
APP_ID="wizard.thanksgiving"
PKG="$ROOT/app/dist/$APP_ID.tgz"

node24() { npx -y -p node@24 -c "$*"; }   # BUSY CLI needs Node 24 (docs/DECISIONS.md D9)
auth=(); [ -n "$TOKEN" ] && auth=(-H "X-API-Token: $TOKEN")

echo "==> Checking the bar at $ADDR"
if ! version=$(curl -sf -m 5 ${auth[@]+"${auth[@]}"} "http://$ADDR/api/version"); then
  echo "Cannot reach http://$ADDR/api/version."
  echo "  - Is the bar on the same network as this computer?"
  echo "  - Is HTTP API access over Wi-Fi turned on (bar web UI -> Network -> HTTP API)?"
  echo "  - Over USB, run with BUSYBAR_ADDR=10.0.4.20"
  exit 1
fi
echo "    $version"

if [ "${1:-}" != "--no-render" ]; then
  echo "==> Rendering scenes"
  python3 "$ROOT/renderer/build.py" --no-gif
fi

echo "==> Building the app (Node 24)"
cd "$ROOT/app"
[ -d node_modules ] || node24 "npm install --no-fund --no-audit"
node24 "npm run typecheck && npm run build"

echo "==> Installing"
# Installing over a running copy fails (HTTP 400) and leaves the app uninstalled, so quit it first.
# 409 just means nothing was running. See docs/DECISIONS.md D23.
curl -s -m 20 ${auth[@]+"${auth[@]}"} -o /dev/null -X POST "http://$ADDR/api/apps/quit" || true
sleep 1
pw=(); [ -n "$TOKEN" ] && pw=(--password "$TOKEN")
if node24 "./node_modules/.bin/busy-cli app install --addr $ADDR ${pw[*]:-}" && \
   node24 "./node_modules/.bin/busy-cli app run --addr $ADDR ${pw[*]:-}"; then
  echo "==> Running. Short-press Back on the bar to quit, OK to skip a scene."
  exit 0
fi

echo "==> busy-cli failed; falling back to the raw HTTP API"
key=$(curl -sf ${auth[@]+"${auth[@]}"} -X POST "http://$ADDR/api/apps/stage" --data-binary @"$PKG" \
      | python3 -c 'import sys,json;print(json.load(sys.stdin)["install_key"])')
curl -sf ${auth[@]+"${auth[@]}"} -X POST "http://$ADDR/api/apps/install?install_key=$key" >/dev/null
curl -sf ${auth[@]+"${auth[@]}"} -X POST "http://$ADDR/api/apps/launch?app_id=$APP_ID" >/dev/null
echo "==> Running. Short-press Back on the bar to quit, OK to skip a scene."
