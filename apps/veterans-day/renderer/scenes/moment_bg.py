"""The 11:00 moment card backdrop: a seamless 4 s loop, as still as possible: a deep night blue with a single poppy
in each bottom corner and the faintest rose glow along the bottom row, breathing slowly (docs/DECISIONS.md D6, D8).
It sits behind 11TH HOUR, 11TH DAY / 11TH MONTH, ARMISTICE / NOV 11 1918 and THANK YOU / VETERANS."""

import math

from busybar.canvas import W, add, put, sec, vgradient

from vfx import STEM, poppy

NAME = "moment_bg"
TITLE = "11:00 moment backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
# Boxes (x0, y0, x1, y1, inclusive) holding edge art: live text must stay clear (tests/text_parity.py).
ART = [(1, 13, 3, 15), (68, 13, 70, 15)]  # the corner poppies and stems
KEYFRAMES = [(0.0, "11:00 moment backdrop")]


def render():
    bg = vgradient((4, 6, 26), (14, 12, 38))
    for x, y in ((2, 13), (69, 13)):
        for yy in (y + 2, y + 3):
            put(bg, x, yy, STEM, 0.7)
        poppy(bg, x, y + 1, 3, 0.85)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        breathe = 0.5 - 0.5 * math.cos(2 * math.pi * f / LOOP)
        for x in range(10, W - 10):
            add(img, x, 15, (150, 50, 60), (0.06 + 0.1 * breathe) * (1 - abs(x - 36) / 26))
        frames.append(img)
    return frames
