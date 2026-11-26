"""App-local St. Patrick's Day art: the leprechaun, shamrocks, the rainbow, the pot of gold and coins, captions.

Everything is seeded or a pure function of the frame number, so builds are byte-identical. These build on the
shared render kit (busybar.canvas / busybar.party) and stay in this app until another app needs them (repo R2).

Black is an unlit LED (AGENTS.md): the leprechaun's eyes are a lit blue, his hat band a lit dark green, and his
shoes a lit brown, so none of them reads as a hole (docs/DECISIONS.md D5).
"""

from __future__ import annotations

import math

from busybar.canvas import W, add, mix, put
from busybar.font import draw_text, text_width
from busybar.party import hash01

# --- palette (linear colors; the build's tone curve lifts them) ------------------------------------------------

GREEN = (34, 164, 64)
GREEN_HI = (110, 220, 110)
GREEN_DK = (18, 104, 40)
SHAMROCK = (52, 190, 70)
SHAMROCK_HI = (140, 236, 120)
SHAMROCK_DK = (22, 120, 44)
GOLD = (255, 196, 46)
GOLD_HI = (255, 238, 150)
GOLD_DK = (200, 130, 24)
WHITE = (240, 244, 236)
ORANGE = (255, 136, 30)  # the tricolor's orange
GINGER = (226, 104, 30)
GINGER_HI = (255, 150, 60)
SKIN = (250, 198, 156)
ROSY = (255, 126, 106)
EYE = (60, 116, 236)  # lit blue: black eyes would be holes
SHOE = (132, 76, 40)
BELT = (120, 70, 36)
STOCKING = (236, 236, 228)
RAINBOW = ((236, 40, 40), (255, 128, 20), (255, 216, 30), (60, 200, 60), (40, 120, 240), (90, 60, 200),
           (170, 70, 210))
IRON = (70, 76, 92)  # the pot: a lit blue-grey, never black
IRON_HI = (128, 136, 156)
IRON_DK = (48, 52, 66)

# --- the leprechaun ----------------------------------------------------------------------------------------------

# Front view, 11 px wide, 14 rows: a tall buckled hat, ginger hair and beard, lit blue eyes, a green coat with a gold
# button and a belt. Arms and legs are drawn separately (poses). '.' is transparent.
LEP_HAT = """
....hHH....
....hHH....
....KYK....
..hHHHHHH..
"""
LEP_BODY = """
...rSSSr...
...SeSeS...
...rScSr...
....BBB....
...CCBCC...
...CgYGC...
...CbYbC...
"""  # rows 4-10
LEP_COLORS = {
    "h": GREEN_HI, "H": GREEN, "K": (20, 84, 36), "Y": GOLD, "r": GINGER, "S": SKIN, "e": EYE, "c": ROSY,
    "B": GINGER, "C": GREEN, "g": GREEN_HI, "G": GREEN_DK, "b": BELT,
}

# Legs (rows 11-13) and arms (from the shoulders at x 2 and 8, row 8), as (dx, dy, color key) lists.
# L = breeches, W = stocking, s = shoe; C = sleeve, S = hand.
LEGS = {
    "stand": [(4, 11, "L"), (6, 11, "L"), (4, 12, "W"), (6, 12, "W"), (3, 13, "s"), (4, 13, "s"), (6, 13, "s"),
              (7, 13, "s")],
    "kick_r": [(4, 11, "L"), (6, 11, "L"), (4, 12, "W"), (7, 12, "W"), (3, 13, "s"), (4, 13, "s"), (8, 12, "s"),
               (9, 11, "s")],
    "kick_l": [(4, 11, "L"), (6, 11, "L"), (3, 12, "W"), (6, 12, "W"), (2, 12, "s"), (1, 11, "s"), (6, 13, "s"),
               (7, 13, "s")],
    "click": [(4, 11, "L"), (6, 11, "L"), (3, 12, "W"), (7, 12, "W"), (2, 12, "s"), (1, 12, "s"), (8, 12, "s"),
              (9, 12, "s")],
    "tuck": [(4, 11, "L"), (6, 11, "L"), (3, 12, "s"), (4, 12, "s"), (6, 12, "s"), (7, 12, "s")],
}
LEG_COLORS = {"L": GREEN_DK, "W": STOCKING, "s": SHOE}
_HIPS_L = [(2, 8, "C"), (1, 9, "C"), (2, 10, "S")]
_HIPS_R = [(8, 8, "C"), (9, 9, "C"), (8, 10, "S")]
_UP_L = [(2, 8, "C"), (1, 7, "C"), (0, 6, "S")]
_UP_R = [(8, 8, "C"), (9, 7, "C"), (10, 6, "S")]
_OUT_L = [(2, 8, "C"), (1, 8, "C"), (0, 8, "S")]
_OUT_R = [(8, 8, "C"), (9, 8, "C"), (10, 8, "S")]
ARMS = {
    "hips": _HIPS_L + _HIPS_R, "up": _UP_L + _UP_R, "up_l": _UP_L + _HIPS_R, "up_r": _HIPS_L + _UP_R,
    "out": _OUT_L + _OUT_R, "out_up": _OUT_L + _UP_R,
}
ARM_COLORS = {"C": GREEN, "S": SKIN}

LEP_W, LEP_H = 11, 14


def _grid(img, rows: str, x: int, y: int, colors: dict, alpha: float = 1.0) -> None:
    for dy, row in enumerate(rows.strip("\n").splitlines()):
        for dx, ch in enumerate(row):
            if ch != ".":
                put(img, x + dx, y + dy, colors[ch], alpha)


def leprechaun(img, x: int, top: int, legs: str = "stand", arms: str = "hips", hat_lift: int = 0, blink: bool = False,
               alpha: float = 1.0) -> None:
    """The leprechaun, top-left at (x, top), 11 x 14. hat_lift raises the hat (tipping it); blink closes the eyes."""
    colors = dict(LEP_COLORS)
    if blink:
        colors["e"] = SKIN
    _grid(img, LEP_BODY, x, top + 4, colors, alpha)
    if hat_lift:  # hair shows under a raised hat
        for dx in (3, 4, 5, 6, 7):
            put(img, x + dx, top + 3, GINGER, alpha)
    _grid(img, LEP_HAT, x, top - hat_lift, colors, alpha)
    for dx, dy, k in LEGS[legs]:
        put(img, x + dx, top + dy, LEG_COLORS[k], alpha)
    for dx, dy, k in ARMS[arms]:
        put(img, x + dx, top + dy, ARM_COLORS[k], alpha)


# --- shamrocks ---------------------------------------------------------------------------------------------------

_HEART_UP = (".##.##.", "#######", "#######", ".#####.", "..###..", "...#...")  # a leaf, notch up, point down


def _rot_cw(rows):
    h = len(rows)
    return tuple("".join(rows[h - 1 - j][i] for j in range(h)) for i in range(len(rows[0])))


def _leaves(four: bool):
    """Pixels of the big clover (13 x 13 around its center): {(dx, dy): 'leaf' | 'edge' | 'vein'}. Where two leaves
    meet, the pixels become 'edge' (a darker green), so the leaves read as separate hearts."""
    up = _HEART_UP
    right = _rot_cw(up)  # notch right, point left
    down = tuple(r for r in reversed(up))
    left = tuple(r[::-1] for r in right)
    owner = {}

    def place(rows, x0, y0, k):
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                if ch == "#":
                    p = (x0 + dx, y0 + dy)
                    owner[p] = -1 if p in owner else k
    place(up, -3, -6, 0)
    place(right, 1, -3, 1)
    place(left, -6, -3, 2)
    if four:
        place(down, -3, 1, 3)
    out = {}
    for (x, y), k in owner.items():
        near = {owner.get((x + dx, y + dy), k) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))}
        out[(x, y)] = "edge" if k == -1 or any(n not in (k, -1) for n in near) else "leaf"
    veins = [(0, 0), (0, -1), (0, -2), (0, -3), (-1, 0), (-2, 0), (-3, 0), (1, 0), (2, 0), (3, 0)]
    if four:
        veins += [(0, 1), (0, 2), (0, 3)]
    for p in veins:
        out[p] = "vein"
    return out


_BIG = {False: _leaves(False), True: _leaves(True)}
_SMALL = """
.h#.#h.
.#####.
..###..
h#.o.#h
###o###
.#.s.#.
...s...
"""


def shamrock(img, cx: float, cy: float, size: int = 1, color=SHAMROCK, hi=SHAMROCK_HI, stem=SHAMROCK_DK,
             four: bool = False, sway: float = 0.0, alpha: float = 1.0) -> None:
    """A shamrock centered on (cx, cy): three heart-shaped leaves (four with four=True) and a stem.

    size 0: a 3x3 plus of leaves and a stem; size 1: 7x7 with notched leaves; size 2: the big 13x13 clover.
    sway shifts the leaves sideways (the stem stays rooted) for wind.
    """
    cx, cy = int(round(cx)), int(round(cy))
    s = int(round(sway))
    if size == 0:
        for dx, dy in ((0, -1), (-1, 0), (1, 0)) + (((0, 1),) if four else ()):
            put(img, cx + dx + s, cy + dy, color, alpha)
        put(img, cx + s, cy, hi, alpha)
        put(img, cx, cy + 1 + (1 if four else 0), stem, alpha)
        return
    if size == 1:
        rows = _SMALL.strip("\n").splitlines()
        for dy, r in enumerate(rows):
            for dx, ch in enumerate(r):
                if ch == ".":
                    continue
                c = {"#": color, "h": hi, "o": hi, "s": stem}[ch]
                put(img, cx - 3 + dx + (s if dy < 5 else 0), cy - 4 + dy, c, alpha)
        if four:
            for dx, dy in ((-1, 2), (1, 2), (0, 2)):
                put(img, cx + dx + s, cy + dy, color, alpha)
        return
    leaves = _BIG[four]
    for (dx, dy), kind in leaves.items():
        if kind == "vein":
            c = stem  # a darker cross between the leaves keeps them apart
        elif any((dx + ex, dy + ey) not in leaves for ex, ey in ((1, 0), (-1, 0), (0, 1), (0, -1))):
            c = hi  # a lit rim traces each heart
        else:
            c = color
        put(img, cx + dx + s, cy + dy, c, alpha)
    if not four:  # the stem, curving down to the right
        for dx, dy in ((0, 1), (0, 2), (0, 3), (1, 4), (1, 5), (2, 6)):
            put(img, cx + dx + (s if dy < 2 else 0), cy + dy, stem, alpha)


def coin(img, x: float, y: float, f: int, seed: int = 0, alpha: float = 1.0) -> None:
    """A spinning gold coin, 2x2 (face) or 1x2 (edge), its phase from the seed."""
    p = (f // 3 + seed) % 4
    x, y = int(round(x)), int(round(y))
    if p == 0:
        put(img, x, y, GOLD_HI, alpha)
        put(img, x + 1, y, GOLD, alpha)
        put(img, x, y + 1, GOLD, alpha)
        put(img, x + 1, y + 1, GOLD_DK, alpha)
    elif p in (1, 3):
        put(img, x, y, GOLD_HI, alpha)
        put(img, x, y + 1, GOLD, alpha)
    else:
        put(img, x, y, GOLD, alpha)
        put(img, x + 1, y, GOLD_HI, alpha)
        put(img, x, y + 1, GOLD_DK, alpha)
        put(img, x + 1, y + 1, GOLD, alpha)


POT_ROWS = (  # the cauldron below the rim, as half-widths (a round belly)
    5, 6, 6, 6, 5, 4)


def pot(img, cx: int, base: int, gold: float = 1.0, f: int = 0, seed: int = 3) -> None:
    """The pot of gold standing on row `base`: a round iron cauldron (13 px at the belly) with a lit rim, three
    stubby feet and gold heaped over the mouth. gold 0..1 grows the heap from the middle outward."""
    rim_y = base - len(POT_ROWS) - 1
    for i, hw in enumerate(POT_ROWS):
        y = rim_y + 1 + i
        for dx in range(-hw, hw + 1):
            c = IRON
            if dx <= -hw + 1 and 0 < i < 4:
                c = IRON_HI  # the shine down the left of the belly
            elif dx >= hw - 1 or i == len(POT_ROWS) - 1:
                c = IRON_DK
            put(img, cx + dx, y, c)
    for dx in (-4, 0, 4):  # feet
        put(img, cx + dx, base, IRON_DK)
    for dx in range(-5, 6):  # the rim
        put(img, cx + dx, rim_y, IRON_HI if abs(dx) == 5 else GOLD if hash01(seed, dx, f // 5) > 0.3 else GOLD_HI)
    if gold <= 0:
        return
    heap = [(dx, -1) for dx in range(-4, 5)] + [(dx, -2) for dx in range(-3, 4)] + [(dx, -3) for dx in range(-1, 2)]
    heap.sort(key=lambda p: (-p[1] if p[1] > -3 else 9, abs(p[0])))
    n = int(len(heap) * min(1.0, gold) + 0.5)
    for dx, dy in heap[:n]:
        k = hash01(seed, dx, dy, f // 4)
        c = GOLD_HI if k > 0.8 else (GOLD if k > 0.25 else GOLD_DK)
        put(img, cx + dx, rim_y + dy, c)


# --- the rainbow -------------------------------------------------------------------------------------------------

def rainbow(img, cx: float, cy: float, rx: float, ry: float, reveal: float = 1.0, alpha: float = 1.0,
            band: float = 1.0, from_left: bool = True) -> None:
    """An elliptical seven-band rainbow arc centered on (cx, cy) (below the horizon), red outside.

    reveal 0..1 draws the arc from one foot (left, or right) over the top to the other.
    """
    for y in range(img.height):
        for x in range(img.width):
            dx, dy = (x - cx) / rx, (y - cy) / ry
            r = math.hypot(dx, dy)
            k = (1 - r) * ry / band  # bands inward from the outer edge, ~1 px each at the top
            if not (0 <= k < 7) or y > cy:
                continue
            ang = math.atan2(-(y - cy), (x - cx))  # pi at the left foot .. 0 at the right foot
            u = (math.pi - ang) / math.pi if from_left else ang / math.pi
            if u > reveal:
                continue
            i = int(k)
            frac = k - i
            c = RAINBOW[i]
            put(img, x, y, c, alpha * (0.85 if frac < 0.15 or frac > 0.85 else 1.0))


# --- captions ----------------------------------------------------------------------------------------------------

CAPTION_GRAD = (GOLD_HI, (255, 172, 36))
CAPTION_SHADOW = (8, 46, 20)


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 0) -> None:
    """Darken the box x0..x1, y0..y1 by k (0..1) so a caption reads over busy art (from Kwanzaa's kfx). `feather`
    fades the darkening out over that many pixels on every side."""
    if k <= 0:
        return
    px = img.load()
    for y in range(max(0, y0 - feather), min(img.height, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(img.width, x1 + feather + 1)):
            d = max(x0 - x, x - x1, y0 - y, y - y1, 0)
            kk = k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - kk)), int(g * (1 - kk)), int(b * (1 - kk)), a)


def caption(img, text: str, y: int, alpha: float, font: str = "big", x: int | None = None, back: float = 0.6,
            grad=CAPTION_GRAD, shadow=CAPTION_SHADOW) -> None:
    """A caption faded in by alpha; the art behind it dims first, so it stays legible."""
    if alpha <= 0:
        return
    w = text_width(text, font)
    x = (W - w) // 2 if x is None else x
    h = 7 if font == "big" else 5
    if back:
        dim_rect(img, x - 1, y - 1, x + w + 1, y + h, back * alpha, feather=2)
    draw_text(img, text, x, y, None, font=font, gradient=grad, shadow=shadow, alpha=alpha)


def glow(img, cx: float, cy: float, r: float, color, a: float) -> None:
    """A soft round additive glow."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def note(img, x: float, y: float, color=GOLD_HI, alpha: float = 1.0, kind: int = 0) -> None:
    """A music note, 3x4: a head and a stem (kind 1: two beamed notes, 4x4)."""
    x, y = int(round(x)), int(round(y))
    if kind == 0:
        for dy in range(3):
            put(img, x + 1, y + dy, color, alpha)
        put(img, x + 2, y, color, alpha * 0.8)
        put(img, x, y + 3, color, alpha)
        put(img, x + 1, y + 3, color, alpha)
    else:
        for dy in range(3):
            put(img, x + 1, y + dy, color, alpha)
            put(img, x + 3, y + dy, color, alpha)
        put(img, x + 2, y, color, alpha)
        put(img, x, y + 3, color, alpha)
        put(img, x + 2, y + 3, color, alpha)


def sparkle4(img, x: float, y: float, k: float, color=GOLD_HI) -> None:
    """A four-point twinkle, k 0..1."""
    if k <= 0.05:
        return
    add(img, x, y, color, k)
    if k > 0.5:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            add(img, x + dx, y + dy, color, 0.6 * (k - 0.5))


def mixc(a, b, t):
    return mix(a, b, t)
