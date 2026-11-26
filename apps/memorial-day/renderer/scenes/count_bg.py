"""Countdown and day card backdrop: a seamless 4 s loop of a quiet dusk: a deep-blue sky over a low rose horizon
that breathes slowly, and a poppy in each bottom corner (docs/DECISIONS.md D8). The text band stays dark, so the
pale words read clearly."""

import math

from busybar.canvas import H, W, add, put, sec, vgradient
from mdfx import STEM, poppy

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

POPPIES = [(2, 13, 3, 0.0), (69, 13, 3, 0.3)]


def render():
    bg = vgradient((6, 10, 34), (22, 18, 50))
    for y in range(H):  # a low rose horizon, strongest at the bottom center
        for x in range(W):
            d = math.hypot((x - 36) / 36, (H + 2 - y) / 7)
            add(bg, x, y, (150, 70, 80), 0.4 * max(0.0, 1 - d) ** 2)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        breathe = 0.5 + 0.5 * math.cos(2 * math.pi * f / LOOP)
        for x in range(14, 58):  # the breathing: only the bottom row, so the frames stay small
            add(img, x, 15, (170, 90, 90), 0.12 * breathe * (1 - abs(x - 36) / 22))
        for x, y, size, ph in POPPIES:
            sway = 1 if math.sin(2 * math.pi * (f / LOOP + ph)) > 0.6 and size == 3 else 0
            for yy in range(y + 1, 16):
                put(img, x + (sway if yy < y + 2 else 0), yy, STEM, 0.8)
            poppy(img, x + sway, y, size, 0.9)
        frames.append(img)
    return frames
