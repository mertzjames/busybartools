"""Scene: latkes in the pan. Three latkes sizzle in oil over blue gas flames, a spatula flips them golden side up
one by one, and the last one goes onto a plate with applesauce and sour cream.

The pan is drawn from a three-quarter view: an ellipse of oil with a dark rim and a handle out to the left.
"""

from __future__ import annotations

import math

from busybar.canvas import FPS, ease_in_out, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.party import hash01
from hfx import BLUE, BLUE_HI, SILVER, WHITE, glow

NAME = "latkes"
TITLE = "Latkes in the Pan"
SECONDS = 15
KEYFRAMES = [(1.0, "Three latkes sizzle in the oil"), (3.6, "The spatula flips the first"),
             (6.4, "Golden side up"), (11.6, "One goes onto the plate"), (14.0, "With applesauce and sour cream")]

PAN_C, PAN_RX, PAN_RY = (26.0, 8.0), 19.5, 4.2
RIM = (92, 94, 110)
RIM_LO = (56, 58, 72)
OIL = (40, 38, 46)
OIL_HI = (120, 100, 50)
PALE, PALE_EDGE = (214, 190, 120), (170, 140, 80)
GOLDEN, GOLDEN_EDGE = (236, 160, 44), (160, 90, 28)
LATKES = [(16.0, 7.0), (33.0, 7.0), (24.0, 10.0)]
FLIPS = [3.0, 5.6, 8.2]  # spatula starts
PLATE_C = (61.0, 12.0)
T_PLATE = 10.8


def ell(cx, cy, rx, ry, x, y):
    return ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2


def latke(img, cx, cy, ry, golden: float, alpha: float = 1.0) -> None:
    """A latke seen from above (ry 1.6) or edge-on while it flips (ry near 0)."""
    rx = 4.2
    top = mix(PALE, GOLDEN, golden)
    edge = mix(PALE_EDGE, GOLDEN_EDGE, golden)
    if ry < 0.5:
        for x in range(int(cx - rx), int(cx + rx) + 1):
            put(img, x, cy, edge, alpha)
        return
    for y in range(int(cy - ry - 1), int(cy + ry + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            d = ell(cx, cy, rx + 0.4, ry + 0.4, x, y)
            if d <= 1:
                c = edge if d > 0.55 else top
                if d <= 0.55 and hash01(int(x * 7), int(y * 3), 5) > 0.7:  # shredded-potato texture
                    c = mix(c, edge, 0.5)
                put(img, x, y, c, alpha)


def spatula(img, bx, by, alpha=1.0) -> None:
    """Blade (5 px) with its left end at (bx, by); the handle rises to the upper right."""
    for dx in range(5):
        put(img, bx + dx, by, SILVER, alpha)
    for i in range(1, 9):
        put(img, bx + 4 + i, by - i * 0.6, (150, 100, 60) if i > 3 else SILVER, alpha)


def render():
    bg = vgradient((14, 26, 52), (22, 38, 70))
    for y in range(16):  # tiled kitchen wall
        for x in range(72):
            if y % 5 == 4 or x % 6 == 5:
                put(bg, x, y, (30, 46, 80))
    for x in range(72):  # stove top
        put(bg, x, 14, (44, 46, 58))
        put(bg, x, 15, (32, 34, 44))
    cx, cy = PAN_C
    # pan: oil inside, rim, front wall and handle
    for y in range(16):
        for x in range(72):
            d = ell(cx, cy, PAN_RX, PAN_RY, x, y)
            if d <= 1:
                put(bg, x, y, RIM if d > 0.78 and y < cy else (RIM_LO if d > 0.8 else mix(OIL, (64, 56, 46), 1 - d)))
    for x in range(int(cx - PAN_RX + 2), int(cx + PAN_RX - 1)):
        u = (x - cx) / PAN_RX
        yb = int(cy + PAN_RY * math.sqrt(max(0.0, 1 - u * u)) + 0.5)
        put(bg, x, yb, RIM)
        put(bg, x, yb + 1, RIM_LO)
    for x in range(0, int(cx - PAN_RX) + 1):
        put(bg, x, 8, RIM)
        put(bg, x, 9, RIM_LO)
    # plate on the right
    for y in range(16):
        for x in range(50, 72):
            d = ell(PLATE_C[0], PLATE_C[1], 9.5, 2.2, x, y)
            if d <= 1:
                put(bg, x, y, (226, 232, 248) if d > 0.62 else (120, 136, 178))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # blue gas flames peeking out under the pan
        for x in range(10, 43):
            k = hash01(x, f // 2)
            put(img, x, 14, BLUE if k > 0.35 else BLUE_HI, 0.5 + 0.5 * k)
            if k > 0.75:
                put(img, x, 13, BLUE_HI, 0.5)
        # oil shimmer
        for i in range(6):
            sx = cx - 14 + ((f * 0.4 + i * 9) % 28)
            put(img, sx, cy - 2 + (i % 3) * 2, OIL_HI, 0.5)
        # latkes: browned as they cook; flips turn the golden side up
        for k, (lx, ly) in enumerate(LATKES):
            s0 = FLIPS[k]
            t_up, t_land = s0 + 0.9, s0 + 1.5
            golden_top = 0.12 + 0.15 * phase(t, 0, s0) if t < (t_up + t_land) / 2 else 1.0
            y, ry = ly, 1.6
            if t_up <= t < t_land:
                u = (t - t_up) / (t_land - t_up)
                y = ly - 6 * math.sin(math.pi * u)
                ry = 1.6 * abs(math.cos(math.pi * u))
            if k == 2 and t >= T_PLATE:  # the last one goes to the plate
                u = ease_in_out(phase(t, T_PLATE, T_PLATE + 1.0))
                y = lerp(ly, PLATE_C[1] - 1, u) - 7 * math.sin(math.pi * u)
                lx = lerp(lx, PLATE_C[0] - 2, u)
            latke(img, lx, y, ry, golden_top)
            # sizzle: pops and spatters around the edges while it is in the oil
            if not (t_up <= t < t_land) and not (k == 2 and t >= T_PLATE):
                for j in range(3):
                    h = hash01(k, j, f // 2)
                    if h > 0.6:
                        a = (j / 3 + h) * math.pi * 2
                        put(img, lx + 5.2 * math.cos(a), ly + 2.0 * math.sin(a), (255, 240, 190), h)
                    if hash01(k, j, f // 3, 9) > 0.92:
                        put(img, lx + (j - 1) * 3, ly - 3, (255, 220, 150), 0.7)
        # the spatula: in, under, flip, out
        for k, s0 in enumerate(FLIPS):
            lx, ly = LATKES[k]
            if s0 <= t < s0 + 2.1:
                a_in = ease_out(phase(t, s0, s0 + 0.8))
                a_out = phase(t, s0 + 1.5, s0 + 2.1)
                bx = lerp(70, lx - 1, a_in) + 30 * a_out ** 2
                by = ly + 1 - 2 * math.sin(math.pi * phase(t, s0 + 0.8, s0 + 1.2))
                spatula(img, bx, by)
        if t >= T_PLATE:  # spatula carries the last one over
            u = phase(t, T_PLATE - 0.4, T_PLATE + 1.2)
            if u < 1:
                spatula(img, lerp(27, 66, u), lerp(11, 4, u) if u < 0.6 else lerp(4.6, 2, u), 1 - phase(u, 0.8, 1))
        # applesauce and sour cream
        if t >= T_PLATE + 1.6:
            a = ease_out(phase(t, T_PLATE + 1.6, T_PLATE + 2.0))
            for x, y in ((62, 10), (63, 10), (62, 9)):
                put(img, x, y, (255, 252, 240), a)
            b = ease_out(phase(t, T_PLATE + 2.2, T_PLATE + 2.6))
            for x, y in ((66, 12), (67, 12), (66, 11), (67, 11)):
                put(img, x, y, (238, 206, 120), b)
        # steam
        for i in range(5):
            p = ((f / FPS) * 0.35 + i / 5) % 1
            x = cx - 12 + i * 6 + 1.5 * math.sin(p * 6 + i)
            put(img, x, 4 - p * 5, (200, 210, 230), 0.35 * math.sin(math.pi * p))
        glow(img, cx, 8, 16, (40, 24, 4), 0.25)
        frames.append(img)
    return frames
