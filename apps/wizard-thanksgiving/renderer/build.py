#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only owl_post,...]     (run from apps/wizard-thanksgiving/)

Outputs
  app/src/animations/<scene>.anim      firmware-played animations (+ clock_bg.anim)
  app/shared/generated/show.ts         playlist, durations, fonts, clock layout for the JS app
  mockup/index.html                    self-contained browser simulator + storyboards
  previews/<scene>.gif                 LED-style GIF previews

Every .anim is decoded again and compared pixel-for-pixel with the rendered frames. The pipeline itself lives
in the shared render kit (lib/python/busybar/showbuild.py).
"""

from __future__ import annotations

import argparse
import json
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
from scenes import CLOCK_BG, PLAYLIST  # noqa: E402

APP_ID = "wizard.thanksgiving"

# Display tone curve (docs/DECISIONS.md D21). Applied to every output frame and to the clock colors, so the
# bar, the mockup and the storyboards all match. 1.0 = original colors; lower = brighter darks/midtones.
GAMMA = 0.8
LUT = tone_lut(GAMMA)


def tone(img):
    """Tone-map one frame (used by tests and review helpers)."""
    return apply_tone(img, LUT)


def clock_layout() -> dict:
    lay = json.loads(json.dumps(CLOCK_BG.LAYOUT))
    for key in ("time", "date"):
        for part in ("top", "bottom", "shadow"):
            lay[key][part] = tone_rgb(lay[key][part], LUT)
    return lay


ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js (src/*.ts become separate entries)
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"

ICON_FRONT = """
...G....
..Gg....
.OoOoO..
OOoOoOO.
OOoOoOO.
OOoOoOO.
.OoOoO..
........
"""  # 8x8 pumpkin, full color
ICON_BACK = """
.....#.....
....##.....
....###....
...####....
...#####...
..######...
..#######..
.########..
.#########.
###########
...........
"""  # 11x11 pointed hat, single grey #888888


def write_icons() -> None:
    """App menu icons (optional per the BUSY app docs): 8x8 color front, 11x11 grey back."""
    save_icon(META / "icon_front_8x8.png", {"G": "#3E8E2E", "g": "#2A6A1E", "O": "#F07B1A", "o": "#B5530C"},
              ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def write_ts(scenes_meta, clock_meta) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    show = {
        "fps": FPS,
        "scenes": [{"name": m["name"], "title": m["title"], "path": f"animations/{m['name']}.anim",
                    "ms": m["ms"]} for m in scenes_meta],
        "clock": {"path": f"animations/{clock_meta['name']}.anim", **clock_layout()},
    }
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("FONTS", font.export_json(), FONT_TS_TYPE, None, False),
    ]))


def write_mockup(scenes_meta, clock_meta) -> None:
    data = {
        "fps": FPS, "w": W, "h": H,
        "scenes": [{k: m[k] for k in ("name", "title", "ms", "frames", "keyframes", "sheet")} for m in scenes_meta],
        "clock": {"name": clock_meta["name"], "frames": clock_meta["frames"], "sheet": clock_meta["sheet"],
                  **clock_layout()},
        "fonts": font.export_json(),
    }
    fill_template(MOCKUP / "template.html", MOCKUP / "index.html", data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gif", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}

    metas = build_scenes(PLAYLIST + [CLOCK_BG], ANIM_DIR, LUT, None if args.no_gif else PREVIEWS,
                         only=only, keep=(CLOCK_BG,))
    clock_meta = metas.pop()  # CLOCK_BG is always rendered last
    write_ts(metas, clock_meta)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(metas, clock_meta)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
