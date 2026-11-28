#!/usr/bin/env python3
"""Render every scene and backdrop and write all outputs.

    python3 renderer/build.py [--no-gif] [--only disco_ball,...]     (run from apps/new-years-eve/)

Outputs
  app/src/animations/<name>.anim      party scenes and live-screen backdrops, played by the firmware
  app/shared/generated/show.ts        playlist, durations, backdrops, live-text layout and fonts for the app
  app/src/appmeta/icon_*.png          menu icons
  mockup/index.html                   self-contained simulator + storyboards (from mockup/template.html)
  previews/<name>.gif                 LED-style GIF previews (git-ignored)

The mockup runs the app's own phase and screen logic: app/shared/nye.ts and screens.ts (plus the shared kit's
walltime.ts and xpmtext.ts) are type-stripped with Node 24 and inlined, so the simulator can't drift from the bar.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(REPO / "lib" / "python"))  # shared busybar package

from busybar import font  # noqa: E402
from busybar.canvas import FPS, H, W  # noqa: E402
from busybar.showbuild import (FONT_TS_TYPE, apply_tone, build_scenes, fill_template, save_icon,  # noqa: E402
                               tone_lut, tone_rgb, ts_module)

import live  # noqa: E402  (registers the "huge" font)
from scenes import BACKDROPS, PLAYLIST  # noqa: E402

APP_ID = "io.github.mertzjames.newyear"

# Display tone curve, the same one approved on the bar for Wizarding Thanksgiving (docs/DECISIONS.md D12). Applied to
# every frame and to every live-text color, so the bar, the mockup and the storyboards match.
GAMMA = 0.8
LUT = tone_lut(GAMMA)

ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"

# Modules inlined into the mockup, in dependency order.
MOCKUP_TS = [REPO / "lib" / "ts" / "busybar" / "walltime.ts", REPO / "lib" / "ts" / "busybar" / "xpmtext.ts",
             ROOT / "app" / "shared" / "nye.ts", ROOT / "app" / "shared" / "screens.ts"]


def tone(img):
    """Tone-map one frame (review helpers)."""
    return apply_tone(img.convert("RGB"), LUT)


def toned(value):
    """Tone-map every color in a layout structure (lists of 3 ints under top/bottom/shadow/on/off)."""
    if isinstance(value, dict):
        return {k: (tone_rgb(v, LUT) if k in ("top", "bottom", "shadow", "on", "off") else toned(v))
                for k, v in value.items()}
    if isinstance(value, list):
        return [toned(v) for v in value]
    return value


def layout() -> dict:
    return toned(json.loads(json.dumps(live.LAYOUT)))


ICON_FRONT = """
..P..G..
.P.GG.C.
..GYYG..
.GYYYYG.
.GYYYYG.
..GYYG..
.C.GG.P.
..G..C..
"""  # 8x8 firework burst, full color
ICON_BACK = """
.....#.....
.....#.....
..#..#..#..
...#...#...
....###....
####.#.####
....###....
...#...#...
..#..#..#..
.....#.....
.....#.....
"""  # 11x11 starburst, single grey #888888


def write_icons() -> None:
    save_icon(META / "icon_front_8x8.png", {"G": "#FFC834", "Y": "#FFF4C0", "P": "#FF2EAA", "C": "#2AD8FF"},
              ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def scene_entry(m, meta) -> dict:
    e = {"name": meta["name"], "title": meta["title"], "path": f"animations/{meta['name']}.anim", "ms": meta["ms"]}
    if getattr(m, "OVERLAY", None):
        e["overlay"] = m.OVERLAY
    return e


def show_data(scene_metas, bg_metas) -> dict:
    return {
        "fps": FPS,
        "scenes": [scene_entry(m, meta) for m, meta in zip(PLAYLIST, scene_metas)],
        "bg": {key: {"path": f"animations/{meta['name']}.anim", "ms": meta["ms"]}
               for key, meta in zip(BACKDROPS, bg_metas)},
    }


def write_ts(show: dict) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("LAYOUT", layout(), None, 2, True),
        ("FONTS", font.export_json(live.FONTS_USED), FONT_TS_TYPE, None, False),
    ]))


def node_cmd() -> list[str]:
    try:
        local = subprocess.run(["node", "-v"], capture_output=True, text=True).stdout.startswith("v24.")
    except FileNotFoundError:
        local = False
    return ["node"] if local else ["npx", "-y", "-p", "node@24", "node"]


STRIP_JS = """
const { stripTypeScriptTypes } = require("node:module");
const fs = require("node:fs");
const out = process.argv.slice(1).map((p) => stripTypeScriptTypes(fs.readFileSync(p, "utf8")));
process.stdout.write(JSON.stringify(out));
"""


def mockup_logic() -> str:
    """The app's TS logic as one browser script: types stripped (Node 24), imports dropped, exports collected."""
    res = subprocess.run(node_cmd() + ["--no-warnings", "-e", STRIP_JS] + [str(p) for p in MOCKUP_TS],
                         capture_output=True, text=True, check=True)
    names, parts = [], []
    for path, js in zip(MOCKUP_TS, json.loads(res.stdout)):
        js = re.sub(r"^import [^\n]*;[ \t]*$", "", js, flags=re.M)
        names += re.findall(r"^export (?:function|const) (\w+)", js, flags=re.M)
        js = re.sub(r"^export ", "", js, flags=re.M)
        js = "\n".join(ln.rstrip() for ln in js.splitlines())
        js = re.sub(r"\n{3,}", "\n\n", js)
        parts.append(f"// ---- {path.relative_to(REPO).as_posix()}\n{js.strip()}\n")
    assert "import " not in "".join(re.findall(r"^\s*import .*$", "".join(parts), flags=re.M)), "leftover import"
    return "const NYE = (() => {\n" + "\n".join(parts) + f"return {{ {', '.join(sorted(set(names)))} }};\n}})();"


def write_mockup(show, scene_metas, bg_metas) -> None:
    keep = ("name", "title", "ms", "frames", "keyframes", "sheet")
    data = {
        "fps": FPS, "w": W, "h": H, "show": show, "layout": layout(), "fonts": font.export_json(live.FONTS_USED),
        "scenes": [{k: m[k] for k in keep} for m in scene_metas],
        "bg": {key: {k: m[k] for k in keep} for key, m in zip(BACKDROPS, bg_metas)},
        "anim_kib": round(sum(m["bytes"] for m in scene_metas + bg_metas) / 1024),
    }
    html = (MOCKUP / "template.html").read_text().replace("/*__NYE_LOGIC__*/", mockup_logic())
    tmp = MOCKUP / ".template.tmp"
    tmp.write_text(html)
    try:
        fill_template(tmp, MOCKUP / "index.html", data)
    finally:
        tmp.unlink()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gif", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}

    bgs = list(BACKDROPS.values())
    metas = build_scenes(PLAYLIST + bgs, ANIM_DIR, LUT, None if args.no_gif else PREVIEWS, only=only)
    if only:
        print("  --only: generated TS and mockup not rewritten")
        return
    scene_metas, bg_metas = metas[:len(PLAYLIST)], metas[len(PLAYLIST):]
    show = show_data(scene_metas, bg_metas)
    write_ts(show)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(show, scene_metas, bg_metas)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
