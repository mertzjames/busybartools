"""Clock card backdrop: a seamless 4 s loop of a calm night sky: a few faint stars along the top and a small cluster
of poppies in each bottom corner that sways in a slow breeze (docs/DECISIONS.md D8). The live time and date are
drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import put, sec, vgradient
from busybar.fx import Stars
from mdfx import STEM, poppy

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

# corner poppies: (x, head row, size, stem phase)
POPPIES = [(2, 13, 3, 0.0), (6, 15, 2, 0.4), (10, 15, 1, 0.7), (69, 13, 3, 0.5), (65, 15, 2, 0.1), (61, 15, 1, 0.8)]


def render():
    bg = vgradient((6, 8, 28), (14, 14, 42))
    stars = Stars(seed=31, n=9, ymax=2, period=LOOP, color=(210, 220, 255), dim=0.08, bright=0.5)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for x, y, size, ph in POPPIES:
            sway = 1 if math.sin(2 * math.pi * (f / LOOP + ph)) > 0.6 and size == 3 else 0
            for yy in range(y + 1, 16):
                put(img, x + (sway if yy < y + 2 else 0), yy, STEM, 0.8)
            poppy(img, x + sway, y, size, 0.9)
        frames.append(img)
    return frames
