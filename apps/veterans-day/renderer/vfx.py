"""App-local drawing helpers for Veterans Day: the calm palette, skies, flags, poppies, people in plain uniforms and
captions. Everything is seeded or a pure function of the frame number, so builds are byte-identical.

Tribute rules (docs/DECISIONS.md D2, D3): calm and warm, never festive; no insignia, seals, branch emblems or medals;
uniforms are plain colors with no patches; no likenesses of real people; nothing that depicts combat or weapons.

Pieces adapted from sibling holiday apps (app-local copies, so their renders never change): the flag and poppy from
Memorial Day's mdfx.py, the person from Mother's Day's mfx.py (extended with caps and gloves), dim_rect from Kwanzaa.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put
from busybar.font import draw_text, text_width

# --- palette ----------------------------------------------------------------------------------------------------

NAVY = (36, 52, 128)
RED = (196, 38, 50)
WHITE = (236, 234, 226)
STAR = (230, 232, 244)
GOLD = (255, 200, 96)
GOLD_LIGHT = (255, 232, 168)
BRASS = (200, 168, 104)
POPPY = (220, 40, 36)
POPPY_DEEP = (156, 24, 30)
POPPY_EYE = (110, 60, 128)  # a lit violet, not black (black is an unlit LED)
STEM = (56, 112, 54)

# plain uniform colors (no patches, no insignia)
U_NAVY = (52, 70, 150)
U_OLIVE = (104, 118, 66)
U_TAN = (186, 160, 110)
U_BLUEGREY = (96, 120, 160)
U_WHITE = (238, 238, 232)
U_DARK = (40, 48, 92)  # trousers / cap bands: a lit dark blue, never near-black

SKIN = ((112, 66, 42), (148, 94, 58), (184, 124, 80), (214, 162, 114), (238, 194, 156))
HAIR_DARK = (96, 60, 42)
HAIR_BROWN = (140, 86, 46)
HAIR_AUBURN = (176, 76, 42)
HAIR_BLOND = (232, 190, 96)
HAIR_GREY = (196, 196, 208)
HAIR_SILVER = (226, 226, 234)


# --- skies and light --------------------------------------------------------------------------------------------

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


def darken(img, k: float) -> None:
    """Darken the whole frame by k (0..1)."""
    if k <= 0:
        return
    px = img.load()
    for y in range(H):
        for x in range(W):
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - k)), int(g * (1 - k)), int(b * (1 - k)), a)


def grid(img, x: int, y: int, rows, pal: dict, alpha: float = 1.0) -> None:
    """Draw a text-grid sprite: each character maps to a color in `pal`; '.' and ' ' are transparent."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            c = pal.get(ch)
            if c is not None:
                put(img, x + dx, y + dy, c, alpha)


def fill(img, x0: int, y0: int, x1: int, y1: int, c, a: float = 1.0) -> None:
    """Fill a box (inclusive corners)."""
    for y in range(max(0, y0), min(H, y1 + 1)):
        for x in range(max(0, x0), min(W, x1 + 1)):
            put(img, x, y, c, a)


# --- flags ------------------------------------------------------------------------------------------------------

def big_flag_color(u: int, v: int, fw: int, rows: int = 13):
    """The flag at full size (13 stripes, one row each) for a cloth fw wide: a canton over the top 7 stripes, about
    0.4 of the fly, with its stars as a dense checker of lit dots (sparse dots read as eyes)."""
    cw = int(fw * 0.4 + 0.5)
    if u < cw and v < 7:
        if 0 < u < cw - 1 and 0 < v < 6 and (u + v) % 2 == 0:
            return STAR
        return NAVY
    return RED if v % 2 == 0 else WHITE


def small_flag_color(u: int, v: int):
    """A small flag (7 rows: red at the top and bottom) with a 4 x 3 canton of lit dots."""
    if u < 4 and v < 3:
        return STAR if (u + v) % 2 == 1 else NAVY
    return RED if v % 2 == 0 else WHITE


def tiny_flag_color(u: int, v: int):
    """A hand flag, 5 x 3 or so: a navy corner with one lit star, then red and white stripes."""
    if u < 2 and v < 2:
        return STAR if (u, v) == (0, 0) else NAVY
    return RED if v % 2 == 0 else WHITE


def draw_flag(img, x0: int, y0: int, fw: int, fh: int, t: float, amp: float = 1.0, wavelength: float = 16.0,
              alpha: float = 1.0, color=small_flag_color, direction: int = 1, shade_levels: int = 0,
              shade_k: float = 0.22) -> None:
    """A flag fw x fh with its hoist at column x0 and top at row y0, waving away from the pole (direction +1 flies to
    the right, -1 to the left).

    Each column shifts by a whole number of rows (fractional shifts blur 1-row stripes into pink) and is shaded by
    the slope of the wave, so the cloth seems to ripple. `t` is the wave's phase in cycles; the hoist never moves.
    shade_levels > 0 quantizes the shading (fewer changed pixels per frame, a smaller .anim).
    """
    for u in range(fw):
        k = u / max(1, fw - 1)
        ph = 2 * math.pi * (u / wavelength - t)
        dy = int(math.floor(amp * k * math.sin(ph) + 0.5))
        s = math.cos(ph) * (0.25 + 0.75 * k)
        if shade_levels:
            s = math.floor(s * shade_levels + 0.5) / shade_levels
        shade = 1.0 + shade_k * s
        for v in range(fh):
            c = tuple(max(0, min(255, int(ch * shade))) for ch in color(u, v))
            put(img, x0 + direction * u, y0 + v + dy, c, alpha)


def pole(img, x: int, top: int, bottom: int = H - 1, color=BRASS, finial=GOLD_LIGHT) -> None:
    """A flagpole with a pale gold ball finial (lit, so it reads against the sky)."""
    for y in range(top + 1, bottom + 1):
        put(img, x, y, color)
    put(img, x, top, finial)


# --- poppies ----------------------------------------------------------------------------------------------------

def poppy(img, x: int, y: int, size: int, a: float = 1.0, petal=POPPY, deep=POPPY_DEEP, halo=None) -> None:
    """A poppy head centred at (x, y): size 1 is a dot, 2 a small cup, 3 a flower with a violet eye, 4 a large one
    (5 x 4, for the nearest row). `halo` draws a 1 px dark ring first, so neighbours don't merge into blobs."""
    if size >= 4:
        rows = (".RRR.", "RRERR", "RDRDR", ".DDD.")
        if halo:
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
    if halo:
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                if abs(dx) + abs(dy) <= 3 and (abs(dx) == 2 or abs(dy) == 2):
                    put(img, x + dx, y + dy, halo, a)
    for dx, dy, c in ((-1, 0, petal), (1, 0, petal), (0, -1, petal), (-1, -1, deep), (1, -1, deep),
                      (0, 1, deep), (-1, 1, deep), (1, 1, deep)):
        put(img, x + dx, y + dy, c, a)
    put(img, x, y, POPPY_EYE, a)


def bud(img, x: int, y: int, a: float = 1.0) -> None:
    """A closed poppy bud: a green drop with a red tip."""
    put(img, x, y, (92, 150, 70), a)
    put(img, x, y - 1, (190, 60, 50), a)


# --- people -----------------------------------------------------------------------------------------------------

def person(img, x: int, feet: int, skin, shirt, legs_c, hair, style: str = "short", hat: str | None = None,
           hat_c=None, hat_c2=None, arms=(0.0, 0.0), legs: int = 0, child: bool = False, skirt: bool = False,
           seated: bool = False, alpha: float = 1.0, shoes=None, gloves=None, buttons=None, back: bool = False,
           salute: float = 0.0, sleeve=None) -> dict:
    """A simple front-facing figure, 3 px wide at the body, centered on column x, feet on row `feet`.

    Adults are 12 rows tall (hair or cap 1, head 3, body 4, legs 3, feet 1), children 9. style: "short", "long"
    (hair to the shoulders), "bun", "puff" or "pony". hat: None, "garrison" (a plain soft cap), "peaked" (a dress cap:
    a wide crown in `hat_c` over a band in `hat_c2`) or "ball" (a cap with a brim to one side). arms: (left, right)
    angles in turns, 0 = down, 0.25 = straight out, 0.5 = straight up. legs: 0 together, 1 apart (a step).
    seated: waist up only. gloves: hand color (white gloves read on a dark uniform). buttons: a lit column down the
    jacket's center. back: seen from behind (the head is all hair or cap; no face). salute: 0..1 raises the right
    hand (viewer's left) from the side to the brow.
    Faces are plain skin: a 3x3 head has no room for lit eyes, and dark pixels would read as holes.
    Returns the hand positions {"l": (x, y), "r": (x, y)} and the head's top row.
    """
    body_rows = 3 if child else 4
    leg_rows = 1 if child else 3
    height = 1 + 3 + body_rows + leg_rows + 1
    top = feet - height + 1
    head = top + 1
    cx = x
    hands_c = gloves or skin
    sleeve = sleeve or shirt
    if style == "long" and not hat:
        for dy in range(1, 5):
            put(img, cx - 2, head + dy, hair, alpha)
            put(img, cx + 2, head + dy, hair, alpha)
    # head (the back of the head is hair)
    for dy in range(3):
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue  # chin / neck
            c = hair if back and dy < 2 else skin
            put(img, cx + dx, head + dy, c, alpha)
    # hair and headwear
    if hat == "peaked":
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, top - 1, hat_c, alpha)
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hat_c2, alpha)
    elif hat == "garrison":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hat_c, alpha)
        put(img, cx - 1, top - 1, hat_c, alpha)
        put(img, cx, top - 1, mix(hat_c, (255, 255, 255), 0.12), alpha)
        put(img, cx - 1, head, hair, alpha)
        put(img, cx + 1, head, hair, alpha)
    elif hat == "ball":
        for dx in (-1, 0, 1):
            put(img, cx + dx, top, hat_c, alpha)
        put(img, cx, top - 1, hat_c, alpha)
        if not back:
            for dx in (-1, 0, 1, 2):
                put(img, cx + dx, head, hat_c2 or hat_c, alpha)
        else:
            put(img, cx - 1, head + 1, hair, alpha)
            put(img, cx + 1, head + 1, hair, alpha)
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
    if buttons:
        for dy in range(0, body_rows, 2):
            put(img, cx, body + dy, buttons, alpha)
    # arms
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        if side == "l" and salute > 0:
            continue
        sgn = -1 if side == "l" else 1
        sx = cx + 2 * sgn
        a = 2 * math.pi * ang
        n = 3 if not child else 2
        hx, hy = float(sx), float(body)
        for k in range(n):
            hx = sx + sgn * math.sin(a) * k
            hy = body + math.cos(a) * k
            put(img, hx, hy, sleeve if k < n - 1 else hands_c, alpha)
        hands[side] = (int(math.floor(hx + 0.5)), int(math.floor(hy + 0.5)))
    if salute > 0:
        hands["l"] = _salute_arm(img, cx, head, body, salute, sleeve, hands_c, alpha)
    hands["top"] = top
    if seated:
        return hands
    shoes = shoes or mix(legs_c, (0, 0, 0), 0.35)
    leg_top = body + body_rows
    spread = 1 if legs == 1 else 0
    for dy in range(leg_rows):
        y = leg_top + dy
        if skirt:
            w = 1 if dy == 0 else 2
            for dx in range(-w, w + 1):
                put(img, cx + dx, y, legs_c, alpha)
        else:
            s = spread if dy == leg_rows - 1 else 0
            put(img, cx - 1 - s, y, legs_c, alpha)
            put(img, cx + 1 + s, y, legs_c, alpha)
            if dy == 0:
                put(img, cx, y, legs_c, alpha)
    fy = leg_top + leg_rows
    put(img, cx - 1 - spread, fy, shoes, alpha)
    put(img, cx + 1 + spread, fy, shoes, alpha)
    return hands


# the right arm (viewer's left) from hanging at the side to a salute, in four poses: (x offset, row offset, part)
# rows are relative to the head's top row; "s" = sleeve, "h" = hand
_SALUTE = [
    [(-2, 3, "s"), (-2, 4, "s"), (-2, 5, "h")],                  # at the side
    [(-2, 3, "s"), (-3, 4, "s"), (-3, 3, "h")],                  # rising, elbow out
    [(-2, 3, "s"), (-3, 3, "s"), (-3, 2, "s"), (-2, 1, "h")],    # nearly there
    [(-2, 3, "s"), (-3, 3, "s"), (-3, 2, "s"), (-2, 1, "s"), (-1, 0, "h")],  # the salute: fingers at the brow
]


def _salute_arm(img, cx: int, head: int, body: int, p: float, sleeve, hand, alpha: float):
    pose = _SALUTE[min(len(_SALUTE) - 1, int(p * (len(_SALUTE) - 1) + 0.5))]
    for dx, dy, part in pose:
        put(img, cx + dx, head + dy, sleeve if part == "s" else hand, alpha)
    dx, dy, _ = pose[-1]
    return (cx + dx, head + dy)


# --- town -------------------------------------------------------------------------------------------------------

BRICK = (150, 66, 52)
BRICK_HI = (176, 86, 66)
CREAM = (214, 196, 160)
SAGE = (110, 140, 120)
SLATE = (96, 104, 136)
TRIM = (232, 226, 210)
WINDOW = (255, 214, 140)
WINDOW_DIM = (176, 140, 96)
GLASS = (58, 76, 96)
SIDEWALK = (150, 146, 140)
STREET = (70, 72, 84)


def storefront(img, x0: int, w: int, top: int, wall, awning=None, base: int = 13, alpha: float = 1.0,
               lit: float = 1.0) -> None:
    """A two-storey small-town storefront from column x0, w wide, roof at row `top`, ground at row `base`: a pale
    cornice, a row of small upper windows, an awning in two alternating colors (if given), and a calm blue-grey shop
    window with a warm display line, so people walking past in light clothes stand out against it."""
    trim = mix(wall, TRIM, 0.55)
    for y in range(top, base + 1):
        for x in range(x0, x0 + w):
            put(img, x, y, wall, alpha)
    for x in range(x0, x0 + w):
        put(img, x, top, trim, alpha)
    win = mix(WINDOW_DIM, WINDOW, lit)
    for x in range(x0 + 2, x0 + w - 2, 4):  # upper windows, 2 x 1
        put(img, x, top + 2, win, alpha)
        put(img, x + 1, top + 2, win, alpha)
    ground = base - 4
    if awning:
        for x in range(x0 + 1, x0 + w - 1):
            put(img, x, ground, awning[(x - x0) // 2 % 2], alpha)
    door = mix(wall, (40, 30, 30), 0.45)
    for y in range(ground + 1, base + 1):
        for x in range(x0 + 1, x0 + w - 4):
            if y < base - 1:
                put(img, x, y, GLASS, alpha)
            elif y == base - 1:
                put(img, x, y, mix(GLASS, win, 0.7), alpha)
        put(img, x0 + w - 3, y, door, alpha)
        put(img, x0 + w - 2, y, door, alpha)


def lamppost(img, x: int, top: int, base: int = 14, color=(70, 84, 110), light=(255, 226, 160)) -> None:
    for y in range(top + 1, base + 1):
        put(img, x, y, color)
    put(img, x, top, light)
    put(img, x - 1, top, mix(light, color, 0.5))
    put(img, x + 1, top, mix(light, color, 0.5))


def leaf(img, x: float, y: float, f: int, color, alpha: float = 1.0) -> None:
    """A drifting autumn leaf: one pixel, with a dimmer second pixel that flips side as it tumbles."""
    put(img, x, y, color, alpha)
    side = 1 if (f // 4) % 2 else -1
    put(img, x + side, y, mix(color, (0, 0, 0), 0.35), 0.7 * alpha)


# --- captions ---------------------------------------------------------------------------------------------------

CAPTION_GRAD = ((255, 246, 226), (238, 206, 150))
CAPTION_SHADOW = (24, 22, 58)


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
