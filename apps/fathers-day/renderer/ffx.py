"""App-local drawing helpers for Father's Day: the summer palette, skies, glows, caption backing, water, and a
procedural person (a parent or a child) with arm angles, hair styles, a cap and a beard. Everything is seeded or a
pure function of the frame number, so builds are byte-identical.

Tone (docs/DECISIONS.md D2): warm, lighthearted and inclusive. Dads, granddads and father figures with a range of
skin tones and hair; faces are plain skin (a 3 px head has no room for lit eyes, and dark pixels read as holes).
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette (summer blues, greens, sunset oranges) -------------------------------------------------------------

SKY = (96, 170, 236)
SKY_PALE = (170, 214, 248)
GRASS = (62, 150, 58)
GRASS_DK = (40, 112, 44)
GRASS_HI = (110, 190, 80)
SUN = (255, 214, 96)
SUN_HI = (255, 244, 190)
ORANGE = (255, 140, 48)
WHITE = (246, 246, 240)
GOLD = (255, 196, 60)
GOLD_HI = (255, 236, 150)
GOLD_DK = (196, 132, 30)
WOOD = (150, 96, 56)
WOOD_DK = (112, 70, 40)
WOOD_HI = (190, 130, 78)

# Skin tones, deep to light. All lit enough to read on LEDs (deep tones get lighter values than they would on paper).
SKIN_DEEP = (124, 78, 52)
SKIN_BROWN = (160, 104, 66)
SKIN_MEDIUM = (190, 132, 88)
SKIN_TAN = (214, 160, 112)
SKIN_LIGHT = (240, 192, 152)

# Hair: lit dark tones (never near-black), grey for a granddad.
HAIR_DARK = (88, 62, 52)
HAIR_BROWN = (122, 76, 44)
HAIR_AUBURN = (160, 80, 40)
HAIR_BLOND = (220, 180, 96)
HAIR_GREY = (196, 196, 204)


def sky(stops, width: int = W) -> Image.Image:
    """A width x 16 vertical gradient through `stops` [(row, color), ...] (rows between stops are blended)."""
    img = Image.new("RGBA", (width, H))
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
        for x in range(width):
            px[x, y] = tuple(c) + (255,)
    return img


def glow(img, cx: float, cy: float, r: float, color, a: float, squash: float = 1.0) -> None:
    """Additive radial glow (keep `a` steady from frame to frame: per-frame flicker bloats the .anim)."""
    for y in range(max(0, int(cy - r / squash) - 1), min(H, int(cy + r / squash) + 2)):
        for x in range(max(0, int(cx - r) - 1), min(img.width, int(cx + r) + 2)):
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
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        t = i / max(1, n)
        put(img, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c, a)


def rnd(v: float) -> int:
    """Round halves up (Python's round() goes to even)."""
    return int(math.floor(v + 0.5))


def sun(img, cx: float, cy: float, r: float = 2.6, core=SUN_HI, rim=SUN, halo: float = 0.0) -> None:
    """A round sun with a soft halo (the halo is steady)."""
    if halo:
        glow(img, cx, cy, r + 5, rim, halo)
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                put(img, x, y, core if d < r - 1 else rim)


def cloud(img, x: float, y: float, w: int = 7, color=(250, 250, 255), a: float = 0.9) -> None:
    """A small flat-bottomed cloud: two rows, the top one shorter."""
    for dx in range(w):
        put(img, x + dx, y + 1, color, a)
    for dx in range(1, w - 1):
        if dx != w // 2 + 1:
            put(img, x + dx, y, color, a * 0.9)


def tree(img, cx: int, top: int, r: float = 4.5, base: int = H - 1, leaf=GRASS_DK, leaf_hi=GRASS, trunk=WOOD_DK,
         seed: int = 0) -> None:
    """A round summer tree: a lumpy crown of two greens on a trunk."""
    cy = top + r
    for y in range(max(0, int(top)), min(H, int(cy + r) + 1)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot((x - cx) * 0.9, (y - cy))
            wob = 0.6 * math.sin(x * 1.7 + seed) * math.cos(y * 1.3 + seed)
            if d <= r + wob:
                hi = (x - cx) + (y - cy) < -1 and ((x * 3 + y * 5 + seed) % 4) != 0
                put(img, x, y, leaf_hi if hi else leaf)
    for y in range(int(cy + r * 0.5), base + 1):
        put(img, cx, y, trunk)


# --- people -----------------------------------------------------------------------------------------------------

def figure(img, x: int, feet: int, skin, shirt, pants, hair=HAIR_DARK, style: str = "short", kid: bool = False,
           arms=(0.0, 0.0), legs: int = 0, beard=None, cap=None, facing: int = 1, shoes=(120, 110, 120),
           seated: bool = False, kneel: bool = False, alpha: float = 1.0) -> dict:
    """A small standing person centered on column x with feet on row `feet`. 5 px wide with arms.

    An adult is 13 rows (hair, 3-row head, 5-row shirt, 3-row legs, shoes); a child (kid=True) is 9 rows.
    style: "short", "curly" (taller and puffy), "bald" (a fringe of `hair` at the sides), "pony" (a ponytail on the
    side away from `facing`), "buzz" (one row).  cap: a cap color (its brim points toward `facing`).
    arms: (left, right) angles in turns: 0 = hanging down, 0.25 = straight out, 0.5 = straight up.
    legs: 0 together, 1 striding. seated: legs stick out toward `facing` and dangle (sitting on an edge); the seat
    is row `feet - 3` for an adult (`feet - 2` for a child). kneel: on one knee (two rows shorter), facing `facing`.
    Returns the hand positions {"l": (x, y), "r": (x, y)} as floats.
    """
    cx = x
    if kid:
        head_rows, torso_rows, leg_rows, arm_len = 2, 3, 2, 3
    else:
        head_rows, torso_rows, leg_rows, arm_len = 3, 5, 3, 4
    if kneel:
        leg_rows = 1
    total = 1 + head_rows + torso_rows + leg_rows + 1
    top = feet - total + 1
    p = lambda xx, yy, c: put(img, xx, yy, c, alpha)  # noqa: E731

    # head
    hy = top + 1
    for dy in range(head_rows):
        for dx in (-1, 0, 1):
            if not kid and dy == head_rows - 1 and dx != 0 and not beard:
                continue  # chin
            p(cx + dx, hy + dy, beard if (beard and dy == head_rows - 1) else skin)
    if beard and not kid:
        p(cx - 1, hy + 1, beard)
        p(cx + 1, hy + 1, beard)
        p(cx, hy + 1, skin)
    # hair / cap
    if cap is not None:
        for dx in (-1, 0, 1):
            p(cx + dx, top, cap)
        p(cx + 2 * facing, top + 1, cap)  # the brim
        p(cx - facing, hy, hair)
    elif style == "bald":
        p(cx, top, skin)
        p(cx - 1, hy, hair)
        p(cx + 1, hy, hair)
    elif style == "buzz":
        for dx in (-1, 0, 1):
            p(cx + dx, top, hair)
    else:
        for dx in (-1, 0, 1):
            p(cx + dx, top, hair)
        p(cx - facing, hy, hair)
        if style == "curly":
            for dx in (-1, 0, 1):
                p(cx + dx, top - 1, hair)
            p(cx - 2, top, hair)
            p(cx + 2, top, hair)
            p(cx + facing, hy, hair)
        elif style == "pony":
            p(cx - 2 * facing, hy, hair)
            p(cx - 2 * facing, hy + 1, hair)
    # torso
    ty = hy + head_rows
    for dy in range(torso_rows):
        for dx in (-1, 0, 1):
            p(cx + dx, ty + dy, shirt)
    # arms
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        sgn = -1 if side == "l" else 1
        a = 2 * math.pi * ang
        sx = cx + sgn * 2
        hx, hy2 = float(sx), float(ty)
        for k in range(arm_len):
            hx = sx + sgn * math.sin(a) * k
            hy2 = ty + math.cos(a) * k
            p(rnd(hx), rnd(hy2), shirt if k == 0 else skin)
        hands[side] = (hx, hy2)
    # legs
    ly = ty + torso_rows
    if seated:
        for k in range(-1, 3):  # the lap and thighs, forward
            p(cx + facing * k, ly, pants)
        for k in range(1, leg_rows + 1):  # shins hanging down
            p(cx + facing * 2, ly + k, pants)
        p(cx + facing * 2, ly + leg_rows + 1, shoes)
        p(cx + facing * 3, ly + leg_rows + 1, shoes)
        return hands
    if kneel:  # hips, then one knee forward and the other shin folded back
        for dx in (-1, 0, 1):
            p(cx + dx, ly, pants)
        p(cx + facing, ly + 1, pants)
        p(cx + 2 * facing, ly + 1, pants)
        p(cx - facing, ly + 1, pants)
        p(cx - 2 * facing, ly + 1, shoes)
        return hands
    for dy in range(leg_rows):
        if dy == 0:
            for dx in (-1, 0, 1):
                p(cx + dx, ly, pants)
            continue
        spread = 1 if (legs and dy >= leg_rows - 1) else 0
        p(cx - 1 - spread, ly + dy, pants)
        p(cx + 1 + spread, ly + dy, pants)
    spread = 1 if legs else 0
    p(cx - 1 - spread, ly + leg_rows, shoes)
    p(cx + 1 + spread, ly + leg_rows, shoes)
    return hands
