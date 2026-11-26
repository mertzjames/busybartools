"""App-local drawing helpers for Labor Day: the palette, skies, glows, caption backing, workers (front, back and tiny
silhouettes), a tower crane, an I-beam, a tractor and bunting. Everything is seeded or a pure function of the frame
number, so builds are byte-identical.

Tone (docs/DECISIONS.md D2): a warm tribute to working people that opens into the end of summer. Generic workers
with a range of skin tones, no faces beyond plain skin, no real people, no union or company logos.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette (all lit enough for LEDs) --------------------------------------------------------------------------

WHITE = (250, 248, 240)
CREAM = (255, 236, 200)
GOLD = (255, 196, 60)
GOLD_LIGHT = (255, 236, 150)
SAFETY = (255, 206, 30)  # hard-hat yellow
SAFETY_DK = (206, 150, 20)
ORANGE = (255, 128, 30)  # hi-vis orange
ORANGE_DK = (200, 86, 20)
RED = (214, 36, 44)
RED_HI = (255, 96, 90)
RED_DK = (150, 22, 30)
NAVY = (36, 52, 130)
BLUE = (62, 110, 210)
BLUE_HI = (120, 170, 255)
DENIM = (70, 110, 196)
DENIM_DK = (50, 80, 150)
TEAL = (40, 180, 170)
TEAL_HI = (110, 224, 210)
GREEN = (60, 170, 70)
GREEN_HI = (130, 220, 100)
GREEN_DK = (28, 110, 44)
LEAF_DK = (22, 80, 36)
STEEL = (150, 160, 180)
STEEL_HI = (210, 216, 230)
GREY = (120, 124, 136)
TIRE = (66, 64, 74)  # lit charcoal: black would be an unlit LED
TIRE_HI = (110, 108, 120)
WOOD = (150, 92, 50)
WOOD_HI = (196, 132, 76)
WOOD_DK = (104, 62, 34)
STRAW = (236, 200, 110)
STRAW_DK = (196, 150, 70)
WHEAT = (230, 180, 66)
WHEAT_HI = (255, 222, 120)
WHEAT_DK = (176, 126, 44)
SAND = (232, 196, 136)
SAND_DK = (196, 156, 100)
PURPLE = (150, 90, 220)

# Skin tones, all lit (the darkest is still far from an unlit LED), darkest first.
SKIN = ((118, 70, 44), (150, 96, 60), (186, 126, 82), (216, 164, 116), (240, 196, 158))
# Hair: lit browns, auburn, blond and silver grey (never near-black: it would read as a hole).
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


def blend_stops(a, b, t: float):
    """Blend two gradient stop lists with the same rows (for slow sky changes; quantize t first)."""
    return [(ya, mix(ca, cb, t)) for (ya, ca), (_, cb) in zip(a, b)]


def quant(t: float, steps: int = 40) -> float:
    """Quantize a slow 0..1 change to `steps` levels, so a slow light change doesn't touch every frame."""
    return math.floor(max(0.0, min(1.0, t)) * steps + 0.5) / steps


def glow(img, cx: float, cy: float, r: float, color, a: float, squash: float = 1.0) -> None:
    """Additive radial glow (keep `a` steady from frame to frame: per-frame flicker bloats the .anim)."""
    for y in range(max(0, int(cy - r / squash) - 1), min(H, int(cy + r / squash) + 2)):
        for x in range(max(0, int(cx - r) - 1), min(W, int(cx + r) + 2)):
            d = math.hypot(x - cx, (y - cy) * squash)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def disc(img, cx: float, cy: float, r: float, c, a: float = 1.0) -> None:
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                put(img, x, y, c, a)


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


def grid(img, x: int, y: int, rows, pal: dict, alpha: float = 1.0) -> None:
    """Pixel art from text rows: each character is a palette key ('.' or ' ' is transparent)."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch in pal:
                put(img, x + dx, y + dy, pal[ch], alpha)


def shade(c, k: float):
    return tuple(max(0, min(255, int(v * k + 0.5))) for v in c[:3])


# --- workers ----------------------------------------------------------------------------------------------------

def person(img, x: int, feet: int, skin, shirt, legs_c, hair=HAIR_BROWN, hat: str = "", hat_c=SAFETY,
           arms=(0.0, 0.0), step: int = 0, vest=None, apron=None, alpha: float = 1.0, shoes=None,
           seated: bool = False) -> dict:
    """A simple front-facing worker, 3 px wide at the body, centered on column x, feet on row `feet`.

    12 rows tall: hat or hair 1, head 3, body 4, legs 3, feet 1 (a tall chef's toque adds 2 rows above).
    hat: "" (hair), "hard" (a hard hat with a brim), "cap" (a ball cap, brim to one side), "straw" (a wide straw
    hat), "toque" (a tall white chef's hat), "nurse" (a small white cap over the hair), "bun" (hair in a bun),
    "long" (hair to the shoulders). vest: a hi-vis vest color over the shirt (with a silver stripe); apron: an apron
    color down the front. arms: (left, right) angles in turns, 0 = down, 0.25 = straight out, 0.5 = straight up.
    step: 0 feet together, 1 or -1 a walking step (one foot forward, the body bobs up a row on 0).
    Faces are plain skin: a 3x3 head has no room for lit eyes, and dark pixels would read as holes.
    Returns the hand positions {"l": (x, y), "r": (x, y)} and the head's top row ("top").
    """
    top = feet - 11
    head = top + 1
    cx = x
    if hat == "long":
        for dy in range(1, 5):
            put(img, cx - 2, head + dy, hair, alpha)
            put(img, cx + 2, head + dy, hair, alpha)
    for dy in range(3):  # head (rounded chin)
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue
            put(img, cx + dx, head + dy, skin, alpha)
    if hat == "hard":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top - 1, hat_c, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, top, hat_c if abs(dx) < 2 else shade(hat_c, 0.8), alpha)
        put(img, cx, top - 1, mix(hat_c, WHITE, 0.45), alpha)  # a sheen on the crown
    elif hat == "cap":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hat_c, alpha)
        put(img, cx + 2, top, shade(hat_c, 0.8), alpha)  # the brim
        put(img, cx - 1, head, hair, alpha)
        put(img, cx + 1, head, hair, alpha)
    elif hat == "straw":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top - 1, STRAW, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, top, hat_c if abs(dx) < 2 else STRAW, alpha)  # hat_c is the band
    elif hat == "toque":
        for dy in (-2, -1, 0):
            for dx in (-1, 0, 1):
                put(img, cx + dx, top + dy, WHITE if dy < 0 or dx == 0 else (226, 226, 236), alpha)
        put(img, cx - 2, top - 2, WHITE, alpha)
        put(img, cx + 2, top - 2, WHITE, alpha)
    elif hat == "nurse":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, WHITE, alpha)
        put(img, cx, top - 1, WHITE, alpha)
        put(img, cx - 1, head, hair, alpha)
        put(img, cx + 1, head, hair, alpha)
    else:
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hair, alpha)
        put(img, cx - 1, head, hair, alpha)
        put(img, cx + 1, head, hair, alpha)
        if hat == "long":
            put(img, cx - 2, head, hair, alpha)
            put(img, cx + 2, head, hair, alpha)
        elif hat == "bun":
            put(img, cx, top - 1, mix(hair, WHITE, 0.15), alpha)
    body = head + 3
    for dy in range(4):
        for dx in (-1, 0, 1):
            c = shirt
            if vest is not None and dx != 0:
                c = vest
            if vest is not None and dy == 2:
                c = STEEL_HI if dx != 0 else shirt
            if apron is not None and dy >= 1 and dx == 0:
                c = apron
            put(img, cx + dx, body + dy, c, alpha)
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        sgn = -1 if side == "l" else 1
        sx = cx + 2 * sgn
        a = 2 * math.pi * ang
        hx, hy = float(sx), float(body)
        for k in range(3):
            hx = sx + sgn * math.sin(a) * k
            hy = body + math.cos(a) * k
            put(img, hx, hy, shirt if k == 0 else skin, alpha)
        hands[side] = (int(math.floor(hx + 0.5)), int(math.floor(hy + 0.5)))
    hands["top"] = top
    if seated:
        return hands
    shoes = shoes or shade(legs_c, 0.6)
    leg_top = body + 4
    for dy in range(3):
        y = leg_top + dy
        put(img, cx - 1, y, legs_c, alpha)
        put(img, cx + 1, y, legs_c, alpha)
        if dy == 0:
            put(img, cx, y, legs_c, alpha)
    fy = leg_top + 3
    if step == 0:
        put(img, cx - 1, fy, shoes, alpha)
        put(img, cx + 1, fy, shoes, alpha)
    else:  # one foot lifted (a row up), the other planted
        lift = -1 if step > 0 else 1
        put(img, cx + lift, fy - 1, shoes, alpha)
        put(img, cx - lift, fy, shoes, alpha)
    return hands


def back_view(img, x: int, top: int, skin, shirt, hair=HAIR_BROWN, hat: str = "", hat_c=SAFETY,
              alpha: float = 1.0) -> None:
    """A worker seen from behind (head and shoulders, 4-5 rows from `top`): no face, so it reads at any size.

    hat: "" (hair), "hard" (a hard hat), "cap" (a ball cap), "puff" (round curly hair)."""
    if hat == "hard":
        for dx in (-1, 0, 1):
            put(img, x + dx, top, hat_c, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, x + dx, top + 1, hat_c if abs(dx) < 2 else shade(hat_c, 0.8), alpha)
        put(img, x, top, mix(hat_c, WHITE, 0.45), alpha)
        for dx in (-1, 0, 1):
            put(img, x + dx, top + 2, hair if dx == 0 else skin, alpha)
    elif hat == "cap":
        for dx in (-1, 0, 1):
            put(img, x + dx, top, hat_c, alpha)
            put(img, x + dx, top + 1, hat_c if dx else shade(hat_c, 0.8), alpha)
        for dx in (-1, 0, 1):
            put(img, x + dx, top + 2, hair, alpha)
    elif hat == "puff":
        for dx in (-2, -1, 0, 1, 2):
            put(img, x + dx, top + (0 if abs(dx) < 2 else 1), hair, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, x + dx, top + 1, hair, alpha)
        for dx in (-1, 0, 1):
            put(img, x + dx, top + 2, hair, alpha)
    else:
        for dx in (-1, 0, 1):
            put(img, x + dx, top, hair, alpha)
            put(img, x + dx, top + 1, hair, alpha)
            put(img, x + dx, top + 2, hair if dx == 0 else skin, alpha)
    for dy in (3, 4):  # shoulders
        for dx in range(-3, 4):
            if dy == 3 and abs(dx) == 3:
                continue
            put(img, x + dx, top + dy, shirt if abs(dx) < 3 else shade(shirt, 0.8), alpha)


def ironworker(img, x: int, feet: int, hat_c, body_c, skin, arms: str = "down", alpha: float = 1.0) -> dict:
    """A tiny worker for wide shots: 5 rows (hard hat 1, head 1, body 2, legs 1). arms: "down", "up", "out", "weld"
    (both forward at chest height, toward +x). Returns the hand position at the end of the reach."""
    put(img, x - 1, feet - 4, hat_c, alpha)
    put(img, x, feet - 4, hat_c, alpha)
    put(img, x + 1, feet - 4, shade(hat_c, 0.8), alpha)
    put(img, x, feet - 5, mix(hat_c, WHITE, 0.3), alpha)
    put(img, x, feet - 3, skin, alpha)
    put(img, x, feet - 2, body_c, alpha)
    put(img, x, feet - 1, body_c, alpha)
    put(img, x - 1, feet, shade(body_c, 0.75), alpha)
    put(img, x + 1, feet, shade(body_c, 0.75), alpha)
    hand = (x, feet - 1)
    if arms == "up":
        put(img, x - 1, feet - 3, body_c, alpha)
        put(img, x + 1, feet - 3, body_c, alpha)
        put(img, x - 1, feet - 4, skin, alpha * 0.0)
        put(img, x + 1, feet - 5, skin, alpha)
        hand = (x + 1, feet - 5)
    elif arms == "out":
        put(img, x - 1, feet - 2, body_c, alpha)
        put(img, x + 1, feet - 2, body_c, alpha)
        put(img, x + 2, feet - 2, skin, alpha)
        hand = (x + 2, feet - 2)
    elif arms == "weld":
        put(img, x + 1, feet - 2, body_c, alpha)
        put(img, x + 2, feet - 2, STEEL_HI, alpha)  # the torch
        hand = (x + 3, feet - 2)
    return hand


# --- machines and structures -------------------------------------------------------------------------------------

def ibeam(img, x0: int, y: int, length: int, color, hi=None, alpha: float = 1.0) -> None:
    """A horizontal I-beam, 2 rows: a lit top flange over the web. `hi` brightens the top edge."""
    for dx in range(length):
        put(img, x0 + dx, y, hi or color, alpha)
        put(img, x0 + dx, y + 1, shade(color, 0.8) if 0 < dx < length - 1 else color, alpha)


def tower_crane(img, mast_x: int, top: int, jib_l: int, jib_r: int, color=SAFETY, base: int = H - 1) -> None:
    """A tower crane: a two-column lattice mast at mast_x..mast_x+1 from `base` up to the jib at row `top`, a cab,
    a counterweight on the short (left) jib and a peak with tie lines."""
    dk = shade(color, 0.7)
    for y in range(top + 1, base + 1):
        put(img, mast_x, y, color)
        put(img, mast_x + 1, y, dk if (y % 3) else color)
    for x in range(jib_l, jib_r + 1):  # the jib, with a lit lower chord every other column
        put(img, x, top, color)
        if x % 2 == 0 and x not in (mast_x, mast_x + 1):
            put(img, x, top + 1, dk, 0.7)
    for dx in range(3):  # counterweight block
        put(img, jib_l + dx, top + 1, (150, 150, 162))
        put(img, jib_l + dx, top + 2, (120, 120, 134))
    put(img, mast_x - 1, top + 1, (170, 210, 240))  # cab window
    put(img, mast_x - 1, top + 2, color)
    put(img, mast_x, top - 1, color)  # the peak and its ties
    put(img, mast_x, top - 2, color)
    line(img, mast_x, top - 2, jib_r - 6, top, dk, 0.55)
    line(img, mast_x, top - 2, jib_l + 1, top, dk, 0.55)


def tiny_flag(img, x: int, y: int, f: int = 0) -> None:
    """A 4x3 US flag on a 1 px pole at (x, y) = the pole's top; flutters by a pixel."""
    put(img, x, y, STEEL_HI)
    for dy in range(4):
        put(img, x, y + dy, (200, 200, 210))
    wave = (f // 4) % 2
    for dx in range(1, 5):
        for dy in range(3):
            yy = y + dy + (1 if (dx == 4 and wave) else 0)
            if dx <= 2 and dy == 0:
                c = (70, 100, 230)
            else:
                c = RED if (dy % 2 == 0) else WHITE
            put(img, x + dx, yy, c)


def evergreen(img, x: int, base: int, alpha: float = 1.0) -> None:
    """A little evergreen tree (topping-out tradition), 4 rows tall, trunk at row `base`."""
    put(img, x, base - 3, GREEN_HI, alpha)
    for dx in (-1, 0, 1):
        put(img, x + dx, base - 2, GREEN, alpha)
    for dx in (-1, 0, 1):
        put(img, x + dx, base - 1, GREEN_DK if dx else GREEN, alpha)
    put(img, x, base, WOOD, alpha)


def bunting(img, oy: float, colors=((54, 84, 200), WHITE, RED), period: int = 24, gold: bool = True) -> None:
    """Swags of red, white and blue cloth across the top, gold rosettes where they hang. `oy` = top row offset."""
    top = math.floor(oy + 0.5)
    for x in range(W):
        u = (x % period) / period
        depth = 1 + 2.2 * math.sin(math.pi * u) ** 0.8
        n = math.floor(depth + 0.5)
        for i in range(n + 1):
            k = min(2, int(3 * i / (n + 1)))
            put(img, x, top + i, colors[k])
    if gold:
        for x in range(0, W + 1, period):
            xx = min(x, W - 1)
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)):
                put(img, xx + dx, top + 1 + dy, GOLD if (dx, dy) != (0, 0) else GOLD_LIGHT)


def wheel(img, cx: float, cy: float, r: float, rot: float, tire=TIRE, hub=STEEL_HI) -> None:
    """A tractor wheel: a lit charcoal tire with tread notches that turn with `rot` (radians) and a silver hub."""
    for y in range(int(cy - r - 1), int(cy + r + 2)):
        for x in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(x - cx, y - cy)
            if d <= r + 0.2:
                c = tire
                if d > r - 1.0:
                    a = math.atan2(y - cy, x - cx) - rot
                    if math.cos(4 * a) > 0.3:
                        c = TIRE_HI
                put(img, x, y, c)
    put(img, cx, cy, hub)
    if r >= 2.5:
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            put(img, cx + dx, cy + dy, (220, 190, 60))  # a gold rim around the hub
