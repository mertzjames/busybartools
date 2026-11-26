"""Fireworks Finale: red and gold fireworks over a pagoda and the rooftops, building to a big volley; the town
dims and HAPPY / NEW YEAR shines in gold (docs/DECISIONS.md D2, D9).
"""

from __future__ import annotations

from busybar.canvas import W, ease_in_out, phase, sec, vgradient
from busybar.party import Firework, glitter

import lnyfx as fx
import textstyle

NAME = "finale"
TITLE = "Fireworks Finale"
SECONDS = 15
KEYFRAMES = [(1.6, "The first rocket bursts in gold"), (4.2, "Red and gold over the pagoda"),
             (7.4, "The big volley"), (10.5, "HAPPY NEW YEAR"), (14.0, "Glitter and willows")]

N = sec(SECONDS)
RED_SET = (fx.RED, (255, 80, 60), fx.GOLD)
GOLD_SET = (fx.GOLD, fx.GOLD_LIGHT, (255, 250, 220))

SHOW = [  # (seconds, x, y, kind, colors)
    (1.2, 20, 5, "peony", GOLD_SET), (2.4, 52, 4, "ring", RED_SET), (3.3, 34, 3, "peony", RED_SET),
    (4.0, 62, 5, "willow", None), (4.6, 10, 4, "ring", GOLD_SET), (5.4, 44, 5, "palm", RED_SET),
    (6.2, 26, 3, "peony", GOLD_SET), (6.6, 58, 3, "peony", RED_SET), (7.0, 16, 6, "ring", RED_SET),
    (7.3, 40, 4, "peony", GOLD_SET), (7.6, 66, 5, "ring", GOLD_SET), (7.9, 30, 5, "willow", None),
    (8.3, 50, 3, "peony", RED_SET), (8.8, 8, 3, "willow", None), (9.6, 36, 2, "ring", GOLD_SET),
    (10.6, 6, 4, "peony", RED_SET), (11.4, 65, 3, "willow", None), (12.3, 7, 5, "ring", GOLD_SET),
    (13.1, 64, 4, "peony", RED_SET), (13.8, 5, 3, "willow", None),
]


def render():
    town = vgradient(fx.NIGHT_TOP, (44, 12, 40))
    fx.rooftops(town, base=13, seed=9, lit=0.6)
    fx.pagoda(town, 40, base=13, tiers=3)
    works = [Firework(100 + i, sec(s), x, y, colors=c, kind=k, speed=1.0 if k != "palm" else 0.9)
             for i, (s, x, y, k, c) in enumerate(SHOW)]
    frames = []
    for f in range(N):
        img = town.copy()
        dim = 0.55 * ease_in_out(phase(f, sec(9.2), sec(10.2)))
        if dim:
            fx.dim_rect(img, 0, 0, W, 16, dim)
        for w in works:
            w.draw(img, f, alpha=1.0 - 0.45 * (dim / 0.55))
        if f >= sec(9.4):
            r1 = int(31 * ease_in_out(phase(f, sec(9.4), sec(10.0))))
            r2 = int(47 * ease_in_out(phase(f, sec(9.9), sec(10.6))))
            textstyle.draw(img, "HAPPY", textstyle.STYLES["top"], x=(W - 29) // 2, reveal=r1, y=0)
            textstyle.draw(img, "NEW YEAR", textstyle.STYLES["bot"], x=(W - 45) // 2, reveal=r2, y=8)
        if f >= sec(10.6):
            glitter(img, seed=21, f=f, n=14, period=36, strength=0.8)
        frames.append(img)
    return frames
