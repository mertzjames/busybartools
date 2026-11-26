"""Scene: a monument skyline at sunset over a long reflecting pool (docs/DECISIONS.md D3). A tall obelisk, a
columned memorial and a domed hall, all generic, stand against the sky as the sun goes down; the memorial's lights
come on, the obelisk's red beacons blink, stars come out, and everything shimmers upside down in the pool."""

import math
import random

from PIL import Image

from busybar.canvas import H, W, mix, phase, put, sec

import pfx

NAME = "monuments"
TITLE = "Monuments at Sunset"
SECONDS = 14
KEYFRAMES = [(0.5, "Sunset over the monuments"), (4.0, "The sun goes down"),
             (8.0, "The memorial's lights come on"), (11.0, "Dusk, and the first stars"),
             (13.5, "Reflections in the pool")]

HORIZON = 10  # the last row of land; the pool is rows 11-15
OBELISK_X = 41


def sky_at(p: float) -> Image.Image:
    """The sky at progress p: 0 sunset (gold and rose, darkened so the stone reads) .. 1 dusk (indigo)."""
    top = mix((44, 38, 104), (12, 12, 44), p)
    mid = mix((150, 62, 100), (46, 28, 80), p)
    low = mix((246, 136, 64), (120, 54, 72), p)
    return pfx.sky([(0, top), (5, mid), (HORIZON - 1, low)])


def stone(lit: float):
    return mix((96, 80, 104), (236, 206, 176), lit)


def monuments(img, p: float, lights: float) -> None:
    """Draw the skyline at progress p (the stone loses its sunset light) with the memorial lit by `lights`."""
    warm = 1 - p
    land = (40, 26, 44)
    for x in range(W):  # a low bank of trees and the far shore
        top = HORIZON - (1 if (x * 7) % 11 < 5 else 0)
        for y in range(top, HORIZON + 1):
            put(img, x, y, land)
    # the columned memorial (left): attic, frieze, eight columns, steps
    x0, x1 = 4, 22
    for x in range(x0, x1 + 1):
        put(img, x, 4, stone(0.55 * warm + 0.15))
        put(img, x, 5, stone(0.75 * warm + 0.2))
        put(img, x, 10, stone(0.5 * warm + 0.15))
    for x in range(x0 + 1, x1):
        put(img, x, 3, stone(0.45 * warm + 0.15))
    for y in range(6, 10):
        for x in range(x0, x1 + 1):
            col = (x - x0) % 2 == 0
            if col:
                put(img, x, y, stone(0.85 * warm + 0.15))
            else:
                put(img, x, y, mix((34, 22, 40), (255, 196, 110), lights * (0.9 if 7 <= y <= 8 else 0.6)))
    # the obelisk (center), lit on its sunward (left) face, with a pyramid cap
    for y in range(1, HORIZON + 1):
        put(img, OBELISK_X - 1, y, stone(0.95 * warm + 0.1))
        put(img, OBELISK_X, y, stone(0.6 * warm + 0.08))
        if y >= 6:
            put(img, OBELISK_X + 1, y, stone(0.45 * warm + 0.06), 0.6)
    put(img, OBELISK_X - 1, 0, stone(0.95 * warm + 0.1), 0.8)
    put(img, OBELISK_X, 0, stone(0.6 * warm + 0.08), 0.5)
    # the domed hall (right): wings, a drum with windows, the dome and a small lantern on top
    for x in range(52, 71):
        for y in range(8, HORIZON + 1):
            put(img, x, y, stone(0.6 * warm + 0.12))
    for x in range(53, 70, 2):
        put(img, x, 9, mix((60, 40, 60), (255, 200, 120), lights * 0.8))
    for y in range(5, 8):
        for x in range(57, 66):
            win = y == 6 and x % 2 == 0
            put(img, x, y, mix((60, 40, 60), (255, 200, 120), lights * 0.8) if win else stone(0.7 * warm + 0.12))
    for y, (a, b) in zip(range(2, 5), ((59, 63), (58, 64), (57, 65))):
        for x in range(a, b + 1):
            put(img, x, y, stone((0.95 if x < 61 else 0.6) * warm + 0.12))
    put(img, 61, 1, stone(0.8 * warm + 0.15))
    put(img, 61, 0, stone(0.8 * warm + 0.15), 0.7)


def render():
    rng = random.Random(5)
    stars = [(rng.randrange(W), rng.randrange(0, 6), rng.random()) for _ in range(16)]
    birds = [(sec(1.5), 2.0, 0.35), (sec(2.2), 3.5, 0.32), (sec(2.9), 1.5, 0.3)]
    frames = []
    for f in range(sec(SECONDS)):
        p = phase(f, 0, sec(12))
        p = round(p * 40) / 40  # the light changes in small steps (keeps the .anim small)
        img = sky_at(p)
        # the sun sinks behind the memorial
        sy = round((4.0 + 8 * phase(f, 0, sec(8))) * 4) / 4
        if sy < HORIZON + 3:
            pfx.glow(img, 31, sy, 14, (255, 150, 60), 0.5 * (1 - p))
            for y in range(int(sy) - 3, int(sy) + 4):
                for x in range(27, 36):
                    if math.hypot(x - 31, y - sy) <= 2.4:
                        put(img, x, y, mix((255, 236, 160), (255, 170, 80), (y - sy + 2.4) / 4.8))
        # stars once the sky is dark enough
        for x, y, ph in stars:
            k = phase(f, sec(8.5 + 2 * ph), sec(10.5 + 2 * ph))
            if k > 0:
                put(img, x, y, (220, 220, 255), 0.6 * k)
        for t0, y, speed in birds:  # a few birds cross early on
            bx = (f - t0) * speed
            if 0 <= bx < W + 4:
                w = (f // 4) % 2
                put(img, W - bx, y, (40, 26, 50))
                put(img, W - bx - 1, y - w, (40, 26, 50))
                put(img, W - bx + 1, y - w, (40, 26, 50))
        lights = phase(f, sec(6.5), sec(8.5))
        lights = round(lights * 10) / 10
        monuments(img, p, lights)
        # the obelisk's red beacons blink once every 2 s
        if (f % 30) < 8:
            put(img, OBELISK_X - 1, 1, (255, 40, 40))
            put(img, OBELISK_X, 1, (255, 40, 40))
        # the reflecting pool: the scene above, upside down at half height, darker, with a slow shimmer
        src = img.copy()
        for k in range(H - HORIZON - 1):
            y = HORIZON + 1 + k
            ry = HORIZON - 1 - 2 * k
            shift = math.floor(0.9 * math.sin(k * 1.9 + (f // 4) * 0.7) + 0.5) if k > 0 else 0
            for x in range(W):
                c = src.getpixel((min(W - 1, max(0, x + shift)), max(0, ry)))[:3]
                put(img, x, y, mix((10, 14, 40), c, 0.62 - 0.06 * k))
        for x in range(W):  # the pool's near edge
            put(img, x, HORIZON + 1, (60, 50, 80), 0.35)
        frames.append(img)
    return frames
