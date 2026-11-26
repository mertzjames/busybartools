"""Card backdrop (clock, countdown and principle cards): a seamless 4 s loop. A kente-colored border glides along
the top and bottom rows, and a warm candlelight glow breathes in the middle of a dark, lit plum-brown field.

The live text is drawn ON TOP of this by the app, so rows 1-14 stay calm (text.py has the layout).
"""

import math

from busybar.canvas import add, sec, vgradient
from kfx import kente_border

NAME = "card_bg"
TITLE = "Card backdrop"
SECONDS = 4
LOOP = sec(SECONDS)  # 60 frames
KEYFRAMES = [(0.0, "Card backdrop")]
BORDER_PERIOD = 12  # kente_border's pattern length: the border moves 12 px per loop, so it never jumps


def render():
    bg = vgradient((22, 8, 16), (34, 14, 14))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        breath = 0.5 + 0.5 * math.cos(2 * math.pi * f / LOOP)
        for x in range(72):
            for y in range(1, 15):
                d = math.hypot((x - 35.5) / 30, (y - 7.5) / 9)
                if d < 1:
                    add(img, x, y, (40, 18, 6), (0.35 + 0.15 * breath) * (1 - d))
        off = (f * BORDER_PERIOD) // LOOP
        kente_border(img, 0, off, alpha=0.7)
        kente_border(img, 15, -off + 5, alpha=0.7)
        frames.append(img)
    return frames
