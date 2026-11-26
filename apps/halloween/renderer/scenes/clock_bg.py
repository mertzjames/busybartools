"""Clock card backdrop: a seamless 6 s loop of a violet night with cobwebs in both top corners, a little spider
bobbing on its thread at the right, a candle burning in the bottom-left corner and a small jack-o'-lantern in the
bottom-right (docs/DECISIONS.md D7). The glows are steady; only the flame's core and a few carved pixels flicker.
The corner art stays in columns 0-7 and 64-71; the text (time rows 2-13, date rows 4-11) uses columns 8-63."""

import math

from busybar.canvas import H, put, sec
from hfx import (NIGHT_MID, NIGHT_TOP, WEB, candle, candle_glow, cobweb, gradient, pumpkin, pumpkin_glow, stars)

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 6
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

CANDLE = (3, 10)  # (left column, wax top row)
LANTERN = (65, 10)  # 7x6 jack-o'-lantern
SPIDER_X = 68


def spider(img, x: int, y: int) -> None:
    """A tiny lit-violet spider with two orange eye dots, hanging from a thread."""
    for yy in range(0, y):
        put(img, x, yy, WEB, 0.45)
    for dx in (-1, 0, 1):
        put(img, x + dx, y, (130, 90, 180))
    put(img, x, y + 1, (130, 90, 180))
    for dx in (-2, 2):  # legs
        put(img, x + dx, y - 1, (110, 80, 160), 0.8)
        put(img, x + dx, y + 1, (110, 80, 160), 0.8)
    put(img, x - 1, y, (255, 150, 40))
    put(img, x + 1, y, (255, 150, 40))


def render():
    bg = gradient([(0, NIGHT_TOP), (8, NIGHT_MID), (15, (46, 12, 62))])
    cobweb(bg, "tl", 7)
    cobweb(bg, "tr", 7)
    candle_glow(bg, *CANDLE, 0.9)
    pumpkin_glow(bg, *LANTERN, 7, 6, 0.8)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars(img, 7, 10, f, ymax=H, period=LOOP // 2, a=0.35, avoid=lambda x, y: x < 8 or x > 63)
        candle(img, *CANDLE, f)
        pumpkin(img, *LANTERN, 7, 6, "happy", lit=1.0, f=f, seed=3, small=True)
        y = 6 + int(math.floor(1.2 * math.sin(2 * math.pi * f / LOOP) + 0.5))
        spider(img, SPIDER_X, y)
        frames.append(img)
    return frames
