#!/usr/bin/env bash
# Tests for the shared render kit (lib/). Run by tools/check.sh before the apps.
set -euo pipefail
cd "$(dirname "$0")/../.."
node_cmd() { if node -v 2>/dev/null | grep -q "^v24\."; then node "$@"; else npx -y -p node@24 node "$@"; fi; }
echo "==> lib: TypeScript kit tests"
node_cmd --experimental-strip-types --no-warnings --test lib/tests/ts_kit.test.mts lib/tests/holidays_runner.test.mts
echo "==> lib: Python kit smoke test"
python3 lib/tests/py_kit_test.py
