"""Countdown and day card backdrop: a seamless 4 s loop of a warm dusk: a deep-blue sky over a low amber horizon
whose bottom row breathes slowly, and a small poppy in each bottom corner (docs/DECISIONS.md D8). The corners hold
only columns 0-3 and 68-71 below row 12, so even VETERANS DAY (69 px) and FOR YOUR SERVICE clear them."""

import math

from busybar.canvas import H, W, add, put, sec, vgradient

from vfx import STEM, poppy

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
# Boxes (x0, y0, x1, y1, inclusive) holding edge art: live text must stay clear (tests/text_parity.py).
ART = [(1, 13, 3, 15), (68, 13, 70, 15)]  # the corner poppies and stems
KEYFRAMES = [(0.0, "Countdown backdrop")]

POPPIES = [(2, 13), (69, 13)]


def render():
    bg = vgradient((8, 12, 40), (26, 20, 52))
    for y in range(H):  # a low amber horizon, strongest at the bottom center
        for x in range(W):
            d = math.hypot((x - 36) / 38, (H + 2 - y) / 7)
            add(bg, x, y, (170, 100, 60), 0.38 * max(0.0, 1 - d) ** 2)
    for x, y in POPPIES:
        for yy in (y + 2, y + 3):
            put(bg, x, yy, STEM, 0.8)
        poppy(bg, x, y + 1, 3, 0.9)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        breathe = 0.5 + 0.5 * math.cos(2 * math.pi * f / LOOP)
        for x in range(14, 58):  # only the bottom row breathes, so the frames stay small
            add(img, x, 15, (190, 120, 70), 0.12 * breathe * (1 - abs(x - 36) / 22))
        frames.append(img)
    return frames
