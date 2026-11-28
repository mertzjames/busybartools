#!/usr/bin/env python3
"""Render every scene and write all outputs.

    python3 renderer/build.py [--no-gif] [--only lanterns,...]     (run from apps/lunar-new-year/)

Outputs
  app/src/animations/<scene>.anim      firmware-played animations: 7 festival scenes, 12 zodiac scenes, card_bg
  app/shared/generated/show.ts         scenes, playlists, text styles and timing, fonts for the JS app
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
from scenes import CARD_BG, PLAYLIST, PLAYLISTS, ZODIAC_SCENES  # noqa: E402
import textstyle  # noqa: E402

APP_ID = "io.github.mertzjames.lunarny"

# Display tone curve (docs/DECISIONS.md D8): the value approved on real hardware for Wizarding Thanksgiving.
# Applied to every output frame and to the live-text colors, so the bar, the mockup and the storyboards all match.
GAMMA = 0.8
LUT = tone_lut(GAMMA)

# Only the fonts the app draws live text with go into the generated TS (keeps main.js small).
LIVE_FONTS = ("big", "tiny", "clock")

ANIM_DIR = ROOT / "app" / "src" / "animations"
GEN_DIR = ROOT / "app" / "shared" / "generated"  # under shared/: bundled into main.js (src/*.ts become separate entries)
MOCKUP = ROOT / "mockup"
PREVIEWS = ROOT / "previews"
META = ROOT / "app" / "src" / "appmeta"


def tone(img):
    """Tone-map one frame (used by tests and review helpers)."""
    return apply_tone(img, LUT)


def text_styles() -> dict:
    """The live-text styles with tone-mapped colors, as the app and the mockup draw them."""
    out = json.loads(json.dumps(textstyle.STYLES))
    for spec in out.values():
        for part in ("top", "bottom", "shadow"):
            spec[part] = tone_rgb(spec[part], LUT)
    return out


def draw_live(img, text: str, spec: dict) -> None:
    """Draw card text exactly as the app does (centered, gradient, 1 px shadow), with tone-mapped colors."""
    font.draw_text(img, text, (W - font.text_width(text, spec["font"])) // 2, spec["y"], None, font=spec["font"],
                   gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]))


# Sample card pages for the review strip: (style, text) lines, as the app would show them.
CARD_SAMPLES = [
    [("time", "18:05")],
    [("date", "SAT 6 FEB")],
    [("head", "72 DAYS"), ("sub", "TO LUNAR NEW YEAR")],
    [("head", "1 DAY"), ("sub", "TO LUNAR NEW YEAR")],
    [("small", "YEAR OF THE"), ("name", "GOAT")],
    [("small", "YEAR OF THE"), ("name", "ROOSTER")],
    [("top", "HAPPY"), ("bot", "NEW YEAR")],
    [("top", "GONG XI"), ("bot", "FA CAI")],
    [("top", "GUNG HEI"), ("bot", "FAT CHOI")],
    [("top", "CHUC MUNG"), ("bot", "NAM MOI")],
    [("head", "SAEHAE BOK"), ("sub", "MANI BADEUSEYO")],
    [("top", "LANTERN"), ("bot", "FESTIVAL")],
]


def card_previews():
    """One tone-mapped frame per sample card page, over the backdrop (for review strips)."""
    bg = [tone(f.convert("RGB")) for f in CARD_BG.render()]
    styles = text_styles()
    out = []
    for i, page in enumerate(CARD_SAMPLES):
        img = bg[(i * 17) % len(bg)].convert("RGBA")
        for style, text in page:
            draw_live(img, text, styles[style])
        out.append(img.convert("RGB"))
    return out


ICON_FRONT = """
...G....
..GGG...
.RRRRR..
RRYRRRR.
RRYRRRR.
.RRRRR..
..GGG...
...Y....
"""  # 8x8 red lantern with gold caps, full color
ICON_BACK = """
.....#.....
....###....
..#######..
.#########.
.#########.
.#########.
.#########.
..#######..
....###....
.....#.....
.....#.....
"""  # 11x11 lantern, single grey #888888


def write_icons() -> None:
    """App menu icons (optional per the BUSY app docs): 8x8 color front, 11x11 grey back."""
    save_icon(META / "icon_front_8x8.png", {"G": "#E6A830", "R": "#E8242C", "Y": "#FFE08C"}, ICON_FRONT)
    save_icon(META / "icon_back_11x11.png", {"#": "#888888"}, ICON_BACK)


def scene_list(metas) -> list[dict]:
    return [{"name": m["name"], "title": m["title"], "path": f"animations/{m['name']}.anim", "ms": m["ms"]}
            for m in metas]


def write_ts(scene_metas, card_meta) -> None:
    GEN_DIR.mkdir(parents=True, exist_ok=True)
    show = {
        "fps": FPS,
        "scenes": scene_list(scene_metas),
        "zodiac": [z.NAME for z in ZODIAC_SCENES],
        "playlists": PLAYLISTS,
        "card": {"path": f"animations/{card_meta['name']}.anim"},
        "styles": text_styles(),
        "timing": textstyle.TIMING,
    }
    (GEN_DIR / "show.ts").write_text(ts_module([
        ("SHOW", show, None, 2, True),
        ("FONTS", font.export_json(LIVE_FONTS), FONT_TS_TYPE, None, False),
    ]))


def write_mockup(scene_metas, card_meta) -> None:
    data = {
        "fps": FPS, "w": W, "h": H,
        "scenes": [{k: m[k] for k in ("name", "title", "ms", "frames", "keyframes", "sheet")} for m in scene_metas],
        "zodiac": [z.NAME for z in ZODIAC_SCENES],
        "festival_scenes": [m.NAME for m in PLAYLIST],
        "playlists": PLAYLISTS,
        "card": {"name": card_meta["name"], "frames": card_meta["frames"], "sheet": card_meta["sheet"]},
        "styles": text_styles(),
        "timing": textstyle.TIMING,
        "fonts": font.export_json(LIVE_FONTS),
        "anim_bytes": sum(m["bytes"] for m in scene_metas) + card_meta["bytes"],
    }
    fill_template(MOCKUP / "template.html", MOCKUP / "index.html", data)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-gif", action="store_true")
    ap.add_argument("--only", default="")
    args = ap.parse_args()
    only = {s for s in args.only.split(",") if s}

    metas = build_scenes(PLAYLIST + ZODIAC_SCENES + [CARD_BG], ANIM_DIR, LUT, None if args.no_gif else PREVIEWS,
                         only=only, keep=(CARD_BG,))
    card_meta = metas.pop()  # CARD_BG is always rendered last
    if only:
        print("  --only: skipped show.ts, icons and mockup (they need every scene)")
        return
    write_ts(metas, card_meta)
    write_icons()
    if (MOCKUP / "template.html").exists():
        write_mockup(metas, card_meta)
        print(f"  wrote {MOCKUP / 'index.html'}")


if __name__ == "__main__":
    main()
