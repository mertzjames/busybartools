"""Clock/date card backdrop: a seamless 4 s loop of floating candles and drifting sparkles.

The live time and date are drawn ON TOP of this by the app (docs/DECISIONS.md D7, D10), so the
center stays calm. Everything here is periodic in LOOP frames so the loop never jumps.
"""

import math

from busybar.canvas import FPS, add, blit, put, sec, vgradient
from busybar.fx import Stars
from sprites import CANDLE

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)  # 60 frames
KEYFRAMES = [(0.0, "Clock backdrop")]

# Clock layout shared with the app and mockup (exported by build.py)
LAYOUT = {
    "time": {"font": "clock", "y": 2, "top": [255, 234, 140], "bottom": [235, 140, 25], "shadow": [110, 45, 0]},
    "date": {"font": "big", "y": 4, "top": [255, 244, 214], "bottom": [226, 176, 96], "shadow": [80, 40, 10]},
    "time_ms": 4500,
    "date_ms": 3500,
}


def render():
    bg = vgradient((12, 5, 26), (28, 10, 38))
    stars = Stars(seed=10, n=14, period=LOOP, dim=0.05, bright=0.35)
    # drifting motes: x, start y, color; each rises exactly 16 px per loop -> seamless
    motes = [(9, 3, (255, 220, 120)), (14, 11, (255, 240, 200)), (58, 7, (255, 220, 120)), (63, 14, (200, 220, 255))]
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        # keep stars out of the text band
        stars.draw(img, f)
        for side, (cx, ph) in enumerate(((3, 0.0), (67, math.pi))):
            cy = 5 + round(1.4 * math.sin(2 * math.pi * f / LOOP + ph))
            blit(img, CANDLE.img((f // 5 + side) % 4), cx - 1, cy)
            add(img, cx, cy, (255, 180, 60), 0.35)
            add(img, cx - 1, cy, (255, 160, 40), 0.12)
            add(img, cx + 1, cy, (255, 160, 40), 0.12)
        for x, y0, c in motes:
            y = (y0 - f * 16 / LOOP) % 16
            a = 0.35 + 0.35 * math.sin(2 * math.pi * (f / LOOP * 2 + x / 10))
            add(img, x + round(math.sin(2 * math.pi * f / LOOP + x)), y, c, max(0.0, a))
        frames.append(img)
    return frames
