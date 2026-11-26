#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only day07,...]     (run from apps/advent-calendar/)

Outputs
  app/src/animations/<name>.anim       25 daily vignettes, the door intro, the winter scene, the card backdrop
  app/shared/generated/show.ts         days, durations, text styles and fonts for the JS app
  app/src/appmeta/icon_*.png           menu icons
  mockup/index.html                    self-contained browser simulator + storyboards
  previews/<name>.gif                  LED-style GIF previews (git-ignored)

Every .anim is decoded again and compared pixel-for-pixel with the rendered frames (lib/python/busybar/showbuild.py).
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
from scenes import CARD, DAYS, DOOR, WINTER  # noqa: E402
from scenes.text import CARD_MS, STYLES, TEXT_FONTS  # noqa: E402

APP_ID = "busybartools.advent"

# Display tone curve, the value approved on real hardware for the collection (docs/DECISIONS.md D9).
# Applied to every output frame and to every live-text color, so the bar and the mockup match.
GAMMA = 0.8
LUT = tone_lut(GAMMA)


def tone(img):
    """Tone-map one frame (used by review helpers). Flattens first: apply_tone needs an RGB image."""
    return apply_tone(img.convert("RGB"), LUT)


def text_styles() -> dict:
    """Live-text styles with tone-mapped colors, exactly as the app and the mockup use them."""
    styles = json.loads(json.dumps(STYLES))
    for spec in styles.values():
        for part in ("top", "bottom", "shadow"):
            spec[part] = tone_rgb(spec[part], LUT)
    return styles


ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"

ICON_FRONT = """
..GBBG..
.GBBBBG.
.RRRRRR.
.RYYYYR.
.RYRRYR.
.RYYYYR.
.RRRRRR.
........
"""  # 8x8 wrapped door with a bow
ICON_BACK = """
.....#.....
....###....
.#########.
..#######..
...#####...
...##.##...
..##...##..
...........
.#########.
.#.#.#.#.#.
.#########.
"""  # 11x11 star over a calendar row, single grey #888888


def write_icons() -> None:
    save_icon(META / "icon_front_8x8.png", {"G": "#2E9E4E", "B": "#FFD24A", "R": "#D21F2B", "Y": "#FFE9A0"},
              ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def scene_entry(m: dict) -> dict:
    return {"name": m["name"], "title": m["title"], "path": f"animations/{m['name']}.anim", "ms": m["ms"]}


def show_data(day_metas, door_meta, winter_meta, card_meta) -> dict:
    return {
        "fps": FPS,
        "days": [{"day": i + 1, **scene_entry(m)} for i, m in enumerate(day_metas)],
        "door": {**scene_entry(door_meta), "text_ms": DOOR.TEXT_MS},
        "winter": scene_entry(winter_meta),
        "card": {**scene_entry(card_meta), "ms": CARD_MS},
        "styles": text_styles(),
    }


def write_ts(show: dict) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("FONTS", font.export_json(TEXT_FONTS), FONT_TS_TYPE, None, False),
    ]))


def write_mockup(show: dict, metas: dict, total_bytes: int) -> None:
    def full(m):
        return {k: m[k] for k in ("name", "title", "ms", "frames", "keyframes", "sheet")}
    data = {
        "fps": FPS, "w": W, "h": H,
        "show": show,
        "anims": {name: full(m) for name, m in metas.items()},
        "fonts": font.export_json(TEXT_FONTS),
        "bytes": total_bytes,
    }
    fill_template(MOCKUP / "template.html", MOCKUP / "index.html", data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gif", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}

    modules = DAYS + [DOOR, WINTER, CARD]
    metas = build_scenes(modules, ANIM_DIR, LUT, None if args.no_gif else PREVIEWS, only=only)
    if only:
        print("  --only: skipped show.ts and mockup (they need every scene)")
        return
    by_name = {m["name"]: m for m in metas}
    show = show_data(metas[:len(DAYS)], by_name[DOOR.NAME], by_name[WINTER.NAME], by_name[CARD.NAME])
    write_ts(show)
    write_icons()
    total = sum(m["bytes"] for m in metas)
    if (MOCKUP / "template.html").exists():
        write_mockup(show, by_name, total)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
