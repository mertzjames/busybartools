"""Scene: a menorah glowing in a snowy window, seen from the street. Like the menorah scene it comes in nine
variants, so the window shows tonight's candles (docs/DECISIONS.md D2). Snow falls, the flames flicker and their
light spills onto the snow under the window. A gust blows through halfway.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

from busybar.canvas import FPS, add, mix, new, phase, put, sec
from busybar.party import Snowfall, hash01
from hfx import CANDLE_COLORS, FLAME_MID, FLAME_TIP, GOLD, GOLD_HI, GOLD_LO, Menorah, SILVER, \
    WHITE, glow

SECONDS = 14
FRAMES = sec(SECONDS)

WALL, WALL_LINE = (34, 40, 74), (26, 30, 58)
FRAME = (128, 100, 80)
ROOM_TOP, ROOM_BOTTOM = (64, 36, 16), (108, 62, 22)
ROOM_DIM_TOP, ROOM_DIM_BOTTOM = (34, 22, 20), (56, 36, 22)
CURTAIN, CURTAIN_HI = (40, 74, 160), (70, 110, 200)
SNOW, SNOW_LO = (230, 238, 255), (170, 186, 220)
WX0, WX1, WY0, WY1 = 16, 55, 2, 11  # window interior box (inclusive)
SLOTS = [24 + 3 * j for j in range(9)]  # small menorah: 1 px candles 3 px apart, shamash at slot 4


def background(n: int):
    img = new(WALL)
    for y in range(16):
        for x in range(72):
            if y % 3 == 2:
                put(img, x, y, WALL_LINE)
    for x in range(72):  # snowy roof edge, a few icicles
        put(img, x, 0, SNOW if hash01(x, 1) > 0.15 else SNOW_LO)
        if hash01(x, 2) > 0.8:
            put(img, x, 1, (170, 200, 240), 0.8)
    top, bottom = (ROOM_TOP, ROOM_BOTTOM) if n else (ROOM_DIM_TOP, ROOM_DIM_BOTTOM)
    for y in range(WY0 - 1, WY1 + 2):
        for x in range(WX0 - 1, WX1 + 2):
            if x in (WX0 - 1, WX1 + 1) or y in (WY0 - 1, WY1 + 1):
                put(img, x, y, FRAME)
            else:
                put(img, x, y, mix(top, bottom, (y - WY0) / (WY1 - WY0)))
    for y in range(WY0, WY1 + 1):  # curtains, tied back
        w = 3 if y < 5 or y > 9 else 2
        for k in range(w):
            put(img, WX0 + k, y, CURTAIN_HI if k == 0 else CURTAIN)
            put(img, WX1 - k, y, CURTAIN if k == 0 else CURTAIN_HI)
    # snow on the sill and the ground
    for x in range(WX0 - 2, WX1 + 3):
        put(img, x, WY1 + 2, SNOW)
        if hash01(x, 3) > 0.6:
            put(img, x, WY1 + 1, SNOW, 0.9)
    for x in range(72):
        top_y = 14 - (1 if hash01(x // 3, 4) > 0.6 else 0)
        for y in range(top_y, 16):
            put(img, x, y, SNOW if y == top_y else SNOW_LO)
    # the small menorah on the sill
    for x in range(SLOTS[0], SLOTS[8] + 1):
        put(img, x, 9, GOLD_HI if x < SLOTS[4] else GOLD)
    for x in SLOTS:
        if x != SLOTS[4]:
            put(img, x, 9, GOLD_HI)
    sx = SLOTS[4]
    put(img, sx, 7, GOLD_HI)
    put(img, sx, 8, GOLD)
    put(img, sx, 10, GOLD)
    for dx in (-2, -1, 0, 1, 2):
        put(img, sx + dx, 11, GOLD_LO if dx > 0 else GOLD)
    return img


def small_flame(img, x: int, base: int, f: int, seed: int) -> None:
    put(img, x, base, FLAME_MID)
    tip = hash01(seed, f // 2)
    put(img, x, base - 1, FLAME_TIP, 0.75 if tip > 0.3 else 0.45)
    glow(img, x, base - 0.5, 2.6, (255, 160, 50), 0.22)


def make(n: int):
    keys = [(1.0, "A window on a snowy night"), (7.4, "A gust of snow"), (12.0, "Light on the snow")]
    if n:
        keys[0] = (1.0, f"Tonight's candles in the window ({n})")

    def render():
        bg = background(n)
        snow = Snowfall(seed=71, n=26, period=FRAMES // 2, color=SNOW, alpha=(0.35, 0.9))
        far = Snowfall(seed=72, n=18, period=FRAMES, color=SNOW_LO, alpha=(0.2, 0.45))
        frames = []
        for f in range(FRAMES):
            t = f / FPS
            img = bg.copy()
            far.draw(img, f)
            flick = 1.0
            if n:
                # candlelight in the room and on the snow outside
                glow(img, 36, 7, 20, (90, 52, 14), 0.35 * (n + 1) / 9 * flick)
                for x in range(WX0 - 4, WX1 + 5):
                    for y in range(13, 16):
                        k = max(0.0, 1 - abs(x - 36) / 24) * (n + 1) / 9 * flick
                        add(img, x, y, (90, 60, 20), 0.45 * k)
            for p in Menorah.placed(n):
                x = SLOTS[p - 1 if p <= 4 else p]
                body, hi = CANDLE_COLORS[p % 2]
                for y in (6, 7, 8):
                    put(img, x, y, body if body != WHITE else (220, 226, 240))
                small_flame(img, x, 5, f, p * 7)
            sx = SLOTS[4]
            for y in (4, 5, 6):
                put(img, sx, y, SILVER)
            if n:
                small_flame(img, sx, 3, f, 99)
            # snow in front; a gust pushes it sideways halfway through
            gust = 14 * phase(t, 6.6, 8.6) ** 2 if t < 8.6 else 14 + 3 * (t - 8.6)
            for x0, y0, laps, ph, a in snow.items:
                y = (y0 + f * laps * 16 / snow.period) % 16
                x = (x0 + gust * (0.6 + 0.4 * laps) + 0.8 * math.sin(2 * math.pi * f / snow.period + ph)) % 72
                put(img, x, y, SNOW, a)
            frames.append(img)
        return frames

    title = "Window in the Snow"
    return SimpleNamespace(NAME=f"window_{n}", TITLE=f"{title} ({n})" if n else title, SECONDS=SECONDS,
                           KEYFRAMES=keys, render=render, NIGHT=n)


VARIANTS = [make(n) for n in range(9)]
