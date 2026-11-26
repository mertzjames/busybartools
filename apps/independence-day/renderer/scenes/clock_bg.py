"""Clock card backdrop: a seamless 4 s loop of a calm summer night: faint stars along the top, a ribbon of red and
white stripes drifting along the bottom row, and two tiny fireworks popping in the far corners in turn (docs/DECISIONS.md
D6). The time (rows 2-14, columns 22-50) and the date (rows 4-11, columns 8-63) sit over the dark, still middle."""

import math

from busybar.canvas import W, add, put, sec
from busybar.fx import Stars

import jfx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop"), (1.0, "A corner burst"), (3.0, "The other corner")]

BURSTS = ((3, 4, 0, jfx.FW_RED), (68, 5, LOOP // 2, jfx.FW_BLUE))  # x, y, start frame, color


def burst(img, cx, cy, age, color):
    """A tiny 8-ray burst that opens over 0.6 s and fades over 1.4 s."""
    if not 0 <= age < sec(2):
        return
    r = min(3.0, 0.5 + age * 0.35)
    k = 1.0 if age < sec(0.6) else max(0.0, 1 - (age - sec(0.6)) / sec(1.4))
    put(img, cx, cy, jfx.FW_WHITE, 0.6 * k)
    for i in range(8):
        a = 2 * math.pi * i / 8
        add(img, cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8, color, 0.75 * k)


def render():
    bg = jfx.sky([(0, (6, 10, 38)), (15, (16, 22, 66))])
    stars = Stars(seed=17, n=12, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.1, bright=0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for x in range(W):  # stripes drifting right, one stripe = 4 px, a full cycle per loop
            red = ((x - 8 * f // LOOP) // 4) % 2 == 0
            put(img, x, 15, jfx.RED if red else (210, 206, 214), 0.5)
        for x, y, t0, c in BURSTS:
            burst(img, x, y, (f - t0) % LOOP, c)
        frames.append(img)
    return frames
