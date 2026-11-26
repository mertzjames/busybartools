"""Red Lanterns Rising: a full moon over curled rooftops; paper sky lanterns drift up from behind the halls, then
three red palace lanterns are lowered into the sky, glowing (docs/DECISIONS.md D2).
"""

from __future__ import annotations

import math
import random

from busybar.canvas import W, ease_in_out, phase, put, sec, vgradient
from busybar.fx import puff

import lnyfx as fx

NAME = "lanterns"
TITLE = "Red Lanterns Rising"
SECONDS = 12
KEYFRAMES = [(0.5, "A full moon over the rooftops"), (3.0, "The first sky lanterns rise"),
             (6.5, "The sky fills with lanterns"), (9.5, "A palace lantern is lowered"),
             (11.5, "Three red lanterns glow")]

N = sec(SECONDS)


def make_sky_lanterns():
    rng = random.Random(41)
    out = []
    for i in range(22):
        t0 = rng.uniform(0.6, 8.5) if i else 1.0
        out.append({
            "t0": sec(t0), "x": rng.uniform(3, W - 5), "speed": rng.uniform(0.09, 0.16),
            "amp": rng.uniform(0.6, 1.6), "w": rng.uniform(0.04, 0.09), "seed": i,
        })
    return out


def render():
    bg = vgradient(fx.NIGHT_TOP, (52, 16, 44))
    rng = random.Random(7)
    stars = [(rng.randrange(W), rng.randrange(0, 9), rng.random()) for _ in range(26)]
    sky = make_sky_lanterns()
    frames = []
    for f in range(N):
        img = bg.copy()
        for i, (x, y, ph) in enumerate(stars):
            k = 0.35 + 0.35 * math.sin(f * 0.15 + ph * 6.28)
            put(img, x, y, (200, 200, 255), k)
        # the full moon of the Lantern Festival, with a soft halo
        puff(img, 61, 3.5, 3.6, (90, 70, 60), 0.35)
        puff(img, 61, 3.5, 2.2, (255, 244, 210))
        put(img, 60, 3, (235, 220, 190))
        # sky lanterns rise from behind the rooftops
        for s in sky:
            age = f - s["t0"]
            if age < 0:
                continue
            y = 12 - age * s["speed"]
            if y < -4:
                continue
            x = s["x"] + s["amp"] * math.sin(age * s["w"] + s["seed"])
            a = min(1.0, (y + 4) / 6) * (0.6 + 0.4 * min(1.0, y / 8 + 0.4))
            fx.sky_lantern(img, x, y, f, s["seed"], alpha=max(0.0, a))
        fx.rooftops(img, base=12, seed=5)
        # palace lanterns are lowered on cords
        for cx, t0, size, length in ((36, 8.0, 2, 3), (20, 9.2, 1, 2), (52, 9.6, 1, 2)):
            p = ease_in_out(phase(f, sec(t0), sec(t0 + 1.6)))
            if p <= 0:
                continue
            top = int(round(-12 + (12 + 0) * p))
            sway = 0.6 * math.sin((f - sec(t0)) * 0.12) if p >= 1 else 0
            fx.lantern(img, cx + sway, top, f, size=size, string=length, seed=cx)
            # the cord above the lantern back to the top edge
            for y in range(0, max(0, top)):
                put(img, cx + sway, y, (140, 90, 60), 0.7)
        frames.append(img)
    return frames
