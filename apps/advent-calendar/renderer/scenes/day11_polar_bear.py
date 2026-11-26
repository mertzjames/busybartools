"""Dec 11: Polar Bear. Under the northern lights a polar bear pads across the ice, stops, and gazes up."""

import math

from busybar.canvas import FPS, add, blit, ease_out, lerp, phase, put, sec, vgradient
from busybar.fx import Stars
from busybar.sprite import Sprite

from common import aurora

NAME = "day11"
TITLE = "Polar Bear"
SECONDS = 8
KEYFRAMES = [(1.0, "The northern lights"), (2.6, "A polar bear pads across the ice"),
             (5.2, "It stops and looks up"), (7.0, "A shooting star")]

_B = {"W": "#F2F5FF", "w": "#B4C0DA", "n": "#7A7A9A", "e": "#5A6A9A", "p": "#FFB0B8"}
BEAR = Sprite("polar_bear", _B, """
.............ww...
....wWWWWWW.wWWW..
..wWWWWWWWWWWWeWW.
.wWWWWWWWWWWWWWWWn
wWWWWWWWWWWWWWW...
.WWWWWWWWWWWWW....
.WW.wW....WW.wW...
.WW.wW....WW.wW...
""", """
.............ww...
....wWWWWWW.wWWW..
..wWWWWWWWWWWWeWW.
.wWWWWWWWWWWWWWWWn
wWWWWWWWWWWWWWW...
.WWWWWWWWWWWWW....
..WWwW.....WWwW...
..WW.wW....WW.wW..
""")
BEAR_UP = Sprite("polar_bear_up", _B, """
..............ww..
....wWWWWWW..wWWWn
..wWWWWWWWWWWWWeW.
.wWWWWWWWWWWWWWW..
wWWWWWWWWWWWWWW...
.WWWWWWWWWWWWW....
.WW.wW....WW.wW...
.WW.wW....WW.wW...
""")


def render():
    bg = vgradient((2, 6, 22), (10, 24, 50))
    stars = Stars(seed=111, n=20, ymax=10, period=FPS * 4, dim=0.1, bright=0.8)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        lights = 0.35 + 0.35 * phase(f, sec(5.0), sec(6.0))
        aurora(img, f, y0=2.5, a=lights)
        # ice floe and dark water
        for x in range(72):
            for y in range(13, 16):
                put(img, x, y, (200, 220, 250) if y == 13 else (120, 150, 200))
            if (x + f // 4) % 9 == 0:
                put(img, x, 15, (180, 200, 240))
        # the bear walks in, stops at center, looks up
        if t < 4.6:
            x = lerp(-18, 26, ease_out(phase(f, 0, sec(4.6))) * 0.3 + phase(f, 0, sec(4.6)) * 0.7)
            frame = (f // 4) % 2 if t < 4.3 else 0
            blit(img, BEAR.img(frame), x, 5)
        else:
            blit(img, BEAR.img(0) if t < 5.0 else BEAR_UP.img(), 26, 5)
        # shooting star
        if 6.4 <= t < 7.4:
            k = phase(f, sec(6.4), sec(7.4))
            sx, sy = lerp(70, 44, k), lerp(0, 5, k)
            for j in range(5):
                put(img, sx + j * 1.6, sy - j * 0.3, (255, 255, 230), (1 - j / 5) * (1 - k * 0.5))
            add(img, sx, sy, (255, 255, 255), 1.0)
        frames.append(img)
    return frames
