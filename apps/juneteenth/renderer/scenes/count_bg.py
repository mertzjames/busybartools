"""Countdown card backdrop: a seamless 4 s loop: deep navy with a small white star in a burst (the flag's nova) at
each end, whose rays twinkle in turn, and the red horizon rising in the two bottom corners (docs/DECISIONS.md D8). The middle
stays dark, so the countdown reads clearly; the bursts sit outside the widest text (TO JUNETEENTH, 50 px)."""

import math

from busybar.canvas import add, put, sec, vgradient

import jfx
from scenes.clock_bg import horizon

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]
TEXT_GAP = (9, 62)  # text (and its shadow) must stay inside these columns, clear of the bursts

BURST = """
...R...
.R...R.
...S...
R.SSS.R
..S.S..
.R...R.
...R...
"""
CENTERS = ((4, 6), (67, 6))


def burst(img, cx: int, cy: int, f: int, k: int) -> None:
    rows = BURST.strip().splitlines()
    rays = [(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "R"]
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch == "S":
                put(img, cx - 3 + x, cy - 3 + y, jfx.WHITE)
    for i, (x, y) in enumerate(rays):
        # each ray brightens in turn around the burst (a slow chase, steady between steps)
        step = (f // 5 + k * 4) % len(rays)
        a = 1.0 if i == step else 0.55
        put(img, cx - 3 + x, cy - 3 + y, jfx.GOLD_LIGHT, a)


def render():
    bg = vgradient((8, 10, 38), (14, 16, 54))
    horizon(bg, rise=4, edge=8, full=False)
    for cx, cy in CENTERS:
        jfx.glow(bg, cx, cy, 5, (40, 50, 120), 0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for k, (cx, cy) in enumerate(CENTERS):
            burst(img, cx, cy, f, k)
        frames.append(img)
    return frames
