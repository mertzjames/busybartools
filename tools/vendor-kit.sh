#!/usr/bin/env bash
# Copy the shared TypeScript kit (lib/ts/busybar) into each app as app/shared/vendor/busybar/.
#
#   tools/vendor-kit.sh                 refresh the copy in every app
#   tools/vendor-kit.sh <app>...        just these
#   tools/vendor-kit.sh --check ...     change nothing; fail if a copy differs from lib/ts, or if app code
#                                       imports from outside its app/ folder (tools/check.sh runs this)
#
# Why: the BUSY Apps Catalog builds an app from its app/ folder alone, offline, so app code can't import
# ../../../../lib/ts. lib/ts stays the one place to edit; this keeps the copies identical (docs/DECISIONS.md R12).
set -euo pipefail
. "$(dirname "$0")/lib.sh"
check=""; [ "${1:-}" = "--check" ] && { check=1; shift; }
apps=("$@"); [ ${#apps[@]} -eq 0 ] && apps=($(ls "$REPO_ROOT/apps"))
src="$REPO_ROOT/lib/ts/busybar"
failed=0
for a in "${apps[@]}"; do
  resolve_app "$a"
  dest="$APP_PROJECT/shared/vendor/busybar"
  if [ -n "$check" ]; then
    if ! diff -r "$src" "$dest" >/dev/null 2>&1; then
      echo "vendor-kit: $a: app/shared/vendor/busybar differs from lib/ts/busybar. Run tools/vendor-kit.sh $a" >&2
      failed=1
    fi
    # App code must stay inside app/: anything that climbs out of it won't exist in the catalog's build.
    if ! python3 - "$APP_PROJECT" <<'VENDOR_PY'
import re, sys
from pathlib import Path
app = Path(sys.argv[1]).resolve()
spec = re.compile(r"""(?:\bfrom|\bimport)\s*\(?\s*["'](\.{1,2}/[^"']*)["']""")
bad = []
for top in ("src", "shared"):
    for f in sorted((app / top).rglob("*.ts")) if (app / top).is_dir() else []:
        for n, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            for m in spec.finditer(line):
                if not (f.parent / m.group(1)).resolve().is_relative_to(app):
                    bad.append(f"{f.relative_to(app.parent)}:{n}: {m.group(1)}")
if bad:
    sys.exit("\n".join(bad))
VENDOR_PY
    then
      echo "vendor-kit: $a: the imports above leave app/. Import the kit from @shared/vendor/busybar/ instead" >&2
      failed=1
    fi
  else
    rm -rf "$dest"
    mkdir -p "$dest"
    cp "$src"/*.ts "$dest"/
    echo "vendor-kit: $a: copied lib/ts/busybar -> app/shared/vendor/busybar"
  fi
done
exit $failed
