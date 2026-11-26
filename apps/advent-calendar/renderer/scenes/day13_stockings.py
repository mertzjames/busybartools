"""Dec 13: Stockings. Stockings hang on the mantel by a crackling fire; one by one, a little gift pops into each."""

import math

from busybar.canvas import FPS, add, blit, ease_out, phase, put, rect, sec, vgradient
from busybar.fx import FIRE, SPARKLE, Particles
from busybar.sprite import Sprite

from common import glow

NAME = "day13"
TITLE = "Stockings"
SECONDS = 8
KEYFRAMES = [(0.6, "Stockings on the mantel"), (2.4, "Pop! A candy cane"), (4.4, "A tiny teddy"),
             (6.4, "And a star"), (7.6, "The fire crackles")]

_ST = """
WWWWW..
WwWwW..
RRRRR..
RRRRR..
RRRRR..
RRRRR..
RRRRRR.
RRRRRRR
.RRRRR.
"""
STOCK_RED = Sprite("stocking_red", {"W": "#F4F4FF", "w": "#C4CCE4", "R": "#D8202E"}, _ST)
STOCK_GREEN = Sprite("stocking_green", {"W": "#F4F4FF", "w": "#C4CCE4", "R": "#2E9E4E"}, _ST)
STOCK_STRIPE = Sprite("stocking_stripe", {"W": "#F4F4FF", "w": "#C4CCE4", "R": "#D8202E", "S": "#FFFFFF"}, """
WWWWW..
WwWwW..
RRRRR..
SSSSS..
RRRRR..
SSSSS..
RRRRRR.
SSSSSSS
.RRRRR.
""")
GIFTS = [
    Sprite("gift_cane", {"R": "#FF3040", "W": "#FFFFFF"}, ".RW\nW.R\n..W\n..R"),
    Sprite("gift_teddy", {"B": "#C08040", "b": "#E0B080"}, "B.B\nBbB\n.B."),
    Sprite("gift_star", {"Y": "#FFE060", "y": "#FFB020"}, ".Y.\nYyY\n.Y."),
]


def render():
    bg = vgradient((40, 20, 30), (60, 30, 30))
    # brick chimney breast
    for y in range(3, 16):
        for x in range(18, 54):
            mortar = y % 3 == 0 or (x + (y // 3) * 3) % 6 == 0
            put(bg, x, y, (120, 50, 40) if not mortar else (80, 36, 30))
    # hearth opening
    rect(bg, 27, 8, 18, 8, (20, 8, 8))
    # mantel shelf
    rect(bg, 8, 2, 56, 2, (160, 100, 50))
    for x in range(8, 64):
        put(bg, x, 2, (200, 140, 70))
    # garland on the mantel
    for x in range(8, 64):
        put(bg, x, 4, (30, 130, 60) if x % 3 else (20, 90, 40))
    sp = Particles(seed=13)
    fire = Particles(seed=31)
    stockings = [(STOCK_RED, 11, 1.8), (STOCK_GREEN, 20, 3.8), (STOCK_STRIPE, 55, 5.8)]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # fire: logs + rising flame particles
        for x in range(29, 43):
            put(img, x, 15, (110, 60, 30))
            put(img, x, 14, (140, 80, 40) if x % 4 else (90, 50, 25))
        fire.emit(36 + math.sin(f * 0.7) * 4, 13, 3, vx=(-0.25, 0.25), vy=(-0.6, -0.3), life=(5, 10), colors=FIRE)
        fire.step_draw(img)
        glow(img, 36, 12, 9, (255, 120, 40), 0.25 + 0.06 * math.sin(f * 0.9))
        for i, (sprite, x, t0) in enumerate(stockings):
            sway = round(0.6 * math.sin(t * 2 + i * 1.7))
            jump = 0
            if t0 <= t < t0 + 0.3:
                jump = -1
            blit(img, sprite.img(), x + sway, 5 + jump)
            if t >= t0 - 0.2:
                k = ease_out(phase(f, sec(t0 - 0.2), sec(t0 + 0.2)))
                gy = 2 + (1 - k) * -3
                gift = GIFTS[i]
                if k > 0:
                    blit(img, gift.img(), x + 1 + sway, 5 - 1 + gy - 2 + (1 - k) * 0)
                if abs(t - t0) < 0.05:
                    sp.emit(x + 3, 4, 8, vx=(-1, 1), vy=(-1, 0.2), life=(8, 14), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        frames.append(img)
    return frames
