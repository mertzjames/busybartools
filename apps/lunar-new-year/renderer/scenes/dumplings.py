"""Dumplings Steaming: a bamboo steamer puffs on the table; the lid lifts in a cloud of steam to show a row of
dumplings. Chopsticks dip one in sauce, then lift another, and out of it pops the lucky coin
(docs/DECISIONS.md D2: a coin hidden in one dumpling is a New Year's Eve custom).
"""

from __future__ import annotations

import math

from busybar.canvas import W, add, blit, ease_in_out, mix, phase, put, sec, vgradient
from busybar.party import glitter

import lnyfx as fx
import sprites
import textstyle

NAME = "dumplings"
TITLE = "Dumplings Steaming"
SECONDS = 12
KEYFRAMES = [(1.0, "A bamboo steamer puffs"), (2.8, "The lid lifts in a cloud of steam"),
             (4.6, "A row of dumplings"), (6.4, "Dipped in sauce"), (9.0, "Another one"),
             (10.8, "The lucky coin!")]

N = sec(SECONDS)
TABLE = 14
SX0, SX1 = 8, 30  # steamer
DISH = (40, 48)
BAMBOO = (206, 164, 92)
BAMBOO_DARK = (150, 110, 56)
STICK = (220, 170, 100)
DUMPS = [(9, 6), (14, 6), (19, 6), (24, 6)]


def steamer(img) -> None:
    for y in range(9, TABLE):
        for x in range(SX0, SX1 + 1):
            band = y in (9, TABLE - 1)
            put(img, x, y, mix(BAMBOO, (255, 230, 170), 0.2) if band else (BAMBOO if (x + y) % 4 else BAMBOO_DARK))


def lid(img, x0: float, y0: float) -> None:
    """The steamer lid: a low dome whose bottom row is at y0 + 3, with a knob on top."""
    x0, y0 = int(round(x0)), int(round(y0))
    w = SX1 - SX0
    for dy, inset in ((0, 6), (1, 3), (2, 1), (3, 0)):
        for x in range(x0 + inset, x0 + w - inset + 1):
            edge = x in (x0 + inset, x0 + w - inset)
            c = mix(BAMBOO, (255, 230, 170), 0.3) if dy == 3 else (BAMBOO_DARK if edge or dy == 0 else BAMBOO)
            put(img, x, y0 + dy, c)
    for x in range(x0 + w // 2 - 1, x0 + w // 2 + 2):
        put(img, x, y0 - 1, (120, 80, 40))  # knob


def chopsticks(img, tip_x: float, tip_y: float, pinch: bool) -> None:
    """Two sticks from off-screen top-right down to a tip; open a little unless pinching."""
    gap = 0 if pinch else 1
    for k, off in enumerate((0, gap + 1)):
        for i in range(18):
            x = tip_x + off + i * 0.9
            y = tip_y - i * 0.75 - (k * 0)
            put(img, x, y, STICK if i else mix(STICK, (255, 255, 255), 0.2))


def big_coin(img, cx: float, cy: float, f: int) -> None:
    """A round gold coin with a square hole (3x3, the hole shows the wall), glinting."""
    cx, cy = int(round(cx)), int(round(cy))
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == dy == 0:
                continue
            c = fx.GOLD_LIGHT if (dx, dy) == (-1, -1) or (f // 4) % 4 == (dx + dy + 2) % 4 else fx.GOLD
            put(img, cx + dx, cy + dy, c)


def render():
    bg = vgradient((52, 14, 18), (82, 30, 22))
    for x in range(W):  # the table
        put(bg, x, TABLE, (176, 112, 62))
        put(bg, x, TABLE + 1, (130, 76, 40))
    # a white bowl of dark sauce
    for x in range(DISH[0], DISH[1] + 1):
        put(bg, x, 11, (240, 240, 250) if x in DISH else (150, 50, 30))
        if DISH[0] < x < DISH[1]:
            put(bg, x, 12, (230, 230, 240))
        if DISH[0] + 1 < x < DISH[1] - 1:
            put(bg, x, 13, (200, 200, 215))
    # a red paper lantern on the wall, clear of the caption on the right
    fx.lantern(bg, 3, 0, 0, size=1, string=1, seed=5)
    frames = []
    for f in range(N):
        img = bg.copy()
        t = f / 15
        lift = ease_in_out(phase(f, sec(2.0), sec(3.2)))
        slide = ease_in_out(phase(f, sec(3.0), sec(3.8)))
        steam_k = 0.35 + 0.65 * (math.sin(math.pi * phase(f, sec(2.0), sec(5.0))) if 2.0 <= t < 5.0 else 0)
        # dumplings sit inside the steamer rim
        eaten = set()
        held = None
        if t >= 5.0:
            eaten.add(3)
        if t >= 8.4:
            eaten.add(0)
        for i, (x, y) in enumerate(DUMPS):
            if i not in eaten:
                blit(img, sprites.DUMPLING.img(0), x, y - 1)
        steamer(img)
        fx.steam(img, f, SX0 + 2, SX1 - 2, 6 if lift > 0.5 else 4, steam_k, seed=4)
        if lift < 1 or slide < 1:
            lid(img, SX0 - 34 * slide, 5 - 4 * lift)
        # first pick: the right-hand dumpling to the sauce and away
        if 4.4 <= t < 8.0:
            if t < 5.0:  # sticks come down
                p = ease_in_out(phase(f, sec(4.4), sec(5.0)))
                tx, ty, pinch = 52 - (52 - 26) * p, -2 + 9 * p, False
            elif t < 6.0:  # carry to the dish
                p = ease_in_out(phase(f, sec(5.0), sec(6.0)))
                tx, ty, pinch = 26 + (44 - 26) * p, 7 - 3 * math.sin(math.pi * p), True
                held = (tx - 2, ty - 1)
            elif t < 6.8:  # dip twice
                tx, ty, pinch = 44, 9 + (1 if (f // 4) % 2 else 0), True
                held = (tx - 2, ty - 1)
            else:  # up and away
                p = ease_in_out(phase(f, sec(6.8), sec(8.0)))
                tx, ty, pinch = 44 + 14 * p, 9 - 14 * p, True
                held = (tx - 2, ty - 1)
            if held:
                blit(img, sprites.DUMPLING.img(0), held[0], held[1])
            chopsticks(img, tx, ty, pinch)
        # second pick: lifted high, and the coin pops out
        if 8.0 <= t < 12.0:
            if t < 8.4:
                p = ease_in_out(phase(f, sec(8.0), sec(8.4)))
                tx, ty = 52 - (52 - 11) * p, -2 + 9 * p
                chopsticks(img, tx, ty, False)
            else:
                p = ease_in_out(phase(f, sec(8.4), sec(9.4)))
                tx, ty = 11 + 3 * p, 7 - 2 * p
                blit(img, sprites.DUMPLING.img(0), tx - 2, ty - 1)
                chopsticks(img, tx, ty, True)
                if t >= 9.6:  # the coin
                    k = ease_in_out(phase(f, sec(9.6), sec(10.2)))
                    cx, cy = tx - 5 * k, ty - 1 - 2 * k
                    big_coin(img, cx, cy, f)
                    if t < 10.4:
                        fx.flash(img, cx, cy, 1 - phase(f, sec(9.6), sec(10.4)))
                    glitter(img, seed=6, f=f, n=6, period=30, area=(int(cx) - 3, 0, int(cx) + 5, 7), strength=0.9)
                if t >= 10.2:
                    w = 3 + len("LUCKY COIN!") * 4
                    r = int(w * ease_in_out(phase(f, sec(10.2), sec(10.8))))
                    textstyle.draw(img, "LUCKY COIN!", textstyle.STYLES["small"], x=W - w + 1, y=2, reveal=r)
                    add(img, W - w + r, 3, fx.GOLD_LIGHT, 0.6 if r < w else 0)
        frames.append(img)
    return frames
