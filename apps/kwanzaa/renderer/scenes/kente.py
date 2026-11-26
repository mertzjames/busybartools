"""Scene: The Kente Weave. A shuttle flies back and forth across a loom, weaving an original kente-inspired cloth
in red, black, green and gold from the bottom up (docs/DECISIONS.md D9). The finished cloth glides past with gold
threads glinting, then HAPPY / KWANZAA appears over it."""

from __future__ import annotations

import math

from busybar.canvas import FPS, add, ease_in_out, mix, new, put, sec
from busybar.font import draw_text, text_width
from busybar.party import glitter
from kfx import GOLD_HI, WOOD_HI, dim_rect, kente_cell

NAME = "kente"
TITLE = "The Kente Weave"
SECONDS = 14
KEYFRAMES = [(0.6, "An empty loom"), (2.6, "The shuttle weaves row by row"), (5.4, "The pattern grows"),
             (8.2, "The cloth glides past"), (12.0, "HAPPY / KWANZAA")]

T_WEAVE0 = 0.6
ROW_S = 0.42  # seconds per woven row (one pass of the shuttle)
T_WOVEN = T_WEAVE0 + 16 * ROW_S  # 7.32 s
T_SCROLL = 7.6
T_CAPTION = 10.2
OFFSET0 = 4  # the first view of the cloth starts mid-strip


def warp(x: int, y: int) -> tuple:
    """An unwoven warp thread: the strip's color, dim, every other column."""
    c = kente_cell(x + OFFSET0, y)
    return mix(c, (0, 0, 0), 0.72) if x % 2 == 0 else mix(c, (0, 0, 0), 0.88)


def render():
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = new()
        px = img.load()
        if t < T_WOVEN:
            done = max(0.0, (t - T_WEAVE0) / ROW_S)  # rows woven so far, fractional
            full = int(done)
            frac = done - full
            for y in range(16):
                row = 15 - y  # weave from the bottom up
                for x in range(72):
                    if row < full:
                        c = kente_cell(x + OFFSET0, y)
                    elif row == full:
                        # the shuttle's pass: left to right on even rows, right to left on odd rows
                        edge = frac * 74 - 1
                        woven = x <= edge if row % 2 == 0 else x >= 71 - edge
                        c = kente_cell(x + OFFSET0, y) if woven else warp(x, y)
                    else:
                        c = warp(x, y)
                    px[x, y] = c + (255,)
            if t >= T_WEAVE0 and full < 16:
                y = 15 - full
                edge = frac * 74 - 1
                sx = edge if full % 2 == 0 else 71 - edge
                for dx in range(-2, 3):  # the shuttle: a pale wooden bobbin, bright against the cloth
                    put(img, sx + dx, y, (240, 214, 170) if abs(dx) < 2 else WOOD_HI)
                add(img, sx, y - 1, GOLD_HI, 0.7)
                if y + 1 < 16:
                    put(img, sx, y + 1, (255, 255, 230), 0.6)
        else:
            u = ease_in_out(min(1.0, (t - T_SCROLL) / 2.2)) if t >= T_SCROLL else 0.0
            drift = (t - T_SCROLL - 2.2) * 4 if t > T_SCROLL + 2.2 else 0.0
            off = OFFSET0 + round(u * 24 + drift)
            for y in range(16):
                for x in range(72):
                    px[x, y] = kente_cell(x + off, y) + (255,)
            # a gentle sheen sweeping across the cloth
            sweep = (t - T_WOVEN) * 20 - 10
            for y in range(16):
                for x in range(72):
                    d = abs(x - sweep - y * 0.6)
                    if d < 3:
                        add(img, x, y, (60, 50, 30), 0.5 * (1 - d / 3))
            glitter(img, 71, f, n=14, period=50, colors=(GOLD_HI, (255, 255, 255)), strength=0.75)
        if t >= T_CAPTION:
            a = min(1.0, (t - T_CAPTION) / 0.6)
            dim_rect(img, 0, 0, 71, 15, 0.55 * a)
            dim_rect(img, 8, 0, 63, 15, 0.45 * a)  # a darker panel behind the words
            draw_text(img, "HAPPY", (72 - text_width("HAPPY", "tiny")) // 2, 1, (200, 255, 190), font="tiny",
                      shadow=(16, 60, 24), alpha=a)
            draw_text(img, "KWANZAA", (72 - text_width("KWANZAA")) // 2, 8, None,
                      gradient=((255, 236, 150), (240, 160, 40)), shadow=(120, 20, 20), alpha=a)
            if t < T_CAPTION + 0.8:
                k = math.sin(math.pi * (t - T_CAPTION) / 0.8)
                add(img, 36, 7, (255, 255, 255), 0.3 * k)
        frames.append(img)
    return frames

