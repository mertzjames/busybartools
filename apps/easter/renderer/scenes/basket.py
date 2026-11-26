"""The Easter Basket: a wicker basket lined with paper grass. Decorated eggs drop in one by one and settle, a
chocolate bunny pops up in the middle, a pink bow ties onto the handle, and the whole basket glitters."""

import math

from busybar.canvas import blit, mix, new, put, sec, vgradient
from busybar.fx import sparkle
from busybar.party import glitter

import efx
from sprites import CHOC_BUNNY

NAME = "basket"
TITLE = "The Easter Basket"
SECONDS = 14
KEYFRAMES = [(0.4, "An empty basket"), (1.6, "The first egg drops in"), (5.4, "Four eggs"),
             (7.6, "A chocolate bunny pops up"), (9.4, "A bow on the handle"), (12.6, "Ready for Easter")]

BX, BW, BH = 22, 28, 5  # basket left edge, width, body height
BASE = 15
RIM = BASE - BH + 1  # the basket's top row (11)
# eggs: (x, color, pattern, drop frame); each lands with its bottom 3 rows inside the basket
EGGS = [(25, efx.PINK, "zigzag", 15), (41, efx.MINT, "dots", 40), (30, efx.LEMON, "stripes", 62),
        (36, efx.LILAC, "band", 84)]
CHOC_T = sec(7.0)
BOW_T = sec(9.0)
FALL = 10


def background():
    img = vgradient((26, 14, 48), (46, 22, 64))
    # a soft pastel polka-dot wall
    for y in range(1, 15, 4):
        for x in range((y // 4) % 2 * 4 + 2, 72, 8):
            put(img, x, y, (90, 60, 120))
    for x in range(72):  # the table
        put(img, x, BASE, (150, 96, 60))
    return img


def egg_y(f, t0):
    """Top row of a dropping egg: falls from above, bounces once, settles."""
    rest = RIM - 4
    age = f - t0
    if age < 0:
        return None
    if age < FALL:
        u = age / FALL
        return round(-8 + (rest + 8) * u * u)
    if age < FALL + 6:
        return rest - round(2 * math.sin(math.pi * (age - FALL) / 6))
    return rest


def bow(img, cx, y):
    pink, deep = (255, 120, 180), (220, 50, 130)
    for dx, dy, c in ((-2, -1, pink), (-1, 0, pink), (-2, 1, pink), (2, -1, pink), (1, 0, pink), (2, 1, pink),
                      (0, 0, deep), (-1, 2, deep), (1, 2, deep)):
        put(img, cx + dx, y + dy, c)


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        efx.basket(img, BX, BASE, BW, BH, handle=9, back=True, front=False)
        # the chocolate bunny rises out of the middle
        if f >= CHOC_T:
            u = min(1.0, (f - CHOC_T) / 8)
            top = round(RIM + 2 - 9 * u + (1 if 8 <= f - CHOC_T < 11 else 0))
            blit(img, CHOC_BUNNY.img(0), BX + BW // 2 - 2, top)
        for x, c, pat, t0 in EGGS:
            y = egg_y(f, t0)
            if y is not None:
                efx.egg(img, x, y, 5, 7, c, pat)
        # paper grass along the rim
        for x in range(BX + 1, BX + BW - 1):
            g = efx.GRASS_HI if x % 2 else efx.GRASS
            put(img, x, RIM - 1, g if (x * 5) % 7 < 4 else efx.GRASS)
        efx.basket(img, BX, BASE, BW, BH)
        if f >= BOW_T:  # the bow lands on the handle's left shoulder
            u = min(1.0, (f - BOW_T) / 6)
            bow(img, BX + 5, round(RIM - 9 - 4 * (1 - u)))
        for x, c, pat, t0 in EGGS:
            a = f - (t0 + FALL)
            if 0 <= a < 8:
                sparkle(img, x + 2, RIM - 5, a, 1 - a / 8)
        if 0 <= f - CHOC_T - 8 < 10:
            a = f - CHOC_T - 8
            sparkle(img, BX + BW // 2, RIM - 8, a, 1 - a / 10, color=(255, 230, 160))
        if f >= sec(10):
            k = min(1.0, (f - sec(10)) / 15)
            glitter(img, 9, f, n=10, period=45, area=(BX - 4, 0, BX + BW + 4, RIM + 2), strength=0.8 * k)
        # little eggs on the table either side
        for x, c in ((4, efx.BLUE), (9, efx.PEACH), (60, efx.PINK), (65, efx.LEMON)):
            efx.small_egg(img, x, BASE - 4, c)
        frames.append(img)
    return frames
