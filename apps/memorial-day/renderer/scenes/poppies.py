"""Scene: A Field of Poppies. Under a soft morning sky, a field of red poppies runs to the hills. A slow breeze
passes through it in waves, nearest flowers first, and a single petal drifts across the field."""

import math
import random

from busybar.canvas import FPS, H, W, ease_in_out, mix, phase, put, sec
from mdfx import POPPY, POPPY_DEEP, STEM, poppy, quant, sky

NAME = "poppies"
TITLE = "A Field of Poppies"
SECONDS = 14
KEYFRAMES = [(0.5, "Poppies under a soft morning sky"), (5.0, "A breeze moves through the field"),
             (9.5, "A single petal drifts"), (13.0, "The field at rest")]

HORIZON = 7
DAWN = [(0, (52, 70, 128)), (5, (120, 124, 168)), (7, (196, 160, 156))]
MORNING = [(0, (64, 92, 152)), (5, (138, 150, 190)), (7, (210, 186, 168))]


def slots(rng, n: int, lo: int, hi: int, spacing: float):
    """n columns spread across [lo, hi) with jitter (shuffled slots beat uniform-random x)."""
    xs = [int(lo + (i + 0.5) * spacing + rng.uniform(-spacing / 3, spacing / 3)) for i in range(n)]
    rng.shuffle(xs)
    return xs


def field():
    rng = random.Random(41)
    far = [(x, HORIZON + 1 + rng.randrange(2)) for x in slots(rng, 34, 0, W, W / 34)]
    mid = [(x, 9 + rng.randrange(2)) for x in slots(rng, 14, 0, W, W / 14)]
    near = [(x, 12 + rng.randrange(2)) for x in slots(rng, 7, 3, W - 3, (W - 6) / 7)]
    return far, mid, near


FAR, MID, NEAR = field()


def gust(x: float, t: float) -> float:
    """Strength of the breeze at column x at time t (s): a slow wave travelling left to right."""
    return math.sin(2 * math.pi * (t / 4.0 - x / 40.0))


def render():
    frames = []
    hills = [HORIZON - (1.2 + 1.0 * math.sin(x * 0.09 + 1) + 0.6 * math.sin(x * 0.23)) for x in range(W)]
    for f in range(sec(SECONDS)):
        t = f / FPS
        light = quant(ease_in_out(phase(f, 0, sec(SECONDS))), 24)
        img = sky([(r, mix(a, b, light)) for (r, a), (_, b) in zip(DAWN, MORNING)])
        for x in range(W):  # distant hills, then the field
            for y in range(int(hills[x] + 0.5), HORIZON + 1):
                put(img, x, y, (64, 70, 112))
            for y in range(HORIZON + 1, H):
                put(img, x, y, mix((40, 78, 48), (22, 54, 30), (y - HORIZON) / (H - HORIZON)))
        # grass blades lean with the breeze (whole pixels only)
        for x in range(0, W, 3):
            lean = 1 if gust(x, t) > 0.55 else 0
            put(img, x + lean, 13 + (x * 5) % 2, (70, 120, 64))
        for x, y in FAR:
            poppy(img, x, y, 1, 0.75, POPPY_DEEP)
        for x, y in MID:
            dx = 1 if gust(x, t - 0.3) > 0.5 else 0
            put(img, x, y + 1, STEM)
            poppy(img, x + dx, y, 2)
        for x, y in NEAR:
            dx = 1 if gust(x, t - 0.6) > 0.4 else (-1 if gust(x, t - 0.6) < -0.85 else 0)
            for yy in range(y + 3, H):
                put(img, x + (dx if yy == y + 3 else 0), yy, STEM)
            poppy(img, x + dx, y, 4, halo=(18, 40, 24))
        # one petal drifts across from 7 s to 13 s
        p = phase(f, sec(7.0), sec(13.0))
        if 0 < p < 1:
            px = 6 + p * 60
            py = 4 + 3 * p + 1.2 * math.sin(p * 9)
            put(img, int(px), int(py + 0.5), POPPY, 1 - 0.4 * p)
        frames.append(img)
    return frames
