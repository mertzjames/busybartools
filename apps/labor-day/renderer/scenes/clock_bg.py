"""Clock card backdrop: a seamless 4 s loop of a calm night over a dim city. A few stars twinkle along the top, and
at the right edge a tower crane's red warning light blinks slowly (docs/DECISIONS.md D7). The time (rows 2-14) and the
date (rows 4-11) are drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import H, W, add, put, sec
from busybar.fx import Stars

import lfx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

CITY = (26, 28, 64)


def render():
    bg = lfx.sky([(0, (4, 6, 30)), (10, (10, 12, 44)), (15, (30, 18, 52))])
    heights = [1 + ((x * 7) % 5 == 0) + ((x // 5) % 3 == 1) for x in range(W)]
    for x in range(W):  # a low, dim skyline along the bottom
        for y in range(H - heights[x], H):
            put(bg, x, y, CITY)
    for y in range(6, H):  # a crane at the right edge, in a lit dark gold
        put(bg, 69, y, (78, 64, 30))
    for x in range(66, 72):
        put(bg, x, 6, (78, 64, 30))
    stars = Stars(seed=19, n=12, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.1, bright=0.55)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        k = 0.5 + 0.5 * math.cos(2 * math.pi * f / LOOP)  # one slow blink per loop
        put(img, 69, 5, (255, 40, 40), 0.35 + 0.65 * k)
        add(img, 69, 4, (255, 40, 40), 0.25 * k)
        frames.append(img)
    return frames
