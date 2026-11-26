"""Confetti Poppers: two party poppers fire confetti and curly streamers across the room. WOOHOO!"""

import math

from busybar.canvas import FPS, add, lerp, phase, put, sec, vgradient
from busybar.font import draw_text
from party import CYAN, GOLD, GOLD_LIGHT, LIME, PINK, VIOLET, WHITE, Confetti, dim, glitter, string_lights

NAME = "poppers"
TITLE = "Confetti Poppers"
SECONDS = 12
KEYFRAMES = [(1.0, "Two poppers, ready"), (1.9, "Pop! from the left"), (3.4, "Pop! from the right"),
             (5.5, "Confetti flutters down"), (7.4, "Both at once"), (10.5, "WOOHOO!")]

# (base x, base y, direction x, direction y, body color, stripe color, pop frames)
POPPERS = [
    (3, 15, 0.75, -0.66, PINK, GOLD, (sec(1.5), sec(7.0))),
    (68, 15, -0.75, -0.66, CYAN, GOLD_LIGHT, (sec(3.0), sec(7.0))),
]


def popper(img, bx, by, dx, dy, body, stripe, recoil: float) -> tuple[float, float]:
    """A cone 7 px long, widening toward the mouth; returns the mouth position."""
    bx -= dx * recoil
    by -= dy * recoil
    px, py = -dy, dx  # perpendicular
    for i in range(7):
        w = 0.5 + i * 0.32
        c = stripe if i % 3 == 1 else body
        for s in range(-int(w + 0.5), int(w + 0.5) + 1):
            put(img, bx + dx * i + px * s * 0.9, by + dy * i + py * s * 0.9, c)
    put(img, bx - dx, by - dy, (230, 230, 240))  # the string
    put(img, bx - 2 * dx, by - dy * 2 + 1, (230, 230, 240))
    return bx + dx * 7, by + dy * 7


def streamer(img, x0, y0, dx, dy, age: int, color, seed: int) -> None:
    """A curly ribbon that shoots out, then hangs and drifts down."""
    length = min(18, age * 2.2)
    drop = max(0, age - 10) * 0.08
    for i in range(int(length)):
        s = i / 18
        x = x0 + dx * i * 1.3 + math.sin(i * 0.9 + seed) * 1.4 * s
        y = y0 + dy * i * 1.1 + math.cos(i * 0.9 + seed) * 1.2 * s + (i * i) * 0.012 + drop * (1 + s * 2)
        put(img, x, y, color if i % 4 else dim(color, 0.6))


def render():
    bg = vgradient((8, 4, 26), (26, 8, 44))
    bursts = []
    for k, (bx, by, dx, dy, body, stripe, pops) in enumerate(POPPERS):
        for j, p in enumerate(pops):
            mouth = (bx + dx * 7, by + dy * 7)
            vx = (0.6, 2.2) if dx > 0 else (-2.2, -0.6)
            bursts.append(Confetti(seed=40 + k * 10 + j, t0=p, x=mouth[0], y=mouth[1], n=46, vx=vx, vy=(-2.0, -0.4),
                                   fall=(0.05, 0.12), stagger=2))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        glitter(img, 41, f, n=10, period=FPS * 4, strength=0.5, ymax=12)
        string_lights(img, f, y0=0, sag=1.8, spacing=7, colors=(GOLD, PINK, CYAN, VIOLET))
        for k, (bx, by, dx, dy, body, stripe, pops) in enumerate(POPPERS):
            recoil = 0.0
            for p in pops:
                if p <= f < p + 4:
                    recoil = 1.0 - (f - p) / 4
            mx, my = popper(img, bx, by, dx, dy, body, stripe, recoil)
            for j, p in enumerate(pops):
                age = f - p
                if 0 <= age < 3:  # muzzle flash
                    for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (dx * 2, dy * 2)):
                        add(img, mx + ox, my + oy, WHITE, 1 - age / 3)
                if age >= 0:
                    streamer(img, mx, my, dx, dy, age, (LIME, PINK, GOLD)[(k + j) % 3], k * 3 + j)
                    streamer(img, mx, my, dx * 0.8, dy * 1.2, age, (CYAN, VIOLET, GOLD_LIGHT)[(k + j) % 3], 7 + j)
        for b in bursts:
            b.draw(img, f, floor=15)
        if t >= 9.2:
            r = int(lerp(0, 46, phase(f, sec(9.2), sec(10.0))))
            fade = 1 - phase(f, sec(11.5), sec(12.0))
            draw_text(img, "WOOHOO!", 15, 5, None, gradient=(GOLD_LIGHT, PINK), shadow=(70, 0, 50), reveal=r,
                      alpha=fade)
        frames.append(img)
    return frames
