"""Scene: A Dove over the City. Before sunrise a white dove carrying an olive sprig flies across a sleeping city.
Windows go dark one by one as the sky lightens. The dove circles back, settles on a rooftop, and the word PEACE
appears."""

import math
import random

from busybar.canvas import FPS, H, W, blit, ease_in_out, ease_out, lerp, phase, put, sec
from busybar.fx import Stars
from mfx import caption, sky, sun
from sprites import DOVE

NAME = "dove"
TITLE = "A Dove over the City"
SECONDS = 14
KEYFRAMES = [(1.5, "A dove crosses the sleeping city"), (4.5, "It passes the first light"),
             (8.0, "It circles back as the windows go dark"), (12.5, "PEACE")]

# (x, width, height) of each building, left to right; the dove lands on the tower at PERCH
BUILDINGS = [(0, 5, 5), (5, 4, 7), (9, 7, 10), (16, 5, 6), (21, 6, 8), (27, 4, 5), (31, 8, 4), (39, 5, 6),
             (44, 6, 7), (50, 4, 5), (54, 7, 6), (61, 5, 5), (66, 6, 6)]
WALL = (16, 14, 36)
EDGE = (34, 30, 66)
ROOF_LIGHT = (255, 170, 90)
WINDOW = (255, 204, 120)
PERCH_X, PERCH_TOWER = 9, 2  # the dove's x on the tower BUILDINGS[2]
SUN_X = 28


def city(seed: int = 5):
    """Building pixels and their windows: [(x, y, off_time_seconds)]."""
    rng = random.Random(seed)
    windows = []
    for bx, w, h in BUILDINGS:
        for y in range(H - h + 1, H - 1, 2):
            for x in range(bx + 1, bx + w - 1, 2):
                if rng.random() < 0.45:
                    windows.append((x, y, rng.uniform(4.0, 13.0) if rng.random() < 0.8 else 99))
    return windows


def draw_city(img, f: int, windows, light: float) -> None:
    t = f / FPS
    for bx, w, h in BUILDINGS:
        for y in range(H - h, H):
            for x in range(bx, bx + w):
                put(img, x, y, EDGE if (y == H - h or x == bx) else WALL)
        for x in range(bx, bx + w):  # rooftops catch the first light
            put(img, x, H - h, ROOF_LIGHT, light * max(0.2, 1 - abs(x - SUN_X) / 40))
    for x, y, off in windows:
        if t < off:
            put(img, x, y, WINDOW, 0.85)
        elif t < off + 0.6:
            put(img, x, y, WINDOW, 0.85 * (1 - (t - off) / 0.6))


def dove_at(f: int):
    """(x, y, frame, flip) of the dove at frame f."""
    t = f / FPS
    flap = (0, 1, 2, 1)[(f // 3) % 4]
    if t < 6.0:  # left to right, high, a gentle wave
        p = t / 6.0
        return lerp(-12, 78, p), 3.2 + 1.3 * math.sin(p * 2 * math.pi * 1.5), flap, False
    if t < 10.0:  # back from the right, gliding down to the tower
        p = (t - 6.0) / 4.0
        e = ease_out(p)
        x = lerp(78, PERCH_X, e)
        top = H - BUILDINGS[PERCH_TOWER][2] - 6  # the sprite's feet row (5) stands on the roof
        y = lerp(2.5, top, ease_in_out(p)) - 1.5 * math.sin(p * math.pi)
        fr = 1 if 0.25 < p < 0.75 else flap  # glide in the middle of the descent
        if p > 0.9:
            fr = 0
        return x, y, fr, True
    top = H - BUILDINGS[PERCH_TOWER][2] - 6
    return PERCH_X, top, 3, True


def render():
    stars = Stars(seed=17, n=18, ymax=7, period=FPS * 4, color=(220, 226, 255), dim=0.1, bright=0.65)
    windows = city()
    frames = []
    for f in range(sec(SECONDS)):
        p = ease_in_out(phase(f, 0, sec(SECONDS)))
        img = sky(0.15 + 0.8 * p, horizon=H - 1)
        stars.draw(img, f, alpha=1 - phase(f, sec(2), sec(9)))
        sun(img, SUN_X, lerp(H + 5, H - 6, p), 3.4, strength=0.5 + 0.5 * p)
        draw_city(img, f, windows, 0.55 * p)
        x, y, fr, flip = dove_at(f)
        blit(img, DOVE.img(fr, flip=flip), x, y)
        a = ease_in_out(phase(f, sec(10.5), sec(12.5))) * (1 - phase(f, sec(13.5), sec(14)))
        caption(img, "PEACE", 1, a, font="big", x=38, back=False)
        frames.append(img)
    return frames
