"""Conga Line: four guests in party hats conga in, dance, blow their noisemakers, and conga out."""

import math

from busybar.canvas import FPS, add, blit, phase, put, sec, vgradient
from party import CYAN, GOLD, LIME, PINK, VIOLET, WHITE, dim, string_lights
from sprites import GUESTS

NAME = "dance_floor"
TITLE = "Conga Line"
SECONDS = 15
KEYFRAMES = [(2.0, "A conga line arrives"), (5.6, "Everyone finds a spot"), (7.0, "Hands up!"),
             (8.4, "Noisemakers: toot!"), (10.2, "One more toot"), (13.0, "...and off they conga")]

SPOTS = [9, 24, 41, 56]           # where each guest stops
LEAVE = sec(11.4)
HORNS = [(sec(8.0), sec(9.2)), (sec(9.9), sec(10.9))]
HORN_COLORS = [(PINK, GOLD), (CYAN, WHITE), (LIME, PINK), (GOLD, CYAN)]
TILES = (PINK, CYAN, GOLD, VIOLET, LIME)


def horn(img, x, y, length: float, colors) -> None:
    """A party blower: a striped tube that unrolls to the right, with a curl at the end while it's short."""
    n = int(round(length))
    for i in range(n):
        put(img, x + i, y, colors[(i // 2) % 2])
    if 0 < length < 5:  # the rolled-up part
        put(img, x + n, y - 1, colors[0])
        put(img, x + n - 1, y - 1, colors[1])
    if length >= 5:
        put(img, x + n, y, GOLD)  # tip
        for k in (1, 2):  # toot lines
            add(img, x + n + 1 + k, y - k, WHITE, 0.6)
            add(img, x + n + 1 + k, y + k, WHITE, 0.6)


def render():
    bg = vgradient((10, 4, 28), (30, 10, 46))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        string_lights(img, f, y0=0, sag=1.5, spacing=6, offset=2)
        beat = f // 6
        for x in range(72):
            c = TILES[(x // 8 + beat) % len(TILES)]
            put(img, x, 15, dim(c, 0.7 if (x // 8 + beat) % 2 == 0 else 0.25))
        for i, g in enumerate(GUESTS):
            # conga in: one line at 12 px/s, the leader first; each guest stops at their spot
            if f < LEAVE:
                x = min(SPOTS[i], -8 - (3 - i) * 12 + 0.8 * f)
            else:
                x = SPOTS[i] + (f - LEAVE) * 1.3
            y = 4
            walking = x < SPOTS[i] or f >= LEAVE
            if walking:
                fr = (2, 0, 3, 0)[(f // 3 + i) % 4]
                y += -1 if (f // 3 + i) % 2 else 0
            else:
                fr = 0
                if sec(6.4) <= f < sec(8.0) or sec(9.2) <= f < sec(9.9):
                    fr = 1 if (f // 4) % 2 == 0 else 0  # hands up on the beat
                    y += -1 if fr == 1 else 0
                for h, (a, b) in enumerate(HORNS):
                    if a <= f < b and i % 2 == h:  # guests 0 and 2 toot first, then 1 and 3
                        fr = 4
                        u = (f - a) / (b - a)
                        ln = 6 * math.sin(math.pi * min(1.0, u * 1.25)) if u < 0.8 else 0
                        horn(img, round(x) + 6, y + 5, ln, HORN_COLORS[i])
            blit(img, g.img(fr), x, y)
        frames.append(img)
    return frames
