"""Countdown card backdrop: a seamless 4 s loop of soft snow with holly and twinkling bulbs at both ends.

The app writes the countdown text on top (docs/DECISIONS.md D4), so the middle stays calm. Every moving thing is
periodic in LOOP frames, so the loop never jumps.
"""

import math
import random

from busybar.canvas import put, sec, vgradient

from common import LIGHTS, SNOW

NAME = "card_bg"
TITLE = "Countdown card"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

LEAF = (34, 140, 70)
LEAF_DARK = (20, 92, 46)
BERRY = (236, 36, 52)

# Holly sprig, 7x7, placed in each corner (mirrored on the right)
HOLLY = [
    "GG.....",
    "GGG.g..",
    ".GgGGg.",
    "..gRR..",
    ".GgRRG.",
    "GGG.gGG",
    "GG...GG",
]


def holly(img, x0, y0, flip):
    for dy, row in enumerate(HOLLY):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            c = {"G": LEAF, "g": LEAF_DARK, "R": BERRY}[ch]
            put(img, x0 + (6 - dx if flip else dx), y0 + dy, c)


def render():
    bg = vgradient((8, 14, 44), (18, 34, 70))
    for (x, y, flip) in ((0, 0, False), (65, 0, True), (0, 9, False), (65, 9, True)):
        holly(bg, x, y if not flip else y, flip)
    rng = random.Random(21)
    # snow: each flake falls a whole number of screen heights per loop, so the loop is seamless
    flakes = [(rng.uniform(8, 64), rng.uniform(0, 16), rng.choice((1, 1, 2)), rng.uniform(0, 6.28),
               rng.uniform(0.18, 0.4)) for _ in range(16)]
    bulbs = [(7, 3), (7, 12), (64, 3), (64, 12), (3, 7), (68, 7)]
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for x0, y0, laps, ph, a in flakes:
            y = (y0 + f * 16 * laps / LOOP) % 16
            x = x0 + 1.2 * math.sin(ph + 2 * math.pi * f / LOOP)
            put(img, x, y, SNOW, a)
        for i, (x, y) in enumerate(bulbs):
            k = 0.55 + 0.45 * math.sin(2 * math.pi * (f / LOOP * 2 + i / len(bulbs)))
            put(img, x, y, LIGHTS[i % len(LIGHTS)], k)
        frames.append(img)
    return frames
