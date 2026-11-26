"""Clock card backdrop: a seamless 4 s loop of a calm summer night: a deep-blue sky over a dark lawn line along the
bottom row, with a few fireflies blinking softly near the edges (docs/DECISIONS.md D7). The time (rows 2-14) and the
date (rows 4-11) are drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import W, add, put, sec
from busybar.fx import Stars

import ffx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

# fireflies: (x, y, phase offset in loops); kept to the edges so they never sit under a digit
FLIES = [(2, 9, 0.0), (5, 13, 0.35), (66, 8, 0.6), (69, 12, 0.15), (63, 14, 0.8), (8, 5, 0.5)]


def render():
    bg = ffx.sky([(0, (6, 10, 36)), (12, (14, 26, 70)), (15, (20, 40, 80))])
    for x in range(W):  # the lawn along the bottom row, a lit deep green
        put(bg, x, 15, (18, 60, 34) if (x * 7) % 5 else (24, 74, 40))
    stars = Stars(seed=21, n=10, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.08, bright=0.5)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for x, y, ph in FLIES:
            k = max(0.0, math.sin(2 * math.pi * (f / LOOP + ph)))
            k = round(k * 6) / 6  # quantized: a few steps keep the file small
            if k > 0:
                add(img, x, y, (200, 255, 90), 0.9 * k)
                if k > 0.6:
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        add(img, x + dx, y + dy, (120, 200, 40), 0.25 * k)
        frames.append(img)
    return frames
