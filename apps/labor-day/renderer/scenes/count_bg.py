"""Countdown and greeting card backdrop: a seamless 4 s loop of a late-summer night: deep indigo with faint stars and
a warm ember glow along the bottom, like the last light of a summer evening (docs/DECISIONS.md D7). Everything stays
dim, because two big lines of text cover all 16 rows."""

import math

from busybar.canvas import H, W, add, sec
from busybar.fx import Stars

import lfx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]


def render():
    bg = lfx.sky([(0, (10, 12, 48)), (9, (14, 14, 52)), (15, (40, 18, 40))])
    for x in range(W):  # the ember glow along the bottom, strongest in the middle
        k = 0.5 + 0.5 * math.cos(math.pi * (x - 35.5) / 40)
        for y in (13, 14, 15):
            add(bg, x, y, (130, 52, 16), k * (0.2, 0.4, 0.65)[y - 13])
    stars = Stars(seed=29, n=24, ymax=H - 3, period=LOOP, color=(200, 206, 250), dim=0.04, bright=0.3)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
