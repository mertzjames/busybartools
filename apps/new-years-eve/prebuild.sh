#!/usr/bin/env bash
# Regenerates this app's assets before the JS build (run by tools/deploy.sh, release.sh, check.sh):
# app/src/animations/*.anim, app/shared/generated/show.ts, app icons and mockup/index.html.
# The mockup step type-strips the app's TS logic with Node 24 (local node if it's v24, else npx node@24).
set -euo pipefail
cd "$(dirname "$0")"
python3 renderer/build.py --no-gif
