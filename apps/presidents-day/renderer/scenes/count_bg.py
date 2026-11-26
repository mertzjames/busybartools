"""Countdown and greeting card backdrop: a seamless 4 s loop of a deep navy field with faint stars twinkling in it and
a soft red glow along the bottom, like a flag's canton at night (docs/DECISIONS.md D7). The stars stay dim, so the
gold and red-white words read clearly over them."""

import math

from busybar.canvas import H, W, add, sec
from busybar.fx import Stars

import pfx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]


def render():
    bg = pfx.sky([(0, (14, 22, 70)), (9, (10, 16, 54)), (15, (34, 14, 44))])
    for x in range(W):  # the red glow along the bottom, strongest in the middle
        k = 0.5 + 0.5 * math.cos(math.pi * (x - 35.5) / 40)
        for y in (13, 14, 15):
            add(bg, x, y, (120, 16, 30), k * (0.25, 0.45, 0.7)[y - 13])
    stars = Stars(seed=31, n=26, ymax=H, period=LOOP, color=(190, 200, 250), dim=0.04, bright=0.3)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
