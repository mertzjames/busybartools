"""Text styles shared by the baked scene captions and the live card text (docs/DECISIONS.md D7).

Colors here are linear (before the tone curve). build.py tone-maps them for the app and the mockup, so the bar draws
live text in exactly the colors the scenes bake.
"""

from __future__ import annotations

from busybar.canvas import W
from busybar.font import draw_text, text_width

SHADOW = [150, 18, 24]
SHADOW_DEEP = [110, 10, 18]

STYLES = {
    # clock card
    "time": {"font": "clock", "y": 2, "top": [255, 240, 170], "bottom": [245, 168, 40], "shadow": SHADOW},
    "date": {"font": "big", "y": 4, "top": [255, 246, 220], "bottom": [255, 196, 90], "shadow": SHADOW},
    # countdown: "18 DAYS" over "TO LUNAR NEW YEAR"
    "head": {"font": "big", "y": 1, "top": [255, 240, 170], "bottom": [255, 180, 40], "shadow": SHADOW},
    "sub": {"font": "tiny", "y": 10, "top": [255, 232, 196], "bottom": [245, 180, 110], "shadow": SHADOW_DEEP},
    # festival: "YEAR OF THE" over "GOAT"
    "small": {"font": "tiny", "y": 1, "top": [255, 232, 196], "bottom": [245, 180, 110], "shadow": SHADOW_DEEP},
    "name": {"font": "big", "y": 8, "top": [255, 240, 170], "bottom": [255, 180, 40], "shadow": SHADOW},
    # two big lines: "HAPPY" over "NEW YEAR"
    "top": {"font": "big", "y": 0, "top": [255, 240, 170], "bottom": [255, 180, 40], "shadow": SHADOW},
    "bot": {"font": "big", "y": 8, "top": [255, 246, 220], "bottom": [255, 196, 90], "shadow": SHADOW},
}


def draw(img, text: str, spec: dict, x: int | None = None, alpha: float = 1.0, reveal: int | None = None,
         y: int | None = None) -> None:
    """Draw text the way the app does (centered on the screen unless x is given)."""
    tx = (W - text_width(text, spec["font"])) // 2 if x is None else x
    draw_text(img, text, tx, spec["y"] if y is None else y, None, font=spec["font"],
              gradient=(tuple(spec["top"]), tuple(spec["bottom"])), shadow=tuple(spec["shadow"]), alpha=alpha,
              reveal=reveal)


# Card page durations (ms), exported to the app and the mockup with the styles.
TIMING = {
    "time": 4500, "date": 3500,  # clock card
    "count": 6500,  # "18 DAYS" / "TO LUNAR NEW YEAR"
    "animal": 4500, "greeting": 3500, "wish": 3000,  # festival: YEAR OF THE / GOAT, HAPPY / NEW YEAR, GONG XI / FA CAI
    "fallback": 5000,  # HAPPY / NEW YEAR when the date table has no entry
}
