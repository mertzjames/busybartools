"""Ball Drop Rehearsal: a glittering ball starts down its pole over the city, stops halfway... NOT YET! and zips
back up. A generic ball and pole, no real landmark."""

import math

from busybar.canvas import FPS, add, ease_in, ease_in_out, ease_out, lerp, phase, put, sec, vgradient
from busybar.font import draw_text
from party import CYAN, GOLD, GOLD_LIGHT, PINK, SILVER, VIOLET, WHITE, dim, glitter, hash01, skyline

NAME = "ball_drop"
TITLE = "Ball Drop Rehearsal"
SECONDS = 13
KEYFRAMES = [(1.0, "The ball waits at the top"), (4.5, "Searchlights; down it goes"), (7.6, "Halfway..."),
             (9.0, "NOT YET!"), (10.4, "Back up it zips"), (12.4, "Wait for midnight")]

CX = 36
R = 3.4
FACETS = (GOLD, SILVER, PINK, CYAN, VIOLET, WHITE)


def ball(img, cy: float, f: int, bright: float = 1.0) -> None:
    for y in range(int(cy - R - 1), int(cy + R + 2)):
        for x in range(int(CX - R - 1), int(CX + R + 2)):
            d2 = (x - CX) ** 2 + (y - cy) ** 2
            if d2 > R * R:
                continue
            facet = (x + 2 * round(y - cy) + f // 4) % len(FACETS)
            c = FACETS[facet]
            k = (0.55 + 0.45 * hash01(x, round(y - cy), f // 2)) * (1 - 0.35 * d2 / (R * R)) * bright
            put(img, x, y, dim(c, k))
    for dx, dy in ((0, -5), (0, 5), (-5, 0), (5, 0), (-4, -4), (4, -4), (-4, 4), (4, 4)):  # halo
        add(img, CX + dx * 0.9, cy + dy * 0.9, GOLD_LIGHT, 0.12 * bright)


def render():
    bg = vgradient((6, 6, 26), (26, 12, 48))
    skyline(bg, seed=71, base=16, color=(28, 30, 60), lit=0.4)
    # the building the pole stands on
    for x in range(CX - 6, CX + 7):
        for y in range(12, 16):
            put(bg, x, y, (44, 46, 82))
    for x in range(CX - 5, CX + 6, 2):
        put(bg, x, 13, (255, 220, 120))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        glitter(img, 72, f, n=10, period=FPS * 5, colors=(SILVER, GOLD_LIGHT), ymax=7, strength=0.55)
        # searchlights sweeping up from the street
        if t >= 3.0:
            k = phase(f, sec(3.0), sec(4.0))
            for sx, ph in ((8, 0.0), (64, 2.0)):
                a = math.pi / 2 + 0.55 * math.sin(t * 1.3 + ph)
                for s in range(2, 26):
                    add(img, sx + s * math.cos(a) * (1 if sx < CX else -1), 15 - s * math.sin(a), (120, 140, 220),
                        0.18 * k * (1 - s / 26))
        # the pole
        for y in range(0, 12):
            put(img, CX, y, (150, 156, 186))
        # the ball's path: top, slow drop to halfway, stop, wobble, zip back up with a bounce
        top, half = 3.5, 8.5
        if t < 3.0:
            cy = top
        elif t < 7.5:
            cy = lerp(top, half, ease_in_out(phase(f, sec(3.0), sec(7.5))))
        elif t < 9.6:
            cy = half + 0.4 * math.sin((t - 7.5) * 14) * (1 - phase(f, sec(7.5), sec(8.4)))
        elif t < 10.4:
            cy = lerp(half, top - 1.5, ease_in(phase(f, sec(9.6), sec(10.4))))
        else:
            cy = top - 1.5 + 1.5 * ease_out(phase(f, sec(10.4), sec(11.0)))
        ball(img, cy, f)
        if 9.6 <= t < 10.4:  # speed lines
            for k in range(3):
                add(img, CX - 4 + k * 4, cy + 4 + k % 2, WHITE, 0.5)
        if 8.2 <= t < 11.6:
            a = phase(f, sec(8.2), sec(8.5)) * (1 - phase(f, sec(11.2), sec(11.6)))
            shake = 1 if t < 8.8 and f % 2 else 0
            draw_text(img, "NOT", 7 + shake, 2, None, gradient=(WHITE, PINK), shadow=(80, 0, 50), alpha=a)
            draw_text(img, "YET!", 46 - shake, 2, None, gradient=(WHITE, PINK), shadow=(80, 0, 50), alpha=a)
        if t >= 11.6:
            a = phase(f, sec(11.6), sec(12.0))
            draw_text(img, "SOON!", 3, 2, None, gradient=(WHITE, GOLD), shadow=(90, 40, 0), alpha=a)
        frames.append(img)
    return frames
