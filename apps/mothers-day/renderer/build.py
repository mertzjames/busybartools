#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only bouquet,...]     (run from apps/mothers-day/)

Outputs
  app/src/animations/<scene>.anim      firmware-played animations (+ clock_bg.anim, count_bg.anim)
  app/shared/generated/show.ts         scenes, durations, card backdrops, text layout and fonts for the JS app
  app/src/appmeta/icon_*.png           menu icons
  mockup/index.html                    self-contained browser simulator + storyboards
  previews/<scene>.gif                 LED-style GIF previews (git-ignored)

Every .anim is decoded again and compared pixel-for-pixel with the rendered frames (shared render kit,
lib/python/busybar/showbuild.py). The mockup runs the app's own card logic: app/shared/mothersday.ts and the kit's
walltime.ts and holidays.ts are type-stripped with Node 24 and inlined, so the simulator can't drift from the bar.
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
from scenes import CLOCK_BG, COUNT_BG, PLAYLIST  # noqa: E402
from scenes.text import DAY_TEXT, LAYOUT  # noqa: E402,F401  (DAY_TEXT is re-exported for review.py)

APP_ID = "busybartools.mothersday"

# Display tone curve (docs/DECISIONS.md D4): the value approved on real hardware for Wizarding Thanksgiving.
GAMMA = 0.8
LUT = tone_lut(GAMMA)

# Only the fonts the app draws live text with go into the generated TS (keeps main.js small).
LIVE_FONTS = ("big", "tiny", "clock")
BACKDROPS = (CLOCK_BG, COUNT_BG)

ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js (src/*.ts become entries)
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"
MOCKUP_TS = [REPO / "lib/ts/busybar/walltime.ts", REPO / "lib/ts/busybar/holidays.ts", ROOT / "app/shared/mothersday.ts"]


def tone(img):
    """Tone-map one frame (used by tests and review helpers)."""
    return apply_tone(img, LUT)


def layout() -> dict:
    """LAYOUT with tone-mapped colors, exactly as the app and the mockup use it."""
    lay = json.loads(json.dumps(LAYOUT))
    for spec in lay.values():
        for part in ("top", "bottom", "shadow"):
            spec[part] = tone_rgb(spec[part], LUT)
    return lay


def draw_live(img, text: str, style: str) -> None:
    """Draw card text exactly as the app does (centered, gradient, 1 px shadow)."""
    spec = layout()[style]
    font.draw_text(img, text, (W - font.text_width(text, spec["font"])) // 2, spec["y"], None, font=spec["font"],
                   gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]))


ICON_FRONT = """
.PP.PP..
PHPPPPP.
PPPPPPP.
.PPPPP..
..PPP...
...P....
..GG....
.G......
"""  # 8x8: a pink heart on a green stem
ICON_BACK = """
..##.##....
.#######...
.#######...
..#####....
...###.....
....#......
....#......
....#.##...
...##.#....
..#.##.....
....#......
"""  # 11x11, single grey #888888: a heart-shaped flower on a leafy stem


def write_icons() -> None:
    """App menu icons (optional per the BUSY app docs): 8x8 color front, 11x11 grey back."""
    save_icon(META / "icon_front_8x8.png", {"P": "#FF6AA8", "H": "#FFC4DC", "G": "#48BA46"}, ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def show_data(metas, bg_metas) -> dict:
    return {
        "fps": FPS,
        "scenes": [{"name": m["name"], "title": m["title"], "path": f"animations/{m['name']}.anim", "ms": m["ms"]}
                   for m in metas],
        "backdrops": {m["name"]: f"animations/{m['name']}.anim" for m in bg_metas},
    }


def write_ts(show: dict) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("LAYOUT", layout(), None, 2, True),
        ("FONTS", font.export_json(LIVE_FONTS), FONT_TS_TYPE, None, False),
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
    """The app's TS card logic as one browser script: types stripped (Node 24), imports dropped, exports collected."""
    res = subprocess.run(node_cmd() + ["--no-warnings", "-e", STRIP_JS] + [str(p) for p in MOCKUP_TS],
                         capture_output=True, text=True, check=True)
    names, parts = [], []
    for path, js in zip(MOCKUP_TS, json.loads(res.stdout)):
        js = re.sub(r"^import [^;]*;[ \t]*$", "", js, flags=re.M)
        names += re.findall(r"^export (?:function|const) (\w+)", js, flags=re.M)
        js = re.sub(r"^export ", "", js, flags=re.M)
        js = "\n".join(ln.rstrip() for ln in js.splitlines())
        js = re.sub(r"\n{3,}", "\n\n", js)
        parts.append(f"// ---- {path.relative_to(REPO).as_posix()}\n{js.strip()}\n")
    assert not re.search(r"^\s*import\s", "".join(parts), flags=re.M), "leftover import"
    return "const MD = (() => {\n" + "\n".join(parts) + f"return {{ {', '.join(sorted(set(names)))} }};\n}})();"


def write_mockup(show, metas, bg_metas) -> None:
    keep = ("name", "title", "ms", "frames", "keyframes", "sheet")
    data = {
        "fps": FPS, "w": W, "h": H, "show": show, "layout": layout(), "fonts": font.export_json(LIVE_FONTS),
        "scenes": [{k: m[k] for k in keep} for m in metas],
        "bg": {m["name"]: {k: m[k] for k in keep} for m in bg_metas},
        "anim_bytes": sum(m["bytes"] for m in metas + bg_metas),
    }
    html = (MOCKUP / "template.html").read_text().replace("/*__MD_LOGIC__*/", mockup_logic())
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

    metas = build_scenes(PLAYLIST + list(BACKDROPS), ANIM_DIR, LUT, None if args.no_gif else PREVIEWS,
                         only=only, keep=BACKDROPS)
    bg_metas = metas[-len(BACKDROPS):]
    metas = metas[:-len(BACKDROPS)]
    if only:
        print("  --only: skipped show.ts, icons and mockup (they need every scene)")
        return
    show = show_data(metas, bg_metas)
    write_ts(show)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(show, metas, bg_metas)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
