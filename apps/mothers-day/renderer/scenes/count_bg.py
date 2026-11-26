"""Countdown and greeting card backdrop: a seamless 4 s loop of a deep rose field where faint hearts glow and fade
in turn, with a soft pink glow along the bottom (docs/DECISIONS.md D7). The hearts stay dim and steady between
their slow fades, so the words (up to 72 px wide, rows 1-15) read clearly over them."""

import math

from busybar.canvas import W, add, sec

import mfx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

# (center column, top row, size, phase): faint hearts spread across the field
HEARTS = [(4, 2, 5, 0.0), (14, 10, 3, 0.35), (24, 0, 3, 0.7), (35, 11, 5, 0.15), (47, 1, 3, 0.55), (57, 10, 3, 0.85),
          (67, 3, 5, 0.45)]


def render():
    bg = mfx.sky([(0, (40, 8, 30)), (9, (32, 6, 28)), (15, (60, 12, 40))])
    for x in range(W):  # the pink glow along the bottom, strongest in the middle
        k = 0.5 + 0.5 * math.cos(math.pi * (x - 35.5) / 40)
        for y in (13, 14, 15):
            add(bg, x, y, (120, 24, 70), k * (0.2, 0.4, 0.6)[y - 13])
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for cx, top, size, ph in HEARTS:
            k = 0.5 - 0.5 * math.cos(2 * math.pi * (f / LOOP + ph))
            k = round(k * 8) / 8  # a few steps, so the fades stay cheap in the .anim
            mfx.heart(img, cx, top, size, (150, 40, 96), (190, 80, 130), alpha=0.25 + 0.35 * k)
        frames.append(img)
    return frames
