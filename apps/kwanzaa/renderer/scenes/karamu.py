"""Scene: The Karamu Feast (December 31, the sixth day). A long table with a kente runner and a small kinara with
six candles lit. KARAMU / DEC 31 comes up over the empty table; the family takes their seats from both sides; the
dishes arrive one by one; then everyone raises their arms and cheers."""

from __future__ import annotations

import math

from busybar.canvas import FPS, add, ease_out, lerp, mix, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles
from busybar.party import glitter
from kfx import (GOLD, GOLD_HI, GREEN, LIGHT_ORDER, RED, ROOM_BOTTOM, ROOM_TOP, SKIN, WOOD, WOOD_HI, Kinara,
                 fruit, kente_cell, person, room_glow)

NAME = "karamu"
TITLE = "The Karamu Feast"
SECONDS = 16
KEYFRAMES = [(1.6, "KARAMU, DEC 31"), (4.4, "The family sits down"), (7.0, "The dishes arrive"),
             (10.4, "A feast on the table"), (13.4, "Everyone cheers")]

TABLE_Y = 11  # tabletop row
KIN = Kinara(8, 10, small=True)
LIT = LIGHT_ORDER[:6]  # the sixth day
T_TITLE_OUT = 3.2
T_SIT0 = 3.0
T_DISH0, T_DISH_STEP = 5.6, 0.8
T_CHEER = 11.0

# seated family: final x, skin, cloth, accent, head, headwear, entering from the left (-1) or right (+1)
FAMILY = [
    (19, SKIN[3], (200, 50, 40), GOLD, "wrap", (40, 150, 70), -1),
    (30, SKIN[0], (40, 140, 70), GOLD, "kufi", (210, 50, 50), -1),
    (44, SKIN[2], (220, 170, 40), RED, "hair", None, 1),
    (55, SKIN[1], (130, 50, 130), GOLD, "wrap", (240, 190, 50), 1),
]


def dish(img, kind: str, x: int, y: int, f: int) -> None:
    """A dish sitting on the table, its base on row y (2-3 rows tall, 4-5 wide)."""
    if kind == "pot":  # a stew pot with steam
        for dx in range(5):
            put(img, x + dx, y, (150, 70, 40))
            put(img, x + dx, y - 1, (190, 96, 50) if dx else (220, 130, 70))
        put(img, x - 1, y - 1, (120, 60, 34))
        put(img, x + 5, y - 1, (120, 60, 34))
        for k in range(2):
            ph = (f / 10 + k * 0.5) % 1.0
            put(img, x + 1 + 2 * k + round(math.sin(ph * 6)), y - 2 - round(ph * 4), (220, 210, 200), 0.5 * (1 - ph))
    elif kind == "greens":
        for dx in range(4):
            put(img, x + dx, y, (220, 220, 230))
            put(img, x + dx, y - 1, (60, 170, 70) if dx % 2 else (40, 130, 50))
        put(img, x + 1, y - 2, (90, 200, 90))
    elif kind == "yams":
        for dx in range(5):
            put(img, x + dx, y, (200, 200, 210))
        fruit(img, "yam", x, y - 2)
        fruit(img, "yam", x + 2, y - 1)
    elif kind == "cornbread":
        for dx in range(4):
            put(img, x + dx, y, (200, 150, 60))
            put(img, x + dx, y - 1, (255, 210, 90) if dx % 2 else (240, 186, 70))
    elif kind == "fruit":
        for dx in range(5):
            put(img, x + dx, y, (214, 170, 96) if dx % 2 else (196, 150, 78))
        fruit(img, "orange", x, y - 2)
        fruit(img, "apple", x + 2, y - 2)
        fruit(img, "banana", x + 1, y - 3)
    elif kind == "pie":
        for dx in range(5):
            put(img, x + dx, y, (190, 120, 60))
            put(img, x + dx, y - 1, (230, 120, 40) if 0 < dx < 4 else (200, 140, 70))


DISHES = [("pot", 21), ("greens", 28), ("yams", 34), ("cornbread", 41), ("fruit", 47), ("pie", 54), ("greens", 61)]


def table(img) -> None:
    for x in range(1, 71):
        put(img, x, TABLE_Y, WOOD_HI if x % 5 else WOOD)
        for y in (TABLE_Y + 1, TABLE_Y + 2):  # a kente runner hanging over the edge
            put(img, x, y, mix(kente_cell(x, y + 3), (0, 0, 0), 0.25))
    for x in (3, 68):  # legs
        for y in range(TABLE_Y + 3, 16):
            put(img, x, y, WOOD)


def render():
    bg = vgradient(ROOM_TOP, ROOM_BOTTOM)
    for x in range(72):  # floor
        for y in (14, 15):
            put(bg, x, y, (70, 34, 20) if (x + y) % 4 else (58, 28, 16))
    sp = Particles(seed=51)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        room_glow(img, KIN, LIT, f, 0.9)
        cheer = t >= T_CHEER
        # the family slides in and sits behind the table
        for i, (x, skin, cloth, accent, head, hw, side) in enumerate(FAMILY):
            t0 = T_SIT0 + i * 0.35
            if t < t0:
                continue
            u = ease_out(min(1.0, (t - t0) / 1.2))
            xx = round(lerp(x + side * 40, x, u))
            hop = 1 if (u < 1 and (f // 3) % 2) else 0
            arms = (0.02, 0.02)
            bob = 0
            if cheer:
                beat = int((t - T_CHEER) * 3 + i) % 2
                arms = (0.48, 0.42) if beat else (0.4, 0.48)
                bob = beat
            person(img, xx, TABLE_Y + 1 - hop - bob, skin, cloth, accent, head=head, wrap=hw, arms=arms, seated=True)
        table(img)
        KIN.draw(img, f, lit=LIT)
        # dishes appear one by one with a sparkle
        for k, (kind, x) in enumerate(DISHES):
            td = T_DISH0 + k * T_DISH_STEP
            if t >= td:
                dish(img, kind, x, TABLE_Y - 1, f)
                if f == sec(td):
                    sp.emit(x + 2, TABLE_Y - 3, 8, vx=(-0.8, 0.8), vy=(-1.0, -0.2), life=(5, 10), colors=SPARKLE,
                            glow=True)
        sp.step_draw(img)
        if cheer:
            glitter(img, 52, f, n=12, period=40, colors=(GOLD_HI, (255, 255, 255)), ymax=3, strength=0.8)
            for k, (kind, x) in enumerate(DISHES):  # the candlelight dances on the dishes
                add(img, x + 1, TABLE_Y - 2, (255, 230, 160), 0.25 * max(0.0, math.sin(t * 5 + k)))
        # title over the empty table at the start
        if t < T_TITLE_OUT + 0.6:
            a = min(1.0, t / 0.6) * (1.0 if t < T_TITLE_OUT else 1 - (t - T_TITLE_OUT) / 0.6)
            x0 = (72 - (text_width("KARAMU") + 4 + text_width("DEC 31", "tiny"))) // 2
            end = draw_text(img, "KARAMU", x0, 2, None, gradient=((255, 236, 150), (240, 160, 40)),
                            shadow=(120, 20, 20), alpha=a)
            draw_text(img, "DEC 31", end + 4, 4, (200, 255, 190), font="tiny", shadow=(16, 60, 24), alpha=a)
            for x in range(x0, end + 4 + text_width("DEC 31", "tiny"), 3):
                add(img, x, 10, (RED, GOLD, GREEN)[(x // 3) % 3], 0.5 * a)
        frames.append(img)
    return frames
