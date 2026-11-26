"""Scene: a quill writes WE THE PEOPLE on a parchment by candlelight, adds a flourish beneath it and returns to the
inkwell; a plain red wax seal (no emblem) presses down at the end (docs/DECISIONS.md D3, D5). The words open the
U.S. Constitution, a public-domain text that belongs to everyone, which suits a non-partisan day."""

import math

from busybar.canvas import H, W, add, ease_in_out, ease_out, mix, phase, put, sec
from busybar.font import draw_text, text_width

import pfx

NAME = "quill"
TITLE = "We the People"
SECONDS = 14
KEYFRAMES = [(0.8, "A quill in the inkwell, by candlelight"), (4.0, "Writing on the parchment"),
             (8.6, "WE THE PEOPLE"), (10.2, "A flourish beneath"), (12.8, "Sealed in red wax")]

TEXT = "WE THE PEOPLE"
TX, TY = 0, 4  # TX is set from the text width below
INK = (70, 38, 24)
PARCH = (226, 204, 156)
PARCH_EDGE = (190, 160, 108)
WOOD = (96, 58, 34)
INKWELL = (60, 18)

WIDTH = text_width(TEXT, "tiny")
TX = (6 + 65 - WIDTH) // 2 + 1
WRITE0, WRITE1 = sec(1.6), sec(8.4)
FLOUR0, FLOUR1 = sec(8.8), sec(10.6)
FL_X0, FL_X1 = TX - 2, TX + WIDTH + 1


def flourish_y(x: float) -> float:
    """The flourish: a long wave under the words with a loop-like swell at each end."""
    u = (x - FL_X0) / (FL_X1 - FL_X0)
    return 11.5 - 1.8 * math.sin(2 * math.pi * u * 2.5) * (0.35 + 0.65 * math.sin(math.pi * u))


def quill(img, tx: float, ty: float, lift: float = 0.0) -> None:
    """A white feather quill with its nib at (tx, ty), leaning up and to the right."""
    dx, dy = 0.62, -0.78
    px_, py_ = 0.78, 0.62
    ty -= lift
    put(img, tx, ty, (200, 160, 60))  # the gold nib
    for i in range(1, 12):
        d = i * 0.9
        cx, cy = tx + dx * d, ty + dy * d
        put(img, cx, cy, (232, 226, 210))
        if 3 <= i <= 11:
            w = 1.6 if 5 <= i <= 9 else 0.9
            for s in (-1, 1):
                for k in (0.6, w):
                    c = (246, 246, 252) if s < 0 else (196, 200, 220)
                    put(img, cx + px_ * k * s, cy + py_ * k * s, c)


def render():
    base = pfx.sky([(0, WOOD), (15, (70, 42, 26))])
    for y in range(1, 15):  # the parchment, darker toward its edges
        for x in range(6, 66):
            e = min(x - 6, 65 - x, y - 1, 14 - y)
            put(base, x, y, PARCH if e >= 2 else mix(PARCH_EDGE, PARCH, e / 2))
    # the inkwell on the desk (glass, lit navy, with a highlight) and the candle
    for y in range(11, 16):
        for x in range(67, 72):
            put(base, x, y, (40, 52, 104) if y > 11 else (90, 100, 150))
    put(base, 68, 12, (150, 170, 220))
    pfx.glow(base, 2, 6, 8, (255, 150, 50), 0.6)  # a steady candle glow (only the flame core flickers)
    for y in range(9, 16):
        put(base, 1, y, (240, 232, 206))
        put(base, 2, y, (210, 196, 166))
    put(base, 1, 8, (60, 40, 30))  # the wick

    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        # flame core flicker
        k = 0.85 + 0.15 * math.sin(f * 1.7) * math.sin(f * 0.53)
        put(img, 1, 7, (255, 236, 160), k)
        put(img, 1, 6, (255, 200, 90), k)
        put(img, 1, 5, (255, 150, 50), 0.7 * k)
        put(img, 2, 7, (255, 170, 60), 0.5 * k)
        put(img, 0, 7, (255, 170, 60), 0.5 * k)
        # the writing so far
        reveal = int((WIDTH + 1) * phase(f, WRITE0, WRITE1))
        draw_text(img, TEXT, TX, TY, INK, font="tiny", reveal=reveal)
        fl = phase(f, FLOUR0, FLOUR1)
        fl_x = FL_X0 + (FL_X1 - FL_X0) * ease_in_out(fl)
        x = FL_X0
        while fl > 0 and x <= fl_x:
            put(img, x, flourish_y(x), INK)
            x += 0.25
        # the wax seal, pressed in near the end
        seal = phase(f, sec(11.6), sec(12.2))
        if seal > 0:
            r = 1.9 * ease_out(seal)
            for yy in range(8, 15):
                for xx in range(57, 65):
                    if math.hypot(xx - 61, (yy - 11) * 1.1) <= r + 0.3:
                        put(img, xx, yy, (190, 26, 40))
            if seal >= 1:
                put(img, 60, 10, (246, 110, 116))
                put(img, 61, 12, (150, 16, 30))
        # where the quill is
        if f < WRITE0:
            p = ease_in_out(phase(f, sec(0.4), WRITE0))
            qx, qy = INKWELL[0] + 9 + (TX - INKWELL[0] - 9) * p, 11 + (TY + 4 - 11) * p
            lift = 3 * math.sin(math.pi * p)
        elif f < WRITE1:
            u = phase(f, WRITE0, WRITE1)
            qx = TX + reveal
            qy = TY + 2 + 2.2 * math.sin(u * 2 * math.pi * 26)  # the pen goes up and down with each stroke
            lift = 0.0
        elif f < FLOUR0:
            p = ease_in_out(phase(f, WRITE1, FLOUR0))
            qx, qy, lift = TX + WIDTH + (FL_X0 - TX - WIDTH) * p, TY + 4 + (flourish_y(FL_X0) - TY - 4) * p, 2.5 * math.sin(math.pi * p)
        elif f < FLOUR1:
            qx, qy, lift = fl_x, flourish_y(fl_x), 0.0
        else:
            p = ease_in_out(phase(f, FLOUR1, sec(11.6)))
            qx = FL_X1 + (INKWELL[0] + 9 - FL_X1) * p
            qy = flourish_y(FL_X1) + (11 - flourish_y(FL_X1)) * p
            lift = 3 * math.sin(math.pi * p)
        quill(img, qx, qy, lift)
        frames.append(img)
    return frames
