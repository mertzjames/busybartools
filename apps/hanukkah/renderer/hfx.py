"""App-local Hanukkah props and effects: candle flames, the menorah, warm glow, dreidel letters, gelt coins.

Everything is seeded or a pure function of the frame number, so builds are byte-identical. These build on the
shared render kit (busybar.canvas, busybar.party) and stay in this app until a second app needs them (repo R2).
"""

from __future__ import annotations

import math

from busybar.canvas import H, W, add, mix, put, rect
from busybar.party import hash01

# --- palette (blue, silver and gold; docs/DECISIONS.md D5) ------------------------------------------------------

GOLD = (236, 180, 60)
GOLD_HI = (255, 226, 130)
GOLD_LO = (160, 110, 34)
SILVER = (206, 216, 236)
SILVER_LO = (130, 142, 170)
BLUE = (60, 116, 236)
BLUE_HI = (130, 176, 255)
BLUE_LO = (34, 66, 160)
WHITE = (240, 244, 255)
FLAME_CORE = (255, 246, 200)
FLAME_MID = (255, 200, 70)
FLAME_TIP = (255, 130, 30)
GLOW = (255, 170, 60)
WICK = (130, 116, 104)  # lit grey-brown: black would be an unlit LED

CANDLE_COLORS = ((BLUE, BLUE_HI), (WHITE, (255, 255, 255)))


def glow(img, cx: float, cy: float, r: float, color, k: float) -> None:
    """Soft additive halo (falls off with the square of the distance)."""
    if k <= 0:
        return
    ri = int(math.ceil(r))
    for y in range(int(cy) - ri, int(cy) + ri + 1):
        for x in range(int(cx) - ri, int(cx) + ri + 1):
            d2 = ((x - cx) ** 2 + (y - cy) ** 2) / (r * r)
            if d2 < 1:
                add(img, x, y, color, k * (1 - d2) ** 2)


def flame(img, x: int, base: int, f: int, seed: int, width: int = 2, size: float = 1.0) -> None:
    """A flickering candle flame whose bottom row is `base` (the row above the wick), over x .. x+width-1.

    A teardrop: a yellow base row, a bright core row and an orange tip that sways and stretches. size 0..1 grows
    a new flame (a spark, then a small flame, then the full one).
    """
    if size <= 0:
        return
    if size < 0.35:  # the first spark
        add(img, x, base + 1, FLAME_MID, 0.5 + size)
        add(img, x, base, FLAME_CORE, 0.4 + size)
        return
    fl = hash01(seed, f // 2)
    full = size > 0.6
    for dx in range(width):
        put(img, x + dx, base, FLAME_MID if full else FLAME_TIP)
        if full:
            put(img, x + dx, base - 1, FLAME_CORE)
    tip_x = x + ((f // 5 + seed) % width)
    if fl > 0.75:
        tip_x = x + (width - 1) - (tip_x - x)
    if full:
        put(img, tip_x, base - 2, FLAME_TIP)
        if hash01(seed, f // 3, 7) > 0.55:
            put(img, tip_x, base - 3, FLAME_TIP, 0.4)
    else:
        put(img, tip_x, base - 1, FLAME_MID)
    # warm halo around the flame
    glow(img, x + (width - 1) / 2, base - 1, 3.4, GLOW, 0.22 * min(1.0, size))


# --- the menorah --------------------------------------------------------------------------------------------------

class Menorah:
    """A nine-branched Hanukkah menorah: eight candle cups on nested curved arms and a raised shamash in the middle.

    Positions are numbered 1..8 from the left (the viewer's view). Candles are placed from right to left, so
    night n uses positions 9-n .. 8, and they are lit from left to right: the newest candle first
    (docs/DECISIONS.md D3).

    Rows: flames 2-4, wicks 5, candles 6-8, cups 9, arms 9-13 (each pair of cups joined by a U), base 14-15.
    The shamash stands 2 px higher: flame 0-2, wick 3, candle 4-6, cup 7, on a riser down to the arms.
    """

    CANDLE_TOP = 6  # first candle row
    CANDLE_ROWS = 3
    CUP_Y = 9
    SHAMASH_TOP = 4
    SHAMASH_CUP = 7

    def __init__(self, x0: int = 16, spacing: int = 5, metal=(GOLD, GOLD_HI, GOLD_LO)):
        self.x0, self.spacing = x0, spacing
        self.metal = metal
        # slot j = 0..8 left to right; j = 4 is the shamash
        self.slots = [x0 + spacing * j for j in range(9)]
        self.cx = self.slots[4]  # the shamash's left column (it is 2 px wide)
        self.mid = self.cx + 0.5

    def pos_x(self, p: int) -> int:
        """Left column of the 2 px candle at position p (1..8)."""
        return self.slots[p - 1 if p <= 4 else p]

    @staticmethod
    def placed(n: int) -> list[int]:
        """Positions holding a candle on night n (right to left)."""
        return list(range(9 - n, 9))

    @staticmethod
    def lighting_order(n: int) -> list[int]:
        """Positions in the order they are lit on night n: the newest (leftmost) first."""
        return list(range(9 - n, 9))

    def arm_y(self, k: int, x: float) -> float:
        """Row of arm k (1 = innermost pair) at column x: a U from the cups (row 9) down to row 9 + k."""
        d = self.spacing * k
        u = (x - self.mid) / d
        return self.CUP_Y + k * max(0.0, 1 - u * u)

    def draw_body(self, img, glint: float | None = None) -> None:
        """Arms, cups, the shamash riser, stem and base. glint: x of a moving highlight, or None."""
        base, hi, lo = self.metal

        def c(x, y, col):
            if glint is not None and abs(x - glint + (y - 10) * 0.6) < 1.2:
                col = mix(col, (255, 250, 225), 0.75)
            put(img, x, y, col)

        # stem and base first, so the arms read over them
        for y in range(self.SHAMASH_CUP + 1, 14):
            c(self.cx, y, hi)
            c(self.cx + 1, y, lo)
        for dx in range(-2, 4):
            c(self.cx + dx, 14, hi if dx < 0 else (lo if dx > 2 else base))
        for dx in range(-5, 7):
            c(self.cx + dx, 15, hi if dx < -2 else (lo if dx > 4 else base))
        for k in range(1, 5):
            d = self.spacing * k
            x0, x1 = int(self.mid - d - 0.5), int(self.mid + d + 0.5)
            prev = None
            for x in range(x0, x1 + 1):
                y = int(math.floor(self.arm_y(k, x) + 0.5))
                ys = [y] if prev is None else list(range(min(prev, y), max(prev, y) + 1)) if abs(prev - y) > 1 \
                    else [y]
                for yy in ys:
                    c(x, yy, (hi if x < self.mid else base) if k % 2 else (base if x < self.mid else lo))
                prev = y
        for j, sx in enumerate(self.slots):
            if j == 4:
                continue
            for dx in range(-1, 3):
                c(sx + dx, self.CUP_Y, hi if dx == -1 else (lo if dx == 2 else base))
        for dx in range(-1, 3):
            c(self.cx + dx, self.SHAMASH_CUP, hi if dx == -1 else (lo if dx == 2 else base))

    def candle(self, img, x: int, top: int, color, lit: float, f: int, seed: int, rows: int = 3,
               alpha: float = 1.0) -> None:
        body, hi = color
        for y in range(top, top + rows):
            put(img, x, y, hi, alpha)
            put(img, x + 1, y, body, alpha)
        put(img, x + (seed % 2), top - 1, WICK, alpha)
        flame(img, x, top - 2, f, seed, size=lit)

    def draw_candles(self, img, f: int, n: int, lit: dict[int, float], shamash: bool, shamash_lit: float) -> None:
        """Candles on night n. lit[p] = flame size (0..1) per position; shamash False while it is out of its
        holder (drawn with held_shamash), else drawn in place with flame size shamash_lit."""
        for p in self.placed(n):
            self.candle(img, self.pos_x(p), self.CANDLE_TOP, CANDLE_COLORS[p % 2], lit.get(p, 0.0), f, seed=p * 13)
        if shamash:
            self.candle(img, self.cx, self.SHAMASH_TOP, (SILVER, WHITE), shamash_lit, f, seed=99)

    def held_shamash(self, img, tx: float, ty: float, f: int) -> None:
        """The shamash out of its holder, tilted 45 degrees: wick end (tx, ty) at the lower left, the candle
        rising to the upper right, its flame just above the wick."""
        tx, ty = int(round(tx)), int(round(ty))
        for i in range(1, 5):
            put(img, tx + i, ty - i + 1, SILVER)
            put(img, tx + i + 1, ty - i + 1, WHITE)
        put(img, tx, ty, WICK)
        flame(img, tx - 1, ty - 1, f, 99, width=2, size=1.0)


def warm_room(img, k: float, cx: float = 36, cy: float = 6) -> None:
    """The warm light of lit candles on the room (k 0..1)."""
    glow(img, cx, cy, 30, (80, 44, 10), 0.4 * k)


# --- dreidel letters (simplified 5x5 shapes; docs/DECISIONS.md D6) -------------------------------------------------

LETTERS = {
    "nun": [".##..",
            "..#..",
            "..#..",
            "..#..",
            "####."],
    "gimel": [".##..",
              "..#..",
              "..#..",
              ".#.#.",
              "#..#."],
    "hei": ["####.",
            "...#.",
            "#..#.",
            "#..#.",
            "#..#."],
    "shin": ["#.#.#",
             "#.#.#",
             "#.#.#",
             "#.#.#",
             "#####"],
}


def letter(img, name: str, x: int, y: int, color, alpha: float = 1.0, clip=None) -> None:
    for gy, row in enumerate(LETTERS[name]):
        for gx, ch in enumerate(row):
            if ch == "#" and (clip is None or clip[0] <= x + gx <= clip[1]):
                put(img, x + gx, y + gy, color, alpha)


# --- gelt -----------------------------------------------------------------------------------------------------------

def coin(img, cx: float, cy: float, spin: float, r: float = 2.0, gold=True, alpha: float = 1.0) -> None:
    """A foil coin seen edge-on as it spins: spin 0..1 per turn sets the apparent width."""
    base, hi, lo = (GOLD, GOLD_HI, GOLD_LO) if gold else (SILVER, WHITE, SILVER_LO)
    wk = abs(math.cos(math.pi * spin))
    rx = max(0.5, r * wk)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - rx - 1), int(cx + rx + 2)):
            dx, dy = (x - cx) / (rx + 0.35), (y - cy) / (r + 0.35)
            if dx * dx + dy * dy <= 1:
                rim = dx * dx + dy * dy > 0.45
                col = (lo if (dx + dy) > 0.3 else hi) if rim else base
                put(img, x, y, col, alpha)


def flat_coin(img, x: int, y: int, gold=True, alpha: float = 1.0) -> None:
    """A coin lying in a pile, seen from the side: a 3x1 bar with a highlight."""
    base, hi, lo = (GOLD, GOLD_HI, GOLD_LO) if gold else (SILVER, WHITE, SILVER_LO)
    put(img, x - 1, y, hi, alpha)
    put(img, x, y, base, alpha)
    put(img, x + 1, y, lo, alpha)


def night_sky(img, top=(4, 8, 30), bottom=(14, 24, 70)) -> None:
    for y in range(H):
        c = mix(top, bottom, y / (H - 1))
        for x in range(W):
            put(img, x, y, c)


__all__ = ["GOLD", "GOLD_HI", "GOLD_LO", "SILVER", "SILVER_LO", "BLUE", "BLUE_HI", "BLUE_LO", "WHITE", "Menorah",
           "flame", "glow", "warm_room", "letter", "LETTERS", "coin", "flat_coin", "night_sky", "rect"]
