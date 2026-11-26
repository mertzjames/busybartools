"""Countdown and greeting card backdrop: a seamless 4 s loop of a deep night-blue field with faint stars twinkling in
it and a soft red glow along the bottom edge (docs/DECISIONS.md D6). Two big lines of text cover all 16 rows, so
everything here stays dim."""

import math

from busybar.canvas import H, W, add, sec
from busybar.fx import Stars

import jfx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]


def render():
    bg = jfx.sky([(0, (12, 18, 62)), (9, (8, 14, 48)), (15, (28, 12, 40))])
    for x in range(W):  # the red glow along the bottom, strongest in the middle
        k = 0.5 + 0.5 * math.cos(math.pi * (x - 35.5) / 40)
        for y in (14, 15):
            add(bg, x, y, (110, 14, 28), k * (0.3, 0.55)[y - 14])
    stars = Stars(seed=31, n=26, ymax=H, period=LOOP, color=(190, 200, 250), dim=0.04, bright=0.3)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
