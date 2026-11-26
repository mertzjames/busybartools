#!/usr/bin/env bash
# Regenerates this app's assets before the JS build (run by tools/deploy.sh, release.sh, check.sh):
# app/src/animations/*.anim, app/shared/generated/show.ts, app icons and mockup/index.html.
set -euo pipefail
cd "$(dirname "$0")"
python3 renderer/build.py --no-gif
