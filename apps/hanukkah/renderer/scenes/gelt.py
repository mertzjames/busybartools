"""Scene: a cascade of gelt. Gold (and a few silver) foil coins tumble down, spinning, bounce once and pile up
into a glittering hill. A glint sweeps across the pile at the end.

The pile is precomputed: coins land in order on the current column heights, so every frame can be drawn on its
own and the build stays deterministic.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, H, W, mix, phase, put, sec, vgradient
from busybar.party import glitter
from busybar.party import hash01
from hfx import GOLD, GOLD_HI, GOLD_LO, SILVER, SILVER_LO, coin, flat_coin

NAME = "gelt"
TITLE = "A Cascade of Gelt"
SECONDS = 14
KEYFRAMES = [(1.0, "The first coins tumble down"), (4.0, "Gelt pours in"), (8.0, "A golden hill"),
             (11.4, "A glint across the pile"), (13.0, "Glittering")]

T_RAIN = 8.6
FALL_G = 0.045  # px per frame^2


def plan():
    """[(f_land, x, row, gold, spin_speed, f_start)] for every coin, in landing order."""
    rng = random.Random(23)
    heights = [0] * W
    coins = []
    f = 2
    while f < sec(T_RAIN):
        # of a few random columns, fill the one furthest below a smooth hill: the pile grows as a hill
        cands = [int(min(W - 2, max(1, rng.gauss(36, 15)))) for _ in range(4)]
        x = max(cands, key=lambda c: 8.5 * math.exp(-((c - 36) / 19) ** 2) - max(heights[c - 1:c + 2]))
        row = H - 1 - max(heights[x - 1:x + 2])
        if row < 7:
            f += 1
            continue
        fall_rows = row + 4
        frames_to_fall = int(math.sqrt(2 * fall_rows / FALL_G))
        coins.append((f + frames_to_fall, x, row, rng.random() > 0.15, rng.uniform(0.08, 0.16), f))
        for k in (x - 1, x, x + 1):
            heights[k] = H - row
        f += rng.choice((1, 1, 2, 2, 3)) if f < sec(5) else rng.choice((1, 1, 1, 2))
    return coins


def render():
    bg = vgradient((8, 12, 44), (22, 30, 84))
    coins = plan()
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        landed = [c for c in coins if c[0] <= f]
        # the body of the pile: under the settled coins, packed coin edges
        surface = [H] * W
        for f_land, x, row, gold, spin, f0 in landed:
            if f - f_land >= 6:
                for k in (x - 1, x, x + 1):
                    surface[k] = min(surface[k], row)
        for x in range(1, W - 1):  # no single-column gaps
            surface[x] = min(surface[x], max(surface[x - 1], surface[x + 1]))
        for x in range(W):
            for y in range(surface[x] + 1, H):
                h = hash01(x // 3 + (y % 2) * 7, y, 3)
                col = GOLD_LO if (x + (y % 2) * 2) % 3 == 2 else (GOLD if h > 0.25 else SILVER_LO)
                put(img, x, y, col, 0.85)
        for f_land, x, row, gold, spin, f0 in landed:
            age = f - f_land
            y = row - (2 * math.sin(math.pi * age / 6) if age < 6 else 0)  # one little bounce
            if age < 6:
                coin(img, x, y, spin=0.5 + age / 12, r=1.3, gold=gold)
            else:
                flat_coin(img, x, row, gold=gold)
        for f_land, x, row, gold, spin, f0 in coins:
            if not (f0 <= f < f_land):
                continue
            age = f - f0
            y = -4 + 0.5 * FALL_G * age * age
            coin(img, x + 0.8 * math.sin(age * 0.2 + x), y, spin=age * spin, r=1.6, gold=gold)
        # a glint sweeps across the pile
        g = phase(t, 10.6, 12.0)
        if 0 < g < 1:
            gx = -6 + 84 * g
            for f_land, x, row, gold, spin, f0 in landed:
                if abs(x - gx + (row - 12) * 0.7) < 1.6:
                    put(img, x, row, mix(GOLD_HI, (255, 255, 255), 0.6))
        glitter(img, 61, f, n=16, period=50, area=(6, 8, 66, 16), colors=(GOLD_HI, (255, 255, 255), SILVER),
                strength=0.9 * phase(t, 4.0, 9.0))
        frames.append(img)
    return frames
