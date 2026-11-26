"""Scene: the backyard grill. On a warm afternoon a dad in an apron tends three burgers on a red kettle grill while
smoke curls up. He flips them one by one, sends one up in a showy high flip, then tosses it onto a waiting bun on the
side table: cheese, top bun, done."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.party import hash01

import ffx

NAME = "grill"
TITLE = "Backyard Grill"
SECONDS = 14
KEYFRAMES = [(1.0, "Burgers on the grill"), (2.5, "Flip"), (4.0, "Flip"), (7.4, "A showy high flip"),
             (9.0, "Ta-da"), (10.6, "Onto the bun"), (12.0, "Cheese and the top bun"), (13.2, "Burger's up")]

LAWN = 12
GRATE = 8  # burgers sit on row 7
BOWL = (196, 52, 44)
BOWL_HI = (236, 96, 80)
CHROME = (210, 210, 222)
PATTY = (150, 84, 50)
PATTY_SEAR = (104, 58, 38)
PATTIES = [34, 38, 42]  # left columns of the three burgers (3 px each)
DAD_X = 27
PLATE_X = 56  # left column of the bun on the side table
BUN = (230, 160, 70)
BUN_HI = (250, 200, 110)
CHEESE = (255, 214, 60)

DAD = dict(skin=ffx.SKIN_TAN, shirt=(70, 120, 210), pants=(110, 90, 70), hair=ffx.HAIR_DARK, style="short")


def base_frame():
    img = ffx.sky([(0, (64, 132, 216)), (5, (120, 182, 238)), (LAWN - 1, (236, 222, 190))])
    ffx.sun(img, 8, 3, 2.4, halo=0.3)
    # a low hedge along the back of the yard (a brown fence swallowed the burgers and the dad's tan skin)
    for x in range(W):
        top = 9 - (1 if math.sin(x * 0.6) + math.sin(x * 0.21) > 0.8 else 0)
        for y in range(top, LAWN):
            put(img, x, y, ffx.GRASS_DK if (x * 5 + y * 3) % 7 else (30, 90, 40))
    for y in range(LAWN, H):
        for x in range(W):
            put(img, x, y, ffx.GRASS if (x * 3 + y) % 7 else ffx.GRASS_HI)
    # the kettle grill: a red bowl with a highlight, three legs, glowing coals under a chrome grate
    for y, (x0, x1) in zip(range(GRATE + 1, GRATE + 4), ((33, 45), (34, 44), (36, 42))):
        for x in range(x0, x1 + 1):
            put(img, x, y, BOWL_HI if x == x0 + 1 else BOWL)
    for x, y0 in ((36, GRATE + 4), (39, GRATE + 4), (42, GRATE + 4)):
        for y in range(y0, 15):
            put(img, x, y, (120, 120, 132))
    for x in range(33, 46):
        put(img, x, GRATE, CHROME if x % 2 else (160, 160, 176))
    # the side table with a plate and the bottom bun
    for x in range(PLATE_X - 3, PLATE_X + 7):
        put(img, x, 10, (210, 170, 110))
    for x in (PLATE_X - 2, PLATE_X + 5):
        for y in range(11, 15):
            put(img, x, y, (170, 130, 80))
    for x in range(PLATE_X - 1, PLATE_X + 5):
        put(img, x, 9, (246, 246, 250))  # the plate
    for x in range(PLATE_X, PLATE_X + 4):
        put(img, x, 8, BUN)
    return img


def patty(img, x: float, y: float, flipped_ph: float) -> None:
    """A 4x1 burger; mid-flip (flipped_ph near 0.5) it shows its edge as a 2x2 block."""
    x, y = ffx.rnd(x), ffx.rnd(y)
    edge = 0.3 < flipped_ph < 0.7
    if edge:
        for dx in (1, 2):
            put(img, x + dx, y, PATTY)
            put(img, x + dx, y - 1, PATTY_SEAR)
        return
    for dx in range(3):
        put(img, x + dx, y, PATTY_SEAR if flipped_ph >= 0.7 else PATTY)


def flip_path(t: float, height: float, x0: float, x1: float, y0: float, y1: float):
    x = x0 + (x1 - x0) * t
    y = y0 + (y1 - y0) * t - height * 4 * t * (1 - t)
    return x, y


def sizzle(img, x: float, y: float, age: int, seed: int) -> None:
    """Sparks and a little smoke when a burger lands."""
    if not (0 <= age < 10):
        return
    for i in range(4):
        sx = x + 1 + (hash01(seed, i) - 0.5) * age * 0.9
        sy = y - age * (0.3 + 0.3 * hash01(seed, i, 1))
        put(img, sx, sy, (255, 200, 90), 1 - age / 10)


def render():
    base = base_frame()
    frames = []
    flips = [  # (patty index, start s, duration, height, to x or None)
        (0, 2.0, 0.9, 3.0, None),
        (1, 3.4, 0.9, 3.0, None),
        (2, 4.8, 0.9, 3.0, None),
        (0, 6.6, 1.8, 9.0, None),
        (0, 9.8, 1.2, 5.0, PLATE_X),
    ]
    for f in range(sec(SECONDS)):
        img = base.copy()
        s = f / 15

        # coals glow through the grate: a steady orange with a few flickering points
        for x in range(34, 45):
            add(img, x, GRATE - 0, (255, 120, 30), 0.25)
        for i in range(4):
            if hash01(5, i, f // 3) > 0.5:
                add(img, 35 + int(hash01(6, i) * 9), GRATE, (255, 200, 80), 0.8)

        # smoke: soft puffs rising from the grill and drifting right
        for i in range(6):
            age = (f + i * 17) % 60
            sx = 37 + (i % 3) * 3 + age * 0.15 + math.sin((f + i * 13) * 0.12) * 0.8
            sy = GRATE - 2 - age * 0.16
            a = 0.9 * (1 - age / 60) * min(1.0, age / 6)
            put(img, sx, sy, (168, 164, 180), a)  # grey: white smoke vanished in the pale sky
            put(img, sx + 1, sy, (168, 164, 180), a * 0.6)
            put(img, sx, sy - 1, (190, 186, 200), a * 0.4)

        # the burgers
        on_bun = s >= 11.0
        for i, px in enumerate(PATTIES):
            state = sum(1 for (pi, t0, dur, h, to) in flips if pi == i and s >= t0 + dur and to is None) % 2
            active = None
            for (pi, t0, dur, h, to) in flips:
                if pi == i and t0 <= s < t0 + dur:
                    active = (t0, dur, h, to)
            if i == 0 and on_bun:
                continue
            if active:
                t0, dur, h, to = active
                t = (s - t0) / dur
                x1, y1 = (to, 7) if to else (px, GRATE - 1)
                x, y = flip_path(t, h, px, x1, GRATE - 1, y1)
                spins = 2 if h > 6 else 1
                ph = (t * spins) % 1.0
                patty(img, x, y, ph)
            else:
                patty(img, px, GRATE - 1, 0.8 if state else 0.0)
        for k, (pi, t0, dur, h, to) in enumerate(flips):
            sizzle(img, (to or PATTIES[pi]), GRATE - 1 if not to else 7, f - sec(t0 + dur), k)

        # on the bun: the burger, a slice of cheese, then the top bun drops on
        if on_bun:
            patty(img, PLATE_X, 7, 0.8)
            put(img, PLATE_X + 3, 7, PATTY_SEAR)
            ch = phase(f, sec(11.4), sec(11.8))
            if ch > 0:
                cy = ffx.rnd(-1 + 7 * ch)
                for dx in range(-1, 5) if ch >= 1 else range(0, 4):
                    put(img, PLATE_X + dx, cy if ch < 1 else 6, CHEESE)
            tb = phase(f, sec(11.9), sec(12.4))
            if tb > 0:
                ty = ffx.rnd(-2 + 7 * tb * tb)
                for dx in range(4):
                    put(img, PLATE_X + dx, ty, BUN_HI if dx in (1, 2) else BUN)
                for dx in range(1, 3):
                    put(img, PLATE_X + dx, ty - 1, BUN)
            if s >= 12.4:
                k = max(0.0, 1 - (s - 12.4) / 1.2)
                for dx, dy in ((-2, -3), (5, -3), (-3, 0), (6, 0), (1, -5)):
                    add(img, PLATE_X + 1.5 + dx, 6 + dy, ffx.GOLD_HI, 0.9 * k)

        # the dad: spatula in the right hand, a cheer after the high flip and at the end
        arms = (0.06, 0.22)
        for (pi, t0, dur, h, to) in flips:
            if t0 - 0.2 <= s < t0 + 0.25:
                arms = (0.06, 0.34)
        cheer = 8.6 <= s < 9.6 or s >= 12.6
        if cheer:
            arms = (0.45, 0.45) if (f // 4) % 2 else (0.5, 0.42)
        hands = ffx.figure(img, DAD_X, 14, facing=1, arms=arms, **DAD)
        for y in range(7, 11):  # a white apron over the shirt
            for dx in (-1, 0, 1):
                if y > 7 or dx == 0:
                    put(img, DAD_X + dx, y, (246, 240, 226))
        if not cheer:
            hx, hy = hands["r"]
            ffx.line(img, hx + 1, hy, hx + 2, hy - 0.5, (120, 80, 50))  # the handle
            ffx.line(img, hx + 3, hy - 0.8, hx + 4, hy - 1, CHROME)  # the blade
        frames.append(img)
    return frames
