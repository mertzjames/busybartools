"""On-the-day card backdrop: a seamless 4 s loop for HAPPY EASTER: the deep violet ground with pastel confetti
drifting down the two edge bands and a few glints, so the greeting in the middle stays clear
(docs/DECISIONS.md D7)."""

import math
import random

from busybar.canvas import H, put, sec, vgradient
from busybar.party import glitter

import efx

NAME = "day_bg"
TITLE = "Holiday backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Holiday backdrop")]
TEXT_GAP = (11, 60)  # text (and its shadow) stays inside these columns, clear of the confetti bands


def render():
    bg = vgradient((22, 10, 44), (40, 18, 62))
    rng = random.Random(14)
    bits = []
    for band in ((0, TEXT_GAP[0]), (TEXT_GAP[1] + 1, 72)):  # outside the widest greeting (SPRING IS, x 12-59)
        for _ in range(9):
            bits.append((rng.uniform(band[0], band[1] - 1), rng.uniform(0, H), rng.choice((1, 2)),
                         rng.uniform(0, 6.28), rng.choice(efx.PASTELS)))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for x0, y0, laps, ph, c in bits:
            y = (y0 + f * laps * H / LOOP) % H
            x = x0 + 0.8 * math.sin(2 * math.pi * f / LOOP + ph)
            bright = (f // 4 + int(ph * 3)) % 2 == 0
            put(img, x, y, c if bright else tuple(int(v * 0.6) for v in c))
        glitter(img, 3, f, n=6, period=LOOP, area=(0, 0, TEXT_GAP[0], H), strength=0.7)
        glitter(img, 4, f, n=6, period=LOOP, area=(TEXT_GAP[1] + 1, 0, 72, H), strength=0.7)
        frames.append(img)
    return frames
