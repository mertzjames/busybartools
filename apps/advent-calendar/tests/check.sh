#!/usr/bin/env bash
# App tests, run by tools/check.sh after the build.
set -euo pipefail
cd "$(dirname "$0")/.."
node_cmd() { if node -v 2>/dev/null | grep -q "^v24\."; then node "$@"; else npx -y -p node@24 node "$@"; fi; }
echo "==> advent-calendar: logic + mockup mirror tests"
node_cmd --experimental-strip-types --no-warnings --test tests/advent.test.mts
echo "==> advent-calendar: live-text parity (app TS vs renderer)"
python3 tests/text_parity.py
