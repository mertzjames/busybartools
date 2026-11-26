"""Scene: The Haunted House. A crooked old house stands on a hill under a full moon. Its windows light up one by
one (candle yellow, one spooky green, one purple), a shadowy figure glides past the green window, and the front
door creaks open in fits and starts, spilling orange light. Three bats flutter out and across the moon."""

import math

from busybar.canvas import FPS, H, W, add, blit, mix, put, sec
from hfx import (NIGHT_MID, NIGHT_TOP, frame_t, full_moon, glow, gradient, in_moon, quant, stars)
from sprites import BAT, HOUSE, HOUSE_X, HOUSE_WINDOWS

NAME = "haunted"
TITLE = "The Haunted House"
SECONDS = 16
KEYFRAMES = [(1.0, "A dark house on the hill"), (3.4, "The windows light up"), (5.8, "...one by one"),
             (7.6, "Someone passes the green window"), (10.4, "The door creaks open"),
             (12.6, "Bats flutter out"), (14.6, "Across the moon")]

MOON = (13.0, 5.0, 4.6)
# window id -> (light-up second, color)
LIGHTS = {
    "1": (2.0, (255, 214, 90)),
    "2": (2.8, (255, 190, 70)),
    "3": (3.5, (140, 255, 90)),   # the spooky green one: the figure passes it
    "4": (4.2, (255, 214, 90)),
    "5": (4.9, (190, 110, 255)),  # purple
    "6": (5.5, (255, 190, 70)),
    "7": (6.1, (255, 214, 90)),
}
PASS = (6.8, 9.0)  # the figure crosses window 3
# door opening: (second, open fraction) keyframes, in fits and starts (a creak)
DOOR = [(9.4, 0.0), (9.8, 0.34), (10.4, 0.34), (10.7, 0.67), (11.4, 0.67), (11.7, 1.0)]
BATS_AT = 12.0


def door_open(t: float) -> float:
    if t <= DOOR[0][0]:
        return 0.0
    for (t0, a), (t1, b) in zip(DOOR, DOOR[1:]):
        if t < t1:
            return a + (b - a) * (t - t0) / (t1 - t0)
    return 1.0


def bat_path(i: int, t: float):
    """Bats leave the door, rise, and swoop left across the moon."""
    age = t - BATS_AT - i * 0.45
    if age < 0:
        return None
    dx, dy = HOUSE_WINDOWS["D"][0][0] + HOUSE_X, HOUSE_WINDOWS["D"][0][1]
    x = dx - age * (9 + 2 * i) + 3 * math.sin(age * 2.5 + i)
    y = dy - 1 - age * (5.5 - i) + 1.5 * math.sin(age * 4 + i * 2)
    y = max(y, 1 + i * 2 + 1.2 * math.sin(age * 3 + i))
    if x < -8:
        return None
    return x, y


def render():
    bg = gradient([(0, NIGHT_TOP), (9, NIGHT_MID), (15, (66, 22, 80))])
    full_moon(bg, *MOON, halo=0.7)
    # the hill: a lit violet mound under the house, with a moonlit rim along its top
    for x in range(W):
        top = 13.5 - 2.6 * math.exp(-((x - 44) / 18) ** 2) + 0.4 * math.sin(x * 0.5)
        top = int(math.floor(top + 0.5))
        for y in range(top, H):
            put(bg, x, y, (40, 20, 56))
        put(bg, x, top, (78, 52, 104))
    # a bare tree on the right
    for y in range(6, 14):
        put(bg, 64, y, (96, 70, 104))
    for x, y in ((65, 8), (66, 7), (67, 6), (63, 9), (62, 8), (61, 7), (65, 11), (66, 10), (67, 10), (68, 9),
                 (63, 5), (64, 5), (62, 4)):
        put(bg, x, y, (96, 70, 104))
    blit(bg, HOUSE.img(0), HOUSE_X, 0)
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 5, 16, f, ymax=8, avoid=lambda x, y: in_moon(x, y, *MOON) or HOUSE_X <= x < HOUSE_X + 26)
        # windows
        for wid, (t_on, color) in LIGHTS.items():
            k = quant((t - t_on) / 0.3, 6)
            if k <= 0:
                continue
            if wid == "6" and 13.0 < t < 13.6 and int(t * FPS) % 3 == 0:  # a flicker
                k *= 0.4
            cells = HOUSE_WINDOWS[wid]
            for cx, cy in cells:
                put(img, HOUSE_X + cx, cy, mix((30, 12, 30), color, k))
            if wid == "3" and PASS[0] < t < PASS[1]:  # the figure: a head and shoulders gliding past
                u = (t - PASS[0]) / (PASS[1] - PASS[0])
                xs = [c[0] for c in cells]
                ys = [c[1] for c in cells]
                fx = min(xs) - 3 + u * (max(xs) - min(xs) + 6)
                for cx, cy in cells:
                    dx = cx - fx
                    head = abs(dx) <= 0.6 and cy == min(ys)
                    body = abs(dx) <= 1.2 and cy > min(ys)
                    if head or body:
                        put(img, HOUSE_X + cx, cy, (40, 14, 56))
        # the door swings open on its left hinge, showing warm light inside
        k = door_open(t)
        cells = HOUSE_WINDOWS["D"]
        x0 = min(c[0] for c in cells)
        dw = max(c[0] for c in cells) - x0 + 1
        panel = int(math.floor(dw * (1 - k) + 0.5))
        for cx, cy in cells:
            if cx - x0 < panel:
                c = (110, 60, 50) if cx - x0 < panel - 1 or panel == dw else (80, 40, 40)
            else:
                c = mix((255, 150, 40), (255, 220, 120), 0.3 + 0.3 * math.sin(f * 0.7))
            put(img, HOUSE_X + cx, cy, c)
        if k > 0:
            glow(img, HOUSE_X + x0 + dw / 2, 15, 4 + 2 * quant(k, 3), (90, 40, 0), 0.5 * quant(k, 3))
        for i in range(3):
            p = bat_path(i, t)
            if p:
                blit(img, BAT.img((f // 2 + i) % len(BAT), flip=True), p[0], p[1])
        frames.append(img)
    return frames
