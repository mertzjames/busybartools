"""App-local Lunar New Year props and effects (docs/DECISIONS.md D4): the red-and-gold palette, lanterns,
firecrackers, red envelopes, rooftops, steam and the gold papercut border. Everything is seeded or a pure function
of the frame number, so builds are byte-identical.

Built on the shared render kit (busybar.canvas, busybar.fx, busybar.party); these stay in this app until a second
app needs them (repo decision R2).
"""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, mix, put, rect

# --- palette ----------------------------------------------------------------------------------------------------

RED = (226, 30, 36)
RED_DARK = (150, 16, 22)
RED_DEEP = (96, 10, 16)
GOLD = (255, 196, 52)
GOLD_LIGHT = (255, 232, 140)
GOLD_DARK = (190, 120, 24)
CREAM = (255, 240, 205)
JADE = (40, 190, 120)
WINE_TOP = (30, 4, 10)
WINE_BOTTOM = (58, 8, 14)
NIGHT_TOP = (8, 6, 26)
NIGHT_BOTTOM = (40, 12, 40)
ROOF = (44, 40, 62)
ROOF_EDGE = (150, 110, 80)
WALL = (96, 22, 26)
SMOKE = (120, 110, 120)
FESTIVE = (RED, GOLD, GOLD_LIGHT, (255, 120, 40))


def hash01(*parts: int) -> float:
    """Deterministic pseudo-random 0..1 from integers (flicker without RNG state)."""
    h = 2166136261
    for p in parts:
        h ^= p & 0xFFFFFFFF
        h = (h * 16777619) & 0xFFFFFFFF
    h ^= h >> 13
    h = (h * 1274126177) & 0xFFFFFFFF
    return ((h ^ (h >> 16)) & 0xFFFF) / 65535.0


# --- lanterns ---------------------------------------------------------------------------------------------------

def lantern(img, cx: float, top: float, f: int, size: int = 1, glow: float = 1.0, string: int = 0,
            seed: int = 0, tassel: bool = True) -> None:
    """A round red palace lantern with gold caps and a tassel, hung from `top` by a `string` px cord.

    size 0: 3x3 body; size 1: 5x5 body; size 2: 7x7 body. The body glows (brighter in the middle) and flickers.
    """
    cx, top = int(round(cx)), int(round(top))
    for y in range(top, top + string):
        put(img, cx, y, (120, 80, 50), 0.8)
    y0 = top + string
    fl = 0.85 + 0.15 * hash01(seed, f // 2)
    if size == 0:
        put(img, cx, y0, GOLD_DARK)
        for dx in (-1, 0, 1):
            put(img, cx + dx, y0 + 1, mix(RED, GOLD_LIGHT, 0.45 * glow * fl) if dx == 0 else RED)
        put(img, cx, y0 + 2, GOLD_DARK)
        if tassel:
            put(img, cx, y0 + 3, GOLD, 0.8)
        return
    half = 2 if size == 1 else 3
    rows = 2 * half - 1
    for dx in range(-half + 1, half):
        put(img, cx + dx, y0, GOLD_DARK)  # top cap
    for r in range(rows):
        yy = y0 + 1 + r
        edge = abs(r - (rows - 1) / 2) / ((rows - 1) / 2 + 0.01)
        w = half if edge < 0.75 else half - 1
        for dx in range(-w, w + 1):
            k = 1 - (abs(dx) / (w + 0.5)) ** 2
            c = mix(RED_DARK, RED, 0.6 + 0.4 * k)
            c = mix(c, GOLD_LIGHT, 0.5 * glow * fl * k * (1 - edge))
            put(img, cx + dx, yy, c)
        if size == 2 and r in (1, rows - 2):  # gold ribs
            put(img, cx, yy, mix(GOLD, GOLD_LIGHT, 0.4))
    yb = y0 + 1 + rows
    for dx in range(-half + 1, half):
        put(img, cx + dx, yb, GOLD_DARK)  # bottom cap
    if tassel:
        sway = 1 if hash01(seed, f // 6) > 0.8 else 0
        put(img, cx, yb + 1, GOLD)
        put(img, cx + sway, yb + 2, GOLD, 0.85)
        if size == 2:
            put(img, cx + sway, yb + 3, GOLD, 0.6)
    add(img, cx, y0 + half, GOLD_LIGHT, 0.12 * glow)


def sky_lantern(img, x: float, y: float, f: int, seed: int, alpha: float = 1.0) -> None:
    """A small paper sky lantern (2x3) with a warm flame glow at the bottom."""
    fl = 0.75 + 0.25 * hash01(seed, f // 2)
    body = mix((230, 90, 30), GOLD_LIGHT, 0.35 * fl)
    for dy in range(3):
        for dx in range(2):
            put(img, x + dx, y + dy, body if dy < 2 else mix(body, (255, 250, 210), 0.5 * fl), alpha)
    add(img, x, y + 3, GOLD, 0.25 * fl * alpha)
    add(img, x + 1, y + 3, GOLD, 0.25 * fl * alpha)


def lantern_string(img, f: int, y0: int = 0, spacing: int = 9, offset: int = 3, sag: float = 1.5,
                   size: int = 0, alpha: float = 1.0) -> None:
    """A cord across the top with small red lanterns hanging from it."""
    for x in range(W):
        u = (x % spacing) / spacing
        put(img, x, y0 + sag * math.sin(math.pi * u), (140, 90, 60), 0.7 * alpha)
    for i, x in enumerate(range(offset, W, spacing)):
        lantern(img, x, y0 + 1, f, size=size, seed=31 + i)


# --- architecture -----------------------------------------------------------------------------------------------

def roof(img, x0: int, x1: int, base: int, color=ROOF, edge=ROOF_EDGE, wall=WALL, window=(255, 190, 90),
         lit: float = 0.7, seed: int = 0) -> None:
    """A hall: a tiled roof with curled-up eave tips over a red wall with warm windows.

    The roof line rises from the eave tips at `base` - 2, dips to `base`, then climbs to a flat ridge at base - 3.
    """
    rng = random.Random(seed)
    profile = (2, 0, 1, 2, 3)
    for x in range(x0, x1 + 1):
        d = min(x - x0, x1 - x)
        y = base - profile[min(d, 4)]
        put(img, x, y, edge)
        if d >= 1:
            put(img, x, y + 1, color)
        if d >= 2:
            for yy in range(y + 2, H):
                put(img, x, yy, color if yy <= base else wall)
    for wx in range(x0 + 3, x1 - 2, 3):
        if rng.random() < lit:
            put(img, wx, base + 2, window, rng.uniform(0.6, 0.9))


def rooftops(img, base: int = 12, color=ROOF, edge=ROOF_EDGE, wall=WALL, seed: int = 3, lit: float = 0.7) -> None:
    """A row of halls with curled eaves along the bottom."""
    rng = random.Random(seed)
    x = -3
    while x < W:
        w = rng.randint(11, 17)
        b = base + rng.randint(-1, 1)
        roof(img, x, x + w, b, color, edge, wall, lit=lit, seed=rng.randint(0, 999))
        x += w + rng.randint(1, 3)


def pagoda(img, cx: int, base: int = H, color=ROOF, edge=ROOF_EDGE, tiers: int = 3) -> None:
    """A small tiered pagoda silhouette centered on cx."""
    y = base
    w = 6
    for t in range(tiers):
        for yy in range(y - 2, y):
            for xx in range(cx - w + 2, cx + w - 1):
                put(img, xx, yy, color)
        y -= 2
        for xx in range(cx - w - 1, cx + w + 2):
            put(img, xx, y, edge)
        put(img, cx - w - 1, y - 1, edge)
        put(img, cx + w + 1, y - 1, edge)
        put(img, cx, y + 1, (255, 190, 90), 0.7)
        y -= 1
        w -= 1
    put(img, cx, y, edge)
    put(img, cx, y - 1, GOLD_DARK)


# --- paper and fortune --------------------------------------------------------------------------------------------

def border(img, f: int, color=GOLD_DARK, light=GOLD, alpha: float = 1.0, rows=(0, H - 1)) -> None:
    """A gold papercut-style meander along the top and bottom rows, with a glint running along it."""
    for y in rows:
        for x in range(W):
            on = (x % 4) != 3 if y == rows[0] else (x % 4) != 1
            if on:
                glint = max(0.0, 1 - abs(((x - f * 0.8) % 48) - 24) / 3)
                put(img, x, y, mix(color, light, glint), alpha)


def envelope(img, x: float, y: float, edge: bool = False, alpha: float = 1.0, open_: float = 0.0) -> None:
    """A red envelope (4x6) with a gold seal; `edge` draws it turned sideways (1 px wide) for tumbling."""
    x, y = int(round(x)), int(round(y))
    if edge:
        for dy in range(6):
            put(img, x + 1, y + dy, RED_DARK, alpha)
        put(img, x + 1, y + 2, GOLD_DARK, alpha)
        return
    for dy in range(6):
        for dx in range(4):
            put(img, x + dx, y + dy, RED if dy else RED_DARK, alpha)
    put(img, x + 1, y + 2, GOLD, alpha)
    put(img, x + 2, y + 2, GOLD, alpha)
    put(img, x + 1, y + 3, GOLD_DARK, alpha)
    put(img, x + 2, y + 3, GOLD_DARK, alpha)
    if open_ > 0:
        for dx in range(4):
            put(img, x + dx, y - 1, RED_DARK, alpha * min(1.0, open_ * 2))


def coin(img, x: float, y: float, f: int, seed: int, alpha: float = 1.0) -> None:
    """A spinning gold coin (2 px wide face, 1 px edge-on)."""
    spin = (f // 3 + seed) % 4
    c = GOLD_LIGHT if spin == 0 else GOLD
    if spin in (0, 2):
        put(img, x, y, c, alpha)
        put(img, x + 1, y, mix(c, GOLD_DARK, 0.4), alpha)
    else:
        put(img, x, y, GOLD_DARK, alpha)


def steam(img, f: int, x0: float, x1: float, base: float, strength: float, seed: int, period: int = 30) -> None:
    """Wisps of steam rising from x0..x1 at `base`, curling as they go (strength 0..1)."""
    if strength <= 0:
        return
    rng = random.Random(seed)
    for i in range(int(26 * max(strength, 0.35))):
        sx = rng.uniform(x0, x1)
        ph = rng.random()
        life = rng.randint(period - 8, period + 8)
        age = ((f / life + ph) % 1.0)
        y = base - age * 10
        x = sx + 1.5 * math.sin(age * 6 + i)
        a = strength * (1 - age) * 0.85
        put(img, x, y, (225, 225, 240), a)


def firecracker(img, x: int, y: int, lit: bool = False) -> None:
    """One 2x3 red firecracker with a gold band, hanging from (x, y)."""
    put(img, x, y, RED)
    put(img, x + 1, y, RED_DARK)
    put(img, x, y + 1, GOLD)
    put(img, x + 1, y + 1, GOLD_DARK)
    put(img, x, y + 2, RED)
    put(img, x + 1, y + 2, RED_DARK)
    if lit:
        add(img, x, y + 3, GOLD_LIGHT, 0.9)


def flash(img, x: float, y: float, k: float, color=(255, 250, 220)) -> None:
    """A small white-gold explosion flash (k = 1 at the pop, fading to 0)."""
    if k <= 0:
        return
    add(img, x, y, color, k)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        add(img, x + dx, y + dy, GOLD_LIGHT, 0.7 * k)
    if k > 0.6:
        for dx, dy in ((1, 1), (-1, -1), (1, -1), (-1, 1), (2, 0), (-2, 0)):
            add(img, x + dx, y + dy, GOLD, 0.5 * k)


def figure(img, x: int, ground: int, shirt, pants=(60, 60, 90), skin=(240, 190, 150), hair=(70, 50, 60),
           step: int = 0, arms_up: bool = False, height: int = 5) -> None:
    """A simple 3-px-wide person standing on `ground` (the row below the feet): head, torso, legs.

    height 5: child (head 1, torso 2, legs 2); 6+: adult (torso grows). `step` alternates the legs.
    """
    torso = height - 3
    y = ground - height
    put(img, x, y, hair)
    put(img, x, y + 1, skin)
    for t in range(torso):
        for dx in (-1, 0, 1):
            put(img, x + dx, y + 2 + t, shirt)
    if arms_up:
        put(img, x - 1, y + 1, skin)
        put(img, x + 1, y + 1, skin)
    ly = y + 2 + torso
    if step % 2 == 0:
        put(img, x - 1, ly, pants)
        put(img, x + 1, ly, pants)
    else:
        put(img, x, ly, pants)
        put(img, x - 1, ly, pants, 0.6)


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float) -> None:
    """Darken a region (behind captions)."""
    px = img.load()
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - k)), int(g * (1 - k)), int(b * (1 - k)), a)


__all__ = [n for n in dir() if not n.startswith("_")] + ["rect"]
