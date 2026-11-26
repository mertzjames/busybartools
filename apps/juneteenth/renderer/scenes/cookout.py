"""Scene: a family cookout in the park (docs/DECISIONS.md D3, D6).

A shade tree, red-white-and-blue bunting, a kettle grill with smoke rising and the cook flipping, a picnic table
with a checked cloth and food on it. Family sits at the table; two more arrive carrying a covered dish; two kids
play catch; and at the end everyone lifts a red cup. Faceless figures with a range of warm skin tones, in light
shirts so they read against the grass and the tree.
"""

import math

from busybar.canvas import H, W, add, ease_in_out, phase, put, sec
from busybar.fx import puff

import jfx

NAME = "cookout"
TITLE = "Family Cookout"
SECONDS = 16
KEYFRAMES = [(1.0, "A cookout in the park: smoke from the grill"), (5.0, "More family arrives with a dish"),
             (9.5, "The kids play catch"), (13.5, "Everyone lifts a red cup")]

GROUND = 14  # feet row
TABLE_Y = 10  # tabletop row
TABLE = (33, 61)
GRILL_X = 14


def backdrop():
    img = jfx.sky([(0, (88, 148, 222)), (7, (140, 190, 236)), (12, (186, 214, 236))])
    for x in range(W):  # distant hedge, then grass
        put(img, x, 11, (70, 130, 70) if (x // 3) % 2 else (60, 116, 62))
        put(img, x, 12, (56, 128, 54))
        for y in range(13, H):
            put(img, x, y, jfx.GRASS if (x + y) % 4 else jfx.GRASS_HI)
    # the shade tree: trunk and a round canopy with highlights
    for y in range(5, GROUND + 1):
        put(img, 4, y, jfx.WOOD)
        put(img, 5, y, jfx.WOOD_HI if y % 3 else jfx.WOOD)
    blobs = ((2.0, 3.0, 3.4), (7.0, 1.6, 3.0), (6.5, 5.0, 2.8), (10.0, 4.0, 2.2))
    for y in range(0, 9):
        for x in range(-2, 14):
            ds = [math.hypot(x - bx, y - by) / r for bx, by, r in blobs]
            d = min(ds)
            if d < 1:
                hi = d < 0.55 and (x + 2 * y) % 4 == 0 and y < 5
                shade = (x - 4) + (y - 3) * 1.5 > 4 or d > 0.8
                put(img, x, y, (104, 184, 76) if hi else ((40, 110, 42) if shade else (60, 146, 54)))
    return img


def bunting(img) -> None:
    """Red, white and blue pennants on a sagging line from the tree to the right edge."""
    x0, x1 = 12, W
    for x in range(x0, x1):
        u = (x - x0) / (x1 - x0)
        y = 0.6 + 2.2 * math.sin(math.pi * u)
        put(img, x, y, (230, 230, 220), 0.7)
        k = (x - x0) % 5
        if k < 3:
            c = (jfx.FLAG_RED, jfx.WHITE, jfx.FLAG_BLUE)[((x - x0) // 5) % 3]
            put(img, x, y + 1, c)
            if k == 1:
                put(img, x, y + 2, c)


def grill(img, f) -> None:
    gx = GRILL_X
    for x in range(gx - 2, gx + 3):  # the bowl (a lit charcoal grey) and the coals' glow at its rim
        put(img, x, 9, (96, 96, 108))
        put(img, x, 10, (80, 80, 92) if abs(x - gx) < 2 else (70, 70, 82))
    for x in range(gx - 1, gx + 2):
        put(img, x, 11, (70, 70, 82))
    for dx, y in ((-2, 12), (-2, 13), (2, 12), (2, 13), (0, 12), (0, 13)):
        put(img, gx + dx, y, (110, 110, 120))
    for x in range(gx - 2, gx + 3):  # the grate with food on it
        flick = (x * 5 + f // 3) % 7 < 2
        put(img, x, 8, (255, 120, 40) if flick else (200, 70, 30))
    put(img, gx - 1, 7, (176, 96, 52))
    put(img, gx + 1, 7, (150, 76, 42))
    # smoke: puffs rising and drifting right with the breeze (a pure function of f)
    for k in range(6):
        age = (f + k * 9) % 54
        a = 0.4 * (1 - age / 54)
        puff(img, gx + age * 0.22 + 0.6 * math.sin(age * 0.2 + k), 6 - age * 0.13, 0.6 + age * 0.03,
             (150, 150, 162), a * 1.6)


def table(img) -> None:
    x0, x1 = TABLE
    for x in range(x0, x1 + 1):
        put(img, x, TABLE_Y, jfx.FLAG_RED if (x // 2) % 2 else jfx.WHITE)
        if x in (x0, x1):
            put(img, x, TABLE_Y + 1, jfx.FLAG_RED if (x // 2) % 2 else jfx.WHITE)
    for x in (x0 + 3, x1 - 3):
        for y in range(TABLE_Y + 1, GROUND + 1):
            put(img, x, y, jfx.WOOD)
    for x in range(x0 + 1, x1):  # the bench, in front
        put(img, x, 12, jfx.WOOD_HI)


def food(img) -> None:
    """On the table: a watermelon slice, corn, a pitcher of strawberry drink, a plate of ribs, a pie."""
    # watermelon wedge
    for dx, c in ((0, (60, 150, 60)), (1, (230, 50, 60)), (2, (230, 50, 60)), (3, (60, 150, 60))):
        put(img, 36 + dx, 9, c)
    put(img, 37, 8, (230, 50, 60))
    put(img, 38, 8, (230, 50, 60))
    # corn
    put(img, 42, 9, (255, 214, 70))
    put(img, 43, 9, (255, 214, 70))
    put(img, 44, 9, (140, 190, 70))
    # pitcher of red drink
    for y in (7, 8, 9):
        put(img, 48, y, (230, 40, 56) if y > 7 else (240, 236, 230))
        put(img, 49, y, (210, 30, 46) if y > 7 else (240, 236, 230))
    put(img, 50, 8, (240, 236, 230))
    # ribs on a plate
    put(img, 53, 9, (240, 236, 230))
    put(img, 54, 9, (160, 72, 40))
    put(img, 55, 9, (180, 86, 46))
    put(img, 56, 9, (240, 236, 230))
    # a sweet potato pie
    put(img, 58, 9, (220, 120, 50))
    put(img, 59, 9, (230, 140, 60))


SEATED = [  # x, skin, shirt, hair style, hat
    (37, jfx.SKIN[3], (240, 236, 226), "puff", None),
    (43, jfx.SKIN[0], (250, 200, 80), "short", None),
    (49, jfx.SKIN[5], (240, 140, 160), "long", None),
    (55, jfx.SKIN[2], (150, 200, 240), "brim", (230, 220, 190)),
]


def render():
    bg = backdrop()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        bunting(img)
        grill(img, f)
        # the cook: apron, cap, flipping with a spatula
        flip = 0.22 + 0.12 * max(0.0, math.sin(2 * math.pi * f / sec(1.6)))
        hands = jfx.person(img, 17, GROUND, jfx.SKIN[1], (240, 240, 236), (70, 90, 140), style="cap",
                           hat=jfx.FLAG_RED, arms=(flip, 0.02))
        hx, hy = hands["l"]
        put(img, hx - 1, hy - 1, (200, 200, 210))
        cheers = ease_in_out(phase(f, sec(12.4), sec(13.2)))
        # family at the table (drawn before the table so it hides their laps)
        for i, (x, skin, shirt, style, hat) in enumerate(SEATED):
            bob = math.sin(2 * math.pi * (f / sec(2.4) + i * 0.3))
            arms = (0.08 + 0.02 * bob, 0.08 - 0.02 * bob)
            if cheers > 0:
                arms = (0.08, 0.08 + 0.36 * cheers)
            h = jfx.person(img, x, 12, skin, shirt, None, style=style, hat=hat, arms=arms, seated=True)
            if cheers > 0.6:
                put(img, h["r"][0], h["r"][1] - 1, (236, 40, 56))
                put(img, h["r"][0], h["r"][1], (210, 30, 46))
        table(img)
        food(img)
        # two arrive from the right with a covered dish
        for i, (x0, x1, t0, skin, shirt, style, hat, dress) in enumerate((
                (80, 64, 2.6, jfx.SKIN[4], (110, 90, 200), "wrap", (250, 190, 60), True),
                (86, 68, 3.0, jfx.SKIN[2], (240, 220, 160), "short", None, False))):
            walk = phase(f, sec(t0), sec(t0 + 3.0))
            x = round(x0 + (x1 - x0) * ease_in_out(walk))
            legs = (1 + (f // 3 + i) % 2) if 0 < walk < 1 else 0
            arms = (0.2, 0.2) if cheers <= 0 else (0.2, 0.2 + 0.24 * cheers)
            h = jfx.person(img, x, GROUND, skin, shirt, (90, 80, 120), style=style, hat=hat, arms=arms, legs=legs,
                           dress=dress)
            if i == 0 and walk < 1:  # the covered dish, carried in front
                for dx in (-2, -1, 0):
                    put(img, h["l"][0] + dx, h["l"][1] - 1, (220, 220, 230))
                put(img, h["l"][0] - 1, h["l"][1] - 2, (200, 200, 214))
            if i == 0 and walk >= 1:  # set down on the end of the table
                put(img, 60, 9, (220, 220, 230))
                put(img, 61, 9, (220, 220, 230))
        # two kids play catch between the grill and the table: a ball arcs back and forth
        throw = sec(1.4)
        n, u = divmod(f, throw)
        u /= throw
        left_has = n % 2 == 0
        for i, kx in enumerate((22, 28)):
            catching = (i == 1) == left_has and u > 0.8
            throwing = (i == 0) == left_has and u < 0.2
            ang = 0.4 if (catching or throwing) else 0.12
            arms = (0.12, ang) if i == 0 else (ang, 0.12)
            jfx.person(img, kx, GROUND + 1, jfx.SKIN[3 - i * 2], ((240, 90, 90), (90, 200, 120))[i], None,
                       style=("buns", "short")[i], arms=arms, legs=0, height=8)
        bx = 26 + (6 * u if left_has else 6 - 6 * u) - 1
        by = 7 - 4 * math.sin(math.pi * u)
        put(img, bx, by, (255, 236, 90))
        if cheers > 0.8:  # a little sparkle over the raised cups
            for x in (39, 45, 51, 57):
                k = 0.5 + 0.5 * math.sin(f * 0.9 + x)
                add(img, x + 2, 2, (255, 240, 200), 0.4 * k)
        frames.append(img)
    return frames
