"""App-local drawing helpers for Independence Day: the palette, skies, glows, caption backing, the waving flag and
its pole, and simple figures. Everything is seeded or a pure function of the frame number, so builds are
byte-identical.

Tone (docs/DECISIONS.md D2): festive, patriotic, family-friendly and non-partisan. No likenesses of real people and
no official seals. The sky, flag and pole helpers come from Presidents' Day (apps/presidents-day/renderer/pfx.py).
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette (red, white, blue and gold) --------------------------------------------------------------------------

NAVY = (24, 38, 104)
NAVY_DEEP = (10, 16, 52)
BLUE = (50, 86, 210)
RED = (206, 28, 46)
RED_DEEP = (150, 18, 34)
WHITE = (246, 244, 236)
CREAM = (250, 234, 196)
GOLD = (255, 196, 70)
GOLD_LIGHT = (255, 236, 160)
STAR = (238, 238, 250)

# fireworks: saturated and bright, so they read as red, white and blue at a glance
FW_RED = (255, 52, 64)
FW_WHITE = (255, 255, 255)
FW_BLUE = (80, 124, 255)
FW_GOLD = (255, 200, 70)
FW_COLORS = (FW_RED, FW_WHITE, FW_BLUE, FW_GOLD)

SKIN = ((236, 188, 150), (198, 140, 100), (160, 104, 70), (122, 78, 52))
HAIR = ((120, 76, 40), (200, 150, 70), (96, 64, 44), (150, 60, 30), (110, 80, 60))


def sky(stops, horizon: int = H - 1) -> Image.Image:
    """A 72x16 vertical gradient through `stops` [(row, color), ...] (rows between stops are blended)."""
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for y in range(H):
        c = stops[-1][1]
        if y <= stops[0][0]:
            c = stops[0][1]
        else:
            for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
                if y0 <= y <= y1:
                    c = mix(c0, c1, (y - y0) / max(1, y1 - y0))
                    break
        for x in range(W):
            px[x, y] = tuple(c) + (255,)
    return img


def glow(img, cx: float, cy: float, r: float, color, a: float, squash: float = 1.0) -> None:
    """Additive radial glow (keep `a` steady from frame to frame: per-frame flicker bloats the .anim)."""
    for y in range(max(0, int(cy - r / squash) - 1), min(H, int(cy + r / squash) + 2)):
        for x in range(max(0, int(cx - r) - 1), min(W, int(cx + r) + 2)):
            d = math.hypot(x - cx, (y - cy) * squash)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float = 0.45, feather: int = 2) -> None:
    """Darken a box (inclusive) behind a caption, fading out over `feather` px around it."""
    px = img.load()
    for y in range(max(0, y0 - feather), min(H, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(W, x1 + feather + 1)):
            dx = max(x0 - x, 0, x - x1)
            dy = max(y0 - y, 0, y - y1)
            d = max(dx, dy)
            f = k if d == 0 else k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - f)), int(g * (1 - f)), int(b * (1 - f)), a)


def line(img, x0: float, y0: float, x1: float, y1: float, c, a: float = 1.0) -> None:
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        put(img, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c, a)


# --- the flag ---------------------------------------------------------------------------------------------------

FLAG_H = 13  # one row per stripe: 7 red, 6 white, red at the top and bottom


def flag_color(u: int, v: int, cw: int, ch: int = 7):
    """Color of flag cell (u, v): stripes, and the blue canton (cw x ch) with the stars as a dense checker of dots
    inside a one-pixel border (a sparse dot canton reads as eyes; a dense checker reads as stars)."""
    if u < cw and v < ch:
        if 1 <= v <= ch - 2 and 1 <= u <= cw - 2 and (u + v) % 2 == 0:
            return STAR
        return NAVY
    return RED if v % 2 == 0 else WHITE


def draw_flag(img, x0: int, y0: int, fw: int, t: float, cw: int = 11, amp: float = 1.2, wavelength: float = 18.0,
              unfurl: float = 1.0, alpha: float = 1.0) -> None:
    """A flag fw wide with its hoist at column x0 and top at row y0, waving away from the pole.

    Each column shifts by a whole number of rows (fractional shifts would blur 1-row stripes into pink), and is
    shaded by the slope of the wave, so the cloth seems to ripple. `t` is the wave's phase in cycles (add
    1/period each frame; integrating it lets the speed change smoothly). `unfurl` (0..1) shortens the fly end.
    """
    n = max(1, int(fw * unfurl + 0.5))
    for u in range(n):
        k = u / max(1, fw - 1)
        ph = 2 * math.pi * (u / wavelength - t)
        dy = int(math.floor(amp * k * math.sin(ph) + 0.5))
        shade = 1.0 + 0.28 * math.cos(ph) * (0.3 + 0.7 * k)
        shade = math.floor(shade * 16 + 0.5) / 16  # a few shade steps: fewer changed pixels per frame
        for v in range(FLAG_H):
            c = flag_color(u, v, cw)
            c = tuple(max(0, min(255, int(ch * shade))) for ch in c)
            put(img, x0 + u, y0 + v + dy, c, alpha)


def pole(img, x: int, top: int, bottom: int = H - 1, color=(176, 150, 100)) -> None:
    """A flagpole (brass by default, so it shows against a pale sky) with a gold ball finial."""
    for y in range(top + 1, bottom + 1):
        put(img, x, y, color)
    put(img, x, top, GOLD_LIGHT)
    add(img, x, top - 1, GOLD, 0.35)


# --- city ----------------------------------------------------------------------------------------------------------

def city(img, seed: int, base: int, color=(30, 32, 68), window=(255, 206, 110), lit: float = 0.3,
         heights=(2, 5), towers=3) -> list:
    """A low generic skyline with a few taller towers, standing on row `base` - 1. Returns each column's roof row
    (the topmost building row), so effects can stay behind the buildings."""
    import random
    rng = random.Random(seed)
    roofs = [base] * W
    tower_at = set(rng.sample(range(2, W - 6), towers))
    x = 0
    while x < W:
        w = rng.randint(3, 7)
        h = rng.randint(*heights)
        if any(t in tower_at for t in range(x, x + w)):
            h = heights[1] + rng.randint(2, 3)
            w = min(w, 5)
        for xx in range(x, min(W, x + w)):
            roofs[xx] = base - h
            for yy in range(base - h, base):
                put(img, xx, yy, color)
        if h > heights[1] and w >= 3:  # a spire with a red beacon on the towers
            sx = x + w // 2
            put(img, sx, base - h - 1, color)
            put(img, sx, base - h - 2, (230, 60, 60))
            roofs[sx] = base - h - 2
        for yy in range(base - h + 1, base - 1, 2):
            for xx in range(x + 1, min(W, x + w) - 1, 2):
                if rng.random() < lit:
                    put(img, xx, yy, window, rng.uniform(0.45, 0.85))
        x += w + rng.randint(0, 1)
    return roofs
