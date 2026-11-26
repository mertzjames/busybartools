"""Dec 7: Advent Candles. Four candles on an evergreen wreath light one by one, and the room glows warmer."""

import math

from busybar.canvas import FPS, add, mix, phase, put, sec, vgradient

from common import PINE, PINE_DARK, glow

NAME = "day07"
TITLE = "Advent Candles"
SECONDS = 8
KEYFRAMES = [(0.5, "Four candles on a wreath"), (1.6, "The first is lit"), (3.6, "Then the second and third"),
             (5.6, "All four burn"), (7.4, "A warm glow")]

CANDLES = [  # x, color, lit at (s)
    (22, (140, 70, 200), 1.2),
    (31, (140, 70, 200), 2.6),
    (40, (240, 120, 180), 4.0),
    (49, (140, 70, 200), 5.4),
]
TOP = 5        # top row of the wax
BASE = 12      # wreath line


def render():
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        lit = sum(1 for _, _, t0 in CANDLES if t >= t0)
        warm = lit / 4
        img = vgradient(mix((8, 6, 24), (40, 18, 14), warm * 0.8), mix((16, 10, 34), (60, 28, 18), warm * 0.8))
        # candles
        for i, (x, c, t0) in enumerate(CANDLES):
            for y in range(TOP, BASE):
                for dx in (-1, 0, 1):
                    shade = 1.15 if dx == -1 else (0.8 if dx == 1 else 1.0)
                    put(img, x + dx, y, tuple(min(255, int(v * shade)) for v in c))
            put(img, x, TOP - 1, (200, 190, 170))  # wick
            if t >= t0:
                age = t - t0
                grow = min(1.0, age / 0.4)
                flick = math.sin(f * 1.3 + i * 2) * 0.5
                # flame: 3 px tall teardrop with a bright core
                put(img, x, TOP - 2, (255, 200, 60), grow)
                put(img, x + (1 if flick > 0.3 else 0), TOP - 3, (255, 150, 40), grow * 0.9)
                put(img, x, TOP - 3, (255, 240, 170), grow)
                put(img, x + (-1 if flick < -0.3 else 0), TOP - 4, (255, 120, 30), grow * 0.6)
                glow(img, x, TOP - 2, 4.5, (255, 160, 60), 0.35 * grow)
                if age < 0.25:  # match spark
                    add(img, x + 1, TOP - 3, (255, 255, 220), 1 - age / 0.25)
        # wreath: an evergreen band with berries and a ribbon
        for x in range(12, 60):
            k = abs(x - 36) / 24
            yt = BASE - 1 + round(k * k * 1.5)
            for y in range(yt, 16):
                put(img, x, y, PINE if (x * 3 + y) % 4 else PINE_DARK)
            if (x - 12) % 2 == 0:
                put(img, x, yt - 1 if (x // 2) % 2 else yt, PINE, 0.9)
        for bx, by in ((16, 13), (26, 14), (35, 13), (45, 14), (55, 13), (20, 15), (51, 15)):
            put(img, bx, by, (230, 30, 40))
        for y in range(BASE + 1, 16):
            put(img, 36, y, (210, 30, 50))
            put(img, 35 + (y % 2), y, (240, 60, 70))
        # all-lit finale: a soft pulse
        if lit == 4:
            add_all = 0.08 * (0.5 + 0.5 * math.sin(f * 0.3)) * phase(f, sec(5.8), sec(6.5))
            for x in range(18, 54):
                add(img, x, 0, (255, 170, 80), add_all)
        frames.append(img)
    return frames
