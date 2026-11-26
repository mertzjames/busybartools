"""Scene: A Box of Chocolates. A red gift box tied with a gold ribbon sits on the table. The lid lifts away to show
two rows of chocolates in gold cups: milk, dark, white, strawberry and heart-shaped ones. One at a time they are
picked (each lifts out with a sparkle) until a single heart-shaped chocolate is left, which twinkles."""

import math

from busybar.canvas import FPS, H, W, add, ease_in, ease_in_out, lerp, put, sec
from vfx import GOLD, GOLD_LIGHT, PINK, RED, ROSE, WARM_WHITE, gradient, heart, twinkle

NAME = "chocolates"
TITLE = "A Box of Chocolates"
SECONDS = 14
KEYFRAMES = [(1.0, "A box tied with a gold ribbon"), (3.0, "The lid lifts away"), (5.0, "Twelve chocolates"),
             (8.5, "Picked one at a time"), (12.8, "The last one: a heart")]

BX, BY, BW, BH = 17, 1, 37, 14  # box (and lid) footprint
LIFT_AT, LIFT_END = 1.8, 3.2
PICK_AT, PICK_EVERY = 4.6, 0.62
CELL_W, CELL_H = 6, 6

# The chocolates, left to right, top row then bottom: (kind). The last heart (index 8) is never picked.
KINDS = ["milk", "heart", "white", "dark", "berry", "milk",
         "dark", "berry", "lastheart", "milk", "white", "dark"]
ORDER = [4, 0, 11, 2, 6, 9, 1, 5, 10, 3, 7]  # picking order (index 8 stays)

COLORS = {
    "milk": ((178, 108, 62), (214, 150, 96)),    # body, drizzle/highlight
    "dark": ((128, 70, 50), (196, 128, 96)),
    "white": ((250, 234, 206), (226, 190, 150)),
    "berry": ((255, 140, 170), (255, 210, 224)),
    "heart": ((220, 30, 60), (255, 130, 160)),
    "lastheart": ((220, 30, 60), (255, 130, 160)),
}
CUP = (176, 120, 44)
SATIN = (54, 4, 20)
BOX = (200, 24, 54)
BOX_DARK = (140, 14, 40)
LID = (226, 34, 64)


def cell_xy(i: int) -> tuple[int, int]:
    col, row = i % 6, i // 6
    return BX + 1 + col * CELL_W, BY + 1 + row * CELL_H


def chocolate(img, x: int, y: int, kind: str, a: float = 1.0) -> None:
    """One 5x5 piece (rounded, or heart-shaped) with its top-left at (x, y)."""
    body, hi = COLORS[kind]
    if kind in ("heart", "lastheart"):
        heart(img, x, y, 5, body, a, shade=False)
        put(img, x + 1, y + 1, hi, a)
        return
    dark = tuple(int(v * 0.75) for v in body)
    for dx in range(5):
        for dy in range(5):
            if (dx in (0, 4)) and (dy in (0, 4)):
                continue
            put(img, x + dx, y + dy, dark if dy == 4 or dx == 4 else body, a)
    if kind == "white":
        for dx in (1, 2, 3):
            put(img, x + dx, y + 2, hi, a)
    elif kind == "berry":
        put(img, x + 1, y + 1, hi, a)
        put(img, x + 3, y + 2, hi, a)
        put(img, x + 2, y + 3, hi, a)
    else:  # a zigzag drizzle
        for dx, dy in ((1, 1), (2, 2), (3, 1), (1, 3), (3, 3)):
            put(img, x + dx, y + dy, hi, a)


def lid(img, x: int, y: int) -> None:
    for yy in range(BH):
        for xx in range(BW):
            c = LID if 0 < yy < BH - 1 and 0 < xx < BW - 1 else BOX_DARK
            put(img, x + xx, y + yy, c)
    cx, cy = x + BW // 2, y + BH // 2
    for xx in range(BW):  # ribbon
        put(img, x + xx, cy, GOLD)
    for yy in range(BH):
        put(img, cx, y + yy, GOLD)
    for dx, dy in ((-3, -2), (-2, -2), (-2, -1), (-1, -1), (1, -1), (2, -1), (2, -2), (3, -2),
                   (-3, -1), (3, -1), (-1, 1), (-2, 2), (1, 1), (2, 2)):  # the bow's loops and tails
        put(img, cx + dx, cy + dy, GOLD_LIGHT if dy < 0 else GOLD)
    put(img, cx, cy, GOLD_LIGHT)


def box(img) -> None:
    for yy in range(BH):
        for xx in range(BW):
            edge = xx in (0, BW - 1) or yy in (0, BH - 1)
            put(img, BX + xx, BY + yy, BOX if edge else SATIN)
    for i in range(12):
        x, y = cell_xy(i)
        for dx in range(5):
            for dy in range(5):
                if dx in (0, 4) or dy in (0, 4):
                    put(img, x + dx, y + dy, CUP)


def render():
    bg = gradient([(0, (26, 4, 26)), (10, (52, 10, 44)), (15, (70, 16, 50))])
    for x in range(W):  # the table edge
        put(bg, x, 15, (110, 40, 70))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        box(img)
        for i, kind in enumerate(KINDS):
            x, y = cell_xy(i)
            if i in ORDER:
                k = ORDER.index(i)
                t0 = PICK_AT + k * PICK_EVERY
                if t >= t0 + 0.5:
                    continue
                if t >= t0:  # lifts out and fades, with a sparkle
                    p = (t - t0) / 0.5
                    chocolate(img, x, y - int(round(4 * ease_in(p))), kind, 1 - p * 0.8)
                    add(img, x + 2 + 2 * p, y - 1 - 3 * p, WARM_WHITE, 0.9 * (1 - p))
                    add(img, x + 2 - 2 * p, y - 1 - 3 * p, GOLD_LIGHT, 0.7 * (1 - p))
                    continue
            chocolate(img, x, y, kind)
        if t < LIFT_END:  # the lid lifts and slides up out of the frame
            p = ease_in_out((t - LIFT_AT) / (LIFT_END - LIFT_AT)) if t > LIFT_AT else 0.0
            wob = int(round(0.6 * math.sin(t * 12))) if 1.0 < t < LIFT_AT else 0  # a little shake first
            lid(img, BX + wob, BY - int(round(p * (BH + BY + 2))))
            if t < LIFT_AT:
                for i, (x, y) in enumerate(((BX - 3, 2), (BX + BW + 2, 4), (BX + BW + 1, 12), (BX - 2, 12))):
                    twinkle(img, x, y, f, GOLD_LIGHT, 0.8, period=20, ph=i / 4)
        end = PICK_AT + len(ORDER) * PICK_EVERY + 0.4
        if t > end:  # the last heart glows and twinkles
            x, y = cell_xy(8)
            k = min(1.0, (t - end) / 0.6)
            for i, (dx, dy) in enumerate(((-1, -1), (6, 0), (2, -1), (6, 5))):
                twinkle(img, x + dx, y + dy, f, GOLD_LIGHT, 0.9 * k, period=18, ph=i / 4)
            for i in range(4):  # little hearts rise from it
                age = t - end - 0.4 - i * 0.6
                if 0 <= age < 2.5:
                    heart(img, x + 1 + (i % 2) * 2 - 1, y - 3 - age * 2.4, 3, (ROSE, PINK)[i % 2])
        frames.append(img)
    return frames
