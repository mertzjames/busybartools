"""App-local Juneteenth drawing helpers: the palette, skies, glows, caption backing, the Juneteenth flag and simple
faceless figures. Everything is seeded or a pure function of the frame number, so builds are byte-identical.

These build on the shared render kit (busybar.canvas / busybar.party) and stay in this app until another app needs
them (repo R2). person() and dim_rect() are adapted from Kwanzaa's kfx.py; draw_flag()'s whole-row waving follows
Presidents' Day's pfx.draw_flag (docs/DECISIONS.md D5, D7).
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put

# --- palette (linear colors; the build's tone curve lifts them) ------------------------------------------------

FLAG_BLUE = (28, 58, 176)
FLAG_BLUE_DK = (18, 38, 128)
FLAG_RED = (204, 26, 42)
FLAG_RED_DK = (150, 16, 30)
WHITE = (246, 244, 240)
CREAM = (250, 236, 200)
GOLD = (255, 196, 60)
GOLD_LIGHT = (255, 234, 150)
NAVY = (10, 14, 46)
GRASS = (40, 120, 46)
GRASS_DK = (24, 82, 32)
GRASS_HI = (80, 168, 64)
WOOD = (120, 72, 40)
WOOD_DK = (84, 48, 28)
WOOD_HI = (164, 104, 60)

# A range of warm skin tones, all lit (no near-black), for faceless figures (docs/DECISIONS.md D6)
SKIN = ((110, 64, 40), (140, 86, 54), (170, 112, 72), (196, 140, 96), (124, 74, 46), (156, 100, 64))
# Hair: lit dark browns and a warm black-brown that still shows on the LEDs
HAIR = ((84, 52, 36), (70, 44, 32), (100, 64, 42), (60, 40, 34))


def sky(stops, quant: int = 0) -> Image.Image:
    """A 72x16 vertical gradient through `stops` [(row, color), ...]. quant > 0 rounds each channel to that step."""
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
        if quant:
            c = tuple(int(v // quant * quant) for v in c)
        for x in range(W):
            px[x, y] = tuple(c) + (255,)
    return img


def qmix(a, b, t: float, steps: int = 40):
    """mix() with t quantized to `steps` levels: slow light changes stay cheap in the .anim (few changed frames)."""
    return mix(a, b, math.floor(max(0.0, min(1.0, t)) * steps + 0.5) / steps)


def glow(img, cx: float, cy: float, r: float, color, a: float, squash: float = 1.0) -> None:
    """Additive radial glow. Keep `a` steady from frame to frame: per-frame flicker bloats the .anim."""
    for y in range(max(0, int(cy - r / squash) - 1), min(H, int(cy + r / squash) + 2)):
        for x in range(max(0, int(cx - r) - 1), min(W, int(cx + r) + 2)):
            d = math.hypot(x - cx, (y - cy) * squash)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float = 0.45, feather: int = 2) -> None:
    """Darken a box (inclusive) behind a caption, fading out over `feather` px around it."""
    if k <= 0:
        return
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


def caption(img, text: str, y: int, style, font: str = "big", alpha: float = 1.0, x: int | None = None) -> None:
    """Baked caption text, centered unless x is given: style = (top, bottom, shadow)."""
    from busybar.font import draw_text, text_width
    if alpha <= 0:
        return
    xx = (W - text_width(text, font)) // 2 if x is None else x
    draw_text(img, text, xx, y, None, font=font, gradient=(style[0], style[1]), shadow=style[2], alpha=alpha)


# --- the Juneteenth flag -----------------------------------------------------------------------------------------
#
# The official design: a white five-point star inside a white outlined twelve-ray "nova" (a new star), centered on
# a field split by an arc that spans the width of the flag (a new horizon): blue above, red below. Pixel versions
# for two sizes, drawn by hand so the burst reads as spikes and not a blob (docs/DECISIONS.md D5).

NOVA_11 = """
..N.NNN.N..
..NNN.NNN..
NNN.....NNN
.N...S...N.
NN...S...NN
N..SSSSS..N
NN..SSS..NN
.N..S.S..N.
NNN.....NNN
..NNN.NNN..
..N.NNN.N..
"""

NOVA_3 = """
.N.
NNN
.N.
"""

NOVA_5 = """
N.N.N
.NSN.
NSSSN
.NSN.
N.N.N
"""


def _grid(s: str) -> list[str]:
    return [r for r in s.strip().splitlines()]


_NOVAS = {11: _grid(NOVA_11), 5: _grid(NOVA_5), 3: _grid(NOVA_3)}


def flag_cell(u: int, v: int, fw: int, fh: int, nova: int = 11, field_only: bool = False):
    """Color of flag cell (u, v) for a fw x fh flag: the arc horizon (blue over red), the star and the nova.
    Returns None for the emblem's pixels when field_only (draw_flag places the emblem as one piece)."""
    if not field_only and emblem_cell(u, v, fw, fh, nova):
        return WHITE
    # the arc: a broad, low curve across the whole width, through the lower part of the nova (a new horizon)
    mid = (fw - 1) / 2
    peak = fh * 0.56
    edge = fh * 0.8
    arc = peak + (edge - peak) * ((u - mid) / mid) ** 2
    return FLAG_BLUE if v < arc else FLAG_RED


def emblem_cell(u: int, v: int, fw: int, fh: int, nova: int = 11) -> bool:
    """True where the white star or nova covers flag cell (u, v). The emblem is centered on the flag."""
    g = _NOVAS[nova]
    gu, gv = u - (fw - nova) // 2, v - (fh - nova) // 2
    return 0 <= gu < nova and 0 <= gv < nova and g[gv][gu] in "NS"


def draw_flag(img, x0: int, y0: int, fw: int, fh: int, t: float, amp: float = 1.0, wavelength: float = 22.0,
              unfurl: float = 1.0, alpha: float = 1.0, nova: int = 11, clip=None) -> None:
    """The Juneteenth flag with its hoist at column x0 and top at row y0, waving away from the pole.

    Each column shifts by a WHOLE number of rows (fractional shifts would blur white into pink and blue) and is
    shaded by the wave's slope. The star and nova ride the cloth as one piece, shifted by the wave at the flag's
    center, so they never shear apart (docs/DECISIONS.md D5). `t` is the wave phase in cycles (accumulate
    1/period per frame). `unfurl` (0..1) shortens the fly end. `clip` = (x0, x1) draws only those screen columns.
    """
    n = max(1, int(fw * unfurl + 0.5))

    def wave(u: int):
        k = u / max(1, fw - 1)
        ph = 2 * math.pi * (u / wavelength - t)
        return int(math.floor(amp * k * math.sin(ph) + 0.5)), 1.0 + 0.22 * math.cos(ph) * (0.3 + 0.7 * k)

    edy, _ = wave(fw // 2)
    for u in range(n):
        xx = x0 + u
        if clip and not (clip[0] <= xx <= clip[1]):
            continue
        dy, shade = wave(u)
        for v in range(fh):
            c = flag_cell(u, v, fw, fh, nova, field_only=True)
            c = tuple(max(0, min(255, int(ch * shade))) for ch in c)
            put(img, xx, y0 + v + dy, c, alpha)
        for v in range(fh):
            if emblem_cell(u, v, fw, fh, nova):
                c = tuple(max(0, min(255, int(ch * min(1.0, shade + 0.1)))) for ch in WHITE)
                put(img, xx, y0 + v + edy, c, alpha)


def pole(img, x: int, top: int, bottom: int = H - 1, color=(176, 150, 100)) -> None:
    """A flagpole (brass, so it shows against sky and grass) with a gold ball finial."""
    for y in range(top + 1, bottom + 1):
        put(img, x, y, color)
    put(img, x, top, GOLD_LIGHT)


# --- people ----------------------------------------------------------------------------------------------------

def person(img, x: int, feet: int, skin, shirt, pants=None, hair=None, style: str = "short", arms=(0.0, 0.0),
           legs: int = 0, height: int = 11, alpha: float = 1.0, seated: bool = False, dress: bool = False,
           hat=None) -> dict:
    """A simple faceless standing figure, 5 px wide at the shoulders, centered on column x+2, feet on row `feet`.

    style (hair): "short" (a cap of hair), "puff" (a rounded afro, one row taller), "buns" (two puffs), "long"
    (hair down the sides), "bald", "wrap" (a headwrap in `hat` color), "cap" (a ball cap in `hat` color) or
    "brim" (a wide-brim hat in `hat` color). arms: (left, right) angles in turns: 0 = down, 0.25 = out, 0.5 = up.
    legs: 0 together, 1 apart, 2 mid-stride (alternate with 1 to walk). seated: waist up only. dress: a skirt.
    Returns the hand positions {"l": (x, y), "r": (x, y)}.
    Faces are plain skin: a 3x3 head has no room for lit eyes, and dark pixels would read as holes (D6).
    """
    hair = hair or HAIR[0]
    pants = pants or shirt
    cx = x + 2
    top = feet - height + 1
    head_y = top + 1
    for dy in range(3):  # head
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue
            put(img, cx + dx, head_y + dy, skin, alpha)
    if style in ("short", "puff", "long", "buns"):
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 1, hair, alpha)
        put(img, cx - 1, head_y, hair, alpha)
        put(img, cx + 1, head_y, hair, alpha)
        if style == "puff":
            for dx in (-2, -1, 0, 1, 2):
                put(img, cx + dx, head_y - 1 if abs(dx) < 2 else head_y, hair, alpha)
            for dx in (-1, 0, 1):
                put(img, cx + dx, head_y - 2, hair, alpha)
        elif style == "long":
            put(img, cx - 2, head_y + 1, hair, alpha)
            put(img, cx + 2, head_y + 1, hair, alpha)
            put(img, cx - 2, head_y + 2, hair, alpha)
            put(img, cx + 2, head_y + 2, hair, alpha)
        elif style == "buns":
            put(img, cx - 2, head_y - 2, hair, alpha)
            put(img, cx + 2, head_y - 2, hair, alpha)
    elif style == "wrap":
        c = hat or (230, 150, 40)
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 1, c, alpha)
            put(img, cx + dx, head_y - 2, mix(c, (255, 255, 255), 0.2) if dx == 0 else c, alpha)
        put(img, cx + 2, head_y - 2, c, alpha)
    elif style == "cap":
        c = hat or FLAG_RED
        for dx in (-1, 0, 1, 2):
            put(img, cx + dx, head_y - 1 if dx < 2 else head_y, c, alpha)
    elif style == "brim":
        c = hat or (150, 110, 70)
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 2, c, alpha)
        for dx in (-2, -1, 0, 1, 2):
            put(img, cx + dx, head_y - 1, mix(c, (0, 0, 0), 0.15) if abs(dx) == 2 else c, alpha)
    body_top = head_y + 3
    body_rows = 4 if height >= 11 else 3
    for dy in range(body_rows):
        for dx in (-1, 0, 1):
            put(img, cx + dx, body_top + dy, shirt, alpha)
    if dress:
        for dx in (-2, 2):
            put(img, cx + dx, body_top + body_rows - 1, shirt, alpha)
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        sx = cx - 2 if side == "l" else cx + 2
        sgn = -1 if side == "l" else 1
        a = 2 * math.pi * ang
        hx, hy = float(sx), float(body_top)
        for k in range(3):
            hx = sx + sgn * math.sin(a) * k
            hy = body_top + math.cos(a) * k
            put(img, hx, hy, shirt if k == 0 else skin, alpha)
        hands[side] = (int(math.floor(hx + 0.5)), int(math.floor(hy + 0.5)))
    if seated:
        return hands
    leg_top = body_top + body_rows
    leg_rows = feet - leg_top + 1
    for dy in range(leg_rows):
        last = dy == leg_rows - 1
        spread = 1 if (legs == 1 and dy >= leg_rows - 2) else 0
        if dress and dy < leg_rows - 1:
            for dx in (-2, -1, 0, 1, 2) if dy == 0 else (-1, 0, 1):
                put(img, cx + dx, leg_top + dy, shirt if dy == 0 else mix(shirt, (0, 0, 0), 0.12), alpha)
            continue
        if not last:
            if legs == 2 and dy >= leg_rows - 2:  # mid-stride: one leg forward
                put(img, cx - 1, leg_top + dy, pants, alpha)
                put(img, cx + 1 + (dy - leg_rows + 3), leg_top + dy, pants, alpha)
            else:
                put(img, cx - 1 - spread, leg_top + dy, pants, alpha)
                put(img, cx + 1 + spread, leg_top + dy, pants, alpha)
                if dy < leg_rows - 2 and not spread:
                    put(img, cx, leg_top + dy, pants, alpha)
        else:  # shoes: a lit dark brown
            shoe = (92, 60, 44)
            if legs == 2:
                put(img, cx - 1, leg_top + dy, shoe, alpha)
                put(img, cx + 2, leg_top + dy, shoe, alpha)
            else:
                put(img, cx - 1 - spread, leg_top + dy, shoe, alpha)
                put(img, cx + 1 + spread, leg_top + dy, shoe, alpha)
    return hands
