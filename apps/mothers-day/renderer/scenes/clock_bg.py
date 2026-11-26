"""Clock card backdrop: a seamless 4 s loop of a calm plum dusk with a small spray of flowers in each bottom corner
that sway gently, and a few soft glints along the top (docs/DECISIONS.md D7). The time (rows 2-14, columns 16-55)
and the widest date (rows 4-11, columns 6-65) sit over the dark, still middle."""

import math

from busybar.canvas import put, sec
from busybar.party import glitter

import mfx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

# (column, head row, kind, color) for each corner spray; the right one mirrors the left
SPRAY = [(1, 10, "tulip", mfx.PINK), (4, 12, "daisy", mfx.WHITE), (2, 13, "lavender", None)]


def corner(img, f: int, mirror: bool) -> None:
    for i, (x, top, kind, color) in enumerate(SPRAY):
        xx = 71 - x if mirror else x
        sway = 1 if math.sin(2 * math.pi * (f / LOOP + i / 3 + mirror * 0.5)) > 0.6 else 0
        for y in range(top + 2, 16):
            put(img, xx, y, mfx.GREEN_DK if y > top + 3 else mfx.GREEN)
        mfx.bloom(img, kind, xx + sway * (-1 if mirror else 1), top, color)


def render():
    bg = mfx.sky([(0, (18, 8, 34)), (10, (34, 12, 46)), (15, (52, 16, 50))])
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        glitter(img, seed=5, f=f, n=6, period=LOOP, colors=(mfx.PINK_HI, mfx.LAVENDER_HI), ymax=2, strength=0.5)
        corner(img, f, False)
        corner(img, f, True)
        frames.append(img)
    return frames
