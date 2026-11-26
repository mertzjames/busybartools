"""Clock card backdrop: a seamless 4 s loop of a spring evening: a deep blue sky with a few soft stars, a strip of
grass along the bottom with tiny tulips, and a small decorated egg tucked in each corner (docs/DECISIONS.md D7).
The live time and date are drawn over the middle, which stays dark and still."""

from busybar.canvas import W, put, sec, vgradient
from busybar.fx import Stars

import efx

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]
TEXT_GAP = (6, 64)  # the time and date stay inside these columns, clear of the corner eggs and tulips


def render():
    bg = vgradient((10, 14, 46), (22, 26, 70))
    for x in range(W):  # a dark spring-green strip of grass, a lit edge on top
        put(bg, x, 15, (24, 84, 40))
        if (x * 7) % 5 < 2:
            put(bg, x, 14, (40, 120, 52))
    for x, c in ((1, efx.PINK), (69, efx.LILAC)):  # tiny tulips at the far edges, clear of the date
        put(bg, x, 14, (40, 130, 56))
        put(bg, x, 13, c)
    efx.small_egg(bg, 3, 12, efx.LEMON)
    efx.small_egg(bg, 65, 12, efx.MINT)
    stars = Stars(seed=5, n=9, ymax=2, period=LOOP, color=(220, 226, 255), dim=0.1, bright=0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        frames.append(img)
    return frames
