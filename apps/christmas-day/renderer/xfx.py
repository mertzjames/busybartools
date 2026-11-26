"""App-local Christmas effects and props (docs/DECISIONS.md D5): snowfall, light strings, trees, houses, presents,
fireworks, fire. Everything is seeded or purely a function of the frame number, so builds are byte-identical.

These build on the shared render kit (busybar.canvas / busybar.fx) and stay in this app until a second app needs
them (repo decision R2).
"""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, mix, put, rect

RED = (226, 36, 44)
GREEN = (40, 170, 72)
GOLD = (255, 204, 60)
SILVER = (220, 228, 245)
BLUE = (70, 130, 255)
BULBS = (RED, GOLD, GREEN, BLUE, (255, 120, 200))
SNOW = (235, 242, 255)


# --- snow -----------------------------------------------------------------------------------------------------

class Snow:
    """Falling snow. Each flake falls an integer number of screen heights per `period` frames, so the snowfall
    is seamless when period is the loop length. `wind` pushes flakes sideways (px per frame, can vary by frame).
    """

    def __init__(self, seed: int, n: int = 24, period: int = 60, laps=(1, 2), bright=(0.35, 0.9),
                 color=SNOW, xmin: int = 0, xmax: int = W):
        rng = random.Random(seed)
        self.flakes = [(rng.uniform(xmin, xmax), rng.uniform(0, H), rng.choice(laps), rng.uniform(*bright),
                        rng.uniform(0, 2 * math.pi), rng.uniform(0.6, 1.6)) for _ in range(n)]
        self.period, self.color, self.xmin, self.xmax = period, color, xmin, xmax

    def draw(self, img, f: int, drift: float = 0.0, alpha: float = 1.0, skip=None) -> None:
        """drift: total sideways offset in px for this frame (e.g. accumulated wind)."""
        span = self.xmax - self.xmin
        for x0, y0, laps, a, ph, amp in self.flakes:
            y = (y0 + f * laps * H / self.period) % H
            x = x0 + amp * math.sin(2 * math.pi * f / self.period * laps + ph) + drift * (0.6 + 0.4 * laps)
            x = self.xmin + (x - self.xmin) % span
            if skip and skip(int(round(x)), int(y)):
                continue
            put(img, x, int(y), self.color, a * alpha)


def snow_ground(img, y: int, color=(214, 226, 250), shade=(150, 170, 215), seed: int = 0) -> None:
    """Snowy ground from row y down, with a gently uneven top edge."""
    rng = random.Random(seed)
    bumps = [rng.choice((0, 0, 0, 1)) for _ in range(W)]
    for x in range(W):
        top = y - bumps[x]
        for yy in range(top, H):
            put(img, x, yy, mix(color, shade, (yy - top) / max(1, H - top)))


# --- light strings ------------------------------------------------------------------------------------------

def light_string(img, f: int, x0: int, x1: int, y: float, sag: float, period: int, spacing: int = 4,
                 wire=(30, 70, 40), phase0: int = 0, alpha: float = 1.0, drop: int = 1) -> None:
    """A drooping string of colored bulbs from x0 to x1 that twinkle (periodic in `period` frames).

    drop: rows the bulbs hang below the wire (0 = on the wire).
    """
    n = 0
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, x1 - x0)
        yy = y + sag * 4 * t * (1 - t)
        put(img, x, round(yy), wire, alpha)
        if (x - x0) % spacing == spacing // 2:
            c = BULBS[(n + phase0) % len(BULBS)]
            k = 0.55 + 0.45 * math.sin(2 * math.pi * (f / period * 2 + n * 0.37))
            put(img, x, round(yy) + drop, c, alpha * (0.45 + 0.55 * k))
            n += 1


# --- trees --------------------------------------------------------------------------------------------------

TREE_DARK = (14, 84, 38)
TREE = (28, 124, 52)
TREE_LIGHT = (70, 170, 80)
TRUNK = (120, 72, 36)


def tree_rows(height: int) -> list[int]:
    """Half-widths of a tiered fir, top row first."""
    out = []
    for r in range(height):
        out.append(int(math.floor((r % 4) * 0.8 + r * 0.45 + 0.5)))
    return out


def draw_tree(img, cx: int, top: int, height: int = 12, trunk: int = 2, snowy: bool = False, alpha: float = 1.0):
    """A tiered fir with shading. Returns the list of lit foliage pixels (for placing ornaments)."""
    pix = []
    for r, hw in enumerate(tree_rows(height)):
        y = top + r
        for dx in range(-hw, hw + 1):
            c = TREE
            if dx == -hw or (dx < 0 and (r + dx) % 5 == 0):
                c = TREE_LIGHT
            elif dx == hw or (dx > 0 and (r - dx) % 4 == 0):
                c = TREE_DARK
            if snowy and (dx == -hw or dx == hw) and r % 4 == 3:
                c = SNOW
            put(img, cx + dx, y, c, alpha)
            pix.append((cx + dx, y))
    for k in range(trunk):
        put(img, cx, top + height + k, TRUNK, alpha)
        put(img, cx - 1, top + height + k, TRUNK, alpha * 0.8)
    return pix


def tree_spots(cx: int, top: int, height: int, n: int, seed: int) -> list[tuple[int, int]]:
    """Spread-out positions inside the tree for ornaments or bulbs (deterministic)."""
    rng = random.Random(seed)
    rows = tree_rows(height)
    spots: list[tuple[int, int]] = []
    tries = 0
    while len(spots) < n and tries < 2000:
        tries += 1
        r = rng.randrange(2, height)
        hw = rows[r]
        if hw < 1:
            continue
        x = cx + rng.randint(-hw + 1, hw - 1) if hw > 1 else cx
        y = top + r
        if all(abs(x - sx) + abs(y - sy) >= 3 for sx, sy in spots):
            spots.append((x, y))
    return spots


def garland_path(cx: int, top: int, height: int) -> list[tuple[int, int]]:
    """A zig-zag of bulb positions wrapping down the tree, in the order they light up."""
    rows = tree_rows(height)
    pts = []
    for band, r in enumerate(range(2, height, 3)):
        hw = rows[r]
        xs = range(-hw + 1, hw) if band % 2 == 0 else range(hw - 1, -hw, -1)
        for i, dx in enumerate(xs):
            if i % 2 == 0:
                pts.append((cx + dx, top + r + (1 if abs(dx) < hw // 2 else 0)))
    return pts


def tree_star(img, x: int, y: int, glow: float = 1.0) -> None:
    """A 5-pixel twinkling star centred on (x, y)."""
    put(img, x, y, (255, 250, 220))
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        put(img, x + dx, y + dy, GOLD)
    if glow > 0:
        for dx, dy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            add(img, x + dx, y + dy, (255, 200, 60), 0.35 * glow)


# --- buildings and props ----------------------------------------------------------------------------------

def house(img, x: int, w: int, base: int, wall_h: int, wall, roof, window_on: float = 1.0,
          chimney: int | None = None, snow_roof: bool = True) -> tuple[int, int] | None:
    """A little house: wall, pitched roof with snow, a warm window. Returns the chimney top (x, y) if any."""
    top = base - wall_h
    rect(img, x, top, w, wall_h, wall)
    rh = (w + 1) // 2
    for r in range(rh):
        for xx in range(x + rh - 1 - r - 1, x + w - rh + 1 + r + 1):
            if x - 1 <= xx <= x + w:
                put(img, xx, top - rh + r, SNOW if (snow_roof and r == 0) else roof)
    if snow_roof:
        for xx in range(x - 1, x + w + 1):
            put(img, xx, top - 1, mix(SNOW, roof, 0.3))
    if window_on > 0 and w >= 4 and wall_h >= 3:
        wx = x + w // 2 - 1
        rect(img, wx, top + 1, 2, 2, mix((40, 30, 20), (255, 196, 90), window_on))
    ch = None
    if chimney is not None:
        cy = top - rh + 1
        rect(img, chimney, cy - 2, 2, 3, (150, 60, 50))
        put(img, chimney, cy - 3, SNOW)
        put(img, chimney + 1, cy - 3, SNOW)
        ch = (chimney, cy - 3)
    return ch


def present(img, x: int, y: int, w: int, h: int, box, ribbon, lid_dy: float = 0.0, lid_dx: float = 0.0,
            lid: bool = True, open_: bool = False) -> None:
    """A wrapped box with a ribbon cross; the lid (top row + bow) can float off by (lid_dx, lid_dy)."""
    rib = x + w // 2
    dark = mix(box, (0, 0, 0), 0.35)
    for yy in range(y + 1, y + h):
        for xx in range(x, x + w):
            c = ribbon if xx == rib else (dark if xx == x + w - 1 else box)
            put(img, xx, yy, c)
    if open_:
        for xx in range(x + 1, x + w - 1):
            put(img, xx, y + 1, mix(box, (0, 0, 0), 0.6))
    if lid:
        ly, lx = y + lid_dy, x + lid_dx
        for xx in range(-1, w + 1):
            put(img, lx + xx, ly, ribbon if xx == w // 2 else mix(box, (255, 255, 255), 0.15))
        put(img, lx + w // 2 - 1, ly - 1, ribbon)
        put(img, lx + w // 2 + 1, ly - 1, ribbon)


def full_moon(img, cx: float, cy: float, r: float = 5.5, color=(255, 248, 214), glow: float = 0.18) -> None:
    for yy in range(int(cy - r - 3), int(cy + r + 4)):
        for xx in range(int(cx - r - 3), int(cx + r + 4)):
            d = math.hypot(xx - cx, yy - cy)
            if d <= r:
                k = 1.0 - 0.18 * ((xx - cx + yy - cy) / (2 * r) + 0.5)
                put(img, xx, yy, tuple(int(v * k) for v in color))
            elif d <= r + 3:
                add(img, xx, yy, (120, 120, 90), glow * (1 - (d - r) / 3))
    for dx, dy in ((-2, -1), (1, 2), (2, -2)):
        put(img, cx + dx, cy + dy, (220, 210, 170))


def fire(img, f: int, x0: int, x1: int, base: int, height: int, seed: int = 0) -> None:
    """Flickering flames between x0..x1 with their base on row `base`."""
    for x in range(x0, x1 + 1):
        t = (x - x0) / max(1, x1 - x0)
        hmax = height * (0.55 + 0.45 * math.sin(math.pi * t))
        flick = 0.65 + 0.35 * math.sin(f * 0.9 + x * 2.1 + seed) * math.sin(f * 0.37 + x * 0.7)
        h = max(1, int(round(hmax * flick)))
        for k in range(h):
            u = k / max(1, h - 1)
            c = mix((255, 236, 120), (230, 60, 20), u) if u < 1 else (200, 40, 16)
            put(img, x, base - k, c)


# --- fireworks ----------------------------------------------------------------------------------------------

class Fireworks:
    """Rockets that rise and burst into rings of sparks. `schedule` is [(frame, x, burst_y, color)]."""

    def __init__(self, schedule, seed: int = 0, sparks: int = 16, speed=(0.45, 0.75), life=(14, 24)):
        rng = random.Random(seed)
        self.shots = []
        for f0, x, by, c in schedule:
            rise = max(4, int((H - by) * 1.2))
            parts = []
            for i in range(sparks):
                ang = 2 * math.pi * (i + rng.random() * 0.4) / sparks
                v = rng.uniform(*speed)
                parts.append((math.cos(ang) * v, math.sin(ang) * v * 0.8, rng.randint(*life)))
            self.shots.append((f0, x, by, c, rise, parts))

    def draw(self, img, f: int) -> None:
        for f0, x, by, c, rise, parts in self.shots:
            age = f - f0
            if age < 0:
                continue
            if age < rise:
                y = H - (H - by) * age / rise
                put(img, x, y, (255, 230, 170))
                put(img, x, y + 1, (200, 120, 60), 0.5)
                continue
            a = age - rise
            if a == 0:
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
                    add(img, x + dx, by + dy, (255, 255, 255), 0.9)
            for vx, vy, life in parts:
                if a >= life:
                    continue
                t = a / life
                px = x + vx * a
                py = by + vy * a + 0.012 * a * a
                k = 1 - t ** 1.5
                col = mix((255, 255, 255), c, min(1.0, t * 3))
                add(img, px, py, col, k)
                if a > 1:
                    add(img, x + vx * (a - 1.5), by + vy * (a - 1.5) + 0.012 * (a - 1.5) ** 2, c, 0.35 * k)
