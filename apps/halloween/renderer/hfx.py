"""App-local drawing helpers for Halloween (docs/DECISIONS.md D5): night skies, a full moon, steady glows,
jack-o'-lanterns with carved faces, cobwebs, candles, tombstones, mist and caption helpers. Everything is seeded or
a pure function of the frame number, so builds are byte-identical.

Glows stay steady: per-frame flicker on halos makes .anim files several times larger, so only a few core pixels
of a flame or a carved face flicker.
"""

from __future__ import annotations

import math
import random

from PIL import Image

from busybar.canvas import FPS, H, W, add, mix, put
from busybar.party import hash01

# --- palette --------------------------------------------------------------------------------------------------

NIGHT_TOP = (8, 2, 22)
NIGHT_MID = (30, 8, 54)
NIGHT_LOW = (58, 16, 74)
ORANGE = (255, 118, 10)
PUMPKIN_DARK = (176, 64, 4)
PUMPKIN_HI = (255, 176, 70)
STEM = (96, 150, 36)
FLAME = (255, 236, 120)
FLAME_CORE = (255, 252, 210)
EMBER = (255, 150, 30)
LIME = (150, 255, 60)
SLIME = (90, 220, 60)
PURPLE = (150, 60, 220)
VIOLET = (100, 40, 160)
MOON = (255, 240, 196)
MOON_SHADE = (206, 182, 136)
BONE = (236, 234, 216)
GHOST = (240, 246, 255)
WEB = (150, 140, 180)
HILL = (36, 16, 50)
STONE = (120, 116, 140)
STONE_HI = (170, 166, 190)
STONE_DARK = (78, 74, 100)
GRASS = (40, 70, 40)
CANDY_CORN = ((255, 250, 225), (255, 140, 20), (255, 210, 40))  # white tip, orange middle, yellow base


def quant(v: float, steps: int = 40) -> float:
    """Quantize a slow 0..1 change, so long fades change pixels only every few frames (smaller .anim files)."""
    return math.floor(max(0.0, min(1.0, v)) * steps + 0.5) / steps


# --- skies ----------------------------------------------------------------------------------------------------

def gradient(stops) -> Image.Image:
    """A vertical gradient through [(row, color), ...] (three or more stops keep the middle from going grey)."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    px = img.load()
    for y in range(H):
        for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
            if y0 <= y <= y1:
                c = mix(c0, c1, (y - y0) / max(1, y1 - y0))
                break
        else:
            c = stops[0][1] if y < stops[0][0] else stops[-1][1]
        for x in range(W):
            px[x, y] = c + (255,)
    return img


def night(low=NIGHT_LOW) -> Image.Image:
    return gradient([(0, NIGHT_TOP), (9, NIGHT_MID), (15, low)])


def glow(img, cx: float, cy: float, r: float, color, a: float = 1.0) -> None:
    """A soft additive glow (round falloff). Draw it on a static background: halos that change every frame make
    .anim files large."""
    ri = int(math.ceil(r))
    for y in range(int(cy) - ri, int(cy) + ri + 2):
        for x in range(int(cx) - ri, int(cx) + ri + 2):
            d = math.hypot(x - cx, y - cy) / r
            if d < 1:
                add(img, x, y, color, a * (1 - d) ** 2)


def stars(img, seed: int, n: int, f: int, ymax: int = H, period: int = 45, avoid=None, a: float = 0.8) -> None:
    """Twinkling stars, periodic in `period` frames. `avoid(x, y)` returns True where no star may sit."""
    rng = random.Random(seed)
    for _ in range(n):
        x, y, sp, ph = rng.randrange(W), rng.randrange(ymax), rng.choice((1, 2)), rng.random()
        if avoid and avoid(x, y):
            continue
        k = 0.5 + 0.5 * math.sin(2 * math.pi * (sp * f / period + ph))
        put(img, x, y, (230, 220, 255), a * (0.25 + 0.75 * k ** 3))


def full_moon(img, cx: float, cy: float, r: float, halo: float = 0.6, color=MOON) -> None:
    """A full moon with a few soft craters and a steady halo."""
    if halo:
        glow(img, cx, cy, r + 5, (90, 70, 120), halo)
    craters = [(-0.35, -0.25, 0.28), (0.3, 0.2, 0.22), (-0.1, 0.45, 0.16), (0.4, -0.4, 0.14)]
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                c = color
                for ox, oy, cr in craters:
                    if math.hypot((x - cx) / r - ox, (y - cy) / r - oy) < cr:
                        c = MOON_SHADE
                put(img, x, y, c, min(1.0, r - d + 0.6))


def in_moon(x: float, y: float, cx: float, cy: float, r: float) -> bool:
    return math.hypot(x - cx, y - cy) <= r + 0.5


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 0) -> None:
    """Darken the box x0..x1, y0..y1 by k (0..1), fading out over `feather` pixels around it, so a caption reads
    over busy art."""
    if k <= 0:
        return
    px = img.load()
    for y in range(max(0, y0 - feather), min(img.height, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(img.width, x1 + feather + 1)):
            dx = max(x0 - x, 0, x - x1)
            dy = max(y0 - y, 0, y - y1)
            d = max(dx, dy)
            kk = k if d == 0 else k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - kk)), int(g * (1 - kk)), int(b * (1 - kk)), a)


# --- jack-o'-lanterns -----------------------------------------------------------------------------------------

# Carved faces on an 11x7 grid ('#' = carved). Each is original and different.
FACES = {
    "classic": """
.#.......#.
###.....###
.....#.....
....###....
##.......##
.##.#.#.##.
..#######..
""",
    "surprised": """
.##.....##.
####...####
.##.....##.
...........
....###....
...#####...
....###....
""",
    "wink": """
...........
###....###.
......#####
..........#
#.........#
.###..####.
...####....
""",
    "goofy": """
##.......##
.##.....##.
..#.....#..
.....#.....
##..##..##.
..##..##..#
...........
""",
}

# Small faces for the 7-px lanterns on the card backdrop (5x4 grids).
SMALL_FACES = {
    "classic": """
#...#
.....
#####
.#.#.
""",
    "happy": """
#...#
..#..
#...#
.###.
""",
}


def face_cells(name: str, small: bool = False) -> list[tuple[int, int]]:
    rows = [r for r in (SMALL_FACES if small else FACES)[name].strip("\n").splitlines()]
    return [(x, y) for y, r in enumerate(rows) for x, ch in enumerate(r) if ch == "#"]


# Hand-drawn pumpkin bodies: B body, D ridge between lobes, H highlight, S shaded edge.
BODIES = {
    (15, 11): """
...BBBBBBBBB...
.BBBBDBBBDBBBB.
BBHBDBBBBBDBBBB
BHBBDBBBBBDBBBS
BBBBDBBBBBDBBBS
BBBBDBBBBBDBBBS
BBBBDBBBBBDBBBS
BBBBDBBBBBDBBSS
.BBBBDBBBDBBBS.
..SBBDBBBDBBS..
....SSSSSSS....
""",
    (7, 6): """
.BBBBB.
BHBDBBB
BBDBDBS
BBDBDBS
BBBDBBS
.SSSSS.
""",
}


def pumpkin(img, x: int, y: int, w: int, h: int, face: str | None = None, carved: float = 1.0, lit: float = 0.0,
            f: int = 0, seed: int = 0, small: bool = False, stem: bool = True) -> None:
    """A pumpkin (15x11 or 7x6) whose body's top-left is (x, y). `carved` 0..1 reveals the face pixels in order;
    `lit` 0..1 fills the carved face with candlelight (a few core pixels flicker with frame f). A lit pumpkin's
    skin darkens a little, so the glowing face stands out."""
    rows = [r for r in BODIES[(w, h)].strip("\n").splitlines()]
    k = 0.5 * lit
    pal = {"B": mix(ORANGE, (150, 46, 0), k), "D": mix((150, 46, 0), (96, 24, 0), k),
           "H": mix(PUMPKIN_HI, (230, 110, 20), k), "S": mix((196, 72, 2), (110, 32, 0), k)}
    for yy, r in enumerate(rows):
        for xx, ch in enumerate(r):
            if ch != ".":
                put(img, x + xx, y + yy, pal[ch])
    if stem:
        sx = x + w // 2
        put(img, sx, y - 1, STEM)
        if w >= 11:
            put(img, sx + 1, y - 2, STEM)
            put(img, sx, y, (80, 120, 26))
    if not face:
        return
    cells = face_cells(face, small)
    fw, fh = (5, 4) if small else (11, 7)
    ox, oy = x + (w - fw) // 2, y + (1 if small else 2)
    n = int(round(len(cells) * max(0.0, min(1.0, carved))))
    order = sorted(cells, key=lambda c: (c[1], c[0]))  # eyes, then nose, then mouth
    hole = (54, 16, 6)
    for cx, cy in order[:n]:
        c = hole
        if lit > 0:
            core = FLAME_CORE if hash01(seed, cx, cy, f // 3) > 0.82 else (255, 226, 70)
            c = mix(hole, core, lit)
        put(img, ox + cx, oy + cy, c)


def pumpkin_glow(img, x: int, y: int, w: int, h: int, a: float = 1.0) -> None:
    """The steady orange halo around a lit jack-o'-lantern (draw it on the background, before the pumpkin)."""
    glow(img, x + (w - 1) / 2, y + (h - 1) / 2, w * 0.95, (150, 60, 0), a)


# --- room and yard dressing ------------------------------------------------------------------------------------

def cobweb(img, corner: str, size: int = 7, color=WEB, a: float = 0.6) -> None:
    """A sparse corner cobweb: three spokes fanning out of the corner and two threads strung straight from spoke to
    spoke (straight segments sag toward the corner, like a real web), anchored on the screen's edges.
    corner: 'tl' or 'tr'."""
    sx = 1 if corner == "tl" else -1
    x0 = 0 if corner == "tl" else W - 1
    pts = set()
    angles = [0.0, 0.47, 0.785, 1.1, math.pi / 2]
    for ang in angles[1:-1]:
        for i in range(1, size + 1):
            pts.add((int(math.floor(math.cos(ang) * i + 0.5)), int(math.floor(math.sin(ang) * i + 0.5))))
    for rr in (3.2, size - 0.4):
        ring = [(math.cos(ang) * rr, math.sin(ang) * rr) for ang in angles]
        for (ax, ay), (bx, by) in zip(ring, ring[1:]):
            n = int(max(abs(bx - ax), abs(by - ay))) + 1
            for j in range(n + 1):
                u = j / n
                pts.add((int(math.floor(ax + (bx - ax) * u + 0.5)), int(math.floor(ay + (by - ay) * u + 0.5))))
    for px_, py_ in pts:
        if px_ < size and py_ < size:
            put(img, x0 + sx * px_, py_, color, a)


def candle(img, x: int, top: int, f: int, h: int | None = None, seed: int = 0, body=(236, 226, 200)) -> None:
    """A 3-px-wide candle with its wax top at row `top` (to the bottom of the screen unless h is given): a dark
    wick row above it, then a flame. Only the flame's tip and core flicker."""
    bottom = H if h is None else top + h
    for yy in range(top, bottom):
        for dx in range(3):
            c = body if dx < 2 else mix(body, (150, 130, 110), 0.5)
            put(img, x + dx, yy, c)
    put(img, x, top, (255, 245, 225))
    put(img, x + 2, top + 2, (255, 240, 210), 0.7)  # a wax drip
    put(img, x + 1, top - 1, (70, 40, 30))  # wick: keeps the flame from merging into the candle
    k = hash01(seed, f // 2)
    put(img, x + 1, top - 2, mix(EMBER, FLAME, 0.5 + 0.5 * k))
    put(img, x + 1, top - 3, mix(FLAME, FLAME_CORE, k))
    put(img, x + 1 + (1 if k > 0.75 else 0), top - 4, FLAME, 0.4 + 0.5 * k)


def candle_glow(img, x: int, top: int, a: float = 1.0) -> None:
    glow(img, x + 1, top - 3, 6, (120, 60, 10), a)


STONE_TONES = [(STONE, STONE_HI, STONE_DARK), ((104, 112, 140), (150, 160, 190), (66, 72, 100)),
               ((130, 120, 132), (176, 166, 178), (86, 78, 92))]


def tombstone(img, x: int, y: int, w: int, h: int, tilt: int = 0, tone: int = 0) -> None:
    """A cartoon tombstone: round top, light upper-left edge, darker right side, a 1 px dark gap around it so
    neighbors stay apart. (x, y) is its top-left; `tone` picks one of three stone colors."""
    body, hi, dark = STONE_TONES[tone % len(STONE_TONES)]
    r = w / 2
    for yy in range(h):
        for xx in range(w):
            if yy < r:
                if math.hypot(xx + 0.5 - r, yy + 0.5 - r) > r + 0.1:
                    continue
            shift = int(round(tilt * (h - yy) / h))
            c = body
            if xx == 0 or (yy < r and math.hypot(xx + 0.5 - r, yy + 0.5 - r) > r - 1.1 and xx < r):
                c = hi
            elif xx == w - 1:
                c = dark
            put(img, x + xx + shift, y + yy, c)


def mist(img, f: int, y0: int, seed: int = 0, color=(110, 200, 120), a: float = 0.35, period: int = 90) -> None:
    """Low ghostly mist drifting sideways over the bottom rows (periodic in `period` frames)."""
    ph = 2 * math.pi * f / period
    rng = random.Random(seed)
    p1, p2 = rng.random() * 6, rng.random() * 6
    for x in range(W):
        top = y0 + 1.2 * math.sin(x * 0.17 + ph + p1) + 0.8 * math.sin(x * 0.07 - ph + p2)
        for y in range(int(top), H):
            k = min(1.0, (y - top + 1) / 3)
            put(img, x, y, color, a * k)


def candy_corn(img, x: int, y: int, a: float = 1.0) -> None:
    """A 3x3 candy corn, point up: white tip, orange middle, yellow base."""
    put(img, x + 1, y, CANDY_CORN[0], a)
    for dx in range(3):
        put(img, x + dx, y + 1, CANDY_CORN[1], a)
        put(img, x + dx, y + 2, CANDY_CORN[2], a)


def wobble(t: float, speed: float = 1.0, ph: float = 0.0) -> float:
    return math.sin(2 * math.pi * (t * speed + ph))


def frame_t(f: int) -> float:
    return f / FPS
