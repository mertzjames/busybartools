#!/usr/bin/env bash
# Build and check every app in apps/ (no device needed). Run before committing.
#
#   tools/check.sh                      all apps
#   tools/check.sh <app>...             just these
#   tools/check.sh --no-prebuild ...    skip asset generation; build from the committed assets
#
# First the shared render kit's tests (lib/tests/check.sh), then that each app's vendored kit copy matches lib/ts
# and its app/ folder imports nothing outside itself (tools/vendor-kit.sh --check), then for each app: prebuild.sh (if any),
# typecheck + build of app/, then the app's own tests/check.sh (if any).
set -euo pipefail
. "$(dirname "$0")/lib.sh"
prebuild=""; [ "${1:-}" = "--no-prebuild" ] && { prebuild="--no-prebuild"; shift; }
apps=("$@"); [ ${#apps[@]} -eq 0 ] && apps=($(ls "$REPO_ROOT/apps"))
echo "################ shared render kit (lib/)"
"$REPO_ROOT/lib/tests/check.sh"
echo "################ vendored kit copies and self-contained app/ folders"
"$REPO_ROOT/tools/vendor-kit.sh" --check ${apps[@]+"${apps[@]}"}
for a in "${apps[@]}"; do
  resolve_app "$a"
  echo "################ $APP_ID ($a)"
  build_app $prebuild
  if [ -x "$APP_DIR/tests/check.sh" ]; then
    echo "==> Tests ($APP_DIR/tests/check.sh)"
    (cd "$APP_DIR" && ./tests/check.sh)
  fi
done
echo "==> All checks passed"
