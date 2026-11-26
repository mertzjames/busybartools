"""On-the-day card backdrop: a seamless 4 s loop of deep green with a slow drift of faint gold glints, so the two
big lines of text ("ST. PATRICK'S" / "DAY", "ERIN GO" / "BRAGH") can use the whole display (docs/DECISIONS.md D7).
A thin rainbow edge runs along the very top and bottom rows."""

from busybar.canvas import W, put, sec, vgradient
from busybar.party import glitter
from pfx import GOLD_HI, RAINBOW

NAME = "day_bg"
TITLE = "On-the-day backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "On-the-day backdrop")]


def render():
    bg = vgradient((6, 30, 14), (10, 44, 20))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        for x in range(W):  # a slow rainbow chase along the top and bottom edges, very dim
            c = RAINBOW[int((x + f * 7 * len(RAINBOW) / LOOP) // 3) % len(RAINBOW)]
            put(img, x, 15, c, 0.28)
        glitter(img, 17, f, n=10, period=LOOP, colors=(GOLD_HI,), strength=0.5)
        frames.append(img)
    return frames
