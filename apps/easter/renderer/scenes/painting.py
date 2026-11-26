"""Painting Eggs: three white eggs wait in egg cups on the table. For each, the brush dips into a pot of paint,
sweeps the egg in a pastel, then adds the pattern: a zigzag, then dots, then stripes. Three finished eggs
sparkle at the end."""

import math

from busybar.canvas import mix, new, put, sec, vgradient
from busybar.fx import sparkle

import efx

NAME = "painting"
TITLE = "Painting Eggs"
SECONDS = 16
KEYFRAMES = [(0.3, "Three white eggs"), (1.2, "Dip the brush"), (2.2, "Paint it pink"), (3.6, "A zigzag"),
             (8.6, "Blue with dots"), (12.8, "Yellow with stripes"), (15.4, "All done!")]

EW, EH = 7, 10
EY = 2  # egg top row; the cups hold them from row 11
TABLE = 14
SHELL = (250, 246, 236)
# (egg x, pot x, base color, pattern, alt color for the pattern)
EGGS = [(24, 3, efx.PINK, "zigzag", None), (40, 8, efx.BLUE, "dots", None), (56, 13, efx.LEMON, "stripes", None)]
PERIOD = 70  # frames per egg
T0 = 6
HANDLE = (196, 140, 84)
FERRULE = (190, 196, 214)


def phases(i):
    t = T0 + i * PERIOD
    return {"dip": (t, t + 10), "move": (t + 10, t + 16), "base": (t + 16, t + 34), "pattern": (t + 36, t + 60),
            "away": (t + 60, t + 70)}


def background():
    img = vgradient((30, 18, 50), (52, 30, 66))
    for x in range(72):  # the table
        put(img, x, TABLE, (200, 140, 80))
        put(img, x, TABLE + 1, (150, 96, 52))
    for k, (ex, px, c, pat, alt) in enumerate(EGGS):
        # an egg cup under each egg
        for dx in range(1, EW - 1):
            put(img, ex + dx, TABLE - 1, efx.MINT if k != 1 else efx.LILAC)
            put(img, ex + dx, TABLE - 2, mix(efx.MINT if k != 1 else efx.LILAC, (255, 255, 255), 0.3))
        put(img, ex + 3, TABLE - 1, mix(efx.MINT if k != 1 else efx.LILAC, (0, 0, 0), 0.2))
        # paint pots on the left
        for dx in range(3):
            for dy in range(3):
                put(img, px + dx, TABLE - 1 - dy, (200, 206, 224) if dy < 2 else (230, 234, 246))
        put(img, px, TABLE - 3, c)
        put(img, px + 1, TABLE - 3, c)
        put(img, px + 2, TABLE - 3, c)
    return img


def brush(img, x, y, tip):
    """The brush: a 2-pixel tip at (x, y), a silver ferrule and a wooden handle up and to the right."""
    put(img, x, y, tip)
    put(img, x, y - 1, tip)
    put(img, x + 1, y - 2, FERRULE)
    for k in range(4):
        put(img, x + 2 + k, y - 3 - k, HANDLE)


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        bpos = None
        for i, (ex, px, c, pat, alt) in enumerate(EGGS):
            ph = phases(i)
            base_reveal, pat_reveal = 0.0, 0.0
            if f >= ph["base"][0]:
                base_reveal = min(1.0, (f - ph["base"][0]) / (ph["base"][1] - ph["base"][0]))
            if f >= ph["pattern"][0]:
                pat_reveal = min(1.0, (f - ph["pattern"][0]) / (ph["pattern"][1] - ph["pattern"][0]))
            # the egg: white, painted in from the left, then the pattern painted in from the left
            if base_reveal <= 0:
                efx.egg(img, ex, EY, EW, EH, SHELL, accent=(226, 220, 210))
            else:
                efx.egg(img, ex, EY, EW, EH, SHELL, accent=(226, 220, 210))
                cut = base_reveal * (EW + 1) - 1
                part = new((0, 0, 0))
                efx.egg(part, ex, EY, EW, EH, c, pat if pat_reveal > 0 else "plain", alt=alt, reveal=pat_reveal)
                for dx, dy in efx.egg_mask(EW, EH):
                    if dx <= cut:
                        img.putpixel((ex + dx, EY + dy), part.getpixel((ex + dx, EY + dy)))
            # where the brush is during this egg's turn
            for name, (a, b) in ph.items():
                if a <= f < b:
                    u = (f - a) / (b - a)
                    if name == "dip":
                        bpos = (px + 1, TABLE - 4 + round(2 * math.sin(math.pi * u)), c)
                    elif name == "move":
                        bpos = (round(px + 1 + (ex - px - 1) * u), round(TABLE - 4 - 6 * math.sin(math.pi * u)), c)
                    elif name == "base":
                        bx = ex + round(u * (EW - 1))
                        by = EY + 3 + round(3 * math.sin(2 * math.pi * u * 3))
                        bpos = (bx, by, c)
                    elif name == "pattern":
                        bx = ex + round(u * (EW - 1))
                        by = EY + EH // 2 + (1 if pat == "stripes" and (f // 6) % 2 else 0)
                        bpos = (bx, by, efx.ACCENT[c])
                    else:
                        bpos = (round(ex + EW + 6 * u), round(EY + 4 - 4 * u), efx.ACCENT[c])
            if ph["away"][0] <= f < ph["away"][0] + 10:
                a = f - ph["away"][0]
                sparkle(img, ex + 1, EY + 2, a, 1 - a / 10)
        if bpos:
            brush(img, *bpos)
        if f >= T0 + 3 * PERIOD:
            for k, (ex, px, c, pat, alt) in enumerate(EGGS):
                if (f // 4 + k * 3) % 8 == 0:
                    sparkle(img, ex + 1 + (f // 4) % 3, EY + 1 + k % 3, f, 0.9)
        frames.append(img)
    return frames
