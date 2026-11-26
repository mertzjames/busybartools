"""Clock/date card backdrop: a seamless 4 s loop of a twinkling light string, gentle snowfall and two little
snowy pines on a snowbank (docs/DECISIONS.md D7).

The live time and date are drawn ON TOP of this by the app, so the middle stays calm: the light string keeps to
rows 0-1, the snowbank to rows 14-15, and the snow in the text band is faint. Everything is periodic in LOOP
frames so the loop never jumps.
"""

from busybar.canvas import add, sec, vgradient
from xfx import Snow, draw_tree, light_string, snow_ground, tree_spots, BULBS

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)  # 60 frames
KEYFRAMES = [(0.0, "Clock backdrop")]

# Clock layout shared with the app and mockup (exported by build.py): candy-cane time, gold-and-holly date.
LAYOUT = {
    "time": {"font": "clock", "y": 2, "top": [255, 255, 255], "bottom": [176, 206, 240], "shadow": [176, 18, 30]},
    "date": {"font": "big", "y": 4, "top": [255, 236, 150], "bottom": [236, 160, 40], "shadow": [20, 110, 44]},
    "time_ms": 4500,
    "date_ms": 3500,
}

PINES = ((4, 8), (67, 8))  # (center x, top row)


def render():
    bg = vgradient((4, 8, 26), (10, 22, 34))
    snow_ground(bg, 15, seed=5)
    for cx, top in PINES:
        draw_tree(bg, cx, top, height=6, trunk=1, snowy=True)
    snow = Snow(seed=7, n=20, period=LOOP, laps=(1, 2), bright=(0.2, 0.55))
    bulbs = [s for cx, top in PINES for s in tree_spots(cx, top, 6, 3, seed=cx)]
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        # faint in the middle band, where the text goes
        snow.draw(img, f, alpha=1.0, skip=lambda x, y: 17 <= x <= 55 and 2 <= y <= 14 and (x + y + f) % 3)
        # scalloped light string across the top: four swags
        for k in range(4):
            light_string(img, f, k * 18, k * 18 + 18, -1, 2.0, LOOP, spacing=3, wire=(30, 90, 50), phase0=k * 2,
                         drop=0)
        for i, (x, y) in enumerate(bulbs):
            on = (f // 10 + i) % 3 != 0
            add(img, x, y, BULBS[i % len(BULBS)], 0.9 if on else 0.3)
        frames.append(img)
    return frames
