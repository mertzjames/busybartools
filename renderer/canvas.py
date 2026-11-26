"""72x16 frame helpers: colors, blending, sprite blitting, simple shapes, easing.

Frames are Pillow RGBA images. Everything drawn here is composited over an opaque
background; build.py flattens to RGB before encoding, so the device always gets
fully opaque frames (black = LED off).
"""

from __future__ import annotations

import math
from PIL import Image

W, H = 72, 16
FPS = 15  # see docs/DECISIONS.md D8


def sec(s: float) -> int:
    """Seconds -> frame count."""
    return int(round(s * FPS))


def hexc(s: str) -> tuple[int, int, int]:
    s = s.lstrip("#")
    return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)


def mix(a, b, t: float):
    """Linear blend; rounds half up (math.floor(v + 0.5)) to match JS Math.round in the app and mockup."""
    t = max(0.0, min(1.0, t))
    return tuple(int(math.floor(a[i] + (b[i] - a[i]) * t + 0.5)) for i in range(3))


def scale(c, k: float):
    return tuple(max(0, min(255, int(round(v * k)))) for v in c[:3])


def new(bg=(0, 0, 0)) -> Image.Image:
    return Image.new("RGBA", (W, H), tuple(bg[:3]) + (255,))


def vgradient(top, bottom) -> Image.Image:
    img = new()
    px = img.load()
    for y in range(H):
        c = mix(top, bottom, y / (H - 1))
        for x in range(W):
            px[x, y] = c + (255,)
    return img


def put(img: Image.Image, x: int, y: int, c, a: float = 1.0) -> None:
    """Alpha-blend one pixel (clipped)."""
    x, y = int(round(x)), int(round(y))
    if not (0 <= x < img.width and 0 <= y < img.height) or a <= 0:
        return
    if a >= 1:
        img.putpixel((x, y), tuple(c[:3]) + (255,))
        return
    r, g, b, _ = img.getpixel((x, y))
    img.putpixel((x, y), mix((r, g, b), c, a) + (255,))


def add(img: Image.Image, x: int, y: int, c, a: float = 1.0) -> None:
    """Additive glow for one pixel (clipped)."""
    x, y = int(round(x)), int(round(y))
    if not (0 <= x < img.width and 0 <= y < img.height) or a <= 0:
        return
    r, g, b, _ = img.getpixel((x, y))
    img.putpixel((x, y), (min(255, int(r + c[0] * a)), min(255, int(g + c[1] * a)), min(255, int(b + c[2] * a)), 255))


def rect(img: Image.Image, x: int, y: int, w: int, h: int, c, a: float = 1.0) -> None:
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            put(img, xx, yy, c, a)


def blit(dst: Image.Image, src: Image.Image, x: float, y: float, alpha: float = 1.0) -> None:
    """Composite `src` (RGBA) onto `dst` at integer-rounded (x, y); clips at edges."""
    x, y = int(round(x)), int(round(y))
    if alpha < 1.0:
        src = src.copy()
        a = src.getchannel("A").point(lambda v: int(v * max(0.0, alpha)))
        src.putalpha(a)
    # Crop the part of src that lands on dst so negative offsets work.
    sx0, sy0 = max(0, -x), max(0, -y)
    sx1, sy1 = min(src.width, dst.width - x), min(src.height, dst.height - y)
    if sx1 <= sx0 or sy1 <= sy0:
        return
    part = src.crop((sx0, sy0, sx1, sy1))
    dst.alpha_composite(part, dest=(x + sx0, y + sy0))


def tint(src: Image.Image, color, keep_alpha: bool = True) -> Image.Image:
    """Recolor every opaque pixel of a sprite to `color`, keeping per-pixel brightness."""
    out = src.copy()
    px = out.load()
    for yy in range(out.height):
        for xx in range(out.width):
            r, g, b, a = px[xx, yy]
            if a:
                lum = (0.3 * r + 0.59 * g + 0.11 * b) / 255
                k = 0.45 + 0.75 * lum
                px[xx, yy] = scale(color, k) + (a,)
    return out


def flatten(img: Image.Image) -> Image.Image:
    return img.convert("RGB")


# --- easing -----------------------------------------------------------------

def clamp01(t: float) -> float:
    return max(0.0, min(1.0, t))


def ease_in_out(t: float) -> float:
    t = clamp01(t)
    return 0.5 - 0.5 * math.cos(math.pi * t)


def ease_out(t: float) -> float:
    t = clamp01(t)
    return 1 - (1 - t) ** 2


def ease_in(t: float) -> float:
    t = clamp01(t)
    return t * t


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def phase(f: int, start: int, end: int) -> float:
    """Progress 0..1 of frame f through [start, end)."""
    if end <= start:
        return 1.0
    return clamp01((f - start) / (end - start))
