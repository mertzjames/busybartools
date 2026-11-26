"""Dec 17: Carolers. Three carolers sing under a street lamp; music notes float up into the falling snow."""

import math

from busybar.canvas import FPS, blit, phase, put, rect, sec
from busybar.sprite import Sprite

from common import SNOW, SNOW_SHADE, Snow, glow, notes, sky

NAME = "day17"
TITLE = "Carolers"
SECONDS = 8
KEYFRAMES = [(0.8, "Carolers under the lamp"), (2.6, "They begin to sing"), (5.0, "Notes float up"),
             (7.4, "A window glows")]

_C = """
.HHH.
HHHHH
.SSS.
.SMS.
CCCCC
CbbbC
CbwbC
CCCCC
.CCC.
.c.c.
"""
_C_OPEN = _C.replace(".SMS.", ".SOS.")
_PAL = {"S": "#F6C79C", "M": "#E09080", "O": "#B03040", "b": "#8A4A20", "w": "#FFF6E0", "c": "#6A4A3A"}
SINGERS = [
    Sprite("caroler_red", {**_PAL, "H": "#2E9E4E", "C": "#D8202E"}, _C, _C_OPEN),
    Sprite("caroler_green", {**_PAL, "H": "#F4F4FF", "C": "#2E9E4E"}, _C, _C_OPEN),
    Sprite("caroler_blue", {**_PAL, "H": "#E8283A", "C": "#3A6AD8"}, _C, _C_OPEN),
]


def render():
    bg = sky(((8, 12, 40), (26, 30, 70)))
    snow = Snow(seed=17, n=28, speed=(0.12, 0.3), ymax=14)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # house with a window on the right
        rect(img, 56, 3, 16, 11, (70, 40, 40))
        for x in range(54, 72):
            put(img, x, 2 + abs(x - 63) * 0 // 1, (170, 60, 50))
        win = 0.4 + 0.6 * phase(f, sec(6.6), sec(7.4))
        rect(img, 60, 6, 6, 5, (255, 200, 90), win)
        put(img, 62, 6, (120, 60, 40))
        put(img, 62, 8, (120, 60, 40))
        for x in range(60, 66):
            put(img, x, 8, (120, 60, 40))
        # street lamp
        for y in range(3, 14):
            put(img, 12, y, (60, 60, 80))
        rect(img, 10, 1, 5, 2, (60, 60, 80))
        rect(img, 11, 3, 3, 2, (255, 220, 130))
        glow(img, 12, 4, 10, (255, 190, 90), 0.32 + 0.03 * math.sin(f * 0.5))
        # snowy ground
        for x in range(72):
            put(img, x, 14, SNOW)
            put(img, x, 15, SNOW_SHADE)
        singing = t > 2.0
        for i, s in enumerate(SINGERS):
            x = 24 + i * 9
            sway = round(math.sin(t * 3 + i)) if singing else 0
            mouth = 1 if singing and (f // 5 + i) % 3 != 0 else 0
            blit(img, s.img(mouth), x + sway * 0, 4 + (1 if sway > 0 and singing else 0))
        if singing:
            notes(img, f, [sec(2.2), sec(3.0), sec(3.8), sec(4.4), sec(5.0), sec(5.6), sec(6.2), sec(6.8)],
                  28, 3, color=(255, 230, 120))
            notes(img, f, [sec(2.6), sec(3.4), sec(4.8), sec(5.9), sec(7.0)], 42, 2, color=(200, 230, 255))
        snow.draw(img, f, alpha=0.8)
        frames.append(img)
    return frames
