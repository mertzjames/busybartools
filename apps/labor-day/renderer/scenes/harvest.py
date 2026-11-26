"""Scene: harvest time. In the golden hour a farmer drives a red tractor across a field, pulling a baler that picks
up the windrow and drops round hay bales behind it. A red barn and a silo stand on the horizon, swallows follow the
tractor, and the sun hangs low (docs/DECISIONS.md D3)."""

from __future__ import annotations

import math

from busybar.canvas import H, W, add, mix, put, sec
from busybar.fx import puff

import lfx

NAME = "harvest"
TITLE = "Harvest Time"
SECONDS = 14
KEYFRAMES = [(0.8, "Golden hour on the farm"), (3.5, "The tractor rolls in"), (7.0, "Baling the hay"),
             (10.5, "Round bales left behind"), (13.4, "Bales in the evening sun")]

HORIZON = 9
X0, X1 = -6.0, 92.0  # the rear wheel's column at the start and the end
WINDROW = 12
BALE_EVERY = sec(1.9)
STUBBLE = (178, 128, 62)  # cut stubble: browner than the windrow and bales, so they stand out
STUBBLE_DK = (146, 100, 50)


def tractor_x(f: int) -> int:
    return int(math.floor(X0 + (X1 - X0) * f / (sec(SECONDS) - 1) + 0.5))


def backdrop():
    img = lfx.sky([(0, (90, 140, 226)), (3, (196, 164, 206)), (6, (255, 192, 142)), (HORIZON, (255, 170, 80))])
    lfx.glow(img, 60, 5, 9, (255, 190, 90), 0.45, squash=1.2)
    lfx.disc(img, 60, 5, 2.2, (255, 244, 200))
    for x in range(W):  # a far tree line on the horizon
        top = HORIZON - 1 - (1 if (x * 5) % 9 < 4 else 0)
        for y in range(top, HORIZON + 1):
            put(img, x, y, (78, 112, 54) if y > top else (100, 136, 62))
    lfx.grid(img, 3, 3, [  # the barn: a gambrel roof, white trim and a hayloft door; a silo beside it
        "....rr....ss",
        "..rRRRRr..SS",
        ".rRRwwRRr.SS",
        "rRRRwwRRRrSS",
        "RRwRRRRwRRSS",
        "RRRwwwwRRRSS",
        "RRRwddwRRRSS",
    ], {"r": (156, 30, 34), "R": (196, 44, 40), "w": (250, 240, 226), "d": (120, 30, 30),
        "s": (210, 214, 224), "S": (170, 174, 190)})
    for y in range(HORIZON + 1, H):  # the field: cut stubble with furrows, golden in the low sun
        for x in range(W):
            c = STUBBLE if y % 2 == 0 else STUBBLE_DK
            if y == HORIZON + 1:
                c = mix(STUBBLE_DK, (120, 110, 60), 0.5)
            put(img, x, y, c)
    return img


def bale(img, x: int) -> None:
    """A round hay bale seen end-on: 3x3 with a spiral center."""
    lfx.grid(img, x - 1, WINDROW - 1, [".hh.", "hhcH", "hcHH", ".HH."],
             {"h": (255, 236, 150), "H": (236, 186, 84), "c": (196, 130, 50)})


def tractor(img, tx: int, f: int) -> None:
    rot = -tx / 2.6
    # the baler, hitched behind
    for x in range(tx - 11, tx - 5):
        for y in range(10, 14):
            c = (230, 170, 40) if y > 10 else (255, 214, 90)
            put(img, x, y, c)
    put(img, tx - 10, 11, (180, 120, 30))
    put(img, tx - 7, 11, (180, 120, 30))
    lfx.wheel(img, tx - 8, 14, 1.2, rot)
    for x in range(tx - 5, tx - 2):
        put(img, x, 13, lfx.STEEL)  # the hitch
    # the tractor: fender, hood, grille, stack and the farmer in a straw hat
    lfx.wheel(img, tx, 12.6, 2.6, rot)
    lfx.wheel(img, tx + 8, 14, 1.4, rot * 1.8)
    for x in range(tx - 2, tx + 3):
        put(img, x, 9, lfx.RED_HI if x != tx + 2 else lfx.RED)
    for x in range(tx + 2, tx + 10):
        put(img, x, 10, lfx.RED_HI)
        put(img, x, 11, lfx.RED)
        put(img, x, 12, lfx.RED_DK if x > tx + 2 else lfx.RED)
    put(img, tx + 10, 11, lfx.STEEL_HI)
    put(img, tx + 10, 12, lfx.STEEL)
    put(img, tx + 7, 9, lfx.STEEL)
    put(img, tx + 7, 8, lfx.STEEL_HI)
    put(img, tx + 1, 8, (60, 100, 200))  # the farmer: denim shirt, plain face, straw hat
    put(img, tx + 1, 7, (60, 100, 200))
    put(img, tx + 2, 8, lfx.SKIN[2])
    put(img, tx + 1, 6, lfx.SKIN[2])
    for dx in (-1, 0, 1, 2):
        put(img, tx + dx, 5, lfx.STRAW)
    put(img, tx + 1, 4, lfx.STRAW_DK)
    put(img, tx, 4, lfx.STRAW)
    # exhaust puffs drift back from the stack
    for k in range(3):
        age = (f + k * 6) % 18
        puff(img, tx + 7 - age * 0.35, 7 - age * 0.22, 0.6 + age * 0.06, (210, 200, 196), 0.5 * (1 - age / 18))


def birds(img, tx: int, f: int) -> None:
    """Two swallows circling above and behind the tractor, wings spread and flapping."""
    for k, (r, sp, ph) in enumerate(((5, 0.11, 0.0), (4, 0.15, 2.4))):
        a = f * sp + ph
        x = tx - 6 + r * 1.6 * math.cos(a)
        y = 3 + 1.2 * math.sin(a)
        up = (f // 3 + k) % 2
        c = (84, 70, 110)
        put(img, x, y, c)
        put(img, x - 1, y - up, c)
        put(img, x + 1, y - up, c)


def render():
    base = backdrop()
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        tx = tractor_x(f)
        pick = tx - 6  # the baler's pickup: windrow ahead of it, bales behind it
        for x in range(max(0, pick), W):
            put(img, x, WINDROW + 1, lfx.WHEAT_HI)
            put(img, x, WINDROW, lfx.WHEAT)
        n = f // BALE_EVERY
        for i in range(1, n + 1):
            bx = tractor_x(i * BALE_EVERY) - 12
            if bx < W + 2:
                bale(img, bx)
        for x in range(W):  # a few glints in the stubble, slow
            if (x * 13 + (f // 5) * 7) % 41 == 0:
                add(img, x, 14 + (x % 2), (255, 236, 150), 0.5)
        tractor(img, tx, f)
        birds(img, tx, f)
        frames.append(img)
    return frames
