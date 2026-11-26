"""App-local drawing helpers for Memorial Day: the muted palette, skies, the small flag on its pole, poppies, glows
and captions. Everything is seeded or a pure function of the frame number, so builds are byte-identical.

Tribute rules (docs/DECISIONS.md D2): slow and calm; muted colors; no party effects, no insignia, seals or branch
emblems, no likenesses of real people, nothing that depicts combat.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put
from busybar.font import draw_text, text_width

# --- palette (muted: a calm flag, not a parade) -----------------------------------------------------------------

NAVY = (34, 46, 112)
RED = (184, 36, 48)
WHITE = (232, 230, 222)
STAR = (226, 228, 240)
STONE = (214, 216, 222)  # headstones: pale, cool and lit
POPPY = (210, 40, 36)
POPPY_DEEP = (150, 24, 30)
POPPY_EYE = (104, 56, 120)  # a lit violet, not black (black is an unlit LED)
STEM = (52, 104, 52)
GOLD = (255, 196, 96)
BRASS = (196, 164, 104)


def sky(stops) -> Image.Image:
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


def blend_stops(a, b, k: float):
    """Blend two stop lists with the same rows."""
    return [(ya, mix(ca, cb, k)) for (ya, ca), (_, cb) in zip(a, b)]


def quant(p: float, steps: int = 40) -> float:
    """Quantize a slow 0..1 change, so a gradual light change keeps the .anim small (frames repeat between steps)."""
    return math.floor(max(0.0, min(1.0, p)) * steps + 0.5) / steps


def glow(img, cx: float, cy: float, r: float, color, a: float, squash: float = 1.0) -> None:
    """Additive radial glow. Keep `a` steady from frame to frame: per-frame flicker bloats the .anim."""
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
            d = max(x0 - x, 0, x - x1, y0 - y, 0, y - y1)
            f = k if d == 0 else k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - f)), int(g * (1 - f)), int(b * (1 - f)), a)


# --- the flag ---------------------------------------------------------------------------------------------------

FLAG_H = 7  # seven stripes, one row each: red at the top and bottom (a 72x16 panel can't show thirteen)
CANTON_W, CANTON_H = 9, 4


def flag_color(u: int, v: int):
    """Color of flag cell (u, v): stripes, and the blue canton with stars as a checker of lit dots."""
    if u < CANTON_W and v < CANTON_H:
        if u <= CANTON_W - 2 and (u + v) % 2 == 1:  # a dense field of lit dots reads as stars, not as eyes
            return STAR
        return NAVY
    return RED if v % 2 == 0 else WHITE


def draw_flag(img, x0: int, y0: int, fw: int, t: float, amp: float = 1.0, wavelength: float = 16.0,
              alpha: float = 1.0) -> None:
    """A flag fw wide with its hoist at column x0 and top at row y0, waving away from the pole.

    Each column shifts by a whole number of rows (fractional shifts blur 1-row stripes into pink) and is shaded by
    the slope of the wave, so the cloth seems to ripple. `t` is the wave's phase in cycles; the hoist never moves.
    """
    for u in range(fw):
        k = u / max(1, fw - 1)
        ph = 2 * math.pi * (u / wavelength - t)
        dy = int(math.floor(amp * k * math.sin(ph) + 0.5))
        shade = 1.0 + 0.22 * math.cos(ph) * (0.25 + 0.75 * k)
        for v in range(FLAG_H):
            c = tuple(max(0, min(255, int(ch * shade))) for ch in flag_color(u, v))
            put(img, x0 + u, y0 + v + dy, c, alpha)


def pole(img, x: int, top: int, bottom: int = H - 1, color=BRASS) -> None:
    """A flagpole with a pale gold ball finial (lit, so it reads against the sky)."""
    for y in range(top + 1, bottom + 1):
        put(img, x, y, color)
    put(img, x, top, (255, 232, 168))


# --- poppies ----------------------------------------------------------------------------------------------------

def poppy(img, x: int, y: int, size: int, a: float = 1.0, petal=POPPY, deep=POPPY_DEEP, halo=None) -> None:
    """A poppy head centred at (x, y): size 1 is a dot, 2 a small cup, 3 a flower with a violet eye, 4 a large one
    (5 x 4, for the nearest row)."""
    if size >= 4:
        rows = (".RRR.", "RRERR", "RDRDR", ".DDD.")
        if halo:  # a 1 px dark ring keeps neighbouring flowers from merging into blobs
            for dy, row in enumerate(rows):
                for dx, ch in enumerate(row):
                    if ch != ".":
                        for ox, oy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                            put(img, x - 2 + dx + ox, y - 1 + dy + oy, halo, a)
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    put(img, x - 2 + dx, y - 1 + dy, {"R": petal, "D": deep, "E": POPPY_EYE}[ch], a)
        return
    if size <= 1:
        put(img, x, y, petal, a)
        return
    if size == 2:
        put(img, x, y, petal, a)
        put(img, x + 1, y, deep, a)
        put(img, x, y - 1, petal, 0.8 * a)
        return
    for dx, dy, c in ((-1, 0, petal), (1, 0, petal), (0, -1, petal), (-1, -1, deep), (1, -1, deep),
                      (0, 1, deep), (-1, 1, deep), (1, 1, deep)):
        put(img, x + dx, y + dy, c, a)
    put(img, x, y, POPPY_EYE, a)


# --- captions ---------------------------------------------------------------------------------------------------

CAPTION_GRAD = ((246, 242, 232), (206, 212, 230))
CAPTION_SHADOW = (20, 22, 52)


def caption(img, text: str, y: int, alpha: float, font: str = "big", x: int | None = None, back: float = 0.5,
            grad=CAPTION_GRAD, shadow=CAPTION_SHADOW) -> None:
    """A caption faded in slowly; the background behind it dims first so it stays legible."""
    if alpha <= 0:
        return
    w = text_width(text, font)
    x = (W - w) // 2 if x is None else x
    h = 7 if font == "big" else 5
    if back:
        dim_rect(img, x - 1, y - 1, x + w + 1, y + h, k=back * alpha, feather=2)
    draw_text(img, text, x, y, None, font=font, gradient=grad, shadow=shadow, alpha=alpha)
