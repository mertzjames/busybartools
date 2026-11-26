"""Scene: A Day of Service. Three small stories, joined by slow dissolves: neighbors plant a tree in the park,
volunteers fill a crate at a food drive, and two painters roll a community mural onto a wall: a rising sun and the
word SERVICE."""

import math

from PIL import Image, ImageOps

from busybar.canvas import FPS, H, W, blit, ease_in_out, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.font import draw_text
from mfx import BOTTOMS, HAIR, SKIN, TOPS, Person, glow

NAME = "service"
TITLE = "A Day of Service"
SECONDS = 18
KEYFRAMES = [(1.8, "Digging in the park"), (4.8, "A young tree, planted and growing"),
             (8.4, "A food drive fills a crate"), (13.6, "Painters roll out a mural"), (17.0, "SERVICE")]

PART = 6.0  # seconds per vignette
FADE = 0.6  # dissolve between vignettes

GRASS = (46, 112, 64)
GRASS_DARK = (30, 80, 50)
SOIL = (120, 84, 56)
LEAF = (86, 178, 84)
LEAF_LIGHT = (150, 214, 110)
BARK = (140, 96, 60)


def figure(person: Person, x: int, feet: int, flip: bool = False, stride: bool = False, front_hand=True):
    """A person as a transparent layer (so it can face left), plus the layer's x."""
    layer = Image.new("RGBA", (8, 16), (0, 0, 0, 0))
    person.draw(layer, 2, feet, stride, front_hand=front_hand)
    if flip:
        layer = ImageOps.mirror(layer)
        return layer, x - 8 + 2 + 4
    return layer, x - 2


def put_person(img, person, x, feet, flip=False, stride=False, front_hand=True):
    layer, lx = figure(person, x, feet, flip, stride, front_hand)
    blit(img, layer, lx, 0)


# --- 1. planting a tree ------------------------------------------------------------------------------------------

DIGGER = Person("adult", SKIN[4], HAIR[0], TOPS[2], BOTTOMS[0])
HELPER = Person("child", SKIN[0], HAIR[4], TOPS[3], BOTTOMS[1])
NEIGHBOR = Person("elder", SKIN[2], HAIR[2], TOPS[1], BOTTOMS[2])
HOLE_X = 36


def park(t: float):
    img = vgradient((34, 56, 128), (96, 100, 160))
    glow(img, 62, 1, 16, (255, 200, 120), 0.35)
    for x in range(W):  # a dark hedge behind the people, then the grass
        top = 8 + round(1.2 * math.sin(x * 0.45) + 0.8 * math.sin(x * 1.3))
        for y in range(top, 13):
            put(img, x, y, (22, 52, 44) if (x * 3 + y) % 7 else (30, 66, 52))
        for y in range(13, H):
            put(img, x, y, GRASS if y == 13 else GRASS_DARK)
    # the digger, shovel going down and up
    dig = 0.0 if t > 2.8 else 0.5 + 0.5 * math.sin(t * 2 * math.pi * 0.9)
    put_person(img, DIGGER, 28, 13, front_hand=False)
    hx, hy = 31, 7 + round(dig)  # hands
    put(img, hx, hy, DIGGER.skin)
    for k in range(5):  # shovel handle down to the blade at the hole
        put(img, hx + 1 + k * 0.5, hy + 1 + k, (190, 150, 100))
    put(img, hx + 4, hy + 6, (200, 206, 220))
    put(img, hx + 5, hy + 6, (200, 206, 220))
    # soil pile grows while digging
    pile = min(3, int(t / 0.9))
    for k in range(pile):
        put(img, 42 + k, 12, SOIL)
        if k:
            put(img, 42 + k, 11, SOIL)
    put(img, HOLE_X + 2, 13, SOIL)
    put(img, HOLE_X + 3, 13, SOIL)
    # the child brings the sapling, then it is planted and grows
    walk = ease_in_out(phase(int(t * FPS), sec(0.0), sec(2.6)))
    cx = round(lerp(54, 45, walk))
    put_person(img, HELPER, cx, 13, flip=True, stride=walk < 1 and int(t * 4) % 2 == 1)
    grow = ease_out(phase(int(t * FPS), sec(3.2), sec(5.6)))
    if t < 3.0:  # carried
        tree(img, cx - 3, 9, 0.0)
    else:
        tree(img, HOLE_X + 3, 12, grow)
    put_person(img, NEIGHBOR, 12, 13)  # an elder watches with a watering can
    put(img, 16, 9, (150, 170, 200))
    put(img, 17, 9, (150, 170, 200))
    put(img, 17, 8, (150, 170, 200))
    if t > 4.2:  # water falls on the young tree
        for k in range(3):
            if int(t * 10 + k) % 3 == 0:
                put(img, 18 + k, 9 + k, (120, 190, 255), 0.7)
    return img


def tree(img, x: int, base: int, g: float) -> None:
    """A sapling (g=0) growing into a small leafy tree (g=1)."""
    h = 2 + round(3 * g)
    for y in range(base - h + 1, base + 1):
        put(img, x, y, BARK)
    top = base - h
    r = 1 + 2 * g
    for yy in range(int(top - r - 1), top + 2):
        for xx in range(int(x - r - 1), int(x + r + 2)):
            d = math.hypot(xx - x, (yy - top) * 1.3)
            if d <= r:
                put(img, xx, yy, LEAF_LIGHT if (xx + yy) % 3 == 0 else LEAF)


# --- 2. food drive -------------------------------------------------------------------------------------------------

LEFT_VOL = Person("adult", SKIN[1], HAIR[5], TOPS[0], BOTTOMS[3])
RIGHT_VOL = Person("teen", SKIN[5], HAIR[0], TOPS[6], BOTTOMS[0])
ITEMS = [(214, 70, 60), (240, 200, 90), (110, 180, 90), (230, 140, 60), (180, 180, 200), (200, 90, 120)]
CRATE_X, CRATE_W = 31, 10


def food(t: float):
    img = vgradient((70, 54, 84), (84, 64, 82))
    for x in range(W):  # the hall floor
        put(img, x, 15, (110, 86, 76))
        put(img, x, 14, (96, 74, 70))
    for y in range(1, 6):  # a window of morning light, top left
        for x in range(3, 13):
            put(img, x, y, (120, 140, 200) if (x - 3) % 5 and y != 3 else (90, 100, 150))
    for x in range(20, 52):  # table
        put(img, x, 11, (176, 124, 76))
    for y in range(12, 14):
        put(img, 21, y, (120, 84, 56))
        put(img, 50, y, (120, 84, 56))
    put_person(img, LEFT_VOL, 17, 13)
    put_person(img, RIGHT_VOL, 55, 13, flip=True)
    # cans arc from each side into the crate; the crate fills, then heaps up
    n_in = 0
    for k in range(12):
        t0 = 0.3 + k * 0.42
        side = k % 2
        sx, sy = (20, 7) if side == 0 else (52, 7)
        tx = CRATE_X + 2 + (k * 3) % (CRATE_W - 4)
        if t >= t0 + 0.7:
            n_in += 1
            continue
        if t >= t0:
            u = (t - t0) / 0.7
            x = lerp(sx, tx, u)
            y = lerp(sy, 5, u) - 3 * math.sin(math.pi * u)
            c = ITEMS[k % len(ITEMS)]
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                put(img, x + dx, y + dy, c)
    # contents: one 2x2 can per arrival, packed from the bottom
    for j in range(n_in):
        col, row = j % 4, j // 4
        x, y = CRATE_X + 1 + col * 2 + (row % 2), 9 - row * 2
        c = ITEMS[(j * 5) % len(ITEMS)]
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put(img, x + dx, y + dy, c)
    for x in range(CRATE_X - 1, CRATE_X + CRATE_W + 1):  # crate: front slats over the lower cans
        put(img, x, 10, (210, 160, 96))
        put(img, x, 8, (186, 136, 80))
    for y in range(7, 11):
        put(img, CRATE_X - 1, y, (210, 160, 96))
        put(img, CRATE_X + CRATE_W, y, (210, 160, 96))
    return img


# --- 3. the mural ------------------------------------------------------------------------------------------------

PAINTER_A = Person("adult", SKIN[3], HAIR[3], TOPS[7], BOTTOMS[0])
PAINTER_B = Person("adult", SKIN[0], HAIR[1], TOPS[5], BOTTOMS[2])
WALL_TOP, WALL_BOTTOM = (54, 44, 86), (40, 34, 66)
WORD = "SERVICE"
WORD_X = 26
WORD_Y = 1


def mural_art(full: Image.Image) -> None:
    """The finished mural: a rising sun with rays on the left, the word on the right."""
    for y in range(0, 12):
        for x in range(0, 24):
            d = math.hypot(x - 11, (y - 11) * 1.1)
            if d <= 6:
                put(full, x, y, mix((255, 236, 160), (255, 170, 70), d / 6))
    for deg in (20, 55, 90, 125, 160):  # five painted rays
        a = math.radians(deg)
        for r in (8, 9, 10):
            put(full, 11 + r * math.cos(a), 11 - r * math.sin(a) / 1.1, (250, 150, 80))
    for x in range(0, 24):
        put(full, x, 11, (90, 150, 210))
    draw_text(full, WORD, WORD_X, WORD_Y, None, font="big", gradient=((255, 240, 200), (255, 180, 70)),
              shadow=(120, 60, 110))


def mural(t: float, art: Image.Image):
    img = vgradient(WALL_TOP, WALL_BOTTOM)
    for x in range(W):  # sidewalk
        for y in (13, 14, 15):
            put(img, x, y, (84, 82, 96) if y == 13 else (60, 58, 72))
    # paint is revealed behind the rollers as they sweep right
    # the lead painter's roller is the edge of the paint; both walk off once the wall is done
    reveal = lerp(-2, W + 22, phase(int(t * FPS), sec(0.4), sec(4.6)))
    px_art = art.load()
    for y in range(0, 13):
        for x in range(W):
            if x < reveal:
                c = px_art[x, y]
                if c[3]:
                    put(img, x, y, c[:3])
    # painters: one rolls the top, one the bottom, just ahead of the reveal
    for k, (p, top) in enumerate(((PAINTER_A, 1), (PAINTER_B, 7))):
        x = round(reveal) - 4 - k * 9
        if -6 < x < W + 4:
            put_person(img, p, x, 12, stride=int(t * 3) % 2 == 1)
            bob = round(1.5 * math.sin(t * 6 + k))
            for yy in range(top + 2 + bob, 7):  # pole
                put(img, x + 3, yy, (190, 190, 200))
            for yy in range(top + bob, top + 3 + bob):  # roller
                put(img, x + 4, yy, (255, 220, 150))
    return img


def render():
    art = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mural_art(art)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        part = min(2, int(t // PART))
        lt = t - part * PART
        scene = (park, food, lambda u: mural(u, art))
        img = scene[part](lt)
        if part > 0 and lt < FADE:  # dissolve in from the previous vignette
            prev = scene[part - 1](lt + PART)
            img = Image.blend(prev, img, ease_in_out(lt / FADE))
        frames.append(img)
    return frames
