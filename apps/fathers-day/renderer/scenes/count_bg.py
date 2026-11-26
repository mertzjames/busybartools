"""Countdown and greeting card backdrop: a seamless 4 s loop of a summer dusk: a deep-blue sky that warms to a low
sunset band, the far shore of a lake as a lit green line, and a few stars twinkling at the top (docs/DECISIONS.md
D7). The sunset band sits low and dim, so the cream and orange words read clearly over the whole card."""

import math

from busybar.canvas import W, add, put, sec
from busybar.fx import Stars

import ffx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]


def render():
    bg = ffx.sky([(0, (8, 14, 48)), (9, (16, 26, 74)), (13, (60, 34, 70)), (15, (110, 50, 46))])
    for x in range(W):  # the far shore: a lit dark-green ridge on row 15, a little higher in two places
        h = 1 + (1 if 8 <= x <= 20 or 50 <= x <= 58 else 0)
        for y in range(16 - h, 16):
            put(bg, x, y, (20, 58, 40) if (x + y) % 3 else (26, 70, 46))
    for x in range(W):  # a soft orange glow along the horizon, strongest left of center (the set sun)
        k = 0.5 + 0.5 * math.cos(math.pi * (x - 30) / 44)
        add(bg, x, 13, (110, 50, 20), 0.35 * k)
    stars = Stars(seed=33, n=18, ymax=6, period=LOOP, color=(200, 210, 250), dim=0.05, bright=0.35)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
