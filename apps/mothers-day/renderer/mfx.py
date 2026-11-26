"""App-local drawing helpers for Mother's Day: the spring palette, skies, glows, flowers, hearts, petals, butterflies
and simple figures. Everything is seeded or a pure function of the frame number, so builds are byte-identical.

Tone (docs/DECISIONS.md D2): warm, sweet and inclusive. Figures are generic (plain faces, no features), with a range
of skin tones and hair, so any family can see itself: moms, grandmothers, step-moms and adoptive moms alike.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette: soft pinks, lavender, warm yellows, spring greens (all lit enough for LEDs) -------------------------

PINK = (255, 104, 168)
PINK_HI = (255, 176, 210)
PINK_DK = (206, 52, 118)
ROSE = (236, 34, 72)
ROSE_HI = (255, 112, 128)
ROSE_DK = (164, 18, 48)
CORAL = (255, 128, 96)
LAVENDER = (176, 124, 255)
LAVENDER_HI = (214, 186, 255)
LAVENDER_DK = (118, 74, 210)
YELLOW = (255, 206, 52)
YELLOW_HI = (255, 240, 150)
YELLOW_DK = (226, 150, 24)
ORANGE = (255, 150, 40)
GREEN = (72, 186, 70)
GREEN_HI = (146, 226, 104)
GREEN_DK = (30, 122, 44)
WHITE = (252, 248, 242)
CREAM = (255, 236, 206)
PAPER = (255, 222, 228)
SKY = (120, 190, 255)
SKY_HI = (186, 226, 255)
WOOD = (150, 88, 48)
WOOD_HI = (190, 122, 70)
WOOD_DK = (104, 58, 32)
SOIL = (112, 66, 38)
SOIL_DK = (80, 46, 28)
SILVER = (200, 206, 222)
STRAW = (232, 196, 112)

# Skin tones, all lit (the darkest is still far from an unlit LED), lightest last.
SKIN = ((118, 70, 44), (150, 96, 60), (186, 126, 82), (216, 164, 116), (240, 196, 158))
# Hair: lit browns, auburn, blond and a silver grey (never near-black: it would read as a hole).
HAIR_DARK = (92, 58, 40)
HAIR_BROWN = (138, 84, 44)
HAIR_AUBURN = (176, 74, 40)
HAIR_BLOND = (236, 192, 96)
HAIR_GREY = (196, 196, 210)


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


def line(img, x0: float, y0: float, x1: float, y1: float, c, a: float = 1.0) -> None:
    """A 1 px line (simple DDA)."""
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        put(img, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c, a)


def grid(img, x: int, y: int, rows, pal: dict, alpha: float = 1.0) -> None:
    """Draw a text-grid sprite: each character maps to a color in `pal`; '.' and ' ' are transparent."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            c = pal.get(ch)
            if c is not None:
                put(img, x + dx, y + dy, c, alpha)


# --- hearts -------------------------------------------------------------------------------------------------------

HEARTS = {
    3: ["P.P", "PPP", ".P."],
    5: [".P.P.", "PHPPP", "PPPPP", ".PPP.", "..P.."],
    7: [".PP.PP.", "PHPPPPP", "PPPPPPP", ".PPPPP.", "..PPP..", "...P..."],
    9: [".PPP.PPP.", "PHHPPPPPP", "PHPPPPPPP", "PPPPPPPPP", ".PPPPPPP.", "..PPPPP..", "...PPP...", "....P...."],
}


def heart(img, cx: float, y: int, size: int = 5, color=PINK, hi=None, alpha: float = 1.0, halo=None) -> None:
    """A heart `size` px wide (3, 5, 7 or 9) centered on column cx, top at row y. `halo` draws a 1 px ring first
    (a dark ring keeps overlapping hearts apart)."""
    rows = HEARTS[size]
    x0 = int(math.floor(cx - size / 2 + 0.5))
    y0 = int(math.floor(y + 0.5))
    if halo is not None:
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch != ".":
                    for ox, oy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = dx + ox, dy + oy
                        inside = 0 <= ny < len(rows) and 0 <= nx < size and rows[ny][nx] != "."
                        if not inside:
                            put(img, x0 + nx, y0 + ny, halo, alpha * 0.7)
    grid(img, x0, y0, rows, {"P": color, "H": hi or mix(color, WHITE, 0.55)}, alpha)


# --- flowers ------------------------------------------------------------------------------------------------------

def tulip(img, cx: int, top: int, color=PINK, alpha: float = 1.0) -> None:
    """A 3x3 tulip cup, top row at `top`, centered on cx."""
    hi, dk = mix(color, WHITE, 0.45), mix(color, (0, 0, 0), 0.3)
    grid(img, cx - 1, top, ["P.P", "HPP", "DPD"], {"P": color, "H": hi, "D": dk}, alpha)


def rose(img, cx: int, top: int, color=ROSE, alpha: float = 1.0) -> None:
    """A 3x3 rose with a lighter swirl, top row at `top`."""
    hi, dk = mix(color, WHITE, 0.4), mix(color, (0, 0, 0), 0.35)
    grid(img, cx - 1, top, ["DPD", "PHP", "DPD"], {"P": color, "H": hi, "D": dk}, alpha)


def daisy(img, cx: int, cy: int, petals=WHITE, center=YELLOW, alpha: float = 1.0) -> None:
    """A 3x3 daisy centered on (cx, cy): four petals, dimmer diagonals and a yellow heart."""
    dim = mix(petals, (120, 120, 140), 0.45)
    grid(img, cx - 1, cy - 1, ["dWd", "WYW", "dWd"], {"W": petals, "d": dim, "Y": center}, alpha)


def big_daisy(img, cx: int, cy: int, petals=WHITE, center=YELLOW, alpha: float = 1.0) -> None:
    """A 5x5 daisy centered on (cx, cy)."""
    dim = mix(petals, (120, 120, 140), 0.4)
    grid(img, cx - 2, cy - 2, [".dWd.", "dWWWd", "WWYWW", "dWWWd", ".dWd."], {"W": petals, "d": dim, "Y": center},
         alpha)
    put(img, cx, cy, center, alpha)


def lavender_sprig(img, cx: int, top: int, n: int = 4, alpha: float = 1.0) -> None:
    """A spike of lavender buds, `n` rows tall, alternating sides."""
    for k in range(n):
        put(img, cx, top + k, LAVENDER if k % 2 else LAVENDER_HI, alpha)
        if k % 2 == 0 and k:
            put(img, cx + (1 if k % 4 == 0 else -1), top + k, LAVENDER_DK, alpha)


def bloom(img, kind: str, cx: int, top: int, color=None, grow: float = 1.0, alpha: float = 1.0) -> None:
    """A flower head of `kind` ("tulip", "rose", "daisy", "lavender") opening with `grow` (0 bud .. 1 open)."""
    if grow <= 0:
        return
    if grow < 0.5:  # a bud: one or two pixels
        bud = GREEN_HI if grow < 0.25 else mix(GREEN_HI, color or PINK, 0.6)
        put(img, cx, top + 1, bud, alpha)
        if grow >= 0.25:
            put(img, cx, top + 2, GREEN, alpha)
        return
    a = alpha * min(1.0, 0.5 + (grow - 0.5) * 2)
    if kind == "tulip":
        tulip(img, cx, top, color or PINK, a)
    elif kind == "rose":
        rose(img, cx, top, color or ROSE, a)
    elif kind == "daisy":
        daisy(img, cx, top + 1, color or WHITE, YELLOW, a)
    else:
        lavender_sprig(img, cx, top, 4, a)


def stem(img, x: int, y0: int, y1: int, leaf: int | None = None, leaf_side: int = 1, alpha: float = 1.0) -> None:
    """A vertical stem from row y0 down to y1, with an optional leaf at row `leaf`."""
    for y in range(y0, y1 + 1):
        put(img, x, y, GREEN, alpha)
    if leaf is not None and y0 <= leaf <= y1:
        put(img, x + leaf_side, leaf, GREEN_HI, alpha)
        put(img, x + 2 * leaf_side, leaf - 1, GREEN, alpha * 0.8)


# --- petals and butterflies ---------------------------------------------------------------------------------------

def petal(img, x: float, y: float, f: int, color=PINK_HI, alpha: float = 1.0) -> None:
    """A drifting petal: one bright pixel that tumbles (every few frames a dimmer neighbor shows its edge)."""
    put(img, x, y, color, alpha)
    if (f // 4) % 2:
        put(img, x + 1, y, mix(color, PINK_DK, 0.5), alpha * 0.6)


def butterfly(img, x: float, y: float, f: int, color=YELLOW, body=WOOD_DK, alpha: float = 1.0) -> None:
    """A tiny butterfly: wings open and close every few frames around a 1 px body."""
    xi, yi = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    open_ = (f // 3) % 2 == 0
    put(img, xi, yi, mix(body, WHITE, 0.25), alpha)
    if open_:
        for dx in (-1, 1):
            put(img, xi + dx, yi - 1, color, alpha)
            put(img, xi + dx, yi, mix(color, WHITE, 0.3), alpha)
            put(img, xi + 2 * dx, yi - 1, mix(color, (0, 0, 0), 0.15), alpha * 0.8)
    else:
        put(img, xi, yi - 1, color, alpha)
        put(img, xi - 1, yi - 1, mix(color, (0, 0, 0), 0.2), alpha * 0.7)


# --- figures ------------------------------------------------------------------------------------------------------

def person(img, x: int, feet: int, skin, shirt, legs_c, hair, style: str = "short", arms=(0.0, 0.0), legs: int = 0,
           child: bool = False, skirt: bool = False, seated: bool = False, alpha: float = 1.0, shoes=None) -> dict:
    """A simple front-facing figure, 3 px wide at the body, centered on column x, feet on row `feet`.

    Adults are 12 rows tall (hair 1, head 3, body 4, legs 3, feet 1), children 9 (hair 1, head 3, body 3, legs 1,
    feet 1). style: "short", "long" (hair to the shoulders), "bun" (a bun on top), "puff" (a round curly puff),
    "pony" (a ponytail to one side) or "hat" (a straw sun hat; `hair` is its band). arms: (left, right) angles in turns, 0 = down, 0.25 = straight out,
    0.5 = straight up. legs: 0 together, 1 apart (a step), -1 kneeling (two rows shorter). seated: waist up only.
    Faces are plain skin: a 3x3 head has no room for lit eyes, and dark pixels would read as holes.
    Returns the hand positions {"l": (x, y), "r": (x, y)} and the head's top row.
    """
    body_rows = 3 if child else 4
    leg_rows = 1 if child else 3
    height = 1 + 3 + body_rows + leg_rows + 1
    kneel = 2 if legs == -1 else 0
    top = feet - height + 1 + kneel
    head = top + 1
    cx = x
    # hair behind the head first (long hair falls past the shoulders)
    if style == "long":
        for dy in range(1, 5):
            put(img, cx - 2, head + dy, hair, alpha)
            put(img, cx + 2, head + dy, hair, alpha)
    # head
    for dy in range(3):
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue  # chin
            put(img, cx + dx, head + dy, skin, alpha)
    # hair on top (or a wide-brimmed sun hat, its band in `hair`)
    if style == "hat":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top - 1, STRAW, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, top, hair if abs(dx) < 2 and dx != 0 else STRAW, alpha)
    else:
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hair, alpha)
        put(img, cx - 1, head, hair, alpha)
        put(img, cx + 1, head, hair, alpha)
    if style == "long":
        put(img, cx - 2, head, hair, alpha)
        put(img, cx + 2, head, hair, alpha)
    elif style == "bun":
        put(img, cx, top - 1, mix(hair, WHITE, 0.15), alpha)
    elif style == "puff":
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, top - 1 if abs(dx) < 2 else top, hair, alpha)
        put(img, cx - 2, head, hair, alpha)
        put(img, cx + 2, head, hair, alpha)
    elif style == "pony":
        put(img, cx + 2, head, hair, alpha)
        put(img, cx + 2, head + 1, hair, alpha)
    # body
    body = head + 3
    for dy in range(body_rows):
        for dx in (-1, 0, 1):
            put(img, cx + dx, body + dy, shirt, alpha)
    # arms
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        sgn = -1 if side == "l" else 1
        sx = cx + 2 * sgn
        a = 2 * math.pi * ang
        n = 3 if not child else 2
        hx, hy = float(sx), float(body)
        for k in range(n):
            hx = sx + sgn * math.sin(a) * k
            hy = body + math.cos(a) * k
            put(img, hx, hy, shirt if k == 0 else skin, alpha)
        hands[side] = (int(math.floor(hx + 0.5)), int(math.floor(hy + 0.5)))
    hands["top"] = top
    if seated:
        return hands
    shoes = shoes or mix(legs_c, (0, 0, 0), 0.35)
    leg_top = body + body_rows
    rows = max(0, leg_rows - kneel)
    spread = 1 if legs == 1 else 0
    for dy in range(rows):
        y = leg_top + dy
        if skirt:
            w = 1 if dy == 0 else 2
            for dx in range(-w, w + 1):
                put(img, cx + dx, y, legs_c, alpha)
        else:
            s = spread if dy == rows - 1 else 0
            put(img, cx - 1 - s, y, legs_c, alpha)
            put(img, cx + 1 + s, y, legs_c, alpha)
            if dy == 0:
                put(img, cx, y, legs_c, alpha)
    fy = leg_top + rows
    put(img, cx - 1 - spread, fy, shoes, alpha)
    put(img, cx + 1 + spread, fy, shoes, alpha)
    return hands


def mix_paper(fold: bool):
    """The bouquet wrap's paper: cream, with a slightly darker fold line."""
    return mix(CREAM, (230, 180, 170), 0.5) if fold else CREAM
