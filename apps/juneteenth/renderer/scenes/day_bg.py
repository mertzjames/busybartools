"""On-the-day card backdrop: a seamless 4 s loop for the Juneteenth greetings: deep navy with red, white, blue and
gold glints twinkling in the two edge bands, so the words in the middle stay clear (docs/DECISIONS.md D8)."""

from busybar.canvas import sec, vgradient
from busybar.party import glitter

import jfx

NAME = "day_bg"
TITLE = "Holiday backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Holiday backdrop")]
TEXT_GAP = (4, 67)  # text (and its shadow) stays inside these columns, clear of the glints (FREEDOM DAY: x 4-67)

COLORS = ((255, 110, 100), jfx.WHITE, (110, 150, 255), jfx.GOLD_LIGHT)


def render():
    bg = vgradient((10, 10, 42), (22, 12, 50))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        glitter(img, 31, f, n=9, period=LOOP, colors=COLORS, area=(0, 0, TEXT_GAP[0] - 1, 16), strength=0.9)
        glitter(img, 32, f, n=9, period=LOOP, colors=COLORS, area=(TEXT_GAP[1] + 2, 0, 72, 16), strength=0.9)
        frames.append(img)
    return frames
