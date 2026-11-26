"""Clock card backdrop: a seamless 4 s loop of a calm navy night: a few twinkling stars along the top and a slow
ribbon of red and white stripes along the bottom row (docs/DECISIONS.md D7). The time (rows 2-14) and the date
(rows 4-11) are drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import W, put, sec
from busybar.fx import Stars

import pfx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]


def render():
    bg = pfx.sky([(0, (6, 10, 40)), (15, (16, 24, 72))])
    stars = Stars(seed=17, n=12, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.1, bright=0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for x in range(W):  # stripes drifting right, one stripe = 4 px, a full cycle per loop
            red = ((x - 8 * f // LOOP) // 4) % 2 == 0
            put(img, x, 15, pfx.RED if red else (210, 206, 214), 0.5)
        for x in (2, 69):  # two gold stars in the corners breathe slowly
            k = 0.6 + 0.4 * math.cos(2 * math.pi * (f / LOOP + (x > 30) * 0.5))
            put(img, x, 1, pfx.GOLD, k)
        frames.append(img)
    return frames
