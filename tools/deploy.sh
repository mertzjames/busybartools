#!/usr/bin/env bash
# Build an app and install + launch it on a BUSY Bar.
#
#   tools/deploy.sh <app> [--no-prebuild]
#   tools/deploy.sh wizard-thanksgiving
#
# Config (env vars or the git-ignored .env at the repo root; see .env.example):
#   BUSYBAR_ADDR   bar IP/hostname (default 10.0.4.20 = USB)
#   BUSYBAR_TOKEN  the bar's HTTP API password, only if "Password protection" is on (never commit it)
set -euo pipefail
. "$(dirname "$0")/lib.sh"
resolve_app "${1:-}"
PKG="$APP_PROJECT/dist/$APP_ID.tgz"

echo "==> Checking the bar at $BAR_ADDR"
if ! version=$(curl_bar -sf -m 5 "http://$BAR_ADDR/api/version"); then
  echo "Cannot reach http://$BAR_ADDR/api/version. See docs/INSTALLING.md#troubleshooting"
  exit 1
fi
echo "    $version"
if ! curl_bar -sf -m 5 -o /dev/null "http://$BAR_ADDR/api/time"; then
  echo "The bar refused the API request (403?). Turn on HTTP API access over Wi-Fi, or set BUSYBAR_TOKEN."
  echo "See docs/INSTALLING.md#enable-the-http-api-over-wi-fi"
  exit 1
fi

build_app "${2:-}"

echo "==> Installing $APP_ID"
# Installing over a running app fails (HTTP 400) and leaves it uninstalled, so quit first (409 = nothing running).
curl_bar -s -m 20 -o /dev/null -X POST "http://$BAR_ADDR/api/apps/quit" || true
sleep 1
pw=""; [ -n "$BAR_TOKEN" ] && pw="--password $BAR_TOKEN"
if (cd "$APP_PROJECT" && node24 "./node_modules/.bin/busy-cli app install --addr $BAR_ADDR $pw" \
                     && node24 "./node_modules/.bin/busy-cli app run --addr $BAR_ADDR $pw"); then
  echo "==> Running $APP_ID on $BAR_ADDR"
  exit 0
fi

echo "==> busy-cli failed; falling back to the raw HTTP API"
key=$(curl_bar -sf -X POST "http://$BAR_ADDR/api/apps/stage" --data-binary @"$PKG" \
      | python3 -c 'import sys,json;print(json.load(sys.stdin)["install_key"])')
curl_bar -sf -X POST "http://$BAR_ADDR/api/apps/install?install_key=$key" >/dev/null
curl_bar -sf -X POST "http://$BAR_ADDR/api/apps/launch?app_id=$APP_ID" >/dev/null
echo "==> Running $APP_ID on $BAR_ADDR"
