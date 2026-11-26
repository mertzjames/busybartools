"""Scene: the last swim of summer. The sun sinks into the sea and the sky turns from gold to rose. Waves roll in
and foam up the sand past a striped umbrella and a sandcastle; a swimmer runs down for one last dip, splashes in
and waves from the water; a gull glides by and the first star comes out (docs/DECISIONS.md D3, D10)."""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, ease_in_out, mix, phase, put, sec

import lfx

NAME = "beach"
TITLE = "Last Swim of Summer"
SECONDS = 14
KEYFRAMES = [(0.8, "Golden hour at the beach"), (3.0, "One last swim"), (4.4, "Splash!"),
             (8.0, "Waving from the water"), (12.8, "The sun sets on summer")]

HORIZON = 8  # first row of sea
SHORE = 12  # first row of sand
GOLD_SKY = [(0, (96, 120, 210)), (4, (236, 160, 160)), (HORIZON - 1, (255, 196, 110))]
ROSE_SKY = [(0, (36, 34, 104)), (4, (178, 84, 140)), (HORIZON - 1, (255, 120, 76))]
SEA_DAY, SEA_DUSK = (40, 96, 176), (44, 54, 128)
SUN_X = 30
RUN0, RUN1 = sec(1.0), sec(4.0)
SPLASH = sec(4.2)
WAVE_PERIOD = sec(3.5)


def umbrella(img) -> None:
    for y in range(6, H - 1):
        put(img, 60, y, (236, 232, 222))
    for row, (a, b) in enumerate(((58, 62), (56, 64), (55, 65))):
        for x in range(a, b + 1):
            put(img, x, 4 + row, lfx.RED if ((x - 55) // 2) % 2 == 0 else lfx.WHITE)
    for x in range(52, 59):  # a towel
        put(img, x, 14, (60, 140, 240) if x % 2 else (255, 214, 60))
        put(img, x, 15, (60, 140, 240) if x % 2 else (255, 214, 60))


def sandcastle(img) -> None:
    """Two towers and a wall, darker than the dry sand so it doesn't vanish into it; a red pennant on top."""
    lfx.grid(img, 8, 10, [
        ".pf....",
        "TTT.TTT",
        "TtTTTtT",
        "TTTTTTT",
        "ttttttt",
    ], {"T": (206, 146, 80), "t": (156, 104, 58), "f": lfx.RED, "p": (236, 236, 236)})


def render():
    rng = random.Random(11)
    splash = [(rng.uniform(-1.2, 1.2), rng.uniform(-1.4, -0.5), rng.choice(((255, 255, 255), (180, 230, 255))))
              for _ in range(14)]
    frames = []
    n = sec(SECONDS)
    for f in range(n):
        k = lfx.quant(f / (n - 1), 40)
        img = lfx.sky(lfx.blend_stops(GOLD_SKY, ROSE_SKY, k))
        sun_y = 3.5 + 6.5 * k
        sun = mix((255, 240, 180), (255, 150, 90), k)
        lfx.glow(img, SUN_X, min(sun_y, HORIZON - 0.5), 12, mix((255, 180, 90), (255, 100, 70), k), 0.45,
                 squash=1.5)
        lfx.disc(img, SUN_X, sun_y, 2.6, sun)  # drawn before the sea, so it sinks behind the horizon
        sea = mix(SEA_DAY, SEA_DUSK, k)
        for y in range(HORIZON, SHORE):
            for x in range(W):
                put(img, x, y, mix(sea, (90, 150, 220), 0.12 * (y - HORIZON)))
        for y in range(SHORE, H):
            for x in range(W):
                put(img, x, y, mix(lfx.SAND, (180, 120, 120), k * 0.5) if y > SHORE else lfx.SAND_DK)
        # the sun's path on the water: a few glints that shimmer slowly
        for y in range(HORIZON, SHORE):
            half = 1 + (y - HORIZON) // 2
            for x in range(SUN_X - half, SUN_X + half + 1):
                if (x * 7 + y * 3 + f // 3) % 4 == 0:
                    add(img, x, y, sun, 0.7)
        # waves: a swell rolls in, breaks into foam and washes up the sand
        for w in range(2):
            p = ((f + w * WAVE_PERIOD // 2) % WAVE_PERIOD) / WAVE_PERIOD
            y = HORIZON + 1 + p * (SHORE - HORIZON + 0.5)
            for x in range(W):
                if math.sin(x * 0.45 + w * 2 + p * 3) > -0.2:
                    put(img, x, y, (230, 244, 255), 0.85 * min(1.0, 3 * (1 - p)) * min(1.0, p * 4))
        wash = math.sin(math.pi * ((f % WAVE_PERIOD) / WAVE_PERIOD))
        for x in range(W):
            reach = SHORE + (1 if math.sin(x * 0.3 + f / 20) + wash > 1.2 else 0)
            put(img, x, reach, (236, 246, 255), 0.6 * wash)
        sandcastle(img)
        umbrella(img)
        # the swimmer: runs down from the towel, splashes in, waves from the water
        if f < SPLASH:
            r = ease_in_out(phase(f, RUN0, RUN1))
            x = round(54 - 14 * r)
            feet = round(15 - 4 * r)
            step = (f // 3) % 2 if RUN0 <= f < RUN1 else 0
            put(img, x, feet - 5, lfx.HAIR_BROWN)
            put(img, x, feet - 4, lfx.SKIN[1])
            put(img, x, feet - 3, (255, 90, 140))  # a pink swimsuit
            put(img, x, feet - 2, (255, 90, 140))
            put(img, x - 1, feet - 3, lfx.SKIN[1])
            put(img, x + 1, feet - 3, lfx.SKIN[1])
            put(img, x - 1 + step, feet - 1, lfx.SKIN[1])
            put(img, x + 1 - (1 - step), feet, lfx.SKIN[1])
        else:
            bob = 1 if (f // 8) % 2 else 0
            put(img, 40, 9 + bob, lfx.SKIN[1])
            put(img, 40, 8 + bob, lfx.HAIR_BROWN)
            if sec(6.0) <= f < sec(11.0):
                put(img, 41, 8 + bob - (f // 4) % 2, lfx.SKIN[1])
            for x in (39, 41):
                add(img, x, 10 + bob, (220, 240, 255), 0.5)
            age = f - SPLASH
            for vx, vy, c in splash:
                if age < 12:
                    put(img, 40 + vx * age, 10 + vy * age + 0.12 * age * age, c, 1 - age / 12)
        # a gull glides across
        gx = -4 + (f - sec(5.0)) * 0.6
        if 0 <= f - sec(5.0) and gx < W + 3:
            up = (f // 5) % 2
            gy = 2 + round(math.sin(f / 9))
            for dx in (-2, -1, 1, 2):
                put(img, gx + dx, gy - (up if abs(dx) == 1 else (0 if up else 1)), (244, 244, 250))
            put(img, gx, gy, (244, 244, 250))
        # the first star
        if f >= sec(11.5):
            put(img, 12, 1, (255, 250, 220), 0.4 + 0.4 * phase(f, sec(11.5), sec(13)))
        frames.append(img)
    return frames
