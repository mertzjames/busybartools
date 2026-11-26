#!/usr/bin/env bash
# App tests, run by tools/check.sh after the build.
set -euo pipefail
cd "$(dirname "$0")/.."
node_cmd() { if node -v 2>/dev/null | grep -q "^v24\."; then node "$@"; else npx -y -p node@24 node "$@"; fi; }
echo "==> new-years-eve: phase logic and live screens (Node tests)"
node_cmd --experimental-strip-types --no-warnings --test tests/logic.test.mts
echo "==> new-years-eve: live-text parity with the renderer"
python3 tests/live_parity.py
