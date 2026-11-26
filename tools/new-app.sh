#!/usr/bin/env bash
# Scaffold a new app in the collection layout (see docs/DEVELOPMENT.md#adding-a-new-app).
#
#   tools/new-app.sh <folder> --id <app.id> --name "<Display Name>" --description "<one line>" [--author "<name>"]
#   tools/new-app.sh fireplace --id busybartools.fireplace --name "Fireplace" --description "Crackling fire loop"
#
# Creates apps/<folder>/ with:
#   app/              official BUSY JS app scaffold (@busy-app/create-app), dependencies installed
#   README.md         app page stub
#   docs/DECISIONS.md decision log stub
set -euo pipefail
. "$(dirname "$0")/lib.sh"

folder="${1:-}"; shift || true
id=""; name=""; desc=""; author="busybartools contributors"
while [ $# -gt 0 ]; do
  case "$1" in
    --id) id="$2"; shift 2 ;;
    --name) name="$2"; shift 2 ;;
    --description) desc="$2"; shift 2 ;;
    --author) author="$2"; shift 2 ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
done
if [ -z "$folder" ] || [ -z "$id" ] || [ -z "$name" ] || [ -z "$desc" ]; then
  sed -n 2,10p "$0"; exit 2
fi
[[ "$folder" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "folder: lowercase letters, digits and dashes" >&2; exit 2; }
[[ "$id" =~ ^[A-Za-z0-9_.-]{1,32}$ ]] || { echo "id: up to 32 chars of A-Z a-z 0-9 _ . -" >&2; exit 2; }
dest="$REPO_ROOT/apps/$folder"
[ -e "$dest" ] && { echo "$dest already exists" >&2; exit 1; }
mkdir -p "$dest/docs"

echo "==> Scaffolding $id into apps/$folder/app (Node 24)"
(cd "$dest" && npx -y -p node@24 -p @busy-app/create-app@0.5.0 -c "busy-create-app app --id '$id' --name '$name' \
   --description '$desc' --author '$author' --api-version 27.12.0 --no-git --no-install" </dev/null)
rm -f "$dest/app/.gitignore" "$dest/app/AGENTS.md"   # the repo-level .gitignore and docs/DEVELOPMENT.md cover these
rm -rf "$dest/app/.github"                           # CI/release workflows live at the repo level, not per app
(cd "$dest/app" && node24 "npm install --no-fund --no-audit")

cat > "$dest/README.md" <<EOF
# $name

$desc

## Install

Upload \`releases/$id-<version>.tgz\` to your bar. See [Installing apps](../../docs/INSTALLING.md).

## Develop

\`\`\`bash
tools/check.sh $folder     # build + typecheck (+ tests/check.sh if present)
tools/deploy.sh $folder    # install and launch on the bar in .env
tools/release.sh $folder   # publish releases/$id-<version>.tgz
\`\`\`

Design notes and decisions: [docs/DECISIONS.md](docs/DECISIONS.md).
EOF
cat > "$dest/docs/DECISIONS.md" <<EOF
# Decision log — $name

What was decided, why, and what else was considered. Newest at the bottom.

---

## D1 — <first decision>
*$(date +%Y-%m-%d)*

**Decision:**

**Why:**
EOF
echo "==> Created apps/$folder. Next: edit app/src/main.ts, then tools/deploy.sh $folder"
echo "    Add a row for it to the catalog in README.md and releases/README.md when you release it."
