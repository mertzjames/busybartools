"""Scene: flags on Main Street. A small-town street on a clear November morning: storefronts with awnings and
bunting brighten in the sunrise, the town puts a flag out on each lamppost in turn, and they wave together against
the sky while a few autumn leaves drift down (docs/DECISIONS.md D3, D10)."""

import math

from busybar.canvas import H, W, ease_out, mix, phase, put, sec
from busybar.party import hash01

import vfx
from vfx import (BRICK, BRICK_HI, CREAM, NAVY, RED, SAGE, SIDEWALK, SLATE, STREET, WHITE, blend_stops,
                 draw_flag, lamppost, leaf, person, quant, sky, storefront)

NAME = "main_street"
TITLE = "Flags on Main Street"
SECONDS = 14
KEYFRAMES = [(0.5, "Sunrise on Main Street"), (3.0, "The first flag goes out"), (5.6, "One lamppost after another"),
             (9.0, "A flag on every lamppost"), (13.0, "Autumn leaves drift down")]

SKY_DAWN = [(0, (40, 70, 140)), (4, (100, 130, 190)), (6, (220, 170, 150))]
SKY_DAY = [(0, (60, 110, 200)), (4, (130, 175, 230)), (6, (236, 214, 180))]

# (x0, width, roof row, wall, awning colors)
SHOPS = [
    (0, 14, 6, BRICK, (RED, WHITE)),
    (14, 13, 5, (170, 150, 120), (NAVY, WHITE)),
    (27, 15, 6, SAGE, ((190, 120, 60), CREAM)),
    (42, 13, 5, BRICK_HI, (RED, WHITE)),
    (55, 17, 6, SLATE, ((70, 130, 80), CREAM)),
]
POSTS = [8, 26, 44, 62]
UNFURL = [sec(2.4 + 1.4 * k) for k in range(4)]  # when each lamppost's flag unfurls
LEAF_COLORS = [(232, 120, 40), (220, 170, 50), (196, 76, 36)]


def mini_flag(u: int, v: int):
    """A lamppost flag, 7 x 5: a 3 x 3 canton of lit dots and red and white stripes."""
    if u < 3 and v < 3:
        return vfx.STAR if (u + v) % 2 == 1 else NAVY
    return RED if v % 2 == 0 else WHITE


def bunting(img, x0: int, w: int, y: int) -> None:
    """A pleated half-fan of bunting under a cornice: blue, white and red bands."""
    cx = x0 + w / 2
    half = min(4, w // 2 - 1)
    for x in range(int(cx - half), int(cx + half) + 1):
        d = abs(x + 0.5 - cx) / half
        depth = 3 if d < 0.5 else 2 if d < 0.9 else 1
        for i in range(depth):
            put(img, x, y + i, (NAVY, WHITE, RED)[i])


def street(light: float):
    img = sky(blend_stops(SKY_DAWN, SKY_DAY, light))
    for x0, w, top, wall, awning in SHOPS:
        storefront(img, x0, w, top, mix(wall, (40, 40, 60), 0.25 * (1 - light)), awning, lit=1.0)
    bunting(img, 14, 13, 6)
    bunting(img, 42, 13, 6)
    for x in range(W):
        put(img, x, 14, SIDEWALK)
        put(img, x, 15, STREET)
    for x in POSTS:
        lamppost(img, x, 1)
    return img


def render():
    n = sec(SECONDS)
    frames = []
    cache = {}
    leaves = [(hash01(7, i) * W, hash01(8, i), LEAF_COLORS[i % 3]) for i in range(5)]
    for f in range(n):
        light = quant(f / sec(4.0), 20)
        if light not in cache:
            cache[light] = street(light)
        img = cache[light].copy()
        # the town puts its flags out at sunrise, one lamppost after another, then they all wave in one breeze
        for k, x in enumerate(POSTS):
            p = phase(f, UNFURL[k], UNFURL[k] + sec(0.8))
            fw = int(math.floor(7 * ease_out(p) + 0.5))
            if fw >= 2:
                draw_flag(img, x + 1, 1, fw, 5, f / 30 + k * 0.23, amp=1.0 * fw / 7, wavelength=9,
                          color=mini_flag, shade_levels=2)
            elif fw == 1:
                for y in range(1, 6):
                    put(img, x + 1, y, RED if y % 2 else WHITE)
        for i, (lx, ph, c) in enumerate(leaves):
            t = (f / n + ph) % 1.0
            y = -1 + t * (H + 1)
            x = (lx + 6 * math.sin(2 * math.pi * (t * 1.5 + ph))) % W
            if 0 <= y < 14:
                leaf(img, x, y, f + i, c)
        frames.append(img)
    return frames
