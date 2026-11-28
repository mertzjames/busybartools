#!/usr/bin/env python3
"""Check an app against the BUSY Apps Catalog's rules and write its catalog manifest.

    python3 tools/catalog.py hanukkah                       # check the app as of origin/main, print manifest.yml
    python3 tools/catalog.py hanukkah --build               # ...and build app/ alone, the way the catalog does
    python3 tools/catalog.py hanukkah --sha <40-char sha> --out ../busy-apps-catalog/applications/<id>/manifest.yml
    python3 tools/catalog.py hanukkah --worktree            # dry run on uncommitted files (no manifest printed)

The catalog (github.com/busy-app/busy-apps-catalog) builds an app from a pinned commit of this public repo, using
only the folder `subdir` points at (apps/<app>/app), offline. So everything it needs lives in app/:

  app/CATALOG.md            catalog description (restricted Markdown, 50-4000 chars), referenced as "@CATALOG.md"
  app/CHANGELOG.md          "## <version>" sections; the current version's section becomes the changelog
  app/screenshots/*.png     1-10 front screenshots, 72x16, captured on a bar (tools/screens.py --raw); first = cover
  app/src/appmeta/          manifest.json (id, name, version, description = short description) and icons

The commit must be on origin/main: catalog commits have to stay reachable for as long as a version is published, and
only main is never rewritten. See docs/CATALOG.md and docs/DECISIONS.md R12.
"""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
CATEGORIES = ("productivity", "clocks", "info-feeds", "social", "dev-monitoring", "music", "art", "games",
              "smart-home", "utilities")
APP_ID = re.compile(r"^(?=.{3,32}$)[a-z0-9_-]+(?:\.[a-z0-9_-]+){2,}$")
NAME = re.compile(r"^(?=.{1,32}$)[A-Za-z0-9!?&'()+,\-./:#$%@_]+(?: [A-Za-z0-9!?&'()+,\-./:#$%@_]+)*$")
VERSION = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_MAIN_JS = 256_000


class Source:
    """Read app files either at a commit (what the catalog sees) or from the working tree (dry run)."""

    def __init__(self, app: str, sha: str | None) -> None:
        self.sha = sha
        self.app = f"apps/{app}/app"

    def read(self, rel: str, root: bool = False) -> bytes | None:
        path = rel if root else f"{self.app}/{rel}"
        if self.sha is None:
            p = ROOT / path
            return p.read_bytes() if p.is_file() else None
        r = subprocess.run(["git", "-C", str(ROOT), "show", f"{self.sha}:{path}"], capture_output=True)
        return r.stdout if r.returncode == 0 else None

    def list(self, rel: str) -> list[str]:
        """File names directly inside app/<rel>."""
        if self.sha is None:
            d = ROOT / self.app / rel
            return sorted(p.name for p in d.iterdir() if p.is_file()) if d.is_dir() else []
        r = subprocess.run(["git", "-C", str(ROOT), "ls-tree", "--name-only", f"{self.sha}:{self.app}/{rel}"],
                           capture_output=True, text=True)
        return sorted(r.stdout.split()) if r.returncode == 0 else []


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True, text=True).stdout.strip()


def markdown_problems(text: str) -> list[str]:
    """The catalog allows only h1/h2 headings, paragraphs, bold, italic, lists and http(s) links."""
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        checks = [
            ("`" in line, "backticks (code) aren't allowed"),
            ("![" in line, "images aren't allowed"),
            (re.search(r"<[A-Za-z/!]", line) is not None, "HTML isn't allowed"),
            (re.search(r"&[#A-Za-z0-9]+;", line) is not None, "HTML entities aren't allowed"),
            (re.match(r"\s*#{3,}\s", line) is not None, "only # and ## headings are allowed"),
            (re.match(r"( {4}|\t)", line) is not None and not re.match(r"\s+([-*+]|\d+\.)\s", line),
             "indented lines become code blocks"),
            (line.lstrip().startswith(">"), "quotes aren't allowed"),
            (re.fullmatch(r"\s*(?:[-*_]\s*){3,}", line) is not None, "horizontal lines aren't allowed"),
            (re.fullmatch(r"\s*(?:=+|-+)\s*", line) is not None and n > 1, "underlined (setext) headings aren't allowed"),
            (re.match(r"\s*\[[^\]]+\]:\s", line) is not None, "reference links aren't allowed"),
        ]
        problems += [f"line {n}: {why}" for bad, why in checks if bad]
        for url in re.findall(r"\]\(([^)\s]+)", line):
            if not re.match(r"https?://[^/\s]+", url):
                problems.append(f"line {n}: link {url} must be an absolute http(s) URL")
    return problems


def changelog_section(text: str, version: str) -> str | None:
    """The body under '## <version>' in CHANGELOG.md, up to the next '## ' heading."""
    m = re.search(rf"^## {re.escape(version)}[ \t]*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    return m.group(1).strip() + "\n" if m else None


def check_png(data: bytes, size: tuple[int, int], limit: int, what: str, errors: list[str]) -> None:
    if len(data) > limit:
        errors.append(f"{what}: {len(data)} bytes, over {limit}")
    try:
        img = Image.open(io.BytesIO(data))
        img.load()
    except Exception as e:  # noqa: BLE001 - any decode failure is a finding
        errors.append(f"{what}: not a readable PNG ({e})")
        return
    if img.format != "PNG":
        errors.append(f"{what}: {img.format}, not PNG")
    if img.size != size:
        errors.append(f"{what}: {img.size[0]}x{img.size[1]}, expected {size[0]}x{size[1]}")
    if img.mode not in ("1", "L", "LA", "P", "RGB", "RGBA"):
        errors.append(f"{what}: mode {img.mode}; save it as an 8-bit PNG")


def check(src: Source, app: str, category: str) -> tuple[dict, list[str], list[str], list[str]]:
    """Return (facts, screenshot paths, errors, warnings) for the app in `src`."""
    errors: list[str] = []
    warnings: list[str] = []
    facts: dict = {}

    raw = src.read("src/appmeta/manifest.json")
    if raw is None:
        return facts, [], ["app/src/appmeta/manifest.json is missing"], warnings
    if len(raw) > 512:
        errors.append(f"appmeta/manifest.json is {len(raw)} bytes; the catalog allows 512")
    meta = json.loads(raw)
    facts.update(meta)
    for key in ("format_version", "id", "name", "version", "api_version"):
        if key not in meta:
            errors.append(f"appmeta/manifest.json has no {key}")
    if not APP_ID.match(meta.get("id", "")):
        errors.append(f"id {meta.get('id')!r}: lowercase a-z 0-9 _ -, at least two dots, up to 32 characters (busy-cli's limit)")
    if meta.get("id", "").startswith("app.busy."):
        errors.append("app.busy.* ids are reserved for official apps")
    if not NAME.match(meta.get("name", "")):
        errors.append(f"name {meta.get('name')!r}: 1-32 ASCII letters, digits, single spaces and !?&'()+,-./:#$%@_")
    for key in ("version", "api_version"):
        if not VERSION.match(meta.get(key, "")):
            errors.append(f"{key} {meta.get(key)!r}: MAJOR.MINOR.PATCH, no leading zeros or suffixes")
    if meta.get("debug"):
        errors.append("debug must be false or unset")
    if "heap_size_kib" in meta and not 1 <= int(meta["heap_size_kib"]) <= 512:
        errors.append("heap_size_kib must be 1-512")
    short = meta.get("description", "")
    if not 10 <= len(short) <= 120 or "\n" in short:
        errors.append(f"appmeta description (the catalog short_description) is {len(short)} chars; needs 10-120, one line")

    for name, size in (("icon_front_8x8.png", (8, 8)), ("icon_back_11x11.png", (11, 11))):
        data = src.read(f"src/appmeta/{name}")
        if data is None:
            warnings.append(f"no appmeta/{name}: the catalog shows a default icon")
        else:
            check_png(data, size, 64 * 1024, f"appmeta/{name}", errors)

    desc = src.read("CATALOG.md")
    if desc is None:
        errors.append("app/CATALOG.md (the catalog description) is missing")
    else:
        text = desc.decode("utf-8")
        if not 50 <= len(text) <= 4000:
            errors.append(f"app/CATALOG.md is {len(text)} chars; needs 50-4000")
        errors += [f"app/CATALOG.md {p}" for p in markdown_problems(text)]

    log = src.read("CHANGELOG.md")
    section = changelog_section(log.decode("utf-8"), meta.get("version", "")) if log else None
    if section is None:
        errors.append(f"app/CHANGELOG.md has no '## {meta.get('version')}' section")
    else:
        if not 10 <= len(section) <= 4000:
            errors.append(f"changelog for {meta.get('version')} is {len(section)} chars; needs 10-4000")
        errors += [f"app/CHANGELOG.md {p}" for p in markdown_problems(section)]
        facts["changelog"] = section

    shots = [n for n in src.list("screenshots") if n.lower().endswith(".png") and "@" not in n]
    if not 1 <= len(shots) <= 10:
        errors.append(f"app/screenshots/ has {len(shots)} PNGs; the catalog needs 1-10 (72x16, from a bar)")
    for n in shots:
        check_png(src.read(f"screenshots/{n}") or b"", (72, 16), 2 * 1024 * 1024, f"screenshots/{n}", errors)

    lock = src.read("package-lock.json")
    if lock is None:
        errors.append("app/package-lock.json is missing")
    else:
        cli = json.loads(lock).get("packages", {}).get("node_modules/@busy-app/cli", {}).get("version")
        if not cli:
            errors.append("package-lock.json doesn't pin @busy-app/cli")
        facts["cli"] = cli
    for other in ("pnpm-lock.yaml", "yarn.lock", "bun.lockb", "bun.lock"):
        if src.read(other) is not None:
            errors.append(f"app/{other}: keep exactly one lock file, package-lock.json")
    if not any(src.read(n, root=True) is not None for n in ("LICENSE", "LICENCE", "COPYING")):
        errors.append("no LICENSE at the repo root")
    if category not in CATEGORIES:
        errors.append(f"category {category!r}: one of {', '.join(CATEGORIES)}")
    return facts, [f"screenshots/{n}" for n in shots], errors, warnings


def build_isolated(app: str, sha: str | None, app_id: str) -> list[str]:
    """Build app/ alone in a temp dir (only the files the catalog gets), then check the package like the catalog."""
    errors: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "app"
        if sha is None:
            shutil.copytree(ROOT / f"apps/{app}/app", work, ignore=shutil.ignore_patterns("node_modules", "dist"))
        else:
            archive = subprocess.run(["git", "-C", str(ROOT), "archive", sha, f"apps/{app}/app"],
                                     check=True, capture_output=True).stdout
            with tarfile.open(fileobj=io.BytesIO(archive)) as t:  # our own git archive, so trusted
                try:
                    t.extractall(tmp, filter="data")
                except TypeError:  # Python < 3.10.12 has no extraction filters
                    t.extractall(tmp)
            (Path(tmp) / f"apps/{app}/app").rename(work)
        print(f"==> Building app/ alone in {work} (npm ci --ignore-scripts, then busy-cli build)", file=sys.stderr)
        cmd = (f'. "{ROOT}/tools/lib.sh" && cd "{work}" && '
               'node24 "npm ci --ignore-scripts --no-fund --no-audit && ./node_modules/.bin/busy-cli build"')
        r = subprocess.run(["bash", "-c", cmd], stdout=sys.stderr)
        if r.returncode:
            return [f"isolated build failed (exit {r.returncode}); see the output above"]
        pkg = work / "dist" / f"{app_id}.tgz"
        if not pkg.is_file():
            return [f"build didn't produce dist/{app_id}.tgz"]
        with tarfile.open(pkg) as t:
            # "._*" entries are macOS AppleDouble metadata from a local tar; the catalog builds on Linux.
            scripts = [m for m in t.getmembers() if m.name.startswith(f"{app_id}/scripts/") and m.name.endswith(".js")
                       and not m.name.rsplit("/", 1)[1].startswith("._")]
        names = sorted(m.name.rsplit("/", 1)[1] for m in scripts)
        if names != ["main.js"]:
            errors.append(f"package scripts are {names}; expected only main.js")
        errors += [f"{m.name} is {m.size} bytes; the catalog allows {MAX_MAIN_JS}" for m in scripts if m.size > MAX_MAIN_JS]
        print(f"==> Isolated build OK: {pkg.name}, scripts {names}", file=sys.stderr)
    return errors


def origin_url() -> str:
    url = git("remote", "get-url", "origin")
    m = re.match(r"(?:https://github\.com/|git@github\.com:)([^/]+)/([^/]+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit(f"origin {url} isn't a GitHub repo")
    return f"https://github.com/{m.group(1)}/{m.group(2)}.git"


def yaml_str(s: str) -> str:
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(app: str, sha: str, facts: dict, shots: list[str], category: str) -> str:
    lines = [
        "sourcecode:",
        "  type: git",
        "  location:",
        f"    origin: {origin_url()}",
        f"    commit_sha: {sha}  # {facts['version']}",
        f"    subdir: apps/{app}/app",
        f"category: {category}",
        f"short_description: {yaml_str(facts['description'])}",
        'description: "@CATALOG.md"',
        "changelog: |",
        *[f"  {line}".rstrip() for line in facts["changelog"].rstrip("\n").splitlines()],
        "screenshots:",
        *[f"  - {s}" for s in shots],
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("app", help="folder under apps/")
    ap.add_argument("--sha", help="commit to publish (default: origin/main)")
    ap.add_argument("--worktree", action="store_true", help="check uncommitted files instead; prints no manifest")
    ap.add_argument("--category", default="art", help="catalog category, fixed by the first published version")
    ap.add_argument("--build", action="store_true", help="also build app/ alone, as the catalog does (needs npm)")
    ap.add_argument("--out", help="write manifest.yml here instead of stdout")
    args = ap.parse_args()
    if not (ROOT / "apps" / args.app / "app").is_dir():
        raise SystemExit(f"no apps/{args.app}/app")

    sha = None
    if not args.worktree:
        sha = git("rev-parse", "--verify", f"{args.sha or 'origin/main'}^{{commit}}")
        if not SHA.match(sha):
            raise SystemExit(f"{sha} isn't a full commit SHA")
        on_main = subprocess.run(["git", "-C", str(ROOT), "merge-base", "--is-ancestor", sha, "origin/main"]).returncode == 0
        if not on_main:
            raise SystemExit(f"{sha[:12]} isn't on origin/main. Catalog commits must stay reachable; merge to main first "
                             "(git fetch origin if it was just merged).")

    src = Source(args.app, sha)
    facts, shots, errors, warnings = check(src, args.app, args.category)
    if args.build and APP_ID.match(facts.get("id", "")):
        errors += build_isolated(args.app, sha, facts["id"])
    where = f"{sha[:12]}" if sha else "working tree"
    for w in warnings:
        print(f"warning: {w}", file=sys.stderr)
    if errors:
        print(f"{args.app} @ {where}: not ready for the catalog:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        raise SystemExit(1)
    print(f"{args.app} @ {where}: {facts['id']} {facts['version']} meets the catalog rules this tool checks",
          file=sys.stderr)
    if sha is None:
        return
    text = render(args.app, sha, facts, shots, args.category)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"wrote {out}", file=sys.stderr)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
