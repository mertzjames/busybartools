"""Party effects for this app: fireworks, confetti, string lights, a skyline, glitter (all deterministic).

Built app-locally on top of the shared kit (busybar.canvas / fx). Everything is a pure function of the frame
number (no stateful simulation), so loops can be made seamless by drawing events at t, t - period and t + period.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, mix, put

# Party palette (golds, silvers, neon): docs/DECISIONS.md D11
GOLD = (255, 196, 52)
GOLD_LIGHT = (255, 236, 150)
SILVER = (206, 214, 236)
WHITE = (255, 255, 255)
PINK = (255, 46, 170)
CYAN = (30, 214, 255)
LIME = (150, 255, 70)
VIOLET = (170, 90, 255)
ORANGE = (255, 130, 30)
NEON = (PINK, CYAN, LIME, GOLD, VIOLET)
CONFETTI = (GOLD, SILVER, PINK, CYAN, LIME, VIOLET)

NIGHT_TOP = (6, 4, 22)
NIGHT_BOTTOM = (22, 8, 40)


def hash01(*parts: int) -> float:
    """Deterministic pseudo-random 0..1 from integers (for per-frame flicker without RNG state)."""
    h = 2166136261
    for p in parts:
        h ^= p & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


def dim(c, k: float):
    return tuple(max(0, min(255, int(v * k + 0.5))) for v in c[:3])


# --- fireworks ------------------------------------------------------------------------------------------------

class Firework:
    """One rocket and its burst. `t0` is the burst frame; the rocket rises during the `rise` frames before it.

    kind: "peony" (round, mixed speeds), "ring" (one speed), "willow" (gold, droops and glitters), "palm" (a few
    heavy arms with long trails). Star positions are closed-form in the age (drag saturates the radius, gravity
    droops it), so any frame can be drawn on its own.
    """

    RADIUS = 8.0

    def __init__(self, seed: int, t0: int, x: float, y: float, colors=None, kind: str = "peony", n: int = 30,
                 speed: float = 1.0, life: int = 24, rise: int = 10, launch_x: float | None = None,
                 rocket: bool = True):
        rng = random.Random(seed)
        self.seed, self.t0, self.x, self.y, self.kind = seed, t0, x, y, kind
        self.colors = colors or (rng.choice(NEON),)
        self.life = life + (12 if kind == "willow" else 0)
        self.rise, self.rocket = rise, rocket
        self.launch_x = x + rng.uniform(-4, 4) if launch_x is None else launch_x
        if kind == "palm":
            n = 8
        elif kind == "ring":
            n = 24
        self.parts = []
        for i in range(n):
            a = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / n
            s = speed * (1.0 if kind in ("ring", "palm") else rng.uniform(0.45, 1.0))
            self.parts.append((a, s, self.colors[i % len(self.colors)]))
        self.k = 0.2 if kind != "palm" else 0.14
        self.g = 0.012 if kind != "willow" else 0.022
        self.trail = 6 if kind in ("palm", "willow") else 4

    def pos(self, a, s, age):
        d = s * self.RADIUS * (1 - math.exp(-self.k * age))
        return self.x + math.cos(a) * d, self.y + math.sin(a) * d * 0.8 + 0.5 * self.g * age * age

    def draw(self, img, f: int, alpha: float = 1.0) -> None:
        age = f - self.t0
        if self.rocket and -self.rise <= age < 0:
            for k in range(4):
                p = max(0.0, (age - k + self.rise) / self.rise)
                e = 1 - (1 - p) ** 2
                c = GOLD_LIGHT if k == 0 else ORANGE
                add(img, self.launch_x + (self.x - self.launch_x) * e, H + (self.y - H) * e, c,
                    alpha * (1.0, 0.55, 0.3, 0.15)[k])
            return
        if not (0 <= age < self.life):
            return
        if age < 3:  # flash at the heart of the burst
            fl = (1 - age / 3) * alpha
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    add(img, self.x + dx, self.y + dy, WHITE, fl * (1.0 if dx == dy == 0 else 0.6))
        t = age / self.life
        fade = min(1.0, 2.2 * (1 - t))
        for i, (a, s, c) in enumerate(self.parts):
            col = WHITE if age < 2 else (mix(GOLD_LIGHT, GOLD, t) if self.kind == "willow" else c)
            k = fade
            if t > 0.6 or self.kind == "willow":
                k *= 0.35 + 0.65 * hash01(self.seed, i, age)  # glitter as it dies
            for j in range(self.trail):
                if age - j < 0:
                    break
                x, y = self.pos(a, s, max(0.0, age - j * 1.6))
                add(img, x, y, col if j == 0 else dim(col, 0.8), k * alpha * (1.0, 0.6, 0.38, 0.24, 0.15, 0.1)[j])


def draw_looped(items, img, f: int, period: int) -> None:
    """Draw time-based items so a `period`-frame loop is seamless (events near the ends wrap around)."""
    for it in items:
        for shift in (-period, 0, period):
            it.draw(img, f + shift)


# --- confetti -------------------------------------------------------------------------------------------------

class Confetti:
    """Pieces launched at (x, y) with an initial velocity that drag kills, then a slow flutter down.

    Each piece tumbles: it alternates between a bright and a dim shade of its color.
    """

    def __init__(self, seed: int, t0: int, x: float, y: float, n: int = 30, vx=(-1, 1), vy=(-2, -0.5),
                 fall=(0.06, 0.14), colors=CONFETTI, spread: float = 0.0, stagger: int = 0):
        rng = random.Random(seed)
        self.items = []
        for _ in range(n):
            self.items.append({
                "t0": t0 + rng.randint(0, stagger), "x": x + rng.uniform(-spread, spread), "y": y,
                "vx": rng.uniform(*vx), "vy": rng.uniform(*vy), "fall": rng.uniform(*fall),
                "amp": rng.uniform(0.4, 1.4), "w": rng.uniform(0.15, 0.35), "ph": rng.uniform(0, 6.28),
                "c": rng.choice(colors), "tumble": rng.randint(3, 6),
            })

    def draw(self, img, f: int, alpha: float = 1.0, floor: float | None = None) -> None:
        k = 0.16
        for p in self.items:
            age = f - p["t0"]
            if age < 0:
                continue
            e = (1 - math.exp(-k * age)) / k
            x = p["x"] + p["vx"] * e + p["amp"] * math.sin(p["w"] * age + p["ph"]) * min(1.0, age / 12)
            y = p["y"] + p["vy"] * e + p["fall"] * age
            if floor is not None and y > floor:
                y = floor
            if y > H + 1:
                continue
            bright = (age // p["tumble"]) % 2 == 0
            put(img, x, y, p["c"] if bright else dim(p["c"], 0.55), alpha)


class Snowfall:
    """Steady falling flakes (or glitter), periodic in `period` frames."""

    def __init__(self, seed: int, n: int, period: int, color=(220, 230, 255), alpha=(0.3, 0.8)):
        rng = random.Random(seed)
        self.period = period
        self.items = [(rng.uniform(0, W), rng.uniform(0, H), rng.choice((1, 2)), rng.uniform(0, 6.28),
                       rng.uniform(*alpha)) for _ in range(n)]
        self.color = color

    def draw(self, img, f: int) -> None:
        for x0, y0, laps, ph, a in self.items:
            y = (y0 + f * laps * H / self.period) % H
            x = x0 + 0.8 * math.sin(2 * math.pi * f / self.period + ph)
            put(img, x % W, y, self.color, a)


# --- room dressing -----------------------------------------------------------------------------------------------

def string_lights(img, f: int, y0: int = 0, sag: float = 2.0, spacing: int = 6, offset: int = 0,
                  colors=(GOLD, PINK, CYAN, LIME), period: int = 30) -> None:
    """A sagging wire of bulbs across the top, twinkling in a chase (period frames per cycle)."""
    wire = (70, 60, 90)
    for x in range(W):
        u = ((x + offset) % (spacing * 4)) / (spacing * 4)
        y = y0 + sag * math.sin(math.pi * u)
        put(img, x, y, wire, 0.8)
    for i, x in enumerate(range((spacing // 2 - offset) % spacing, W, spacing)):
        u = ((x + offset) % (spacing * 4)) / (spacing * 4)
        y = y0 + sag * math.sin(math.pi * u) + 1
        c = colors[(i + (x + offset) // spacing) % len(colors)]
        k = 0.55 + 0.45 * math.cos(2 * math.pi * (f / period - i / 4))
        put(img, x, y, dim(c, 0.45 + 0.55 * k))
        add(img, x, y + 1, c, 0.18 * k)


def skyline(img, seed: int, base: int = H, color=(26, 30, 58), window=(255, 210, 110), lit: float = 0.35) -> list:
    """A generic city skyline along the bottom with lit windows. Returns the roof heights per column."""
    rng = random.Random(seed)
    roofs = [H] * W
    x = 0
    while x < W:
        w = rng.randint(4, 9)
        h = rng.randint(3, 7)
        for xx in range(x, min(W, x + w)):
            roofs[xx] = base - h
            for yy in range(base - h, base):
                put(img, xx, yy, color)
        if rng.random() < 0.3 and w >= 5:  # a spire
            put(img, x + w // 2, base - h - 1, color)
            put(img, x + w // 2, base - h - 2, (200, 60, 60))
        for yy in range(base - h + 1, base - 1, 2):
            for xx in range(x + 1, min(W, x + w) - 1, 2):
                if rng.random() < lit:
                    put(img, xx, yy, window, rng.uniform(0.55, 0.95))
        x += w + rng.randint(0, 1)
    return roofs


def glitter(img, seed: int, f: int, n: int = 12, period: int = 60, colors=(GOLD_LIGHT, SILVER), ymax: int = H,
            area=None, strength: float = 0.8) -> None:
    """Twinkling glints, periodic in `period` frames. area = (x0, y0, x1, y1) to keep them in a region."""
    rng = random.Random(seed)
    x0, y0, x1, y1 = area or (0, 0, W, ymax)
    for i in range(n):
        x, y = rng.randrange(x0, x1), rng.randrange(y0, y1)
        speed = rng.choice((1, 2, 3))
        ph = rng.random()
        c = colors[i % len(colors)]
        k = max(0.0, math.sin(2 * math.pi * (speed * f / period + ph)))
        if k > 0.05:
            add(img, x, y, c, strength * k ** 3)
            if k > 0.85:
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    add(img, x + dx, y + dy, c, strength * 0.35 * (k - 0.85) / 0.15)


def line(img, x0: float, y0: float, x1: float, y1: float, c, a: float = 1.0) -> None:
    """A 1 px line (simple DDA)."""
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        put(img, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c, a)


def disc(img, cx: float, cy: float, r: float, c, a: float = 1.0) -> None:
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(img, x, y, c, a)
