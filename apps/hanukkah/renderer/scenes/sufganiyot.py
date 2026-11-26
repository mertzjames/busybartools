"""Scene: sufganiyot. Three jelly doughnuts sit on a silver tray; a sifter passes over them shaking powdered sugar,
which settles where it lands. Then each one gets its jelly, with a little puff, and the sugar sparkles.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, ease_in_out, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.party import glitter
from hfx import SILVER, SILVER_LO, WHITE

NAME = "sufganiyot"
TITLE = "Sufganiyot"
SECONDS = 14
KEYFRAMES = [(0.8, "Three sufganiyot on a tray"), (3.6, "Powdered sugar from the sifter"),
             (8.4, "Sugared all over"), (10.6, "Jelly in each one"), (12.8, "Sweet and sparkling")]

DOUGH = (206, 124, 52)
DOUGH_HI = (236, 164, 80)
DOUGH_LO = (150, 80, 34)
BAND = (244, 214, 150)  # the pale ring around the middle
JELLY = (226, 34, 64)
SUGAR = (250, 250, 255)
NUTS = [18, 36, 54]
CY, RX, RY = 9.4, 6.4, 4.6
BASE = 13
T_SIFT0, T_SIFT1 = 1.4, 8.6
T_JELLY = 9.6


def top(x: float) -> float | None:
    """Row of the doughnut surface at column x, or None over the tray."""
    for cx in NUTS:
        u = (x - cx) / RX
        if abs(u) < 1:
            return CY - RY * math.sqrt(1 - u * u)
    return None


def sifter_x(t: float) -> float:
    return lerp(-8, 80, ease_in_out(phase(t, T_SIFT0 - 1.0, T_SIFT1 + 1.0)))


def grains():
    rng = random.Random(77)
    out = []
    f = sec(T_SIFT0)
    while f < sec(T_SIFT1):
        for _ in range(2):
            t = f / FPS
            x = sifter_x(t) + rng.uniform(-3, 3)
            y_land = top(x)
            if y_land is None:
                y_land = 14.0
            else:
                y_land = math.floor(y_land + 0.5) + (rng.random() < 0.35)
            out.append((f, x, y_land, rng.uniform(0.35, 0.6)))
        f += 1
    return out


def doughnut(img, cx: float, puff: float, sugar_px) -> None:
    rx, ry = RX + puff, RY + puff
    for y in range(int(CY - ry) - 1, BASE + 1):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = ((x - cx) / (rx + 0.3)) ** 2 + ((y - CY) / (ry + 0.3)) ** 2
            if d > 1:
                continue
            c = DOUGH
            if y == int(CY + 2):
                c = BAND
            elif y > CY + 2:
                c = DOUGH_LO if d > 0.55 or y == BASE else DOUGH
            elif d > 0.72 and x > cx:
                c = DOUGH_LO
            elif d < 0.4 and x < cx and y < CY:
                c = DOUGH_HI
            put(img, x, y, c)


def render():
    bg = vgradient((10, 14, 46), (26, 30, 80))
    for x in range(72):
        put(bg, x, 14, SILVER)
        put(bg, x, 15, SILVER_LO)
    gs = grains()
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        glitter(img, 51, f, n=10, period=60, ymax=6, colors=(SILVER, (150, 180, 255)), strength=0.5)
        for k, cx in enumerate(NUTS):
            tj = T_JELLY + k * 0.7
            puff = 0.6 * math.sin(math.pi * phase(t, tj, tj + 0.4))
            doughnut(img, cx, puff, None)
        # sugar: falling grains, and the ones that have landed
        for f0, x, y_land, v in gs:
            age = f - f0
            if age < 0:
                continue
            y = 4 + age * v * 1.6
            if y >= y_land:
                put(img, x, y_land, SUGAR, 0.9)
            else:
                put(img, x, y, SUGAR, 0.75)
        # jelly peeking out of each side, piped in one by one
        for k, cx in enumerate(NUTS):
            tj = T_JELLY + k * 0.7
            if t >= tj:
                a = ease_out(phase(t, tj, tj + 0.3))
                for dx, dy, col in ((-1, 0, JELLY), (0, 0, JELLY), (-1, 1, (180, 20, 50)), (0, 1, JELLY),
                                    (-1, -1, (255, 110, 130))):
                    put(img, cx + RX + dx, CY + dy, col, a)
                if t < tj + 0.5:  # a little squirt
                    put(img, cx + RX + 1 + 3 * phase(t, tj, tj + 0.5), CY, JELLY, 1 - phase(t, tj, tj + 0.5))
        # the sifter: a silver drum with a mesh bottom, shaking as it goes
        sx = sifter_x(t)
        if T_SIFT0 - 1.0 <= t <= T_SIFT1 + 1.0:
            jig = 1 if (f // 2) % 2 else 0
            x0 = int(sx) - 4 + jig
            for dx in range(9):
                put(img, x0 + dx, 1, SILVER)
                put(img, x0 + dx, 2, mix(SILVER, SILVER_LO, dx / 8))
                put(img, x0 + dx, 3, (200, 206, 220) if dx % 2 else SILVER_LO)
            put(img, x0 - 1, 1, WHITE)
            for i in range(1, 5):  # handle
                put(img, x0 + 8 + i, 1 - i * 0.5, (150, 100, 60))
        if t > T_SIFT1:
            glitter(img, 52, f, n=14, period=40, area=(10, 6, 62, 12), colors=(WHITE, (255, 230, 240)),
                    strength=0.9 * phase(t, T_SIFT1, T_SIFT1 + 1.0))
        frames.append(img)
    return frames
