"""Scene: Bats Across the Moon. A big full moon rises over a bare tree on a hill. Bats pour out of the tree's hollow
and stream across the moon in a wavy ribbon, then one big bat swoops close past it, and a few circle the moon to
the end."""

import math
import random

from busybar.canvas import FPS, H, W, blit, put, sec
from hfx import NIGHT_MID, NIGHT_TOP, frame_t, full_moon, gradient, in_moon, stars
from sprites import BAT, BIG_BAT

NAME = "bats"
TITLE = "Bats Across the Moon"
SECONDS = 14
KEYFRAMES = [(0.8, "A full moon over a bare tree"), (3.0, "Bats pour out of the tree"),
             (5.5, "A ribbon of bats crosses the moon"), (9.4, "A big bat swoops close"),
             (12.5, "Bats circle the moon")]

MOON = (40.0, 7.5, 6.5)
HOLLOW = (8, 8)
STREAM = [(1.2 + i * 0.42, i) for i in range(12)]  # (launch second, index)
BIG = (8.4, 11.0)
ORBIT_AT = 10.6


def stream_pos(t0: float, i: int, t: float):
    age = t - t0
    if age < 0:
        return None
    rng = random.Random(100 + i)
    speed = rng.uniform(12, 16)
    amp = rng.uniform(1.0, 2.6)
    base = 4 + 4 * math.sin(i * 1.7)
    x = HOLLOW[0] + age * speed
    y = HOLLOW[1] + (base - HOLLOW[1]) * min(1.0, age / 0.8) + amp * math.sin(age * 4 + i)
    if x > W + 4:
        return None
    return x, y


def render():
    bg = gradient([(0, NIGHT_TOP), (9, NIGHT_MID), (15, (70, 24, 84))])
    full_moon(bg, *MOON, halo=0.8)
    for x in range(W):  # the hill
        top = int(math.floor(13.6 + 1.4 * math.sin(x * 0.09 + 1.0) + 0.5))
        for y in range(top, H):
            put(bg, x, y, (40, 20, 56))
        put(bg, x, top, (80, 54, 106))
    tree = (96, 70, 104)
    for y in range(4, 15):  # trunk, two pixels wide, with a dark hollow
        put(bg, 7, y, tree)
        put(bg, 8, y, (76, 54, 84))
    for x, y in ((6, 4), (5, 3), (4, 2), (9, 5), (10, 4), (11, 3), (12, 3), (11, 2), (6, 7), (5, 6), (4, 6),
                 (3, 5), (9, 9), (10, 8), (11, 8), (12, 7), (13, 7), (7, 3), (7, 2), (8, 1)):
        put(bg, x, y, tree)
    put(bg, 8, 8, (30, 10, 30))
    put(bg, 8, 9, (30, 10, 30))
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 21, 18, f, ymax=12, avoid=lambda x, y: in_moon(x, y, *MOON) or x < 14)
        for t0, i in STREAM:
            p = stream_pos(t0, i, t)
            if p:
                blit(img, BAT.img((f // 2 + i) % len(BAT)), p[0] - 3, p[1] - 2)
        if t >= ORBIT_AT:  # three bats circle the moon
            for j in range(3):
                ang = 2 * math.pi * ((t - ORBIT_AT) / 3.2 + j / 3)
                a = min(1.0, (t - ORBIT_AT) / 0.6)
                x = MOON[0] + math.cos(ang) * (MOON[2] + 5) * (0.4 + 0.6 * a) - 3
                y = MOON[1] + math.sin(ang) * (MOON[2] - 0.5) - 2
                blit(img, BAT.img((f // 2 + j) % len(BAT), flip=math.sin(ang) < 0), x, y)
        if BIG[0] <= t < BIG[1]:  # the big bat swoops right to left across the moon
            u = (t - BIG[0]) / (BIG[1] - BIG[0])
            x = W + 2 - u * (W + 20)
            y = 6 - 4 * math.sin(math.pi * u) + 2 * u
            blit(img, BIG_BAT.img((f // 2) % len(BIG_BAT), flip=True), x, y)
        frames.append(img)
    return frames
