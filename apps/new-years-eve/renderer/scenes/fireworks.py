"""Fireworks Finale: rockets over the city skyline, peonies, rings, gold willows, then a big finale."""

from busybar.canvas import sec, vgradient
from party import CYAN, GOLD, GOLD_LIGHT, LIME, PINK, SILVER, VIOLET, WHITE, Firework, glitter, skyline

NAME = "fireworks"
TITLE = "Fireworks Finale"
SECONDS = 15
KEYFRAMES = [(1.2, "A first rocket"), (2.6, "Pink peony"), (5.0, "Rings and willows"), (8.4, "Over the skyline"),
             (12.6, "The finale"), (14.0, "Glitter falls")]

SHOW = [  # (seconds, x, y, kind, colors, speed)
    (1.6, 20, 5, "peony", (PINK, WHITE), 0.9),
    (3.0, 50, 4, "ring", (CYAN,), 1.0),
    (4.2, 33, 6, "willow", (GOLD,), 0.9),
    (5.4, 12, 4, "peony", (LIME, GOLD), 0.85),
    (6.2, 60, 6, "palm", (VIOLET, PINK), 1.0),
    (7.4, 40, 3, "peony", (GOLD, SILVER), 1.0),
    (8.4, 24, 5, "ring", (PINK,), 0.9),
    (9.0, 54, 4, "peony", (CYAN, WHITE), 0.9),
    (10.2, 36, 5, "willow", (GOLD,), 1.0),
    # finale
    (11.4, 14, 4, "peony", (PINK, GOLD), 0.9),
    (11.7, 58, 4, "peony", (CYAN, LIME), 0.9),
    (12.0, 36, 3, "ring", (GOLD_LIGHT,), 1.05),
    (12.3, 26, 6, "palm", (VIOLET, WHITE), 1.0),
    (12.5, 48, 6, "palm", (PINK, GOLD), 1.0),
    (12.8, 6, 5, "peony", (LIME, CYAN), 0.8),
    (13.0, 66, 5, "peony", (GOLD, PINK), 0.8),
    (13.2, 36, 5, "willow", (GOLD,), 1.1),
]


def render():
    bg = vgradient((4, 4, 20), (20, 10, 40))
    skyline(bg, seed=81, base=16, color=(24, 26, 54), lit=0.35)
    rockets = [Firework(seed=800 + i, t0=sec(s), x=x, y=y, kind=k, colors=c, speed=sp, rise=sec(0.7))
               for i, (s, x, y, k, c, sp) in enumerate(SHOW)]
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        glitter(img, 82, f, n=8, period=60, colors=(SILVER, (180, 190, 255)), ymax=8, strength=0.4)
        for r in rockets:
            r.draw(img, f)
        frames.append(img)
    return frames
