"""Scene: Special Delivery. A love letter with little white wings flutters across an evening sky in a lazy wave,
circles back and settles in the middle. The heart seal pops, the flap opens, and a letter rises with a red heart on
it. Small hearts float up from the envelope and the words FOR YOU appear."""

import math

from busybar.canvas import FPS, H, W, add, ease_in_out, ease_out, lerp, put, sec
from busybar.fx import Stars, puff
from vfx import (BLUSH, CRIMSON, GOLD_LIGHT, PINK, RED, ROSE, WARM_WHITE, caption, dim_rect, gradient, heart,
                 heart_size, twinkle)

NAME = "love_letter"
TITLE = "Special Delivery"
SECONDS = 14
KEYFRAMES = [(1.5, "A winged letter flutters by"), (4.6, "It circles back"), (7.2, "It lands; the flap opens"),
             (9.0, "A letter rises with a heart"), (12.5, "FOR YOU")]

EW, EH = 15, 10  # envelope size
REST_X, REST_Y = 7, 6  # top-left when it has landed (the caption goes on the right)
LAND, OPEN, RISE = 6.6, 7.4, 8.1  # seconds
PAPER = (255, 238, 220)
PAPER_SHADE = (232, 196, 186)
FOLD = (196, 104, 128)
INSIDE = (150, 44, 86)
LETTER = (255, 206, 222)
LETTER_EDGE = (236, 150, 180)


def path(t: float):
    """(x, y, flying) of the envelope's top-left."""
    if t < 3.6:  # left to right in a lazy wave
        p = t / 3.6
        return lerp(-EW - 2, W + 2, p), 3 + 2.2 * math.sin(p * 2 * math.pi * 1.2), True
    if t < LAND:  # back from the right, gliding down to the rest spot
        p = ease_out((t - 3.6) / (LAND - 3.6))
        return lerp(W + 2, REST_X, p), lerp(1, REST_Y, ease_in_out(p)) - 2.5 * math.sin(p * math.pi), True
    return REST_X, REST_Y, False


def envelope(img, x: float, y: float, flap_open: float, lift: int = 0) -> None:
    """The envelope, seen from the back. flap_open 0 = sealed (flap V down), 1 = flap folded up above it; `lift`
    raises the letter out of the open pocket by that many rows."""
    x0, y0 = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    mid = EW // 2
    if flap_open > 0.5:  # the open flap: a triangle above the envelope, its inside showing
        tall = int(round(4 * (flap_open - 0.5) * 2))
        for r in range(1, tall + 1):
            half = mid * (1 - (r - 1) / tall)
            for xx in range(EW):
                d = abs(xx - mid)
                if d <= half:
                    put(img, x0 + xx, y0 - r, FOLD if d > half - 1 else INSIDE)
    for yy in range(EH):  # the body
        for xx in range(EW):
            c = PAPER
            if xx in (0, EW - 1) or yy == EH - 1:
                c = PAPER_SHADE
            if flap_open > 0.5 and yy < 2:
                c = INSIDE  # the open mouth of the pocket
            put(img, x0 + xx, y0 + yy, c)
    if lift > 0:  # the letter, above the pocket's front
        lx, ly = x0 + 2, y0 + 2 - lift
        for yy in range(ly, y0 + 2):
            for xx in range(lx, lx + EW - 4):
                put(img, xx, yy, LETTER_EDGE if xx in (lx, lx + EW - 5) or yy == ly else LETTER)
        if lift >= 5:
            heart(img, lx + 3, ly + 1, 5, RED, shade=False)
            put(img, lx + 4, ly + 2, PINK)
    for xx in range(EW):  # the side flaps' folds: a shallow ^ from the bottom corners
        d = abs(xx - mid)
        put(img, x0 + xx, y0 + EH - 2 - (mid - d) * 4 // mid, FOLD, 0.85)
    if flap_open <= 0.5:  # the closed flap: a V from the top corners down to the seal
        tall = 5 * (1 - flap_open * 2)
        for xx in range(EW):
            d = abs(xx - mid)
            put(img, x0 + xx, y0 + int(round(tall * (1 - d / mid))), FOLD)


def wings(img, x: float, y: float, f: int) -> None:
    up = (f // 3) % 2 == 0
    x0, y0 = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    for side, sx in ((-1, x0 - 1), (1, x0 + EW)):
        pts = ((0, 1), (1 * side, 0), (2 * side, -1), (1 * side, 1)) if up else ((0, 3), (1 * side, 3), (2 * side, 4), (1 * side, 4))
        for dx, dy in pts:
            put(img, sx + dx, y0 + dy, (250, 250, 255))
        put(img, sx, y0 + 2, (190, 200, 240))


def render():
    bg = gradient([(0, (14, 8, 40)), (9, (54, 20, 72)), (15, (96, 34, 84))])
    for cx, cy, r in ((6, 16, 3), (20, 15.5, 3.5), (34, 16, 3), (48, 15.5, 4), (62, 16, 3.5)):
        puff(bg, cx, cy, r, (140, 70, 120), 0.5)
    stars = Stars(seed=31, n=14, ymax=8, period=FPS * 3, color=(230, 220, 255), dim=0.1, bright=0.65)
    # little hearts rise on both sides of the envelope once the letter is out: (x, start s, color, width)
    floaters = [((1, 23, 3, 24, 0, 23, 2, 24)[i], 9.0 + i * 0.6, (ROSE, PINK, RED, BLUSH)[i % 4], (5, 3, 3, 5)[i % 4])
                for i in range(8)]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        x, y, flying = path(t)
        if flying:
            y += 0.6 * math.sin(f * 0.9)
        flap = 0.0 if t < OPEN else min(1.0, (t - OPEN) / 0.6)
        lift = int(round(7 * ease_out(min(1.0, (t - RISE) / 1.2)))) if t >= RISE else 0
        envelope(img, x, y, flap, lift)
        if flying:
            wings(img, x, y, f)
        if t < OPEN + 0.2:  # the heart seal, which pops as the flap opens
            sx, sy = int(math.floor(x + 0.5)) + EW // 2 - 2, int(math.floor(y + 0.5)) + 3
            heart(img, sx, sy, 5, CRIMSON, shade=False)
            put(img, sx + 1, sy + 1, PINK)
        elif t < OPEN + 0.6:
            k = 1 - (t - OPEN - 0.2) / 0.4
            for dx, dy in ((0, 0), (-2, -1), (2, -1), (-3, 1), (3, 1)):
                add(img, REST_X + EW // 2 + dx, REST_Y + 4 + dy, WARM_WHITE, k)
        if t > RISE + 1.0:  # little hearts float up from the letter
            for i, (hx, t0, c, w) in enumerate(floaters):
                age = t - t0
                if 0 <= age < 5.5:
                    hy = H - age * 3.4
                    heart(img, hx + 0.8 * math.sin(age * 2 + i), hy, w, c)
        if t > 11.0:
            a = min(1.0, (t - 11.0) / 0.6)
            dim_rect(img, 30, 3, 71, 12, 0.55 * a, feather=2)
            caption(img, "FOR YOU", 5, WARM_WHITE, PINK, (96, 8, 44), a, x=31)
            for i, (tx, ty) in enumerate(((29, 2), (70, 2), (49, 14), (68, 14))):
                twinkle(img, tx, ty, f, GOLD_LIGHT, 0.85 * a, period=24, ph=i / 4)
        frames.append(img)
    return frames
