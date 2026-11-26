"""App-local drawing helpers for MLK Day (docs/DECISIONS.md D3, D5): the dawn sky, the sun, people of every age and
skin tone drawn as small figures, raised arms, captions. Everything is seeded or a pure function of the frame
number, so builds are byte-identical.

Tribute rules (D2): calm, warm colors; no likeness of any real person (figures are generic and faceless); no
quotations; no party effects.
"""

from __future__ import annotations

import math

from PIL import Image

from busybar.canvas import H, W, add, mix, put
from busybar.font import draw_text, text_width

# --- palette --------------------------------------------------------------------------------------------------

GOLD = (255, 196, 80)
GOLD_LIGHT = (255, 236, 170)
WARM_WHITE = (255, 244, 220)
DEEP_BLUE = (30, 44, 120)
NIGHT = (4, 6, 26)

# A range of skin tones, lightest to deepest. The deepest stay lit on the panel (black is an unlit LED) and get a
# warm rim light from the sun, so every figure reads against the sky (D5).
SKIN = [(255, 222, 190), (238, 190, 150), (212, 156, 112), (178, 118, 78), (146, 92, 60), (118, 74, 50)]
HAIR = [(120, 84, 60), (150, 104, 62), (206, 206, 216), (184, 118, 60), (232, 200, 120), (96, 76, 88)]
TOPS = [(74, 96, 176), (156, 62, 74), (60, 134, 124), (192, 150, 62), (116, 116, 140), (104, 136, 72),
        (172, 100, 144), (206, 206, 218)]
BOTTOMS = [(84, 96, 156), (140, 112, 84), (116, 116, 136), (84, 126, 134)]

# --- the dawn sky ---------------------------------------------------------------------------------------------

# (progress, top, middle, horizon): night, blue hour, first light, sunrise.
DAWN = [
    (0.0, (4, 6, 26), (12, 14, 46), (30, 22, 60)),
    (0.35, (8, 14, 48), (22, 26, 76), (46, 40, 96)),
    (0.7, (16, 28, 84), (34, 42, 104), (66, 60, 124)),
    (1.0, (26, 46, 120), (44, 60, 132), (84, 78, 140)),
]


def dawn_stops(p: float):
    p = max(0.0, min(1.0, p))
    for (p0, *a), (p1, *b) in zip(DAWN, DAWN[1:]):
        if p <= p1:
            k = (p - p0) / (p1 - p0)
            return tuple(mix(a[i], b[i], k) for i in range(3))
    return tuple(DAWN[-1][1:])


def sky(p: float, horizon: int = 13) -> Image.Image:
    """A 72x16 dawn sky at progress p (0 night .. 1 sunrise), brightest at row `horizon`."""
    top, mid, low = dawn_stops(p)
    img = Image.new("RGBA", (W, H))
    px = img.load()
    half = horizon * 0.5
    for y in range(H):
        if y <= half:
            c = mix(top, mid, y / half)
        else:
            c = mix(mid, low, min(1.0, (y - half) / max(1.0, horizon - half)))
        for x in range(W):
            px[x, y] = c + (255,)
    return img


def sun(img, cx: float, cy: float, r: float, strength: float = 1.0) -> None:
    """The rising sun: a soft halo, then a gold disc with a pale core."""
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, (y - cy) * 1.1)
            if d <= r:
                c = mix(GOLD_LIGHT, GOLD, d / max(0.5, r))
                put(img, x, y, c, strength)
            elif d <= r + 14:
                add(img, x, y, (255, 140, 60), 0.5 * strength * (1 - (d - r) / 14) ** 2)


def glow(img, cx: float, cy: float, r: float, color, a: float) -> None:
    """Additive radial glow."""
    for y in range(H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                add(img, x, y, color, a * (1 - d / r) ** 2)


def mix_light(p: float, x: int, sun_x: float = 60):
    """Color of the horizon line: dusky violet at night, gold near the sun at sunrise."""
    near = max(0.0, 1 - abs(x - sun_x) / 28)
    return mix((40, 32, 70), (255, 170, 90), p * (0.25 + 0.75 * near))


def ground(img, y0: int, top=(40, 30, 50), bottom=(22, 18, 34)) -> None:
    for y in range(y0, H):
        c = mix(top, bottom, (y - y0) / max(1, H - 1 - y0))
        for x in range(W):
            put(img, x, y, c)


# --- people ---------------------------------------------------------------------------------------------------

class Person:
    """A small generic figure facing right. kind: adult (10 px), teen (9), child (7), elder (9, cane),
    carrier (an adult with a child on the shoulders, 15 px). No faces: just a head, clothes and a gait."""

    HEIGHTS = {"adult": 10, "teen": 9, "child": 7, "elder": 9, "carrier": 10}

    def __init__(self, kind: str, skin, hair, top, bottom, child=None):
        self.kind, self.skin, self.hair, self.top, self.bottom = kind, skin, hair, top, bottom
        self.child = child  # (skin, hair, top) for a carrier
        self.h = self.HEIGHTS[kind]

    def hand(self, x: int, feet: int):
        """Front-hand pixel (x, y) at rest, used to join hands with the person ahead."""
        return x + 3, feet - (3 if self.kind == "child" else 5)

    def back_hand(self, x: int, feet: int):
        return x - 1 + (1 if self.kind == "child" else 0), feet - (3 if self.kind == "child" else 5)

    def draw(self, img, x: int, feet: int, stride: bool, swing: int = 0, front_hand=True) -> None:
        T = feet - self.h + 1
        P = lambda dx, dy, c: put(img, x + dx, T + dy, c)  # noqa: E731
        child = self.kind == "child"
        torso = 3 if child else (3 if self.kind in ("teen", "elder") else 4)
        # head: hair on top, skin below (the figures have no faces)
        P(1, 0, self.hair)
        P(2, 0, self.hair)
        P(1, 1, self.hair if self.kind != "child" else self.skin)
        P(2, 1, self.skin)
        if self.kind == "elder":  # a slight stoop: the head sits one column forward
            P(1, 1, self.skin)
        # torso
        x0 = 1 if child else 0
        for dy in range(2, 2 + torso):
            for dx in range(x0, 3):
                P(dx, dy, self.top)
        # front hand swings a little with the stride
        hy = 2 + torso - 1 + (0 if child else 0)
        if front_hand and self.kind != "carrier":
            P(3, hy - (1 if (stride and swing) else 0), self.skin)
        # legs
        leg = 2 + torso
        n = self.h - leg
        for i in range(n):
            if stride and i >= n // 2:
                P(0 if not child else 1, leg + i, self.bottom)
                P(3, leg + i, self.bottom)
            else:
                P(1, leg + i, self.bottom)
                P(2, leg + i, self.bottom)
        if self.kind == "elder":  # cane from the hand to the ground
            for dy in range(hy + 1, self.h):
                P(4, dy, (176, 134, 88))
            P(3, hy, self.skin)
        if self.kind == "carrier" and self.child:
            cs, ch, ct = self.child
            # the child's legs hang either side of the parent's head; the parent's hands hold them
            P(0, 0, ct)
            P(3, 0, ct)
            P(0, -1, ct)
            P(3, -1, ct)
            P(3, 1, self.skin)
            for dx in (1, 2):
                P(dx, -1, ct)
                P(dx, -2, ct)
            P(1, -3, ch)
            P(2, -3, cs)
            P(1, -4, ch)
            P(2, -4, ch)


def rim_light(layer: Image.Image, color, a: float) -> None:
    """Warm sun rim on the right edge of every figure in a transparent layer (light comes from the right)."""
    if a <= 0:
        return
    px = layer.load()
    edge = [(x, y) for y in range(layer.height) for x in range(layer.width)
            if px[x, y][3] and (x + 1 >= layer.width or not px[x + 1, y][3])]
    for x, y in edge:
        r, g, b, al = px[x, y]
        px[x, y] = (min(255, int(r + color[0] * a)), min(255, int(g + color[1] * a)),
                    min(255, int(b + color[2] * a)), al)


def join_hands(img, a: tuple, b: tuple, ca, cb) -> None:
    """A clasped-hands link between hand pixel a (left person) and b (right person)."""
    (x0, y0), (x1, y1) = a, b
    n = max(1, x1 - x0)
    for i in range(n + 1):
        t = i / n
        put(img, x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, ca if t < 0.5 else cb)


# --- captions -------------------------------------------------------------------------------------------------

CAPTION_GRAD = ((255, 240, 200), (255, 184, 80))
CAPTION_SHADOW = (40, 34, 96)


def caption(img, text: str, y: int, alpha: float, font: str = "big", x: int | None = None, back=True,
            grad=CAPTION_GRAD, shadow=CAPTION_SHADOW) -> None:
    """A single word, faded in slowly; the background behind it dims first so it stays legible (D6)."""
    if alpha <= 0:
        return
    w = text_width(text, font)
    x = (W - w) // 2 if x is None else x
    h = 7 if font == "big" else 5
    if back:
        for yy in range(y - 1, y + h + 2):
            for xx in range(x - 2, x + w + 3):
                put(img, xx, yy, (8, 10, 34), 0.55 * alpha)
    draw_text(img, text, x, y, None, font=font, gradient=grad, shadow=shadow, alpha=alpha)


def shade(layer: Image.Image, k: float) -> None:
    """Darken every pixel of a figure layer (backlit by the sunrise), keeping them lit."""
    px = layer.load()
    for y in range(layer.height):
        for x in range(layer.width):
            r, g, b, a = px[x, y]
            if a:
                px[x, y] = (int(r * k + 0.5), int(g * k + 0.5), int(b * k + 0.5), a)
