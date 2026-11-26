"""Scene: Carving Night. Four plain pumpkins sit on a porch rail under the stars. One at a time, each is carved
with a different face (a glinting knife cuts it pixel by pixel) and then lit from inside, until all four
jack-o'-lanterns glow. A bat flits past at the end."""

from busybar.canvas import FPS, H, W, add, blit, put, sec
from hfx import (NIGHT_MID, NIGHT_TOP, frame_t, glow, gradient, pumpkin, pumpkin_glow, quant, stars)
from sprites import BAT

NAME = "lanterns"
TITLE = "Carving Night"
SECONDS = 16
KEYFRAMES = [(0.6, "Four plain pumpkins"), (1.8, "The first is carved"), (2.9, "...and lit"),
             (5.6, "A surprised one"), (8.8, "A winking one"), (11.8, "A goofy one"), (14.2, "All four glow")]

PW, PH = 15, 11
PY = 3
XS = (1, 19, 37, 55)
FACES = ("classic", "surprised", "wink", "goofy")
START = 1.0
EACH = 3.0
CARVE = 1.2
LIGHT_AT = 1.5
LIGHT_LEN = 0.5


def state(i: int, t: float) -> tuple[float, float]:
    """(carved, lit) of pumpkin i at time t."""
    t0 = START + i * EACH
    carved = max(0.0, min(1.0, (t - t0) / CARVE))
    lit = quant((t - t0 - LIGHT_AT) / LIGHT_LEN, 8)
    return carved, lit


def render():
    bg = gradient([(0, NIGHT_TOP), (8, NIGHT_MID), (13, (52, 14, 66))])
    for x in range(W):  # the porch rail: a lit wooden plank with a darker lower edge
        put(bg, x, 14, (120, 70, 40))
        put(bg, x, 15, (80, 44, 30))
        if x % 9 == 4:
            put(bg, x, 14, (96, 54, 32))
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 3, 22, f, ymax=4, a=0.7)
        for i, x in enumerate(XS):
            _, lit = state(i, t)
            if lit > 0:
                pumpkin_glow(img, x, PY, PW, PH, 0.9 * lit)
                for dx in range(PW):  # candlelight on the rail
                    add(img, x + dx, 14, (90, 50, 10), 0.6 * lit * (1 - abs(dx - PW / 2) / (PW / 2)))
        for i, x in enumerate(XS):
            carved, lit = state(i, t)
            pumpkin(img, x, PY, PW, PH, FACES[i], carved=carved, lit=lit, f=f, seed=i)
            t0 = START + i * EACH
            if 0 < t - t0 < CARVE + 0.1:  # the knife's glint hops along the cut
                k = int((t - t0) * FPS)
                gx = x + 3 + (k * 5) % 9
                gy = PY + 3 + (k // 2) % 5
                put(img, gx, gy, (255, 255, 255))
                add(img, gx + 1, gy - 1, (200, 210, 255), 0.5)
                add(img, gx - 1, gy + 1, (200, 210, 255), 0.5)
        if t > 13.4:  # a bat flits across the top
            u = (t - 13.4) / 2.4
            bx = -8 + u * (W + 16)
            by = 1 + 1.5 * abs(((t * 3) % 2) - 1)
            blit(img, BAT.img((f // 2) % len(BAT)), bx, by)
        frames.append(img)
    return frames
