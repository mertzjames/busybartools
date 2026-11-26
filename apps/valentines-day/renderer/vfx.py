"""App-local drawing helpers for Valentine's Day (docs/DECISIONS.md D3, D5): hearts of every size, rising-heart
drifts, a heart-shaped burst, soft skies and caption bands. Everything is seeded or a pure function of the frame
number, so builds are byte-identical.

Glows stay steady: per-frame flicker on halos makes .anim files several times larger (only a few core pixels
twinkle).
"""

from __future__ import annotations

import math
import random

from PIL import Image

from busybar.canvas import FPS, H, W, add, mix, put
from busybar.font import draw_text, text_width

# --- palette --------------------------------------------------------------------------------------------------

RED = (230, 30, 60)
CRIMSON = (176, 16, 52)
ROSE = (255, 70, 120)
PINK = (255, 130, 175)
BLUSH = (255, 190, 210)
WARM_WHITE = (255, 238, 228)
GOLD = (255, 196, 70)
GOLD_LIGHT = (255, 232, 150)
PLUM = (34, 6, 30)
BERRY = (70, 10, 48)

HEARTS = (RED, ROSE, PINK, BLUSH, CRIMSON, WARM_WHITE)

# Pastel candy-heart colors (the candy itself), each with a darker rim and the printed-ink color.
CANDY = [
    ((255, 176, 204), (226, 110, 150)),  # pink
    ((255, 236, 214), (226, 180, 150)),  # vanilla
    ((214, 186, 255), (160, 120, 220)),  # lavender
    ((255, 214, 150), (226, 160, 90)),   # apricot
    ((190, 240, 214), (120, 190, 160)),  # mint
    ((255, 240, 160), (220, 190, 90)),   # lemon
]
INK = (210, 30, 70)

# --- heart shapes ---------------------------------------------------------------------------------------------

_SMALL = {
    3: ["#.#", "###", ".#."],
    5: [".#.#.", "#####", "#####", ".###.", "..#.."],
    7: [".##.##.", "#######", "#######", ".#####.", "..###..", "...#..."],
    9: [".##...##.", "####.####", "#########", "#########", ".#######.", "..#####..", "...###...", "....#...."],
}
_CACHE: dict[int, list[str]] = {}


def heart_rows(w: int) -> list[str]:
    """A heart mask `w` pixels wide (odd widths 3, 5, 7, 9 are hand-drawn; larger ones come from the classic
    implicit heart curve, sampled at pixel centers)."""
    if w in _SMALL:
        return _SMALL[w]
    if w in _CACHE:
        return _CACHE[w]
    h = int(math.floor(w * 0.92 + 0.5))
    rows = []
    for y in range(h):
        row = ""
        for x in range(w):
            # map to the curve's box: x -1.15..1.15, y 1.25 (top) .. -1.05 (tip)
            u = (x + 0.5) / w * 2.3 - 1.15
            v = 1.25 - (y + 0.5) / h * 2.3
            row += "#" if (u * u + v * v - 1) ** 3 - u * u * v ** 3 <= 0 else "."
        rows.append(row)
    while rows and "#" not in rows[-1]:
        rows.pop()
    _CACHE[w] = rows
    return rows


def heart_size(w: int) -> tuple[int, int]:
    rows = heart_rows(w)
    return len(rows[0]), len(rows)


def heart(img, x: float, y: float, w: int, color, a: float = 1.0, shade: bool = True, rim=None,
          highlight=WARM_WHITE, halo=None) -> None:
    """Draw a heart with its top-left corner at (x, y). `shade` darkens the lower right and adds a highlight on the
    upper-left lobe; `rim` outlines it in a color; `halo` draws a 1 px dark ring around it first, to separate it
    from what is behind."""
    rows = heart_rows(w)
    x0, y0 = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    hh = len(rows)
    if halo is not None:
        ring = set()
        for yy, row in enumerate(rows):
            for xx, bit in enumerate(row):
                if bit == "#":
                    ring.update((xx + dx, yy + dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1))
        for xx, yy in ring:
            put(img, x0 + xx, y0 + yy, halo, a)
    dark = tuple(int(c * 0.72) for c in color[:3])
    for yy, row in enumerate(rows):
        for xx, bit in enumerate(row):
            if bit != "#":
                continue
            c = color
            if rim is not None:
                edge = any(not (0 <= xx + dx < w and 0 <= yy + dy < hh and rows[yy + dy][xx + dx] == "#")
                           for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))
                if edge:
                    c = rim
            if shade and w >= 5 and c is color:
                k = (xx / w + yy / hh) / 2
                if k > 0.62:
                    c = mix(color, dark, min(1.0, (k - 0.62) * 3))
            put(img, x0 + xx, y0 + yy, c, a)
    if shade and w >= 7 and highlight is not None:
        hx, hy = x0 + max(1, w // 5), y0 + 1
        put(img, hx, hy, highlight, 0.75 * a)
        if w >= 11:
            put(img, hx + 1, hy, highlight, 0.45 * a)
            put(img, hx, hy + 1, highlight, 0.45 * a)


def heart_c(img, cx: float, cy: float, w: int, color, a: float = 1.0, **kw) -> None:
    """A heart centered on (cx, cy)."""
    hw, hh = heart_size(w)
    heart(img, cx - (hw - 1) / 2, cy - (hh - 1) / 2, w, color, a, **kw)


def heart_glow(img, cx: float, cy: float, r: float, color, a: float = 0.5) -> None:
    """A soft, steady round glow (additive)."""
    ri = int(r) + 1
    for y in range(int(cy) - ri, int(cy) + ri + 2):
        for x in range(int(cx) - ri, int(cx) + ri + 2):
            d = math.hypot(x - cx, (y - cy) * 1.1)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def heart_curve(t: float) -> tuple[float, float]:
    """The parametric heart (x right, y down), about -1..1 wide and -0.9..1 tall."""
    x = 16 * math.sin(t) ** 3 / 17
    y = -(13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 17
    return x, y


# --- skies and bands ------------------------------------------------------------------------------------------

def gradient(stops) -> Image.Image:
    """A vertical gradient through (row, color) stops."""
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for y in range(H):
        for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
            if y0 <= y <= y1:
                c = mix(c0, c1, (y - y0) / max(1, y1 - y0))
                break
        else:
            c = stops[-1][1] if y > stops[-1][0] else stops[0][1]
        for x in range(W):
            px[x, y] = c + (255,)
    return img


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 0) -> None:
    """Darken x0..x1, y0..y1 by k (0..1), fading out over `feather` pixels on every side, so text reads."""
    if k <= 0:
        return
    px = img.load()
    for y in range(max(0, y0 - feather), min(img.height, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(img.width, x1 + feather + 1)):
            d = max(x0 - x, x - x1, y0 - y, y - y1, 0)
            kk = k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - kk)), int(g * (1 - kk)), int(b * (1 - kk)), a)


def caption(img, text: str, y: int, top, bottom, shadow, a: float = 1.0, x: int | None = None,
            reveal: int | None = None) -> None:
    """Baked caption in the big font: centered (or at x), gradient, 1 px shadow."""
    x = (W - text_width(text)) // 2 if x is None else x
    draw_text(img, text, x, y, None, gradient=(top, bottom), shadow=shadow, alpha=a, reveal=reveal)


# --- moving hearts --------------------------------------------------------------------------------------------

class Drift:
    """Hearts rising and swaying, periodic in `period` frames (so a backdrop loops seamlessly).

    Each heart: x, start phase, size, color, sway amplitude and speed, laps per period.
    """

    def __init__(self, seed: int, n: int, period: int, sizes=(3, 3, 5, 5, 7), colors=HEARTS, laps=(1,),
                 alpha=(0.5, 1.0), x_range=(0, W)):
        rng = random.Random(seed)
        self.period = period
        self.items = []
        for _ in range(n):
            self.items.append({
                "x": rng.uniform(*x_range), "ph": rng.random(), "w": rng.choice(sizes), "c": rng.choice(colors),
                "amp": rng.uniform(0.6, 2.0), "sw": rng.choice((1, 2)), "sp": rng.random() * 6.28,
                "laps": rng.choice(laps), "a": rng.uniform(*alpha),
            })

    def pos(self, it, f: int):
        hw, hh = heart_size(it["w"])
        travel = H + hh + 2
        u = (it["ph"] + it["laps"] * f / self.period) % 1.0
        y = H + 1 - u * travel
        x = it["x"] + it["amp"] * math.sin(2 * math.pi * it["sw"] * f / self.period + it["sp"])
        return x, y

    def draw(self, img, f: int, alpha: float = 1.0, mask=None) -> None:
        """mask(x, y) -> brightness factor 0..1 (e.g. to dim hearts behind text)."""
        for it in self.items:
            x, y = self.pos(it, f)
            k = it["a"] * alpha * (mask(x, y) if mask else 1.0)
            if k > 0.02:
                heart(img, x, y, it["w"], it["c"], k)


class HeartBurst:
    """A firework whose stars fly out to the outline of a heart, hang, then droop and fade. `t0` is the burst
    frame (a rocket rises during `rise` frames before it)."""

    def __init__(self, t0: int, cx: float, cy: float, size: float = 7.0, colors=(ROSE, PINK), n: int = 28,
                 life: int = 30, rise: int = 10, rocket: bool = True, seed: int = 1):
        self.t0, self.cx, self.cy, self.size = t0, cx, cy, size
        self.colors, self.n, self.life, self.rise, self.rocket = colors, n, life, rise, rocket
        rng = random.Random(seed)
        self.jit = [rng.uniform(-0.15, 0.15) for _ in range(n)]
        self.tw = [rng.random() for _ in range(n)]
        self.launch_x = cx + rng.uniform(-3, 3)

    def draw(self, img, f: int, alpha: float = 1.0) -> None:
        age = f - self.t0
        if self.rocket and -self.rise <= age < 0:
            p = (age + self.rise) / self.rise
            e = 1 - (1 - p) ** 2
            for k in range(3):
                pe = max(0.0, e - k * 0.08)
                add(img, self.launch_x + (self.cx - self.launch_x) * pe, H + (self.cy - H) * pe,
                    GOLD_LIGHT if k == 0 else GOLD, alpha * (1.0, 0.5, 0.25)[k])
            return
        if not (0 <= age < self.life):
            return
        if age < 3:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    add(img, self.cx + dx, self.cy + dy, WARM_WHITE, alpha * (1 - age / 3) * (1 if dx == dy == 0 else 0.5))
        t = age / self.life
        spread = 1 - math.exp(-age / 4)
        fade = min(1.0, 2.5 * (1 - t))
        for i in range(self.n):
            hx, hy = heart_curve(2 * math.pi * i / self.n + self.jit[i] * 0.2)
            x = self.cx + hx * self.size * spread
            y = self.cy + hy * self.size * 0.8 * spread + 0.012 * age * age
            c = WARM_WHITE if age < 2 else self.colors[i % len(self.colors)]
            k = fade
            if t > 0.55:
                k *= 0.4 + 0.6 * ((i * 7 + age) % 3 != 0)
            add(img, x, y, c, alpha * k)
            if age > 1:
                x2 = self.cx + hx * self.size * (1 - math.exp(-(age - 1.5) / 4))
                y2 = self.cy + hy * self.size * 0.8 * (1 - math.exp(-(age - 1.5) / 4)) + 0.012 * (age - 1.5) ** 2
                add(img, x2, y2, c, alpha * k * 0.35)


def twinkle(img, x: int, y: int, f: int, color=GOLD_LIGHT, a: float = 1.0, period: int = 18, ph: float = 0.0) -> None:
    """A 4-point star that grows and fades once per `period` frames."""
    k = max(0.0, math.sin(2 * math.pi * (f / period + ph)))
    if k <= 0.05:
        return
    add(img, x, y, color, a * k)
    if k > 0.6:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            add(img, x + dx, y + dy, color, a * 0.5 * (k - 0.6) / 0.4)


def seconds(f: int) -> float:
    return f / FPS
