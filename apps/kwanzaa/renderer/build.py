#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only harvest,...]     (run from apps/kwanzaa/)

Outputs
  app/src/animations/<scene>.anim      firmware-played animations: kinara_0..7, kinara_center_2..7, the scenes,
                                       card_bg
  app/shared/generated/show.ts         scenes, durations, text styles, timings, the Nguzo Saba, fonts
  app/src/appmeta/icon_*.png           menu icons
  mockup/index.html                    self-contained browser simulator + storyboards
  previews/<scene>.gif                 LED-style GIF previews (git-ignored)

Every .anim is decoded again and compared pixel-for-pixel with the rendered frames. The pipeline lives in the
shared render kit (lib/python/busybar/showbuild.py).
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
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "lib" / "python"))  # shared busybar package

from busybar import font  # noqa: E402
from busybar.canvas import FPS, H, W  # noqa: E402
from busybar.showbuild import (FONT_TS_TYPE, apply_tone, build_scenes, fill_template, save_icon,  # noqa: E402
                               tone_lut, tone_rgb, ts_module)
from kfx import DEFAULT_ORDER, LIGHT_ORDERS  # noqa: E402
from scenes import CARD_BG, KINARA, KINARA_CENTER, PLAYLIST  # noqa: E402
from scenes.kinara import variant_names  # noqa: E402
from scenes.text import GREETING, PRINCIPLES, STYLES, TEXT_FONTS, TIMING  # noqa: E402

APP_ID = "io.github.mertzjames.kwanzaa"

# Display tone curve (docs/DECISIONS.md D10): the value approved on real hardware for Wizarding Thanksgiving.
# Applied to every output frame and to the text colors, so the bar, the mockup and the storyboards all match.
GAMMA = 0.8
LUT = tone_lut(GAMMA)

ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js (src/*.ts become separate entries)
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"
REPO = HERE.parents[2]
# The app's own date and card logic, run by the mockup (in dependency order; see docs/DECISIONS.md D13)
MOCKUP_TS = [REPO / "lib" / "ts" / "busybar" / "walltime.ts", REPO / "lib" / "ts" / "busybar" / "holidays.ts",
             REPO / "lib" / "ts" / "busybar" / "settings.ts", ROOT / "app" / "shared" / "kwanzaa.ts"]


def tone(img):
    """Tone-map one frame (used by tests and review helpers)."""
    return apply_tone(img, LUT)


def text_styles() -> dict:
    """Live-text styles with tone-mapped colors, exactly as the app and the mockup use them."""
    styles = json.loads(json.dumps(STYLES))
    for spec in styles.values():
        for part in ("top", "bottom", "shadow"):
            spec[part] = tone_rgb(spec[part], LUT)
    return styles


def draw_live(img, text: str, spec: dict, alpha: float = 1.0) -> None:
    """Draw card text exactly as the app does (centered, gradient, 1 px shadow)."""
    font.draw_text(img, text, (W - font.text_width(text, spec["font"])) // 2, spec["y"], None, font=spec["font"],
                   gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]), alpha=alpha)


ICON_FRONT = """
...Y....
.Y.R.Y..
.R.K.G..
.R.K.G..
RRRKGGG.
RRRKGGG.
BBBBBBB.
..BBB...
"""  # 8x8 kinara: flames over red, black (charcoal) and green candles
ICON_BACK = """
.....#.....
.#...#...#.
.#...#...#.
.#.#.#.#.#.
.#.#.#.#.#.
.#.#.#.#.#.
.#.#.#.#.#.
###########
###########
....###....
...#####...
"""  # 11x11 kinara, single grey #888888


def write_icons() -> None:
    """App menu icons (optional per the BUSY app docs): 8x8 color front, 11x11 grey back."""
    save_icon(META / "icon_front_8x8.png", {"Y": "#FFD84A", "R": "#D8282E", "K": "#6A6A78", "G": "#2E9A48",
                                            "B": "#A0602E"}, ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def scene_entry(m: dict) -> dict:
    return {"name": m["name"], "title": m["title"], "path": f"animations/{m['name']}.anim", "ms": m["ms"]}


def show_data(metas, card_meta) -> dict:
    """What the app needs. scenes = every kinara variant, then the playlist. kinara[order][day] is the scene index of
    that day's kinara (day 0 = unlit) in each lighting order; playlist lists the scenes that follow it."""
    names = [m["name"] for m in metas]
    return {
        "fps": FPS,
        "scenes": [scene_entry(m) for m in metas],
        "kinara": {order: [names.index(n) for n in variant_names(order)] for order in LIGHT_ORDERS},
        "orders": list(LIGHT_ORDERS),
        "default_order": DEFAULT_ORDER,
        "playlist": [names.index(m.NAME) for m in PLAYLIST],
        "card": {"path": f"animations/{card_meta['name']}.anim"},
        "styles": text_styles(),
        "timing": TIMING,
        "principles": PRINCIPLES,
        "greeting": GREETING,
    }


def write_ts(show: dict) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("FONTS", font.export_json(TEXT_FONTS), FONT_TS_TYPE, None, False),
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
    """The app's TS logic as one browser script (the approach of apps/new-years-eve): types stripped by Node 24,
    imports dropped, exports collected into a KW object. kwanzaa.ts reads the global SHOW, which the mockup
    defines with the same fields as show.ts."""
    res = subprocess.run(node_cmd() + ["--no-warnings", "-e", STRIP_JS] + [str(p) for p in MOCKUP_TS],
                         capture_output=True, text=True, check=True)
    names, parts = [], []
    for path, js in zip(MOCKUP_TS, json.loads(res.stdout)):
        js = re.sub(r"^import\b[^;]*;[ \t]*$", "", js, flags=re.M)  # also multi-line imports
        names += re.findall(r"^export (?:function|const) (\w+)", js, flags=re.M)
        js = re.sub(r"^export ", "", js, flags=re.M)
        js = "\n".join(ln.rstrip() for ln in js.splitlines())
        js = re.sub(r"\n{3,}", "\n\n", js)
        parts.append(f"// ---- {path.relative_to(REPO).as_posix()}\n{js.strip()}\n")
    assert not re.search(r"^\s*import ", "".join(parts), flags=re.M), "leftover import"
    return "const KW = (() => {\n" + "\n".join(parts) + f"return {{ {', '.join(sorted(set(names)))} }};\n}})();"


def write_mockup(show: dict, metas, card_meta) -> None:
    def full(m):
        return {k: m[k] for k in ("name", "title", "ms", "frames", "keyframes", "sheet")}
    data = {
        **show, "w": W, "h": H,
        "scenes": [full(m) for m in metas],
        "card": {"frames": card_meta["frames"], "sheet": card_meta["sheet"]},
        "fonts": font.export_json(TEXT_FONTS),
        "anim_bytes": sum(m["bytes"] for m in metas) + card_meta["bytes"],
    }
    tmp = MOCKUP / ".template.tmp"
    tmp.write_text((MOCKUP / "template.html").read_text().replace("/*__KW_LOGIC__*/", mockup_logic()))
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

    metas = build_scenes(KINARA + KINARA_CENTER + PLAYLIST + [CARD_BG], ANIM_DIR, LUT,
                         None if args.no_gif else PREVIEWS, only=only, keep=(CARD_BG,))
    if only:
        print("  --only: skipped show.ts, icons and mockup (they need every scene)")
        return
    card_meta = metas.pop()  # CARD_BG is always rendered last
    show = show_data(metas, card_meta)
    write_ts(show)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(show, metas, card_meta)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
