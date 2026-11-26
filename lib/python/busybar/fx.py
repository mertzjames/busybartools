"""Deterministic effects: starfields, sparkles, particles, smoke, mist, confetti (shared render kit).

Everything is seeded so a rebuild produces byte-identical .anim files.
"""

from __future__ import annotations

import math
import random

from .canvas import H, W, add, mix, put


class Stars:
    """Twinkling stars. Periodic in `period` frames so loops are seamless."""

    def __init__(self, seed: int, n: int = 18, ymax: int = H, period: int = 60, color=(255, 255, 255),
                 dim: float = 0.15, bright: float = 0.9):
        rng = random.Random(seed)
        self.stars = [(rng.randrange(W), rng.randrange(ymax), rng.randrange(1, 4), rng.random()) for _ in range(n)]
        self.period, self.color, self.dim, self.bright = period, color, dim, bright

    def draw(self, img, f: int, alpha: float = 1.0) -> None:
        for x, y, speed, ph in self.stars:
            k = 0.5 + 0.5 * math.sin(2 * math.pi * (speed * f / self.period + ph))
            a = (self.dim + (self.bright - self.dim) * k ** 3) * alpha
            put(img, x, y, self.color, a)


class Particles:
    """Simple ballistic particles with life, fade and color ramp."""

    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
        self.items: list[dict] = []

    def emit(self, x, y, n=1, vx=(0, 0), vy=(0, 0), life=(10, 20), colors=((255, 255, 255),), gravity=0.0,
             drag=1.0, glow=False):
        for _ in range(n):
            self.items.append({
                "x": x, "y": y,
                "vx": self.rng.uniform(*vx), "vy": self.rng.uniform(*vy),
                "life": self.rng.randint(*life), "age": 0,
                "c": self.rng.choice(colors), "g": gravity, "drag": drag, "glow": glow,
            })

    def step_draw(self, img) -> None:
        alive = []
        for p in self.items:
            t = p["age"] / max(1, p["life"])
            a = 1.0 - t ** 2
            (add if p["glow"] else put)(img, p["x"], p["y"], p["c"], a)
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += p["g"]
            p["vx"] *= p["drag"]
            p["vy"] *= p["drag"]
            p["age"] += 1
            if p["age"] < p["life"]:
                alive.append(p)
        self.items = alive


SPARKLE = ((255, 255, 255), (255, 242, 160), (255, 216, 74), (190, 220, 255))
FIRE = ((255, 240, 120), (255, 190, 40), (255, 120, 20), (230, 50, 20))
HOUSE = ((200, 16, 46), (242, 181, 21), (30, 140, 70), (190, 195, 205), (40, 80, 200), (150, 100, 50),
         (250, 210, 40), (30, 30, 30))


def sparkle(img, x, y, f, a: float = 1.0, color=(255, 255, 255)) -> None:
    """A 4-point twinkle that pulses with frame f."""
    k = 0.5 + 0.5 * math.sin(f * 0.9)
    add(img, x, y, color, a)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        add(img, x + dx, y + dy, color, a * 0.55 * k)


def puff(img, cx, cy, r: float, color, a: float = 1.0) -> None:
    """Soft round smoke/cloud puff."""
    ri = int(math.ceil(r)) + 1
    for yy in range(int(cy) - ri, int(cy) + ri + 1):
        for xx in range(int(cx) - ri, int(cx) + ri + 1):
            d = math.hypot(xx - cx, yy - cy)
            k = max(0.0, min(1.0, r - d + 0.5))
            if k > 0:
                put(img, xx, yy, color, a * k)


def moon(img, x, y, color=(255, 246, 200)) -> None:
    """3x4 crescent."""
    for dx, dy in ((1, 0), (2, 0), (0, 1), (0, 2), (1, 3), (2, 3)):
        put(img, x + dx, y + dy, color)
    put(img, x + 1, y + 1, color, 0.5)
    put(img, x + 1, y + 2, color, 0.5)


def hills(img, seed: int, base: int, amp: float, color, scroll: float = 0.0, freq: float = 0.12) -> None:
    """Rolling hill silhouette filling from y=base-amp.. to bottom."""
    rng = random.Random(seed)
    p1, p2 = rng.random() * 6, rng.random() * 6
    for x in range(W):
        xx = x + scroll
        h = base - amp * (0.6 * math.sin(xx * freq + p1) + 0.4 * math.sin(xx * freq * 2.3 + p2))
        for y in range(int(round(h)), H):
            put(img, x, y, color)


def bricks(img, color, mortar, y0: int = 0, y1: int = H, bw: int = 6, bh: int = 3) -> None:
    for y in range(y0, y1):
        row = (y - y0) // bh
        for x in range(W):
            edge = (y - y0) % bh == bh - 1 or (x + (row % 2) * (bw // 2)) % bw == 0
            put(img, x, y, mortar if edge else color)


def mix_colors(a, b, t):
    return mix(a, b, t)
