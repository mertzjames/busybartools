"""Scene: The Green River. Morning over a city river. A little work boat speeds across, puffing orange powder off its
stern, and where the powder lands the water turns green, spreading until the whole river glows emerald. Then a
small sailboat with a shamrock on its sail drifts in and bobs on the green water."""

import math
import random

from busybar.canvas import W, ease_in_out, mix, phase, put, sec, vgradient
from busybar.party import glitter, hash01, skyline
from pfx import GOLD_HI, ORANGE, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, shamrock

NAME = "river"
TITLE = "The Green River"
SECONDS = 14
KEYFRAMES = [(1.0, "Morning on the city river"), (3.6, "A work boat puffs orange powder"),
             (6.0, "Where it lands, the water turns green"), (8.6, "The whole river glows emerald"),
             (11.6, "A little shamrock sailboat drifts in")]

WATER_Y = 10
BOAT = (sec(1.6), sec(7.0))  # the dye boat crosses left to right
SAIL = (sec(8.4), sec(12.4))
BLUE = (28, 74, 150)
BLUE_HI = (110, 160, 220)
EMERALD = (20, 170, 70)
EMERALD_HI = (130, 240, 140)


def boat_x(f: int) -> float:
    return -10 + (W + 20) * phase(f, *BOAT)


def dye(x: int, y: int, f: int) -> float:
    """How green the water is at (x, y): it starts where the boat passed and spreads down and outward."""
    u = (x + 10) / (W + 20)
    passed = BOAT[0] + u * (BOAT[1] - BOAT[0])
    depth = abs(y - (WATER_Y + 1))
    delay = 4 + depth * 5 + 6 * hash01(3, x, y)
    return max(0.0, min(1.0, (f - passed - delay) / 16))


def background():
    img = vgradient((70, 126, 206), (190, 206, 226))
    skyline(img, 9, base=WATER_Y, color=(70, 82, 120), window=(255, 224, 160), lit=0.15)
    for x in range(W):  # the far embankment
        put(img, x, WATER_Y - 1, (96, 96, 104))
    return img


def render():
    bg = background()
    rng = random.Random(8)
    puffs = [(BOAT[0] + i, rng.uniform(-1, 1), rng.uniform(-0.7, -0.3)) for i in range(BOAT[1] - BOAT[0])]
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        # the water: ripples drift; each pixel is blue or emerald by how far the dye has spread
        for y in range(WATER_Y, 16):
            for x in range(W):
                g = dye(x, y, f)
                base = mix(BLUE, EMERALD, g)
                hi = mix(BLUE_HI, EMERALD_HI, g)
                r = math.sin(x * 0.7 + y * 2.1 - f * 0.18 * (1 + (y - WATER_Y) * 0.1))
                put(img, x, y, mix(base, hi, 0.55) if r > 0.93 else mix(base, (0, 0, 0), 0.12 * (y - WATER_Y) / 5))
        # the dye boat: a white hull with a red stripe and a little cabin, its wake behind it
        if BOAT[0] <= f < BOAT[1] + 4:
            bx = int(round(boat_x(f)))
            for dx in range(7):
                put(img, bx + dx, WATER_Y + 1, (236, 236, 230))
                put(img, bx + dx + (1 if dx < 6 else 0), WATER_Y + 2, (200, 60, 60) if dx < 6 else (236, 236, 230))
            for dx in (2, 3, 4):
                put(img, bx + dx, WATER_Y, (210, 220, 236))
            put(img, bx + 3, WATER_Y - 1, (140, 190, 236))
            for k in range(1, 5):  # foam
                put(img, bx - k, WATER_Y + 2, (220, 236, 240), 0.7 - 0.15 * k)
            # orange powder puffing off the stern, drifting back and settling
            for t0, vx, vy in puffs:
                age = f - t0
                if 0 <= age < 16:
                    ox = boat_x(t0) - 1 + vx * age * 0.3 - age * 0.15
                    oy = WATER_Y - 1 + vy * age + 0.045 * age * age
                    if oy < WATER_Y + 1:
                        a = 1 - age / 16
                        put(img, ox, oy, ORANGE, a)
                        if age < 8:
                            put(img, ox - 1, oy, (255, 170, 70), 0.6 * a)
        # once green, a few glints on the water
        if f >= sec(7.5):
            glitter(img, 15, f, n=10, period=sec(2), colors=(GOLD_HI, EMERALD_HI), area=(0, WATER_Y + 1, W, 16),
                    strength=0.6 * phase(f, sec(7.5), sec(8.5)))
        # the shamrock sailboat drifts in from the right and bobs
        if f >= SAIL[0]:
            sx = int(round(W + 2 - (W / 2 - 4 + 6) * ease_in_out(phase(f, *SAIL))))
            bob = 1 if math.sin(f * 0.22) > 0.5 else 0
            hy = WATER_Y + 2 + bob
            for dx in range(-4, 5):
                put(img, sx + dx, hy, (150, 92, 50) if abs(dx) < 4 else (120, 70, 40))
            for dx in range(-3, 4):
                put(img, sx + dx, hy + 1, (120, 70, 40))
            for y in range(hy - 8, hy):  # the mast
                put(img, sx, y, (190, 150, 100))
            for r in range(7):  # the sail: a white triangle behind the mast
                for dx in range(1, 1 + (r + 2) // 2 + 1):
                    put(img, sx - dx, hy - 8 + r, (240, 240, 232))
            shamrock(img, sx - 2, hy - 4, 0, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK)
            put(img, sx, hy - 9, (255, 200, 60))  # a gold pennant tip
        frames.append(img)
    return frames
