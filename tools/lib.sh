# Shared helpers for tools/*.sh. Source it; don't run it.
# App convention (docs/DEVELOPMENT.md): apps/<name>/app/ is a BUSY JS app project, and an optional
# apps/<name>/prebuild.sh generates assets (e.g. .anim files) before the JS build.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$REPO_ROOT/.env" ] && set -a && . "$REPO_ROOT/.env" && set +a
BAR_ADDR="${BUSYBAR_ADDR:-10.0.4.20}"   # USB address by default; set your bar's Wi-Fi IP in .env
BAR_TOKEN="${BUSYBAR_TOKEN:-}"

node24() {   # the BUSY CLI needs Node 24: use the local node if it is v24, otherwise fetch one with npx
  if node -v 2>/dev/null | grep -q '^v24\.'; then bash -c "$*"; else npx -y -p node@24 -c "$*"; fi
}

# resolve_app <name-or-path>  ->  sets APP_DIR, APP_PROJECT, APP_ID, APP_VERSION
resolve_app() {
  local arg="${1:-}"
  if [ -z "$arg" ]; then
    echo "usage: $0 <app>   (one of: $(ls "$REPO_ROOT/apps" | tr '\n' ' '))" >&2
    exit 2
  fi
  if [ -d "$REPO_ROOT/apps/$arg" ]; then APP_DIR="$REPO_ROOT/apps/$arg"; else APP_DIR="$(cd "$arg" && pwd)"; fi
  APP_PROJECT="$APP_DIR/app"
  local manifest="$APP_PROJECT/src/appmeta/manifest.json"
  [ -f "$manifest" ] || { echo "no $manifest — is $APP_DIR an app folder?" >&2; exit 2; }
  APP_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["id"])' "$manifest")
  APP_VERSION=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["version"])' "$manifest")
}

# build_app [--no-prebuild]  ->  app/dist/<id>.tgz
build_app() {
  if [ "${1:-}" != "--no-prebuild" ] && [ -x "$APP_DIR/prebuild.sh" ]; then
    echo "==> Prebuild ($APP_DIR/prebuild.sh)"
    (cd "$APP_DIR" && ./prebuild.sh)
  fi
  echo "==> Building $APP_ID $APP_VERSION (Node 24)"
  (cd "$APP_PROJECT" && { [ -d node_modules ] || node24 "npm ci --no-fund --no-audit"; } && node24 "npm run typecheck && npm run build")
}

curl_bar() {  # curl_bar <args...>  — adds the API token header when one is configured
  if [ -n "$BAR_TOKEN" ]; then curl -H "X-API-Token: $BAR_TOKEN" "$@"; else curl "$@"; fi
}
