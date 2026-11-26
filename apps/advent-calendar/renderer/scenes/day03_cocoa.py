"""Dec 3: Hot Cocoa. A steaming mug by a frosty window; marshmallows plop in and the steam curls into a heart."""

import math

from busybar.canvas import FPS, blit, ease_in, lerp, phase, put, rect, sec
from busybar.sprite import Sprite

from common import Snow, sky

NAME = "day03"
TITLE = "Hot Cocoa"
SECONDS = 8
KEYFRAMES = [(0.6, "A steaming mug by the window"), (2.4, "Plop! A marshmallow"), (4.0, "And another"),
             (6.6, "The steam curls into a heart")]

MUG = Sprite("mug", {
    "R": "#D21F2B", "r": "#8E1020", "W": "#F4F4FF", "C": "#7A3E1C", "c": "#A8602E",
}, """
.rRRRRRRRRRr..
.RCcCCcCCcCR..
.RRRRRRRRRRRR.
.RRRRWRWRRRR.R
.RRRWWWWWRRR.R
.RRRRWWWRRRR.R
.RRRRRWRRRRRR.
.rRRRRRRRRRr..
..rrrrrrrrr...
""")
MARSH = Sprite("marshmallow", {"W": "#FFFFFF", "p": "#FFD8E8"}, """
WW
pW
""")
HEART = [(0, 1), (1, 0), (2, 0), (3, 1), (4, 0), (5, 0), (6, 1), (6, 2), (5, 3), (4, 4), (3, 5), (2, 4), (1, 3),
         (0, 2)]


def render():
    # wooden table, window with night snow
    frames = []
    snow = Snow(seed=33, n=18, speed=(0.15, 0.3), ymax=11)
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky(((70, 34, 22), (90, 46, 26)))  # warm wall
        # window: frame 40..69 x, 1..11 y
        rect(img, 41, 1, 28, 10, (12, 22, 58))
        win = img.crop((41, 1, 69, 11))
        snow.draw(win, f)
        img.paste(win, (41, 1))
        for x in range(40, 70):
            put(img, x, 0, (200, 150, 90))
            put(img, x, 11, (200, 150, 90))
        for y in range(0, 12):
            for x in (40, 54, 69):
                put(img, x, y, (200, 150, 90))
        for x in range(41, 69):
            put(img, x, 6, (200, 150, 90))
        # frost in the window corners
        for (x, y) in ((41, 10), (42, 10), (41, 9), (68, 10), (67, 10), (68, 9), (53, 10), (55, 10)):
            put(img, x, y, (200, 220, 255), 0.7)
        # table
        rect(img, 0, 12, 72, 4, (120, 66, 30))
        for x in range(72):
            put(img, x, 12, (170, 100, 48))
        # mug at x=10..23, y=4..12
        mx, my = 12, 4
        blit(img, MUG.img(), mx, my)
        # marshmallows: drop in at 1.8 s and 3.5 s, bob on the surface after
        for k, (t0, ox) in enumerate(((1.8, 3), (3.5, 7))):
            if t < t0 - 0.6:
                continue
            drop = ease_in(phase(f, sec(t0 - 0.6), sec(t0)))
            y = lerp(-3, my, drop)
            if t >= t0:
                y = my + 0.4 * math.sin((t - t0) * 4 + k) - 0.6
                if t < t0 + 0.35:  # splash droplets
                    a = 1 - (t - t0) / 0.35
                    for dx, dy in ((-2, -2), (3, -2), (-1, -3), (2, -3)):
                        put(img, mx + ox + dx, my - 1 + dy * (t - t0) / 0.35 * 1.5, (160, 90, 46), a)
            blit(img, MARSH.img(), mx + ox, y)
        # steam: three wavy wisps rising; after 5.6 s they gather into a heart above the mug
        gather = phase(f, sec(5.4), sec(6.4))
        fade_heart = 1.0 - phase(f, sec(7.4), sec(8.0))
        for w in range(3):
            for k in range(6):
                age = (t * 3 + k * 1.1 + w * 0.7) % 6.6
                sy = my - 1 - age
                sx = mx + 3 + w * 3 + math.sin(age * 1.4 + w) * 1.2
                a = 0.85 * (1 - age / 6.6) * (1 - gather)
                put(img, sx + age * gather * 2, sy, (236, 236, 250), a)
        if gather > 0:
            for i, (hx, hy) in enumerate(HEART):
                a = gather * fade_heart * (0.7 + 0.3 * math.sin(f * 0.4 + i))
                put(img, mx + 16 + hx - (1 - gather) * 8, 2 + hy + (1 - gather) * 2, (255, 150, 180), a)
        frames.append(img)
    return frames
