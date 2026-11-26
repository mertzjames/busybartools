"""Scene: a backyard cookout on a summer afternoon (docs/DECISIONS.md D3). By a green hedge, a cook in an apron
tends a red kettle grill of burgers and hot dogs; smoke curls up and a burger is flipped. On the picnic table, with
its red-and-white checked cloth, sit watermelon slices, a pitcher of lemonade and a little flag. A kid dashes in,
takes a slice of watermelon and runs off with it."""

import math

from busybar.canvas import H, W, blit, ease_in_out, ease_out, mix, phase, put, sec
from busybar.sprite import Sprite

import jfx

NAME = "cookout"
TITLE = "Backyard Cookout"
SECONDS = 14
KEYFRAMES = [(0.8, "Burgers on the grill"), (3.6, "Flip!"), (5.6, "Watermelon and lemonade"),
             (8.4, "A kid dashes in"), (9.8, "One slice, please"), (12.4, "Off with the prize")]

LAWN = 11
GRILL_X = 16
TABLE_X0, TABLE_X1 = 36, 67
TABLE_TOP = 9

# the cook, side view facing right: cap, plain face, blue shirt, white apron, khaki shorts
COOK_PAL = {"C": "#E83040", "h": "#7A4E30", "S": "#E2AA80", "B": "#4870D8", "A": "#F2F2F2", "K": "#C8B078",
            "s": "#E2AA80"}
COOK = Sprite("cook", COOK_PAL, """
.CCC..
.CCCC.
.hSS..
.hSS..
.BAA..
BBAA..
BBAA..
.BAA..
.KKK..
.s.s..
.s.s..
""")

KID_PAL = {"H": "#C89040", "S": "#9C6440", "T": "#40C8F0", "D": "#4060C0"}
KID = Sprite("kid", KID_PAL, """
.HH.
.HS.
TTT.
TTT.
.D..
.D..
""", """
.HH.
.HS.
TTT.
TTT.
D.D.
D..D
""")


def hedge(img):
    """A leafy green hedge behind the lawn (no white fence: it drowned out the apron, the cloth and the food)."""
    for x in range(W):
        top = 6 - (1 if (x * 5) % 7 < 3 else 0)
        for y in range(top, LAWN):
            put(img, x, y, (34, 100, 54) if (x * 7 + y * 3) % 5 else (52, 124, 66))


def grill(img, f, flip):
    """A red kettle grill: grate with two burgers and a hot dog, bowl, legs, and steady coals glowing below the grate."""
    x0 = GRILL_X
    for i, (y, a, b) in enumerate(((9, 0, 8), (10, 1, 7), (11, 2, 6))):  # the bowl
        for x in range(x0 + a, x0 + b + 1):
            put(img, x, y, (214, 40, 48) if i < 2 else (170, 30, 36))
        put(img, x0 + a, y, (255, 110, 110))
    for x in range(x0, x0 + 9):  # the grate
        put(img, x, 8, (190, 190, 200))
    for k, x in enumerate(range(x0 + 1, x0 + 8)):  # coals showing through
        if (x + f // 4) % 3 == 0 and k % 2 == 0:
            put(img, x, 8, (255, 140, 40))
    for x, y in ((x0 + 1, 12), (x0 + 1, 13), (x0 + 1, 14), (x0 + 7, 12), (x0 + 7, 13), (x0 + 7, 14), (x0 + 4, 12),
                 (x0 + 4, 13)):
        put(img, x, y, (150, 150, 160))
    # food: a hot dog and two burgers; the second burger is flipped (it arcs up and lands browner)
    put(img, x0 + 6, 7, (210, 110, 80))
    put(img, x0 + 7, 7, (210, 110, 80))
    for dx in (4, 5):
        put(img, x0 + dx - 1, 7, (150, 80, 50))
    p = flip
    raw, done = (186, 106, 76), (126, 66, 40)
    if 0 < p < 1:
        hy = 7 - 3.2 * math.sin(math.pi * p)
        c = done if p > 0.5 else raw
        put(img, x0 + 1, hy - (1 if 0.3 < p < 0.7 else 0), c)
        put(img, x0 + 2, hy, c)
    else:
        c = done if p >= 1 else raw
        put(img, x0 + 1, 7, c)
        put(img, x0 + 2, 7, c)


def smoke(img, f):
    """Soft puffs drifting up and to the right from the grate (each puff a few pixels: cheap per frame)."""
    for i in range(7):
        age = (f + i * 9) % 60
        t = age / 60
        x = GRILL_X + 2 + (i * 2) % 5 + t * 9 + math.sin(age * 0.2 + i) * 0.8
        y = 7 - t * 8
        a = 0.55 * (1 - t) * min(1.0, age / 6)
        put(img, x, y, (226, 226, 236), a)
        if t < 0.6:
            put(img, x + 1, y, (210, 210, 224), a * 0.6)


def table(img, slices: int):
    """The picnic table: a checked red-and-white cloth hanging over its edge, brown legs and benches, and on top two
    watermelon slices (or one), a lemonade pitcher with a cup, and a little flag in a jar."""
    for x in range(TABLE_X0, TABLE_X1 + 1):
        for y in (TABLE_TOP, TABLE_TOP + 1, TABLE_TOP + 2):
            check = ((x // 2) + (y - TABLE_TOP)) % 2 == 0
            put(img, x, y, jfx.RED if check else (250, 244, 240))
    for x in (TABLE_X0 + 2, TABLE_X1 - 2):
        for y in range(TABLE_TOP + 3, 15):
            put(img, x, y, (150, 96, 56))
    for x in range(TABLE_X0 - 2, TABLE_X1 + 3):  # a bench in front
        put(img, x, 13, (176, 116, 66))
    # watermelon slices: half-moons, green rind under red flesh (seeds a lit brown, never black)
    for k in range(slices):
        sx = TABLE_X0 + 2 + k * 8
        wedge(img, sx, TABLE_TOP - 1)
    # the lemonade pitcher (pale yellow with a white handle) and a cup
    px = TABLE_X0 + 19
    for y in range(TABLE_TOP - 5, TABLE_TOP):
        for x in range(px, px + 3):
            put(img, x, y, (255, 234, 110) if y > TABLE_TOP - 5 else (250, 250, 250))
    put(img, px + 3, TABLE_TOP - 4, (250, 250, 250))
    put(img, px + 3, TABLE_TOP - 2, (250, 250, 250))
    put(img, px + 4, TABLE_TOP - 3, (250, 250, 250))
    put(img, px - 1, TABLE_TOP - 4, (250, 250, 250))  # the spout
    for y in (TABLE_TOP - 2, TABLE_TOP - 1):
        put(img, px + 6, y, (255, 234, 110))
        put(img, px + 7, y, (255, 234, 110))
    # a little flag in a jar
    fx = TABLE_X1 - 6
    put(img, fx + 1, TABLE_TOP - 1, (170, 220, 240))
    put(img, fx + 2, TABLE_TOP - 1, (170, 220, 240))
    for y in range(TABLE_TOP - 6, TABLE_TOP - 1):
        put(img, fx + 1, y, (220, 200, 160))
    for v, row in enumerate(((jfx.BLUE, jfx.BLUE, jfx.RED, jfx.RED), (jfx.BLUE, jfx.BLUE, jfx.WHITE, jfx.WHITE),
                             (jfx.RED, jfx.RED, jfx.RED, jfx.RED))):
        for u, c in enumerate(row):
            put(img, fx + 2 + u, TABLE_TOP - 7 + v, c)


def wedge(img, x, y):
    """A watermelon slice, 7 wide, its green rind on row y and red flesh above (seeds a lit brown, never black)."""
    for dx in range(7):
        put(img, x + dx, y, (50, 170, 70))
    for dx in range(1, 6):
        put(img, x + dx, y - 1, (255, 66, 86))
    for dx in range(2, 5):
        put(img, x + dx, y - 2, (255, 96, 112))
    put(img, x + 2, y - 1, (150, 70, 40))
    put(img, x + 4, y - 1, (150, 70, 40))


def render():
    base = jfx.sky([(0, (70, 140, 230)), (4, (140, 196, 246))])
    jfx.glow(base, 31, 1, 7, (255, 244, 200), 0.6)
    for dx in (0, 1):
        for dy in (0, 1):
            put(base, 30 + dx, 0 + dy, (255, 252, 230))
    hedge(base)
    for x in range(W):
        for y in range(LAWN, H):
            put(base, x, y, (70, 160, 70) if (x + y) % 4 else (90, 180, 84))
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        flip = phase(f, sec(3.2), sec(4.0))
        # the kid: runs in from the right, stops at the table, takes a slice and runs back out
        taken = f >= sec(9.6)
        table(img, 1 if taken else 2)
        smoke(img, f)
        grill(img, f, flip)
        # the cook's arm reaches the grate with a spatula; it lifts for the flip
        blit(img, COOK.img(0), 10, 4)
        # the arm: sleeve, forearm and hand out to the grate, and the spatula's blade under the burger
        lift = 1 if 0.15 < flip < 0.6 else 0
        put(img, 14, 9 - lift, (72, 112, 216))
        put(img, 15, 8 - lift, (226, 170, 128))
        put(img, 16, 8 - lift, (226, 170, 128))
        put(img, 17, 7 - 2 * lift, (210, 214, 226))
        put(img, 18, 7 - 2 * lift, (210, 214, 226))
        if f < sec(8.0):
            kx = None
        elif f < sec(9.2):
            kx = W + 2 - (W + 2 - (TABLE_X0 + 15)) * ease_out(phase(f, sec(8.0), sec(9.2)))
        elif f < sec(10.4):
            kx = TABLE_X0 + 15
        else:
            kx = TABLE_X0 + 15 + 40 * phase(f, sec(10.4), sec(12.6)) ** 1.3
        if kx is not None and kx < W + 1:
            running = f < sec(9.2) or f >= sec(10.4)
            fr = (f // 2) % 2 if running else 0
            flipx = f < sec(10.4)
            kxi = math.floor(kx + 0.5)
            blit(img, KID.img(fr, flip=flipx), kxi, LAWN - 2)
            if taken:  # the slice, held up high
                hx = kxi + (4 if not flipx else -1)
                put(img, hx, LAWN - 3, (60, 170, 70))
                put(img, hx, LAWN - 4, (255, 70, 90))
        frames.append(img)
    return frames
