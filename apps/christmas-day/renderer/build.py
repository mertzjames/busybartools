#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only sleigh_ride,...]     (run from apps/christmas-day/)

Outputs
  app/src/animations/<scene>.anim      firmware-played animations (+ clock_bg.anim)
  app/shared/generated/show.ts         playlist, durations, fonts, clock layout for the JS app
  app/src/appmeta/icon_*.png           menu icons
  mockup/index.html                    self-contained browser simulator + storyboards
  previews/<scene>.gif                 LED-style GIF previews (git-ignored)

Every .anim is decoded again and compared pixel-for-pixel with the rendered frames. The pipeline lives in the
shared render kit (lib/python/busybar/showbuild.py).
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

APP_ID = "io.github.mertzjames.christmas"

# Display tone curve (docs/DECISIONS.md D4): the value approved on real hardware for Wizarding Thanksgiving.
# Applied to every output frame and to the clock colors, so the bar, the mockup and the storyboards all match.
GAMMA = 0.8
LUT = tone_lut(GAMMA)

# Only the fonts the app draws live text with go into the generated TS (keeps main.js small).
LIVE_FONTS = ("big", "clock")


def tone(img):
    """Tone-map one frame (used by tests and review helpers)."""
    return apply_tone(img, LUT)


def clock_layout() -> dict:
    lay = json.loads(json.dumps(CLOCK_BG.LAYOUT))
    for key in ("time", "date"):
        for part in ("top", "bottom", "shadow"):
            lay[key][part] = tone_rgb(lay[key][part], LUT)
    return lay


def draw_live(img, text: str, spec: dict) -> None:
    """Draw clock-card text exactly as the app does (centered, gradient, 1 px shadow)."""
    font.draw_text(img, text, (W - font.text_width(text, spec["font"])) // 2, spec["y"], None, font=spec["font"],
                   gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]))


def clock_preview(bg_frames, time_text: str = "18:05", date_text: str = "FRI 25 DEC"):
    """A whole clock card (time, then date) over the tone-mapped backdrop, for review strips."""
    lay = clock_layout()
    total = round((lay["time_ms"] + lay["date_ms"]) * FPS / 1000)
    out = []
    for f in range(total):
        img = bg_frames[f % len(bg_frames)].convert("RGBA")
        ms = f * 1000 / FPS
        if ms < lay["time_ms"]:
            draw_live(img, time_text, lay["time"])
        else:
            draw_live(img, date_text, lay["date"])
        out.append(img.convert("RGB"))
    picks = [int(s * FPS) for s in (0.5, 2.5, 4.0, 5.5, 7.5)]
    return out, picks


ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js (src/*.ts become separate entries)
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"

ICON_FRONT = """
...Y....
...G....
..GGG...
..GRG...
.GGGGG..
.GYGRG..
GGGGGGG.
...b....
"""  # 8x8 decorated tree, full color
ICON_BACK = """
.....#.....
....###....
.....#.....
....###....
...#####...
....###....
...#####...
..#######..
.#########.
.....#.....
.....#.....
"""  # 11x11 tree with a star, single grey #888888


def write_icons() -> None:
    """App menu icons (optional per the BUSY app docs): 8x8 color front, 11x11 grey back."""
    save_icon(META / "icon_front_8x8.png", {"Y": "#FFD84A", "G": "#2E9A48", "R": "#E0303A", "b": "#8A5530"},
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
        ("FONTS", font.export_json(LIVE_FONTS), FONT_TS_TYPE, None, False),
    ]))


def write_mockup(scenes_meta, clock_meta) -> None:
    data = {
        "fps": FPS, "w": W, "h": H,
        "scenes": [{k: m[k] for k in ("name", "title", "ms", "frames", "keyframes", "sheet")} for m in scenes_meta],
        "clock": {"name": clock_meta["name"], "frames": clock_meta["frames"], "sheet": clock_meta["sheet"],
                  **clock_layout()},
        "fonts": font.export_json(LIVE_FONTS),
        "anim_bytes": sum(m["bytes"] for m in scenes_meta) + clock_meta["bytes"],
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
    if only:
        print("  --only: skipped show.ts, icons and mockup (they need every scene)")
        return
    write_ts(metas, clock_meta)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(metas, clock_meta)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
