"""Easter Sunrise (the finale): a violet dawn over rolling spring hills. The sun rises and the sky warms into
morning; Easter lilies and daffodils open in the foreground on either side. Then HAPPY EASTER appears in the sky (docs/DECISIONS.md D3: the one calm scene with a traditional symbol, the lily)."""

import math

from busybar import font
from busybar.canvas import W, mix, new, put, sec
from busybar.fx import Stars
from busybar.party import glitter

import efx

NAME = "sunrise"
TITLE = "Easter Sunrise"
SECONDS = 16
KEYFRAMES = [(0.5, "Dawn over the hills"), (3.5, "The sun rises"), (6.5, "Lilies open"),
             (9.0, "Morning"), (12.0, "HAPPY EASTER"), (15.4, "Happy Easter")]

STEPS = 24  # the sky warms in this many steps (keeps the .anim small: no per-frame full-screen change)
# sky colors (top, middle at row 7, horizon at row 10): violet dawn -> clear spring morning with a gold horizon
DAWN = ((16, 12, 56), (70, 30, 92), (200, 84, 84))
MORNING = ((40, 104, 220), (110, 170, 246), (255, 196, 110))
SUN_X = 32  # in the gap between HAPPY and EASTER (x 30-34), so the greeting never covers it
TEXT = "HAPPY EASTER"
TEXT_T = sec(10.5)


def hill(x, base, amp, freq, ph):
    return base - amp * (0.6 * math.sin(x * freq + ph) + 0.4 * math.sin(x * freq * 2.1 + ph * 1.7))


def edge(x):
    """The front hill rises at both ends, so the flowers there stand against green, not the bright sky."""
    return 2.5 * max(0.0, (abs(x - 35.5) - 18) / 18)


def valley(x):
    """The back hills dip where the sun comes up."""
    return 2.0 * max(0.0, 1 - abs(x - SUN_X) / 9)


BACK = [hill(x, 10.6, 1.2, 0.13, 1.0) + valley(x) for x in range(W)]
FRONT = [hill(x, 13.2, 0.8, 0.09, 4.0) - edge(x) for x in range(W)]


def sky_color(y, q):
    top, mid, low = (mix(DAWN[k], MORNING[k], q) for k in range(3))
    if y <= 7:
        return mix(top, mid, y / 7)
    return mix(mid, low, (y - 7) / 3)


def render():
    stars = Stars(seed=9, n=12, ymax=7, period=60, color=(230, 230, 255), dim=0.1, bright=0.7)
    frames = []
    for f in range(sec(SECONDS)):
        u = min(1.0, f / sec(9.0))
        q = round(u * STEPS) / STEPS
        img = new()
        for y in range(16):
            c = sky_color(y, q)
            for x in range(W):
                put(img, x, y, c)
        if q < 0.5:
            stars.draw(img, f, alpha=1 - 2 * q)
        # the sun climbs out of the valley between the hills, then holds
        sy = round(16 - 12 * math.sin(0.5 * math.pi * min(1.0, f / sec(9.5))))
        efx.sun(img, SUN_X, sy, r=3.0, rays=False)
        for x in range(W):
            for y in range(round(BACK[x]), 16):
                put(img, x, y, mix((50, 100, 84), (96, 180, 106), q))
            ft = round(FRONT[x])
            for y in range(ft, 16):
                put(img, x, y, mix((60, 130, 70), (120, 214, 90), q) if y == ft else
                    mix((30, 90, 50), (60, 166, 70), q))
        # lilies and daffodils on the near hill open as the light comes
        bloom = min(1.0, max(0.0, (f - sec(4.5)) / sec(3.0)))
        for k, (x, kind) in enumerate(((3, "lily"), (8, "daff"), (13, "lily"), (58, "lily"), (63, "daff"),
                                       (68, "lily"))):
            o = min(1.0, max(0.0, bloom * 1.6 - (k % 3) * 0.3))
            if kind == "lily":
                efx.lily(img, x, 15, 4, o, flip=x > 36)
            else:
                efx.daffodil(img, x, 15, 4, o)
        # HAPPY EASTER spelled out across the sky, letter by letter, either side of the sun
        if f >= TEXT_T:
            age = f - TEXT_T
            k = min(0.4, age / 25)  # soften the bright sky behind each word, not the sun between them
            efx.dim_rect(img, 0, 0, SUN_X - 5, 8, k, feather=1)
            efx.dim_rect(img, SUN_X + 5, 0, W - 1, 8, k, feather=1)
            n = min(len(TEXT), age // 2 + 1)
            x0 = (W - font.text_width(TEXT, "big")) // 2
            shown = TEXT[:n]
            font.draw_text(img, shown[:6], x0, 1, None, font="big", gradient=((255, 210, 236), (255, 100, 176)),
                           shadow=(80, 20, 100))
            if n > 6:
                font.draw_text(img, shown[6:], x0 + font.text_width("HAPPY ", "big") + 1, 1, None, font="big",
                               gradient=((255, 252, 200), (255, 200, 50)), shadow=(80, 30, 120))
            if age > 30:
                glitter(img, 21, f, n=8, period=45, area=(0, 0, W, 9), strength=0.6)
        frames.append(img)
    return frames
