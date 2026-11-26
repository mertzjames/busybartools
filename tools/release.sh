#!/usr/bin/env bash
# Cut a formal GitHub Release of one app. Run from an up-to-date `main` (see CONTRIBUTING.md#releasing).
#
#   tools/release.sh <app>
#
# Checks that you're on a clean main that matches origin, that the app builds and passes its tests from the
# committed assets, and that the tag doesn't exist yet. Then it creates and pushes the tag
# <app-folder>-v<version> (version from the app's manifest). The Release workflow
# (.github/workflows/release.yml) builds the package on GitHub and publishes the release with the .tgz attached.
set -euo pipefail
. "$(dirname "$0")/lib.sh"
resolve_app "${1:-}"
folder="$(basename "$APP_DIR")"
tag="$folder-v$APP_VERSION"
cd "$REPO_ROOT"

[ "$(git rev-parse --abbrev-ref HEAD)" = "main" ] || { echo "Releases are cut from main (you're on $(git rev-parse --abbrev-ref HEAD))." >&2; exit 1; }
[ -z "$(git status --porcelain)" ] || { echo "Working tree not clean." >&2; exit 1; }
git fetch -q origin main --tags
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || { echo "Local main differs from origin/main; pull first." >&2; exit 1; }
if git rev-parse -q --verify "refs/tags/$tag" >/dev/null; then
  echo "Tag $tag already exists. Bump \"version\" in apps/$folder/app/src/appmeta/manifest.json (via a PR) first." >&2
  exit 1
fi

tools/check.sh --no-prebuild "$folder"
git tag -a "$tag" -m "$APP_ID $APP_VERSION"
git push origin "$tag"
echo "==> Pushed $tag. The Release workflow will publish it: gh run watch / gh release view $tag"
