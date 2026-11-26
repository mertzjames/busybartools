"""Clock card backdrop: a seamless 4 s loop of a calm night: deep navy with a few soft stars along the top and the
flag's new horizon along the bottom, a lit red arc under a blue band that rises at the two ends
(docs/DECISIONS.md D8). The middle stays dark and still, so the time and date read clearly."""

from busybar.canvas import W, put, sec, vgradient
from busybar.fx import Stars

import jfx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]
TEXT_GAP = (6, 65)  # the time and date stay inside these columns, clear of the rising arc at the ends


def horizon(img, low: int = 15, rise: int = 3, edge: int = 6, full: bool = True) -> None:
    """A red arc along the bottom with a blue band over it, rising `rise` rows within `edge` columns of each end.
    full=False draws only the rising ends (for cards whose text reaches the bottom row)."""
    for x in range(W):
        d = min(x, W - 1 - x)
        if not full and d >= edge:
            continue
        lift = rise * max(0, edge - d) / edge
        top = low - int(lift + 0.5)
        for y in range(top, 16):
            put(img, x, y, jfx.FLAG_RED_DK if y > top else jfx.FLAG_RED)
        if top - 1 >= 0 and d < edge + 2:
            put(img, x, top - 1, jfx.FLAG_BLUE, 0.7)


def render():
    bg = vgradient((8, 10, 38), (14, 16, 54))
    horizon(bg)
    stars = Stars(seed=19, n=8, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.1, bright=0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
