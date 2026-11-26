"""Scene: At the Memorial Wall (the closing scene). Night at a polished stone memorial wall. A wreath of evergreen with
a red bow rests at its foot between two candles, whose light is warm on the stone. The words WE REMEMBER fade in
across the wall. The engraving is abstract (short marks, no names). The layout is symmetrical."""

import math
import random

from busybar.canvas import H, W, ease_in_out, mix, phase, put, sec
from mdfx import caption, glow, quant

NAME = "wall"
TITLE = "At the Memorial Wall"
SECONDS = 16
KEYFRAMES = [(1.0, "A memorial wall at night"), (5.0, "A wreath between two candles"),
             (10.5, "WE REMEMBER"), (15.0, "WE REMEMBER")]

GROUND = 13  # the row where the wall meets the plaza
WREATH = (35.5, 10.6, 3.6)  # centre x, centre y, radius
CANDLES = (26, 44)  # left column of each candle (2 wide), symmetrical about the wreath


def wall_base():
    """The wall, its seams and abstract engraving, and the plaza (no light yet)."""
    from PIL import Image
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    rng = random.Random(7)
    for y in range(H):
        for x in range(W):
            if y == 0:
                c = (84, 88, 108)  # the capstone
            elif y < GROUND:
                c = mix((44, 48, 68), (36, 40, 58), y / GROUND)
            else:
                c = mix((46, 44, 56), (30, 30, 40), (y - GROUND) / (H - GROUND))
            put(img, x, y, c)
    for x in range(10, W, 15):  # panel seams
        for y in range(1, GROUND):
            put(img, x, y, (58, 62, 84))
    for y in range(2, GROUND - 1, 2):  # rows of engraving, as short abstract marks
        x = rng.randrange(2)
        while x < W:
            n = rng.randrange(2, 5)
            for i in range(n):
                put(img, x + i, y, (66, 70, 92), 0.7)
            x += n + rng.randrange(2, 4)
    for x in range(W):  # the line where wall meets plaza
        put(img, x, GROUND, (60, 58, 70))
    return img


def wreath(img, a: float) -> None:
    cx, cy, r = WREATH
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if r - 1.5 <= d <= r + 0.3:
                ang = math.atan2(y - cy, x - cx)
                leaf = (52, 120, 64) if (int(ang * 4) % 2) else (40, 100, 54)
                if y < cy - 1:
                    leaf = mix(leaf, (110, 170, 110), 0.25)  # candle-lit upper edge
                put(img, x, y, leaf, a)
    for bx, by in ((-3, -1), (3, -1), (-2, -3), (2, -3)):  # red berries
        put(img, cx + bx, cy + by, (200, 50, 50), a)
    for dx, dy in ((-1, 3), (0, 3), (1, 3), (-2, 4), (2, 4)):  # the bow at the bottom
        put(img, cx + dx, cy + dy, (206, 40, 46), a)


def candle(img, x0: int, f: int, a: float, seed: int) -> None:
    for y in range(GROUND - 2, H - 1):
        put(img, x0, y, (236, 230, 214), a)
        put(img, x0 + 1, y, (200, 192, 176), a)
    put(img, x0, GROUND - 3, (120, 80, 50), a)  # a wick row between the flame and the white candle
    # the flame: the core is steady, only the tip flickers between a few shapes
    put(img, x0, GROUND - 4, (255, 214, 120), a)
    tip = (f // 4 + f // 11 + seed) % 3
    put(img, x0 + (1 if tip == 2 else 0), GROUND - 5, (255, 170, 70), a * (0.9 if tip else 0.6))


def render():
    base = wall_base()
    frames = []
    for f in range(sec(SECONDS)):
        light = quant(ease_in_out(phase(f, 0, sec(2.5))), 20)
        img = base.copy()
        # steady candle glow on the stone (kept constant from frame to frame: flicker bloats the .anim)
        for k, x0 in enumerate(CANDLES):
            glow(img, x0 + 0.5, GROUND - 4, 10, (255, 170, 90), 0.42 * light)
        wreath(img, light)
        for k, x0 in enumerate(CANDLES):
            candle(img, x0, f, light, k)
        a = quant(ease_in_out(phase(f, sec(8.0), sec(10.5))), 20)
        caption(img, "WE REMEMBER", 0, a, font="big", back=0.5)
        if light < 1:  # fade in from the dark
            px = img.load()
            for y in range(H):
                for x in range(W):
                    r, g, b, al = px[x, y]
                    px[x, y] = (int(r * light), int(g * light), int(b * light), al)
        frames.append(img)
    return frames

