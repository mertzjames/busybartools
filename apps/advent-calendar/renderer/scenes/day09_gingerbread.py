"""Dec 9: Gingerbread. Two gingerbread friends run in from either side, leap for a high-five, and dance."""

import math

from busybar.canvas import FPS, blit, lerp, phase, put, sec, vgradient
from busybar.fx import SPARKLE, Particles
from busybar.sprite import Sprite

NAME = "day09"
TITLE = "Gingerbread"
SECONDS = 8
KEYFRAMES = [(1.0, "Two gingerbread friends run in"), (3.0, "High five!"), (5.0, "A little dance"),
             (7.2, "Sprinkles everywhere")]

_G = {"B": "#C07A34", "b": "#8E5220", "W": "#FFFFFF", "R": "#FF3A4A", "G": "#3AD070", "p": "#FF9AB0"}
GINGER = Sprite("gingerbread", _G, """
..BBB..
.BWBWB.
.BBBBB.
..BpB..
BBBBBBB
.BBRBB.
..BGB..
.BB.BB.
BB...BB
""", """
..BBB..
.BWBWB.
.BBBBB.
..BpB..
BBBBBBB
.BBRBB.
..BGB..
..BBB..
..B.B..
""", """
B.BBB.B
BBWBWBB
.BBBBB.
..BpB..
..BBB..
.BBRBB.
..BGB..
.BB.BB.
BB...BB
""")
GINGER_GIRL = GINGER.recolor("gingerbread_pink", R="#FFD24A", G="#FF7ACB")

SPRINKLES = ((255, 80, 90), (90, 220, 120), (255, 220, 80), (120, 180, 255), (255, 140, 220))


def render():
    bg = vgradient((70, 30, 50), (110, 50, 60))
    # baking tray
    for x in range(72):
        for y in range(13, 16):
            put(bg, x, y, (150, 150, 165) if y == 13 else (100, 100, 115))
    # wall tiles
    for y in range(0, 13):
        for x in range(72):
            if y % 4 == 3 or x % 8 == 0:
                put(bg, x, y, (130, 70, 80), 0.5)
    sp = Particles(seed=9)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        run = (f // 3) % 2
        if t < 2.2:
            k = phase(f, 0, sec(2.2))
            ax, bx, ay, by, fa, fb = lerp(-8, 27, k), lerp(73, 38, k), 4, 4, run, run
        elif t < 3.2:  # leap and high-five
            k = phase(f, sec(2.2), sec(3.2))
            hop = 3 * math.sin(math.pi * k)
            ax, bx, ay, by, fa, fb = 27 + 2 * k, 38 - 2 * k, 4 - hop, 4 - hop, 2, 2
            if abs(k - 0.5) < 0.08:
                sp.emit(36, 3, 10, vx=(-1.5, 1.5), vy=(-1.2, 0.4), life=(8, 18), colors=SPARKLE, glow=True)
        else:  # dance: alternate hops, arms up
            ph = (t - 3.2) * 6
            spread = 5 * phase(f, sec(3.2), sec(3.8))
            ax, bx = 29 - spread + math.sin(ph * 0.5) * 2, 36 + spread - math.sin(ph * 0.5) * 2
            ay = 4 - max(0.0, 2 * math.sin(ph))
            by = 4 - max(0.0, 2 * math.sin(ph + math.pi))
            fa = 2 if math.sin(ph) > 0 else 0
            fb = 2 if math.sin(ph) < 0 else 0
            if f % 2 == 0:
                sp.emit((f * 13) % 72, 0, 1, vx=(-0.1, 0.1), vy=(0.3, 0.6), life=(20, 30), colors=SPRINKLES)
        blit(img, GINGER.img(fa), ax, ay)
        blit(img, GINGER_GIRL.img(fb, flip=True), bx, by)
        sp.step_draw(img)
        frames.append(img)
    return frames
