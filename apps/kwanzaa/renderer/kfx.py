"""App-local Kwanzaa props and effects: the kinara and its candles, the mkeka (mat), muhindi (corn), the kikombe
cha umoja (unity cup), a fruit basket, an original kente-inspired weave, and simple people.

Everything is seeded or a pure function of the frame number, so builds are byte-identical. These build on the
shared render kit (busybar.canvas / busybar.party) and stay in this app until another app needs them (repo R2).

Black is an unlit LED (AGENTS.md): the black candle is a lit charcoal grey with a highlight, and the "black" in the
weave is the same charcoal, so neither reads as a hole (docs/DECISIONS.md D5).
"""

from __future__ import annotations

import math

from busybar.canvas import add, mix, put
from busybar.party import hash01

# --- palette (linear colors; the build's tone curve lifts them) ------------------------------------------------

RED = (206, 30, 34)
RED_HI = (255, 96, 84)
RED_DK = (140, 18, 22)
GREEN = (26, 150, 58)
GREEN_HI = (96, 214, 112)
GREEN_DK = (14, 96, 36)
CHARCOAL = (64, 62, 72)  # the black candle: lit, so it reads as a candle and not a hole
CHARCOAL_HI = (138, 136, 150)
CHARCOAL_DK = (44, 42, 50)
GOLD = (255, 192, 46)
GOLD_HI = (255, 236, 150)
GOLD_DK = (196, 128, 24)
WOOD = (112, 50, 28)
WOOD_HI = (164, 86, 46)
WOOD_DK = (78, 34, 20)
STRAW = (196, 150, 78)
STRAW_DK = (150, 104, 48)
FLAME = ((255, 250, 210), (255, 220, 90), (255, 150, 30), (230, 80, 20))  # tip .. base

# A range of warm skin tones, all lit (no near-black), for simple figures (docs/DECISIONS.md D8)
SKIN = ((112, 66, 42), (146, 92, 58), (178, 120, 78), (206, 152, 104), (128, 80, 50))

# Room backdrop: a warm, dark, lit brown (never black, so the scene reads as a room)
ROOM_TOP = (26, 10, 8)
ROOM_BOTTOM = (44, 20, 12)


# --- the kinara ------------------------------------------------------------------------------------------------

# Candle positions, left to right: three red, the black in the center, three green (the official placement).
CANDLE_COLORS = ("red", "red", "red", "black", "green", "green", "green")

# Lighting orders by day: candle positions, day 1 first. Both light the black candle (Umoja) first and then alternate
# red and green, starting with red; they differ in where each color starts (docs/DECISIONS.md D3, D14).
#   position: 0=R Kujichagulia  1=R Ujamaa  2=R Kuumba  3=B Umoja  4=G Ujima  5=G Nia  6=G Imani
# "official": the official Kwanzaa website's "from left to right": the reds outer, middle, inner and the greens inner,
#             middle, outer (each candle on its own principle's day). The default.
# "center_out": outward from the center: the red next to the black, the green next to it, then the middle pair, then
#             the outer pair.
LIGHT_ORDERS = {
    "official": (3, 0, 4, 1, 5, 2, 6),
    "center_out": (3, 2, 4, 1, 5, 0, 6),
}
DEFAULT_ORDER = "official"
LIGHT_ORDER = LIGHT_ORDERS[DEFAULT_ORDER]

for _o in LIGHT_ORDERS.values():  # each is a permutation: black first, then red, green, red, green, ...
    assert sorted(_o) == list(range(7)) and _o[0] == 3
    assert [CANDLE_COLORS[p] for p in _o[1:]] == ["red", "green"] * 3

_SHADES = {
    "red": (RED, RED_HI, RED_DK),
    "black": (CHARCOAL, CHARCOAL_HI, CHARCOAL_DK),
    "green": (GREEN, GREEN_HI, GREEN_DK),
}


class Kinara:
    """A kinara with seven candles, centered on cx, standing on row `base` (its foot).

    big:   candles 2 px wide, 4 px apart (26 px across), side candles 6 rows, the center one raised by 1.
    small: candles 1 px wide, 2 px apart (13 px across), 3 rows (for the karamu table).
    """

    def __init__(self, cx: int, base: int, small: bool = False):
        self.cx, self.base, self.small = cx, base, small
        if small:
            self.cw, self.step, self.h = 1, 2, 3
            self.x0 = cx - 6
            self.bar_y = base - 1
        else:
            self.cw, self.step, self.h = 2, 4, 6
            self.x0 = cx - 13
            self.bar_y = base - 2

    def candle_x(self, i: int) -> int:
        return self.x0 + i * self.step

    def candle_top(self, i: int) -> int:
        cup = self.bar_y - (0 if self.small else 1)
        raise_ = 1 if i == 3 else 0
        return cup - self.h - raise_

    def wick(self, i: int) -> tuple[float, int]:
        """(x, y) just above candle i's top, where the flame sits (x is the candle's center)."""
        return self.candle_x(i) + (self.cw - 1) / 2, self.candle_top(i) - 1

    def draw(self, img, f: int, lit=(), glow: float = 1.0, ignite: dict | None = None) -> None:
        """lit: candle positions with a flame. ignite: {position: age_frames} for flames still catching."""
        ignite = ignite or {}
        self._body(img)
        for i in range(7):
            self._candle(img, i)
        for i in range(7):
            if i in lit:
                age = ignite.get(i)
                grow = 1.0 if age is None else min(1.0, age / 6)
                self.flame(img, i, f, grow * glow)
            else:  # an unlit wick: a lit, dim grey-brown pixel
                x, y = self.wick(i)
                put(img, round(x - 0.01), y, (96, 84, 72), 0.8)

    def _body(self, img) -> None:
        if self.small:
            x0, x1 = self.x0 - 1, self.x0 + 6 * self.step + 1
            for x in range(x0, x1 + 1):
                put(img, x, self.bar_y, WOOD_HI if x % 3 else WOOD)
            put(img, self.cx, self.base, WOOD_DK)
            put(img, self.cx - 1, self.base, WOOD_DK)
            put(img, self.cx + 1, self.base, WOOD_DK)
            return
        x0, x1 = self.x0 - 2, self.x0 + 6 * self.step + self.cw + 1
        # the bar: two rows, a carved highlight on top
        for x in range(x0, x1 + 1):
            put(img, x, self.bar_y, WOOD_HI if (x - x0) % 4 else WOOD)
            put(img, x, self.bar_y + 1, WOOD_DK if x in (x0, x1) else WOOD)
        # the raised center block under the black candle
        cxl = self.candle_x(3)
        for x in range(cxl - 1, cxl + 3):
            put(img, x, self.bar_y - 1, WOOD_HI)
        # the foot
        for x in range(self.cx - 6, self.cx + 6):
            put(img, x, self.base, WOOD_DK if x in (self.cx - 6, self.cx + 5) else WOOD)
        # candle cups (gold rims)
        for i in range(7):
            x = self.candle_x(i)
            y = self.bar_y - (2 if i == 3 else 1)
            for dx in (-1, 0, 1, 2):
                put(img, x + dx, y, GOLD_DK if dx in (-1, 2) else GOLD)

    def _candle(self, img, i: int) -> None:
        base, hi, dk = _SHADES[CANDLE_COLORS[i]]
        x = self.candle_x(i)
        top = self.candle_top(i)
        bottom = top + self.h - 1
        for y in range(top, bottom + 1):
            if self.cw == 1:
                put(img, x, y, hi if y == top else base)
            else:
                put(img, x, y, hi)  # highlight down the left edge
                put(img, x + 1, y, base if y > top else mix(base, hi, 0.5))
        if self.cw == 2 and CANDLE_COLORS[i] == "black":
            put(img, x + 1, bottom, dk)

    def flame(self, img, i: int, f: int, k: float = 1.0) -> None:
        """A flickering flame over candle i, with a warm glow (k scales size and brightness)."""
        if k <= 0:
            return
        x, y = self.wick(i)
        flick = hash01(i, f // 2)
        sway = 0 if flick < 0.6 else (1 if flick < 0.8 else -1)
        if self.small:
            put(img, round(x), y, FLAME[1], k)
            if k > 0.5:
                add(img, round(x), y - 1, FLAME[0], 0.5 * k * (0.6 + 0.4 * flick))
            for dx, dy in ((-1, 0), (1, 0), (0, 1)):
                add(img, round(x) + dx, y + dy, (120, 60, 10), 0.35 * k)
            return
        xl = int(x)  # left column of the 2 px candle
        tip = 0 if sway < 0 else 1
        # a teardrop: 2 px orange base, 2 px yellow body, 1 px white tip that sways (and sometimes stretches)
        put(img, xl, y, FLAME[3], k)
        put(img, xl + 1, y, FLAME[2], k)
        put(img, xl, y - 1, FLAME[1], k)
        put(img, xl + 1, y - 1, FLAME[1], k)
        put(img, xl + tip, y - 2, FLAME[0], k)
        if k > 0.7 and flick > 0.55:
            put(img, xl + tip, y - 3, FLAME[1], 0.55 * k)
        # glow around the flame
        for dx in range(-2, 4):
            for dy in range(-4, 2):
                d = math.hypot(dx - 0.5, (dy + 1) * 0.8)
                if 1.3 < d < 3.4:
                    add(img, xl + dx, y + dy, (90, 40, 6), 0.42 * k * (1 - (d - 1.3) / 2.1))


def room_glow(img, kin: Kinara, lit, f: int, strength: float = 1.0) -> None:
    """Warm ambient light from the lit candles across the room (cheap: per column, falling off with distance)."""
    if not lit:
        return
    n = len(lit)
    xs = [kin.wick(i)[0] for i in lit]
    flick = 0.9 + 0.1 * hash01(77, f // 3)
    for x in range(img.width):
        d = min(abs(x - xx) for xx in xs)
        k = strength * flick * (0.02 + 0.012 * n) * max(0.0, 1 - d / 30)
        if k <= 0.004:
            continue
        for y in range(img.height):
            add(img, x, y, (120, 60, 20), k * (1.0 - 0.5 * y / img.height))


# --- the mkeka and the weave -------------------------------------------------------------------------------------

def mkeka(img, y: int, rows: int = 2, offset: int = 0) -> None:
    """A woven straw mat along the bottom, with red, green and charcoal stripes."""
    stripes = {0: RED, 1: STRAW, 2: STRAW, 3: GREEN, 4: STRAW, 5: STRAW, 6: CHARCOAL, 7: STRAW, 8: STRAW}
    for x in range(img.width):
        c = stripes[(x + offset) % 9]
        for r in range(rows):
            yy = y + r
            cc = c if c != STRAW else (STRAW if (x + yy) % 2 else STRAW_DK)
            put(img, x, yy, cc if r == 0 else mix(cc, (0, 0, 0), 0.25))


# Original kente-inspired strip motifs (docs/DECISIONS.md D9): 8 columns wide, 16 rows tall, using only
# red (R), charcoal (K), green (G) and gold (Y). Letters per pixel; each strip repeats down the cloth.
KENTE_MOTIFS = (
    # gold ground with stacked red and green bars and charcoal ticks
    """
YYYYYYYY
YRRRRRRY
YYYYYYYY
GKGKGKGK
YYYYYYYY
YRRRRRRY
YYYYYYYY
KKYYYYKK
KKYGGYKK
KKYYYYKK
YYYYYYYY
YRRRRRRY
YYYYYYYY
GKGKGKGK
YYYYYYYY
YRRRRRRY
""",
    # green ground with a gold zigzag and red diamonds
    """
GGGYYGGG
GGYYYYGG
GYYRRYYG
YYRRRRYY
GYYRRYYG
GGYYYYGG
GGGYYGGG
KKKKKKKK
YYYYYYYY
KKKKKKKK
GGGYYGGG
GGYYYYGG
GYYRRYYG
YYRRRRYY
GYYRRYYG
GGYYYYGG
""",
    # red ground with gold ladders and charcoal blocks
    """
RRRRRRRR
RYRRRRYR
RYYYYYYR
RYRRRRYR
RRRRRRRR
KKRRRRKK
KKRYYRKK
KKRRRRKK
RRRRRRRR
RYRRRRYR
RYYYYYYR
RYRRRRYR
RRRRRRRR
GGGGGGGG
YGYGYGYG
GGGGGGGG
""",
)
KENTE_COLORS = {"R": RED, "K": CHARCOAL, "G": GREEN, "Y": GOLD}


def kente_cell(x: int, y: int, strip_w: int = 8) -> tuple:
    """The weave color at cloth position (x, y): strips of the motifs side by side, with a thin gold seam."""
    s = (x // strip_w) % len(KENTE_MOTIFS)
    rows = [r.strip() for r in KENTE_MOTIFS[s].strip().splitlines()]
    ch = rows[y % len(rows)][x % strip_w]
    c = KENTE_COLORS[ch]
    # a subtle over-under texture: alternate pixels a touch darker
    if (x + y) % 2:
        c = mix(c, (0, 0, 0), 0.12)
    return c


def kente_border(img, y: int, offset: int = 0, alpha: float = 1.0) -> None:
    """One row of kente-colored stripes (for card borders)."""
    seq = (GOLD, GOLD, RED, RED, GOLD, GREEN, GREEN, GOLD, CHARCOAL_HI, CHARCOAL, GOLD, RED)
    for x in range(img.width):
        put(img, x, y, seq[(x + offset) % len(seq)], alpha)


# --- harvest props ---------------------------------------------------------------------------------------------

def corn(img, x: int, top: int, h: int = 6, lean: int = 0, alpha: float = 1.0) -> None:
    """An ear of corn (muhindi), 3 px wide, kernels on top and husk leaves at the bottom. lean: -1/0/1."""
    for r in range(h):
        yy = top + r
        dx = round(lean * (h - 1 - r) / max(1, h - 1))
        husk = r >= h - 2
        for c in range(3):
            if r == 0 and c != 1:
                continue
            if husk:
                col = (130, 176, 70) if (c + r) % 2 else (176, 162, 82)
            else:
                col = GOLD_HI if (c + r) % 2 == 0 else (236, 176, 40)
            put(img, x + c + dx, yy, col, alpha)
    # husk leaves flaring out at the bottom
    put(img, x - 1, top + h - 1, (130, 176, 70), alpha)
    put(img, x + 3, top + h - 1, (150, 168, 76), alpha)


def corn_lying(img, x: int, y: int, length: int = 6, flip: bool = False, alpha: float = 1.0) -> None:
    """An ear of corn lying on its side, 2 rows tall: kernels, then the husk flaring at one end."""
    for i in range(length):
        xx = x + (length - 1 - i if flip else i)
        husk = i >= length - 2
        for r in range(2):
            if husk:
                col = (130, 176, 70) if (i + r) % 2 else (176, 162, 82)
            else:
                col = GOLD_HI if (i + r) % 2 == 0 else (236, 176, 40)
            if i == 0 and r == 0:
                col = (236, 176, 40)
            put(img, xx, y + r, col, alpha)
    end = x - 1 if flip else x + length
    put(img, end, y, (110, 160, 60), alpha)  # the husk tip


def unity_cup(img, cx: int, base: int, shine: float = 0.0, fill: float = 0.0, alpha: float = 1.0) -> None:
    """The kikombe cha umoja: a gold goblet standing on row `base` (5 px wide bowl, 6 rows tall)."""
    rows = [(-2, 2), (-2, 2), (-1, 1), (0, 0), (0, 0), (-2, 2)]  # bowl, bowl, bowl bottom, stem, stem, foot
    top = base - len(rows) + 1
    for r, (a, b) in enumerate(rows):
        for dx in range(a, b + 1):
            c = GOLD if dx > a else GOLD_HI
            if dx == b and r < 3:
                c = GOLD_DK
            put(img, cx + dx, top + r, c, alpha)
    if fill > 0:  # liquid at the rim
        put(img, cx - 1, top, (150, 40, 60), alpha * fill)
        put(img, cx, top, (170, 50, 70), alpha * fill)
        put(img, cx + 1, top, (150, 40, 60), alpha * fill)
    if shine > 0:
        add(img, cx - 2, top, (255, 255, 230), 0.8 * shine * alpha)
        add(img, cx - 1, top + 1, (255, 255, 230), 0.4 * shine * alpha)


def basket(img, x: int, y: int, w: int = 14, h: int = 4) -> None:
    """A woven basket, top-left corner at (x, y), tapering at the bottom."""
    for r in range(h):
        inset = 1 if r == h - 1 else 0
        for c in range(inset, w - inset):
            col = STRAW if (c + r) % 2 else STRAW_DK
            if r == 0:
                col = (214, 170, 96)
            put(img, x + c, y + r, col)


FRUITS = {
    "orange": ((255, 140, 26), (255, 196, 90)),
    "apple": ((214, 34, 40), (255, 110, 100)),
    "lime": ((90, 190, 50), (170, 236, 110)),
    "yam": ((176, 92, 46), (214, 132, 78)),
    "plum": ((150, 50, 150), (210, 110, 200)),
}


def fruit(img, kind: str, x: float, y: float, alpha: float = 1.0) -> None:
    """A 2x2 fruit (yam 3x2, banana 3x1 curve), top-left at (x, y)."""
    if kind == "banana":
        put(img, x, y, (250, 220, 60), alpha)
        put(img, x + 1, y + 1, (250, 220, 60), alpha)
        put(img, x + 2, y + 1, (250, 232, 100), alpha)
        put(img, x + 3, y, (196, 170, 40), alpha)
        return
    base, hi = FRUITS[kind]
    w = 3 if kind == "yam" else 2
    for dx in range(w):
        for dy in range(2):
            put(img, x + dx, y + dy, hi if (dx, dy) == (0, 0) else base, alpha)


# --- people ----------------------------------------------------------------------------------------------------

def person(img, x: int, feet: int, skin, cloth, cloth2, head: str = "wrap", wrap=None, arms=(0.0, 0.0),
           legs: int = 0, height: int = 11, alpha: float = 1.0, seated: bool = False) -> dict:
    """A simple standing figure, 5 px wide at the shoulders, centered on column x+2, feet on row `feet`.

    head: "wrap" (a tall gele headwrap), "kufi" (a low cap) or "hair" (a lit dark-brown rounded top).
    arms: (left, right) angles in turns: 0 = hanging down, 0.25 = straight out, 0.5 = straight up.
    legs: 0 together, 1 apart, -1 crouched (one row shorter). seated: draw only from the waist up.
    Returns the hand positions {"l": (x, y), "r": (x, y)}.
    Faces are plain skin: no eyes (a 3x3 head has no room for lit eyes, and dark pixels would read as holes).
    """
    cx = x + 2
    crouch = 1 if legs == -1 else 0
    top = feet - height + 1 + crouch
    head_y = top + 2  # 2 rows of headwear above a 3-row head
    # head
    for dy in range(3):
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue  # chin
            put(img, cx + dx, head_y + dy, skin, alpha)
    given = wrap
    wrap = wrap or cloth2
    if head == "wrap":
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 1, wrap, alpha)
        for dx in (-1, 0, 1, 2):
            put(img, cx + dx, head_y - 2, mix(wrap, (255, 255, 255), 0.25) if dx == 0 else wrap, alpha)
    elif head == "kufi":
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 1, wrap if dx else GOLD, alpha)
    else:
        hair = given or (92, 58, 40)  # a lit dark brown by default, never near-black
        for dx in (-1, 0, 1):
            put(img, cx + dx, head_y - 1, hair, alpha)
        put(img, cx - 1, head_y, hair, alpha)
        put(img, cx + 1, head_y, hair, alpha)
    # body: a 3 px garment with a patterned band
    body_top = head_y + 3
    body_rows = 4
    for dy in range(body_rows):
        for dx in (-1, 0, 1):
            c = cloth2 if dy == 1 else cloth
            if dy == 1 and dx == 0:
                c = GOLD
            put(img, cx + dx, body_top + dy, c, alpha)
    hands = {}
    for side, ang in (("l", arms[0]), ("r", arms[1])):
        sx = cx - 2 if side == "l" else cx + 2
        sgn = -1 if side == "l" else 1
        a = 2 * math.pi * ang
        hx, hy = float(sx), float(body_top)
        for k in range(3):
            hx = sx + sgn * math.sin(a) * k
            hy = body_top + math.cos(a) * k
            put(img, hx, hy, cloth if k == 0 else skin, alpha)
        hands[side] = (round(hx), round(hy))
    if seated:
        return hands
    # skirt / legs
    leg_top = body_top + body_rows
    leg_rows = feet - leg_top + 1
    for dy in range(leg_rows):
        spread = 1 if (legs == 1 and dy >= leg_rows - 2) else 0
        if dy < leg_rows - 1:
            for dx in (-1, 0, 1):
                put(img, cx + dx, leg_top + dy, cloth, alpha)
            if spread:
                put(img, cx - 2, leg_top + dy, cloth, alpha)
                put(img, cx + 2, leg_top + dy, cloth, alpha)
        else:  # feet
            put(img, cx - 1 - spread, leg_top + dy, skin, alpha)
            put(img, cx + 1 + spread, leg_top + dy, skin, alpha)
    return hands


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 0) -> None:
    """Darken the rectangle x0..x1, y0..y1 by k (0..1) so a caption reads over busy art. `feather` fades the
    darkening out over that many columns past x1."""
    if k <= 0:
        return
    px = img.load()
    for y in range(max(0, y0), min(img.height, y1 + 1)):
        for x in range(max(0, x0), min(img.width, x1 + feather + 1)):
            kk = k if x <= x1 else k * (1 - (x - x1) / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - kk)), int(g * (1 - kk)), int(b * (1 - kk)), a)
