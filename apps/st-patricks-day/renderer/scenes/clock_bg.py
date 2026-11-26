"""Clock card backdrop: a seamless 4 s loop of a calm, deep-green night: a shamrock in each corner, a strip of grass
along the bottom, and a few gold glints twinkling along the top and bottom edges (docs/DECISIONS.md D7). The time
(rows 2-14, x 19-53) and the date (rows 4-11) are drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import W, add, put, sec, vgradient
from pfx import GOLD_HI, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, shamrock

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

GLINTS = [(10, 0), (24, 15), (47, 0), (61, 15), (36, 15), (66, 1), (5, 14)]


def render():
    bg = vgradient((4, 20, 12), (8, 34, 18))
    for x in range(W):  # grass along the bottom edge
        h = 1 + (x * 7 % 5 == 0)
        for k in range(h):
            put(bg, x, 15 - k, (18, 70, 30) if k == 0 else (26, 96, 40))
    for cx, cy in ((3, 2), (68, 2)):
        shamrock(bg, cx, cy, 0, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK, alpha=0.8)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for i, (x, y) in enumerate(GLINTS):
            k = max(0.0, math.sin(2 * math.pi * (f / LOOP + i / len(GLINTS))))
            add(img, x, y, GOLD_HI, 0.75 * k ** 3)
        frames.append(img)
    return frames
