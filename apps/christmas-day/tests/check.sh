#!/usr/bin/env bash
# App tests, run by tools/check.sh after the build.
set -euo pipefail
cd "$(dirname "$0")/.."
python3 tests/clock_parity.py
