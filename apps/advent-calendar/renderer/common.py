"""App-local drawing helpers shared by the Advent Calendar scenes (snow, ground, pines, glows, aurora, lights).

Everything is deterministic: every random source is a seeded random.Random.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, H, W, add, mix, put, sec, vgradient

# Palette shared across scenes, so the 25 days feel like one calendar.
NIGHT = ((4, 8, 30), (14, 26, 58))          # default night sky (top, bottom)
DUSK = ((10, 10, 38), (40, 24, 62))
SNOW = (226, 236, 255)
SNOW_SHADE = (150, 170, 210)
SNOW_DEEP = (96, 116, 160)
GOLD = (255, 214, 92)
WARM = (255, 170, 70)
RED = (214, 28, 44)
GREEN = (30, 150, 70)
PINE = (24, 104, 58)
PINE_DARK = (14, 70, 40)
LIGHTS = ((255, 70, 70), (255, 210, 60), (70, 200, 255), (90, 230, 110), (255, 120, 220))

TEXT_GOLD = ((255, 240, 170), (240, 160, 40))
TEXT_SHADOW = (90, 20, 10)

FRAMES = sec  # alias: seconds -> frames


def sky(colors=NIGHT):
    return vgradient(*colors)


class Snow:
    """Falling snow. Each flake falls at its own speed with a small sideways sway; wraps top to bottom."""

    def __init__(self, seed: int, n: int = 26, speed=(0.12, 0.35), color=SNOW, dim=(0.35, 0.9), ymax: int = H,
                 wind: float = 0.0):
        rng = random.Random(seed)
        self.flakes = [(rng.uniform(0, W), rng.uniform(0, ymax), rng.uniform(*speed), rng.uniform(0, 6.28),
                        rng.uniform(*dim)) for _ in range(n)]
        self.color, self.ymax, self.wind = color, ymax, wind

    def draw(self, img, f: int, alpha: float = 1.0, below=None) -> None:
        for x0, y0, v, ph, a in self.flakes:
            y = (y0 + v * f) % self.ymax
            x = (x0 + self.wind * v * f + 0.8 * math.sin(ph + f * 0.07)) % W
            if below is not None and y >= below(int(x) % W):
                continue
            put(img, x, y, self.color, a * alpha)


def ground_heights(seed: int, base: float, amp: float = 1.0, freq: float = 0.18):
    rng = random.Random(seed)
    p = rng.random() * 6
    return [base - amp * math.sin(x * freq + p) - 0.5 * amp * math.sin(x * freq * 2.7 + p * 2) for x in range(W)]


def snow_ground(img, heights, color=SNOW, shade=SNOW_SHADE, deep=SNOW_DEEP) -> None:
    """Snowy ground below a height profile: bright crust, shaded body."""
    for x, h in enumerate(heights):
        top = int(round(h))
        for y in range(max(0, top), H):
            d = y - top
            put(img, x, y, color if d == 0 else (shade if d < 3 else deep))


def flat_ground(img, y0: int, color=SNOW, shade=SNOW_SHADE) -> None:
    for y in range(y0, H):
        for x in range(W):
            put(img, x, y, color if y == y0 else shade)


def pine(img, cx: int, base: int, h: int, color=PINE, dark=PINE_DARK, snow: bool = True, a: float = 1.0) -> None:
    """Procedural pine: stacked triangle tiers with optional snow on each tier's edge."""
    trunk = (96, 60, 30)
    put(img, cx, base, trunk, a)
    top = base - h
    for y in range(top, base):
        k = (y - top) / max(1, h - 1)
        tier = ((y - top) % 3) / 2
        half = int(round(k * h * 0.42 + tier * 0.8))
        for x in range(cx - half, cx + half + 1):
            edge = abs(x - cx) == half
            c = dark if (x < cx and not edge) else color
            if snow and edge and (y - top) % 3 == 2:
                c = SNOW
            put(img, x, y, c, a)


def glow(img, cx: float, cy: float, r: float, color, a: float = 1.0) -> None:
    """Soft additive radial glow."""
    ri = int(math.ceil(r))
    for y in range(int(cy) - ri, int(cy) + ri + 1):
        for x in range(int(cx) - ri, int(cx) + ri + 1):
            d = math.hypot(x - cx, y - cy) / max(0.01, r)
            if d < 1:
                add(img, x, y, color, a * (1 - d) ** 2)


def aurora(img, f: int, y0: float = 2.0, amp: float = 1.6, colors=((40, 220, 140), (60, 140, 255)), a: float = 0.5,
           period: int = FPS * 8) -> None:
    """Two soft wavy curtains near the top of the sky."""
    for band, c in enumerate(colors):
        for x in range(W):
            t = 2 * math.pi * f / period
            yc = y0 + band * 2 + amp * math.sin(x * 0.12 + t + band * 1.7) + 0.6 * math.sin(x * 0.31 - t * 2)
            k = 0.5 + 0.5 * math.sin(x * 0.07 + t * 1.5 + band)
            for dy in range(-2, 3):
                put(img, x, yc + dy, c, a * k * (1 - abs(dy) / 3))


def twinkle_lights(img, points, f: int, rate: int = 6, a: float = 1.0, seed: int = 0) -> None:
    """Colored bulbs at points, cycling colors every `rate` frames."""
    for i, (x, y) in enumerate(points):
        c = LIGHTS[(i + f // rate + seed) % len(LIGHTS)]
        put(img, x, y, c, a)


def string_points(x0: int, x1: int, y: int, sag: float, step: int = 3):
    """Bulb positions along a sagging string from x0 to x1."""
    pts = []
    for x in range(x0, x1 + 1, step):
        t = (x - x0) / max(1, x1 - x0)
        pts.append((x, int(round(y + sag * 4 * t * (1 - t)))))
    return pts


def notes(img, f: int, seeds, x0: float, y0: float, color=(255, 230, 120)) -> None:
    """Rising music notes (3x4 eighth notes) launched at the given frame offsets."""
    note = ["..#", "..#", "###", "##."]
    for k, start in enumerate(seeds):
        age = f - start
        if not 0 <= age < 40:
            continue
        x = x0 + k * 3 + math.sin(age * 0.25 + k) * 2
        y = y0 - age * 0.25
        alpha = 1.0 - (age / 40) ** 2
        for dy, row in enumerate(note):
            for dx, ch in enumerate(row):
                if ch == "#":
                    put(img, x + dx, y + dy, color, alpha)


def mix3(a, b, t):
    return mix(a, b, t)
