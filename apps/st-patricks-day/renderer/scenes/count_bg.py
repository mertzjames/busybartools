"""Countdown card backdrop: a seamless 4 s loop on deep green: a small rainbow arcs out of the top-left corner,
a shamrock sits in the top-right one, and gold coins glint along the bottom corners (docs/DECISIONS.md D7). The
text ("111 DAYS", x 13-58 rows 1-8; "TO ST. PATRICK'S", x 7-64 rows 10-15) keeps the middle clear."""

import math

from busybar.canvas import add, put, sec, vgradient
from pfx import GOLD, GOLD_DK, GOLD_HI, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, rainbow, shamrock

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

COINS = [(1, 14), (3, 13), (2, 15), (4, 15), (67, 15), (69, 14), (70, 15), (68, 13)]


def render():
    bg = vgradient((4, 22, 12), (8, 36, 18))
    rainbow(bg, -2, 9, 11, 9, alpha=0.75, band=0.85)
    shamrock(bg, 67, 4, 1, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK, alpha=0.9)
    for i, (x, y) in enumerate(COINS):
        put(bg, x, y, GOLD if i % 2 else GOLD_DK)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for i, (x, y) in enumerate(COINS):
            k = max(0.0, math.sin(2 * math.pi * (f / LOOP + i * 0.37)))
            add(img, x, y, GOLD_HI, 0.8 * k ** 4)
        frames.append(img)
    return frames
