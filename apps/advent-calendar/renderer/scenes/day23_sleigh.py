"""Dec 23: Sleigh Ride. A sleigh and two reindeer swoop across a huge moon over the sleeping rooftops."""

import math

from busybar.canvas import FPS, lerp, phase, put, rect, sec
from busybar.fx import SPARKLE, Particles, Stars

from common import SNOW, sky
from props import draw_sleigh_team

NAME = "day23"
TITLE = "Sleigh Ride"
SECONDS = 8
KEYFRAMES = [(0.6, "Rooftops under a full moon"), (2.6, "Here comes the sleigh"),
             (4.2, "Across the moon!"), (6.6, "A trail of stardust")]


def rooftops(img, f):
    houses = [(0, 6, 10), (7, 9, 8), (17, 7, 11), (29, 10, 7), (37, 6, 9), (48, 8, 10), (59, 7, 13)]
    for i, (x0, w, top) in enumerate(houses):
        rect(img, x0, top, w, 16 - top, (64, 52, 96) if i % 2 else (78, 50, 70))
        for x in range(x0, x0 + w):
            put(img, x, top - 1, SNOW)
        # lit windows (one flickers off late in the scene: everyone is asleep)
        for j, (wx, wy) in enumerate(((x0 + 2, top + 2), (x0 + w - 3, top + 3))):
            if wx >= x0 + w:
                continue
            off = (i + j) % 3 == 0 and f > sec(5.5 + i * 0.2)
            if not off:
                put(img, wx, wy, (255, 200, 90))
    # chimneys
    for cx, top in ((3, 8), (21, 5), (52, 6)):
        rect(img, cx, top, 2, 2, (90, 50, 50))


def render():
    bg = sky(((2, 4, 22), (16, 20, 54)))
    stars = Stars(seed=230, n=26, ymax=12, period=FPS * 4, dim=0.1, bright=0.85)
    sp = Particles(seed=23)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        # the moon: big, center
        for dy in range(-7, 8):
            for dx in range(-7, 8):
                d = math.hypot(dx, dy * 1.0)
                if d <= 6.6:
                    c = (252, 246, 214) if d < 5.8 else (210, 204, 176)
                    put(img, 38 + dx, 6 + dy, c)
        for cx, cy in ((36, 4), (41, 8), (39, 3)):
            put(img, cx, cy, (226, 220, 190))
        rooftops(img, f)
        # sleigh arcs across left to right, 1.6-6.4 s
        k = phase(f, sec(1.6), sec(6.4))
        if 0 < k < 1:
            x = lerp(-34, 74, k)
            y = 5 - 2.5 * math.sin(math.pi * k) + 0.8 * math.sin(t * 5)
            draw_sleigh_team(img, x, y, f)
            sp.emit(x, y + 8, 2, vx=(-0.5, -0.1), vy=(-0.1, 0.3), life=(10, 22), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        frames.append(img)
    return frames
