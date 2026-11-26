"""Dec 16: Sledding. A kid on a red sled races down a moonlit hill, flying off two bumps in sprays of snow."""

import math

from busybar.canvas import FPS, blit, phase, put, sec
from busybar.fx import Particles, Stars, moon
from busybar.sprite import Sprite

from common import SNOW, SNOW_DEEP, SNOW_SHADE, pine, sky

NAME = "day16"
TITLE = "Sledding"
SECONDS = 8
KEYFRAMES = [(1.0, "Whoosh, down the hill"), (2.9, "Up and over the first bump!"), (4.4, "Snow spray"),
             (6.0, "Big air!"), (7.6, "Still going")]

RIDER = Sprite("sled_rider", {
    "R": "#E8283A", "w": "#FFFFFF", "S": "#F6C79C", "G": "#3A7AF0", "g": "#2450B0", "y": "#FFD24A",
    "B": "#D8202E", "b": "#9A1222", "K": "#B8C0D8",
}, """
....wR...
...RRR...
...SSS...
.yyGGGS..
..yGGGG..
.BBBBBBBB
..K....KK
""", """
....wR...
...RRR...
...SSS...
yy.GGGS..
.yyGGGG..
.BBBBBBBB
..K....KK
""")

SPEED = 1.3        # scroll px per frame
SLED_X = 26
JUMPS = [(2.5, 0.9, 3.0), (5.4, 1.2, 4.5)]  # start s, duration s, height px


def ground_y(x, u):
    """Screen-space downhill slope plus scrolling lumps; u is the world offset."""
    return 6.5 + x * 0.09 + 0.6 * math.sin((x + u) * 0.21) + 0.4 * math.sin((x + u) * 0.07)


def render():
    bg = sky(((6, 10, 36), (24, 36, 80)))
    stars = Stars(seed=160, n=14, ymax=8, period=FPS * 4, dim=0.1, bright=0.7)
    sp = Particles(seed=16)
    # bump positions in world space so each crest reaches the sled when its jump starts
    bumps = [SLED_X + 3 + sec(t0) * SPEED for t0, _, _ in JUMPS]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        u = f * SPEED
        img = bg.copy()
        stars.draw(img, f)
        moon(img, 62, 1)
        # far pines scroll slowly
        for k in range(8):
            px = (k * 13 - u * 0.35) % 90 - 9
            pine(img, int(px), int(ground_y(px, u) - 1), 5 + k % 3, snow=True, a=0.55)
        # the slope with bumps
        for x in range(72):
            gy = ground_y(x, u)
            for bx in bumps:
                d = (x + u) - bx
                if -6 < d < 6:
                    gy -= 2.2 * math.cos(d / 6 * math.pi / 2) ** 2
            top = int(round(gy))
            for y in range(max(0, top), 16):
                put(img, x, y, SNOW if y == top else (SNOW_SHADE if y - top < 3 else SNOW_DEEP))
        # rider
        base = ground_y(SLED_X + 4, u) - 7
        lift, airborne = 0.0, False
        for t0, dur, hgt in JUMPS:
            if t0 <= t < t0 + dur:
                k = (t - t0) / dur
                lift, airborne = hgt * math.sin(math.pi * k), True
            if t0 + dur <= t < t0 + dur + 0.1:
                sp.emit(SLED_X + 4, base + 7, 8, vx=(-1.4, 0.6), vy=(-1.2, -0.3), life=(6, 12),
                        colors=(SNOW, (200, 220, 255)), gravity=0.15)
        blit(img, RIDER.img((f // 2) % 2), SLED_X, round(base - lift))
        if not airborne:
            sp.emit(SLED_X, base + 6, 2, vx=(-1.6, -0.6), vy=(-0.8, -0.2), life=(5, 10),
                    colors=(SNOW, (200, 220, 255)), gravity=0.12)
        sp.step_draw(img)
        frames.append(img)
    return frames
