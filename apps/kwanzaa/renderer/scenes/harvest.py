"""Scene: The Harvest (mazao). A field of corn at sunset. Fruit and vegetables arc in from both sides and pile up in
a woven basket, then three ears of corn (muhindi) drop in behind them. MAZAO / THE HARVEST."""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, add, ease_out, lerp, mix, put, sec, vgradient
from busybar.font import draw_text
from busybar.fx import SPARKLE, Particles
from busybar.party import glitter
from kfx import GOLD_HI, basket, corn, dim_rect, fruit

NAME = "harvest"
TITLE = "The Harvest"
SECONDS = 14
KEYFRAMES = [(1.0, "A field of corn at sunset"), (3.6, "The harvest arcs into the basket"),
             (7.5, "The basket fills"), (9.4, "Muhindi: ears of corn"), (12.5, "MAZAO / THE HARVEST")]

GROUND = 14
BX, BY, BW = 44, 11, 18  # basket: top-left and width
T_THROW0, T_THROW_STEP = 1.4, 0.5
T_CORN = (7.8, 8.3, 8.8)
T_CAPTION = 10.2

# Where each piece lands (bottom layer first) and what it is; thrown alternately from the left and the right.
PILE = [("orange", 46, 9), ("yam", 49, 9), ("apple", 53, 9), ("lime", 56, 9), ("orange", 59, 9),
        ("plum", 48, 7), ("banana", 51, 7), ("apple", 56, 7), ("yam", 52, 5), ("orange", 55, 5)]
CORN_X = (47, 52, 57)


def field(img, f: int) -> None:
    """Rows of corn stalks across the field, swaying gently, with gold tassels catching the light."""
    rng = random.Random(11)
    stalks = [(x, rng.randint(6, 9), rng.random()) for x in range(1, 72, 4)]
    for x, top, ph in stalks:
        sway = 0.8 * math.sin(2 * math.pi * (f / 45 + ph))
        for y in range(top, GROUND):
            k = (y - top) / max(1, GROUND - top)
            xx = x + sway * (1 - k)
            behind = BX - 3 <= x <= BX + BW + 2  # keep the stalks behind the basket quiet
            a = 0.45 if behind else 1.0
            put(img, xx, y, mix((58, 104, 34), (30, 60, 22), k), a)
            if (y - top) % 3 == 1:  # leaves
                put(img, xx + (1 if (y + x) % 2 else -1), y, (50, 92, 30), 0.7 * a)
        put(img, x + sway, top - 1, (200, 150, 60), 0.9)


def render():
    bg = vgradient((26, 10, 40), (120, 48, 34))
    for x in range(72):  # the sun setting behind the field
        for y in range(16):
            d = math.hypot(x - 22, y - 10)
            if d < 3.6:
                put(bg, x, y, (255, 170, 80), 1.0 if d < 2.8 else 0.45)
            elif d < 7:
                add(bg, x, y, (90, 40, 10), 0.4 * (1 - (d - 3.6) / 3.4))
    for x in range(72):
        for y in range(GROUND, 16):
            put(bg, x, y, (96, 52, 30) if (x + y) % 3 else (80, 42, 24))
    sp = Particles(seed=21)
    throws = []
    for i, (kind, lx, ly) in enumerate(PILE):
        t0 = T_THROW0 + i * T_THROW_STEP
        left = i % 2 == 0
        throws.append((kind, lx, ly, t0, -4.0 if left else 74.0, 9.0 if left else 8.0))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        field(img, f)
        # ears of corn drop in behind the fruit
        for x, tc in zip(CORN_X, T_CORN):
            if t >= tc:
                u = ease_out(min(1.0, (t - tc) / 0.35))
                y = lerp(-8, 4, u)
                corn(img, x, round(y), h=7)
                if abs(t - tc - 0.35) < 0.5 / FPS:
                    sp.emit(x + 1, 9, 5, vx=(-0.6, 0.6), vy=(-0.8, -0.2), life=(4, 8), colors=SPARKLE, glow=True)
        # landed fruit, then fruit in flight
        for kind, lx, ly, t0, sx, sy in throws:
            dur = 0.7
            if t < t0:
                continue
            u = (t - t0) / dur
            if u >= 1:
                bounce = 1 if 1 <= u < 1.15 else 0
                fruit(img, kind, lx, ly - bounce)
            else:
                x = lerp(sx, lx, u)
                y = lerp(sy, ly, u) - 9 * math.sin(math.pi * u)
                fruit(img, kind, x, y)
        basket(img, BX, BY, w=BW, h=4)
        if t >= T_CAPTION - 0.6:
            for k in range(3):
                put(img, BX + 2 + k * 6, BY + 1, (226, 186, 110), 0.8)  # basket weave highlight
            glitter(img, 23, f, n=8, period=40, area=(BX, 2, BX + BW, 11), colors=(GOLD_HI, (255, 255, 255)),
                    strength=0.7)
        sp.step_draw(img)
        if t >= T_CAPTION:
            a = min(1.0, (t - T_CAPTION) / 0.6)
            dim_rect(img, 0, 0, 41, 15, 0.55 * a, feather=5)
            draw_text(img, "MAZAO", 4, 1, None, font="big", gradient=((255, 236, 150), (240, 160, 40)),
                      shadow=(110, 20, 20), alpha=a)
            draw_text(img, "THE HARVEST", 1, 10, (200, 255, 190), font="tiny", shadow=(16, 60, 24), alpha=a)
            if t < T_CAPTION + 0.2:
                add(img, 20, 4, (255, 255, 255), 0.3)
        frames.append(img)
    return frames
