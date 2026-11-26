"""Backdrops for the live screens. The app draws the time-dependent text on top of these (docs/DECISIONS.md D8).

card        countdown / clock card between scenes          4 s loop
final       final-minute screen, T-60 ... T-31              2 s loop: marquee lights and two beacons
final_fast  final-minute screen, T-30 ... T-11              1 s loop: the same, twice as fast and brighter
final10     one huge digit per second                       1 s loop: a flash and a ring on every second
burst       midnight                                        3 s one-shot: white flash, rings of sparks, rockets
fireworks   HAPPY NEW YEAR                                  6 s loop: fireworks around the text, seamless

Loops are periodic in their frame count, so the firmware's looping never jumps.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

from busybar.canvas import FPS, H, W, add, mix, put, sec, vgradient
from party import (CYAN, GOLD, GOLD_LIGHT, LIME, PINK, SILVER, VIOLET, WHITE, Firework, dim, draw_looped,
                   glitter, hash01)

NIGHT = ((8, 4, 26), (24, 8, 42))


def card_render():
    n = sec(4)
    bg = vgradient(*NIGHT)
    frames = []
    for f in range(n):
        img = bg.copy()
        glitter(img, 91, f, n=16, period=n, colors=(GOLD_LIGHT, SILVER, (255, 160, 220)), strength=0.55)
        # a slow shimmer along the bottom edge
        for x in range(W):
            k = 0.5 + 0.5 * math.sin(2 * math.pi * (x / 24 - f / n))
            put(img, x, 15, dim(GOLD, 0.12 + 0.3 * k ** 4))
        frames.append(img)
    return frames


def marquee(img, f: int, n: int, speed: int, bright: float) -> None:
    """Chasing bulbs along the top row and two spinning beacons at the sides."""
    for x in range(W):
        if x % 3 != 0:
            continue
        lit = ((x // 3) + (f * speed * 3) // n) % 3 == 0
        c = (GOLD, PINK, CYAN)[(x // 3) % 3]
        put(img, x, 0, dim(c, bright if lit else 0.2))
    for bx, direction, c in ((6, 1, PINK), (65, -1, CYAN)):
        a0 = direction * 2 * math.pi * f * speed / n
        for k in range(2):
            a = a0 + k * math.pi
            for s in range(1, 7):
                add(img, bx + s * math.cos(a), 8 + s * 0.8 * math.sin(a), c, bright * (0.7 - s * 0.09))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                put(img, bx + dx, 8 + dy, dim(c, 0.6 if dx or dy else 1.0))
        put(img, bx, 8, WHITE)


def final_render(speed: int, n: int, bright: float):
    def render():
        bg = vgradient((10, 4, 28), (30, 6, 44))
        frames = []
        for f in range(n):
            img = bg.copy()
            glitter(img, 92, f, n=10, period=n, colors=(GOLD_LIGHT, SILVER), strength=0.4 * bright, area=(14, 1, 58, 14))
            marquee(img, f, n, speed, bright)
            frames.append(img)
        return frames
    return render


def final10_render():
    """A beat every second: a soft flash, and sparks and rays thrown out from behind the digit to the edges."""
    n = FPS  # exactly one second
    frames = []
    for f in range(n):
        k = f / n
        flash = (1 - k) ** 3
        img = vgradient(mix((8, 4, 26), (54, 26, 92), flash), mix((24, 8, 42), (84, 20, 80), flash))
        for i in range(16):
            a = 2 * math.pi * (i + 0.5) / 16
            for j in range(3):  # each spark drags a short tail
                d = 13 + k * 30 - j * 2.2
                add(img, 36 + d * math.cos(a), 8 + d * 0.5 * math.sin(a), (CYAN, PINK, GOLD, LIME)[i % 4],
                    (1 - k) ** 1.4 * (1.0, 0.45, 0.2)[j])
        for x in (0, W - 1):  # edge bars pulse with the beat
            for y in range(1, 15):
                put(img, x, y, dim(GOLD, 0.25 + 0.75 * flash))
        frames.append(img)
    return frames


def burst_render():
    n = sec(3)
    rockets = [Firework(seed=900 + i, t0=sec(s), x=x, y=y, kind=k, colors=c, speed=sp, rocket=False)
               for i, (s, x, y, k, c, sp) in enumerate([
                   (0.9, 14, 5, "peony", (PINK, GOLD), 1.0), (1.2, 58, 6, "peony", (CYAN, WHITE), 1.0),
                   (1.6, 36, 4, "ring", (GOLD_LIGHT,), 1.2), (2.0, 24, 9, "palm", (LIME, PINK), 1.0),
                   (2.2, 50, 9, "palm", (VIOLET, GOLD), 1.0)])]
    frames = []
    for f in range(n):
        k = f / FPS
        flash = max(0.0, 1 - k / 0.5) ** 2
        img = vgradient(mix(NIGHT[0], (110, 70, 170), flash), mix(NIGHT[1], (150, 50, 120), flash))
        for ring, (c, speed) in enumerate(((GOLD, 34), (PINK, 26), (CYAN, 19))):
            r = k * speed
            if r < 2:
                continue
            for a in range(0, 360, 6):
                ra = math.radians(a + ring * 2)
                fade = max(0.0, 1 - k / 1.8) * (0.55 + 0.45 * hash01(a, ring, f // 2))
                add(img, 36 + r * math.cos(ra), 8 + r * 0.42 * math.sin(ra), c, fade)
        for rk in rockets:
            rk.draw(img, f)
        frames.append(img)
    return frames


def fireworks_render():
    n = sec(6)
    bg = vgradient(*NIGHT)
    spots = [  # (seconds, x, y, kind, colors, speed): around the edges, the text sits in the middle
        (0.2, 7, 5, "peony", (PINK, WHITE), 0.8), (0.9, 64, 4, "ring", (CYAN,), 0.85),
        (1.7, 22, 3, "palm", (GOLD, PINK), 0.8), (2.4, 52, 3, "peony", (LIME, GOLD), 0.8),
        (3.1, 8, 9, "willow", (GOLD,), 0.8), (3.7, 65, 9, "peony", (VIOLET, CYAN), 0.8),
        (4.4, 36, 2, "ring", (GOLD_LIGHT,), 0.9), (5.2, 14, 4, "peony", (CYAN, PINK), 0.8),
        (5.6, 58, 6, "palm", (PINK, GOLD), 0.8),
    ]
    rockets = [Firework(seed=950 + i, t0=sec(s), x=x, y=y, kind=k, colors=c, speed=sp, rise=sec(0.6))
               for i, (s, x, y, k, c, sp) in enumerate(spots)]
    frames = []
    for f in range(n):
        img = bg.copy()
        glitter(img, 96, f, n=12, period=n, colors=(GOLD_LIGHT, SILVER), strength=0.45)
        draw_looped(rockets, img, f, n)
        band(img)
        frames.append(img)
    return frames


def band(img, x0: int = 11, x1: int = 61, keep: float = 0.35) -> None:
    """Darken the middle, where the live HAPPY NEW YEAR text sits, with soft edges (the text reads cleanly)."""
    px = img.load()
    for x in range(max(0, x0 - 4), min(W, x1 + 4)):
        edge = min(1.0, max(0.0, min(x - (x0 - 4), (x1 + 4) - x) / 4))
        k = 1 - (1 - keep) * edge
        for y in range(H):
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * k + 0.5), int(g * k + 0.5), int(b * k + 0.5), a)


def _mod(name, title, seconds, render, caption):
    return SimpleNamespace(NAME=name, TITLE=title, SECONDS=seconds, KEYFRAMES=[(0.0, caption)], render=render)


CARD = _mod("card_bg", "Countdown card backdrop", 4, card_render, "Card backdrop")
FINAL = _mod("final_bg", "Final minute backdrop", 2, final_render(1, sec(2), 0.85), "Marquee and beacons")
FINAL_FAST = _mod("final_fast_bg", "Final 30 s backdrop", 1, final_render(1, sec(1), 1.0), "Twice as fast")
FINAL10 = _mod("final10_bg", "Final ten backdrop", 1, final10_render, "A flash every second")
BURST = _mod("burst", "Midnight burst", 3, burst_render, "Midnight flash")
FIREWORKS = _mod("fireworks_bg", "Celebration backdrop", 6, fireworks_render, "Fireworks loop")
FIREWORKS.KEYFRAMES = [(0.4, "Fireworks loop"), (2.6, "Around the text"), (4.6, "Seamless 6 s loop")]
BURST.KEYFRAMES = [(0.0, "White flash at 00:00:00"), (0.8, "Rings of sparks"), (1.8, "Rockets everywhere")]
