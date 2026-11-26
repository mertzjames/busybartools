"""Dec 10: Cookies and Milk. Cookies land on a plate, milk pours into a glass, and a note appears: FOR SANTA."""

import math

from busybar.canvas import FPS, add, blit, ease_in, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text
from busybar.sprite import Sprite

NAME = "day10"
TITLE = "Cookies and Milk"
SECONDS = 8
KEYFRAMES = [(0.8, "A plate slides in"), (2.4, "Cookies!"), (4.4, "Milk pours"), (6.8, "A note: FOR SANTA")]

COOKIE = Sprite("cookie", {"C": "#D89A50", "c": "#B87A36", "k": "#6A3A1A"}, """
.CCC.
CkCCc
CCCkC
.cCc.
""")
PLATE = (236, 240, 250)
PLATE_RIM = (170, 180, 210)
GLASS = (170, 200, 230)
MILK = (250, 250, 255)


def render():
    bg = vgradient((20, 20, 50), (40, 30, 70))
    rect(bg, 0, 12, 72, 4, (110, 60, 30))  # tablecloth edge / table
    for x in range(72):
        put(bg, x, 12, (200, 40, 50) if (x // 3) % 2 else (240, 230, 230))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # plate slides in from the left
        px = lerp(-20, 4, ease_out(phase(f, 0, sec(1.0))))
        for x in range(18):
            put(img, px + x, 11, PLATE if 1 <= x <= 16 else PLATE_RIM)
            if 2 <= x <= 15:
                put(img, px + x, 10, PLATE_RIM if x in (2, 15) else PLATE)
        # cookies drop one at a time and stack
        for i, (t0, ox, oy) in enumerate(((1.4, 2, 6), (2.0, 10, 6), (2.6, 6, 3))):
            if t < t0 - 0.4:
                continue
            k = ease_in(phase(f, sec(t0 - 0.4), sec(t0)))
            y = lerp(-5, oy, k)
            if t >= t0 and t < t0 + 0.2:
                y = oy - 1 * math.sin(math.pi * (t - t0) / 0.2)
            blit(img, COOKIE.img(), px + ox, y)
        # glass at x=26..31
        gx = 27
        for y in range(4, 12):
            put(img, gx, y, GLASS, 0.8)
            put(img, gx + 5, y, GLASS, 0.8)
        for x in range(gx, gx + 6):
            put(img, x, 11, GLASS, 0.8)
        put(img, gx + 1, 5, (255, 255, 255), 0.5)
        # milk pours 3.4-5.4 s
        fill = phase(f, sec(3.6), sec(5.4))
        level = 11 - fill * 6
        for y in range(int(round(level)), 11):
            for x in range(gx + 1, gx + 5):
                put(img, x, y, MILK)
        if 3.4 <= t < 5.5:
            for y in range(0, int(round(level))):
                put(img, gx + 3, y, MILK, 0.95)
            if fill > 0:
                add(img, gx + 2, level - 1, (255, 255, 255), 0.6)
                add(img, gx + 4, level - 1, (255, 255, 255), 0.6)
        # the note: a card slides up with FOR SANTA
        nk = ease_out(phase(f, sec(5.8), sec(6.6)))
        if nk > 0:
            ny = lerp(16, 3, nk)
            rect(img, 35, int(ny), 37, 8, (250, 244, 220))
            for x in range(35, 72):
                put(img, x, ny + 7, (200, 180, 140))
            draw_text(img, "FOR SANTA", 36, int(ny) + 1, (210, 30, 40), font="tiny")
            if t > 6.8:  # little heart
                for hx, hy in ((0, 0), (2, 0), (0, 1), (1, 1), (2, 1), (1, 2)):
                    put(img, 68 + hx, int(ny) + 2 + hy, (255, 80, 110), 0.6 + 0.4 * math.sin(f * 0.4))
        frames.append(img)
    return frames
