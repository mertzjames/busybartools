"""Card backdrop for the clock and the countdown/greeting cards: a seamless 4 s loop of a deep wine-red wall, two
glowing red lanterns in the top corners, plum-blossom sprigs in the bottom corners, and a few faint gold glints
(docs/DECISIONS.md D7).

The app draws live text ON TOP of this, so the middle stays calm: the lanterns keep to rows 0-7 and the outer
5 columns, and the blossoms to the outer 3 columns. Text areas: the time occupies rows 2-14, x 19-53; the countdown
`N DAYS` rows 1-8 and `TO LUNAR NEW YEAR` rows 10-15, x 4-68; two big lines rows 0-15, x 12-60.
"""

from __future__ import annotations

from busybar.canvas import put, sec, vgradient
from busybar.party import glitter

import lnyfx as fx

NAME = "card_bg"
TITLE = "Card backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Card backdrop")]

TWIG = (120, 70, 50)
BLOSSOM = (255, 150, 190)


def sprig(img, x0: int, mirror: bool) -> None:
    """A plum-blossom twig rising from the bottom corner."""
    pts = [(0, 15), (1, 14), (1, 13), (0, 12), (1, 11), (0, 10)]
    flowers = [(1, 12), (0, 11), (1, 10), (1, 9)]
    for dx, y in pts:
        put(img, x0 + (-dx if mirror else dx), y, TWIG)
    for dx, y in flowers:
        put(img, x0 + (-dx if mirror else dx), y, BLOSSOM)
    put(img, x0 + (-1 if mirror else 1), 12, fx.GOLD_LIGHT, 0.6)


def render():
    bg = vgradient(fx.WINE_TOP, fx.WINE_BOTTOM)
    sprig(bg, 0, mirror=False)
    sprig(bg, 71, mirror=True)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        glitter(img, seed=77, f=f, n=7, period=LOOP, strength=0.3, colors=(fx.GOLD, fx.GOLD_LIGHT))
        fx.lantern(img, 4, 0, f, size=1, string=1, seed=1)
        fx.lantern(img, 67, 0, f, size=1, string=1, seed=2)
        frames.append(img)
    return frames
