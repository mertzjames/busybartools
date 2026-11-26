"""App-local drawing helpers for Presidents' Day: the palette, skies, the waving flag, mountains, glows and caption
backing. Everything is seeded or a pure function of the frame number, so builds are byte-identical.

Tone (docs/DECISIONS.md D2): light, warm and patriotic, non-partisan. No faces or likenesses of real people, no
official seals: symbols, objects and places only.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette (navy, red, cream, gold) ---------------------------------------------------------------------------

NAVY = (24, 38, 104)
NAVY_DEEP = (10, 16, 52)
RED = (206, 28, 46)
RED_DEEP = (150, 18, 34)
WHITE = (246, 244, 236)
CREAM = (250, 234, 196)
GOLD = (255, 196, 70)
GOLD_LIGHT = (255, 236, 160)
STAR = (238, 238, 250)


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
    """Color of flag cell (u, v): stripes, and the blue canton (cw x ch) with stars as dots."""
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


# --- mountains --------------------------------------------------------------------------------------------------

def peaks_profile(x: float, peaks, base: float) -> float:
    """Row of the ridge line at column x: the highest of triangular peaks [(x, height, half-width), ...]."""
    top = base
    for px_, h, hw in peaks:
        top = min(top, base - max(0.0, h * (1 - abs(x - px_) / hw)))
    return top


def mountains(img, peaks, base: float, color, snow=None, snowline: float = 0.0, shade=None, period: float = 0.0,
              scroll: float = 0.0) -> None:
    """A mountain range of triangular peaks with snow above `snowline` and a shaded right flank (light from the left).
    `period` > 0 repeats the peaks every `period` columns so the range can `scroll`."""
    for x in range(W):
        xx = x + scroll
        if period:
            xx %= period
        cands = [peaks_profile(xx + k * period, peaks, base) for k in ((-1, 0, 1) if period else (0,))]
        top = min(cands)
        right = peaks_profile(xx + 0.5, peaks, base) > peaks_profile(xx - 0.5, peaks, base) if not period else (
            min(peaks_profile(xx + 0.5 + k * period, peaks, base) for k in (-1, 0, 1))
            > min(peaks_profile(xx - 0.5 + k * period, peaks, base) for k in (-1, 0, 1)))
        for y in range(max(0, int(math.floor(top + 0.5))), H):
            c = shade if (shade and right) else color
            if snow and y < snowline and y - top < 3:
                c = snow if not right else mix(snow, c, 0.45)
            put(img, x, y, c)
