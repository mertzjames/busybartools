#!/usr/bin/env bash
# App tests, run by tools/check.sh after the build.
set -euo pipefail
cd "$(dirname "$0")/.."
node_cmd() { if node -v 2>/dev/null | grep -q "^v24\."; then node "$@"; else npx -y -p node@24 node "$@"; fi; }
echo "==> mlk-day: dates, card texts and playlist (Node tests)"
node_cmd --experimental-strip-types --no-warnings --test tests/logic.test.mts
echo "==> mlk-day: live-text parity (app TS vs renderer)"
python3 tests/text_parity.py
