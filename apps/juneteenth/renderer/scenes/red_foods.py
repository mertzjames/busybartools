"""Scene: red drinks and red foods (docs/DECISIONS.md D3, D9).

Red is the traditional color of the Juneteenth table, often said to stand for resilience. On a blue-and-white
gingham cloth under a blue sky (so the reds never sit on red, nor the green rinds on green): strawberry soda
poured into a glass with rising bubbles, a whole watermelon cut into wedges, a red velvet cake with a slice drawn
out, and a bowl of strawberries. Then the table dims behind RED FOR / RESILIENCE.
"""

import math

from busybar.canvas import H, W, add, ease_in_out, ease_out, phase, put, sec

import jfx
from scenes.text import RED, RED_BOTTOM, RED_TOP, STARLIGHT, look

NAME = "red_foods"
TITLE = "Red Drinks and Red Foods"
SECONDS = 14
KEYFRAMES = [(1.8, "Strawberry soda poured over ice"), (4.6, "A whole watermelon"),
             (6.8, "Cut into wedges"), (9.6, "Red velvet cake: a slice drawn out"), (12.8, "RED FOR / RESILIENCE")]

CLOTH = 11  # first tablecloth row
SODA = (230, 34, 64)
SODA_HI = (255, 96, 120)
GLASS = (190, 226, 236)
FLESH = (236, 46, 60)
FLESH_HI = (255, 110, 110)
RIND = (60, 156, 64)
RIND_DK = (36, 110, 46)
SEED = (70, 34, 30)  # a lit deep brown: reads as a seed, not a hole
VELVET = (176, 26, 46)
VELVET_HI = (206, 46, 64)
FROST = (250, 242, 230)


def backdrop():
    img = jfx.sky([(0, (96, 150, 222)), (6, (128, 174, 230)), (10, (160, 196, 236))])
    for y in range(CLOTH, H):  # blue-and-white gingham
        for x in range(W):
            a, b = (x // 2) % 2, ((y - CLOTH) // 2) % 2
            c = (54, 84, 186) if a and b else ((236, 236, 244) if not a and not b else (148, 160, 218))
            put(img, x, y, c)
    return img


def soda(img, f) -> None:
    """A strawberry soda bottle and a glass that fills from a pour above (0.5-3.5 s), with bubbles."""
    # the bottle: red cap, glass neck, red soda body with a white label
    bx = 3
    put(img, bx + 1, 1, (210, 30, 40))
    put(img, bx + 2, 1, (210, 30, 40))
    for y in range(2, 5):
        put(img, bx + 1, y, GLASS)
        put(img, bx + 2, y, mix_soda(0.4))
    for y in range(5, CLOTH + 1):
        for dx in range(4):
            c = SODA if 0 < dx < 3 else (200, 120, 140)
            if y == 7 and 0 < dx < 3:
                c = FROST
            if dx == 1 and y != 7:
                c = SODA_HI
            put(img, bx + dx, y, c)
    # the glass: 5 wide, rows 5-11; level rises with the pour
    gx, top, bot = 10, 5, CLOTH
    level = ease_in_out(phase(f, sec(0.6), sec(3.4)))
    surface = bot - level * (bot - top - 1)
    for y in range(top, bot + 1):
        for dx in range(5):
            edge = dx in (0, 4) or y == bot
            if edge:
                put(img, gx + dx, y, (226, 244, 250))
            elif y >= surface:
                put(img, gx + dx, y, SODA_HI if y <= surface + 0.5 else SODA)
            else:
                put(img, gx + dx, y, GLASS, 0.18)
    # ice cubes floating once the glass is full
    if level > 0.6:
        put(img, gx + 1, math.ceil(surface), (220, 240, 250), 0.8)
        put(img, gx + 3, math.ceil(surface) + 1, (220, 240, 250), 0.6)
    # the pour: a red stream from above
    if 0 < level < 1 and f < sec(3.4):
        for y in range(0, int(surface)):
            put(img, gx + 2, y, SODA)
        add(img, gx + 2, int(surface), (255, 200, 210), 0.6)
    # bubbles rising in the glass (and the bottle)
    for k in range(5):
        per = 20 + 3 * k
        age = (f + k * 7) % per
        y = bot - 1 - age * 0.35
        if y > surface + 0.5 and level > 0.15:
            put(img, gx + 1 + (k % 3), y, (255, 190, 200), 0.8)
        yb = CLOTH - 1 - ((f + k * 5) % 18) * 0.35
        if yb > 5 and yb != 7:
            put(img, bx + 2, yb, (255, 170, 186), 0.6)
    # a straw drops in when the glass is full
    straw = phase(f, sec(3.6), sec(4.2))
    if straw > 0:
        for y in range(int(2 + (1 - straw) * -4), int(surface) + 2):
            if y >= 0:
                put(img, gx + 3 + (1 if y < 4 else 0), y, (250, 250, 250) if (y // 2) % 2 else (230, 60, 80))


def mix_soda(k: float):
    return tuple(int(GLASS[i] + (SODA[i] - GLASS[i]) * k) for i in range(3))


def melon(img, f) -> None:
    """A whole striped watermelon (until 5.4 s), then three wedges standing on their rinds."""
    cx, cy = 29, 8
    cut = phase(f, sec(5.2), sec(5.6))
    if cut <= 0:
        for y in range(4, CLOTH + 1):
            for x in range(cx - 8, cx + 9):
                d = math.hypot((x - cx) / 8.4, (y - cy) / 4.0)
                if d < 1:
                    stripe = (x + (y // 2)) % 4 < 2
                    put(img, x, y, (96, 180, 80) if stripe else RIND_DK)
        add(img, cx - 4, 5, (255, 255, 255), 0.35)
        add(img, cx - 3, 5, (255, 255, 255), 0.25)
        # the knife glint sweeps down just before the cut
        glint = phase(f, sec(4.4), sec(5.2))
        if glint > 0:
            y = 2 + glint * 9
            for dx in (-1, 0, 1):
                add(img, cx + dx, y, (255, 255, 255), 0.8 - 0.25 * abs(dx))
        return
    spread = ease_out(phase(f, sec(5.3), sec(6.4)))
    for i, dxc in enumerate((-9, 0, 9)):
        wx = cx + dxc * (0.5 + 0.5 * spread)
        wedge(img, round(wx), CLOTH - 5, i)


def wedge(img, cx: int, top: int, i: int) -> None:
    """A watermelon slice: a half-disc with its flat cut face up, red flesh with seeds, a pale rind line and a green
    rind along the curve."""
    r = 4.0
    for y in range(top, top + 6):
        for x in range(cx - 5, cx + 6):
            d = math.hypot(x - cx, (y - top + 0.5) * 1.0)
            if d > r + 0.2:
                continue
            if d > r - 0.9:
                c = RIND if y > top else RIND_DK
            elif d > r - 1.7:
                c = (200, 236, 170)
            else:
                c = FLESH_HI if y == top else FLESH
            put(img, x, y, c)
    for sx, sy in ((-2, 1), (0, 2), (2, 1), (-1, 3) if i % 2 else (1, 3)):
        put(img, cx + sx, top + sy, SEED)


def cake(img, f) -> None:
    """A red velvet layer cake on a stand; a slice slides out to the right from 8 s."""
    x0, x1, top = 44, 56, 4
    stand = CLOTH
    for x in range(x0 - 1, x1 + 2):
        put(img, x, stand, (230, 230, 236))
    put(img, (x0 + x1) // 2, stand - 1, (210, 210, 220))
    layers = {top: FROST, top + 1: VELVET_HI, top + 2: VELVET, top + 3: FROST, top + 4: VELVET_HI, top + 5: VELVET,
              top + 6: FROST}
    out = ease_in_out(phase(f, sec(8.0), sec(9.6)))
    gap = (x1 - 3, x1)  # the slice's columns, once cut
    shift = round(out * 2)
    for y, c in layers.items():
        for x in range(x0, x1 + 1):
            if out > 0 and gap[0] <= x <= gap[1]:
                continue
            cc = c
            if c != FROST and x == x0:
                cc = VELVET
            put(img, x, y, cc)
        # the cut face of the cake (the slice's hole shows the layers)
        if out > 0:
            put(img, gap[0] - 1, y, c)
    # crumbs of red on the frosting top
    for x in range(x0 + 1, x1, 3):
        if not (out > 0 and gap[0] <= x <= gap[1]):
            put(img, x, top, (220, 90, 100))
    if out > 0:  # the slice, on its own plate, moving right
        sx = gap[0] + shift
        for x in range(sx - 1, sx + 6):
            put(img, x, stand, (236, 236, 242))
        for y, c in layers.items():
            for dx in range(4):
                put(img, sx + dx, y + 1 if y < top + 6 else y, c if dx else (c if c == FROST else VELVET_HI))
    # sparkles on the frosting
    k = 0.5 + 0.5 * math.sin(f * 0.5)
    add(img, x0 + 3, top, (255, 255, 255), 0.4 * k)


def strawberries(img, f) -> None:
    """A white bowl of strawberries on the right."""
    for x in range(62, 71):
        put(img, x, CLOTH - 1, (236, 236, 244))
        put(img, x, CLOTH, (210, 210, 224))
    put(img, 61, CLOTH - 2, (236, 236, 244))
    put(img, 71, CLOTH - 2, (236, 236, 244))
    for i, (x, y) in enumerate(((62, 8), (64, 8), (66, 8), (68, 8), (63, 7), (65, 6), (67, 7), (69, 8))):
        put(img, x, y, (230, 30, 50))
        put(img, x + 1, y, (210, 24, 44))
        put(img, x, y + 1, (190, 20, 40))
        put(img, x + 1, y - 1 if i % 2 else y - 1, (70, 170, 60))
        if (f // 6 + i) % 5 == 0:
            add(img, x, y, (255, 230, 120), 0.5)


def render():
    bg = backdrop()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        soda(img, f)
        melon(img, f)
        cake(img, f)
        strawberries(img, f)
        t = phase(f, sec(11.0), sec(12.0))
        if t > 0:
            jfx.dim_rect(img, 0, 0, W - 1, H - 1, 0.62 * t, feather=0)
            jfx.caption(img, RED_TOP, 0, look(RED), alpha=t)
            jfx.caption(img, RED_BOTTOM, 8, look(STARLIGHT), alpha=phase(f, sec(11.5), sec(12.5)))
        frames.append(img)
    return frames
