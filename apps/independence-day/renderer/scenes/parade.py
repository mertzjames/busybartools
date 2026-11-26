"""Scene: a small-town parade on Main Street (docs/DECISIONS.md D3). Under bunting-hung storefronts, kids on the far
sidewalk wave little flags as the parade marches past, left to right: a drum major twirling a baton, a marching band
(trumpets, a snare drum, a sousaphone), then a float with a pleated red, white and blue skirt, a big gold star and
two more kids waving from its deck."""

import math

from busybar.canvas import H, W, blit, mix, put, sec
from busybar.sprite import Sprite

import jfx

NAME = "parade"
TITLE = "Hometown Parade"
SECONDS = 15
KEYFRAMES = [(0.6, "Main Street, hung with bunting"), (2.6, "The drum major leads"), (5.0, "Trumpets and a snare drum"),
             (7.4, "The sousaphone"), (10.0, "The float rolls in"), (12.6, "Kids wave from the float"),
             (14.6, "The parade rolls on")]

STREET = 11  # rows 11-15 are the street; marchers' feet on row 14
SPEED = 8.0 / 15  # px per frame (8 px/s): marching pace on a 72 px street

# lit uniform colors: navy shakos are a lit blue, never near-black
PAL = {"r": "#FF5A5A", "w": "#F6F6F6", "N": "#5A78F0", "G": "#FFD050", "S": "#E8B48C", "s": "#B87A52",
       "R": "#D82838", "W": "#F0F0F0", "Y": "#FFC840", "y": "#C89020", "D": "#F4F4F4", "K": "#B0B6C8",
       "H": "#F8F8F8", "B": "#5070E0"}

LEGS = ("..W.W...", ".W...W..")  # two marching steps: together and striding

TRUMPET_TOP = """
...r....
..HHH...
..HGH...
..SSSyYY
..RRRS.Y
..RRR...
..RRR...
"""
DRUM_TOP = """
...r....
..HHH...
..HGH.Y.
..SSS.Y.
..RRSDD.
..RRRDD.
..RRRKK.
"""
SOUSA_TOP = """
..YYYY..
.YHHHYY.
.YHGHY..
..SSSY..
..RYRR..
..RRYR..
..RRRY..
"""
MAJOR_TOP = """
..NNN...
..NNN...
..NGN...
..SSS...
..RGR...
..RGRS..
..RRR...
"""


def marcher(top: str, name: str, skin="S") -> Sprite:
    rows = top.strip("\n").splitlines()
    rows = [r.replace("S", skin) for r in rows]
    frames = ["\n".join(rows + [leg, leg if k == 0 else LEGS[0]]) for k, leg in enumerate(LEGS)]
    return Sprite(name, PAL, *frames)


TRUMPET = marcher(TRUMPET_TOP, "trumpet")
TRUMPET2 = marcher(TRUMPET_TOP, "trumpet2", "s")
DRUM = marcher(DRUM_TOP, "drum", "s")
SOUSA = marcher(SOUSA_TOP, "sousa")
MAJOR = marcher(MAJOR_TOP, "major", "s")

# the parade, by distance behind the drum major (px); each walks a half step out of phase with its neighbor
UNITS = [(MAJOR, 0), (TRUMPET, -10), (DRUM, -18), (TRUMPET2, -26), (SOUSA, -35)]
FLOAT_GAP = -44  # the float's front edge
FLOAT_W = 26


def small_flag(img, x, y, wave: int):
    """A little hand flag, 4x3, its fly end dipping on alternate frames: blue corner, red and white stripes."""
    cells = ((jfx.BLUE, jfx.BLUE, jfx.RED, jfx.RED), (jfx.BLUE, jfx.BLUE, jfx.WHITE, jfx.WHITE),
             (jfx.RED, jfx.RED, jfx.RED, jfx.RED))
    for v, row in enumerate(cells):
        for u, c in enumerate(row):
            put(img, x + u, y + v + (1 if wave and u >= 2 else 0), c)


def kid(img, x, feet, shirt, hair, skin, wave_ph: float, height=6):
    """A kid seen from the front, 3 px wide: hair, a plain face (no eyes: too small to read), shirt, legs. One arm
    holds a flag on a stick above the head and waves it."""
    top = feet - height + 1
    put(img, x, top, hair)
    put(img, x + 1, top, hair)
    put(img, x + 2, top, hair)
    put(img, x, top + 1, hair)
    put(img, x + 1, top + 1, skin)
    put(img, x + 2, top + 1, hair)
    for dy in (2, 3):
        for dx in range(3):
            put(img, x + dx, top + dy, shirt)
    for dy in range(4, height):
        put(img, x, top + dy, (70, 90, 170))
        put(img, x + 2, top + dy, (70, 90, 170))
    up = math.sin(wave_ph) > 0
    hx, hy = x + 3, top + (1 if up else 2)
    put(img, hx, hy, skin)
    stick = (210, 180, 130)
    put(img, hx, hy - 1, stick)
    put(img, hx, hy - 2, stick)
    small_flag(img, hx, hy - 4 + (0 if up else 1), int(math.sin(wave_ph * 2) > 0))


def storefronts(img):
    """Muted shopfronts along the top (so the bright parade stands out in front of them), one thin bunting swag,
    warm windows, the far sidewalk and the street."""
    shops = [(0, 14, (92, 96, 118)), (14, 13, (118, 112, 100)), (27, 16, (84, 100, 96)), (43, 12, (112, 92, 86)),
             (55, 17, (96, 104, 126))]
    for x0, w, c in shops:
        for x in range(x0, x0 + w):
            for y in range(3, 7):
                put(img, x, y, c)
            put(img, x, 3, mix(c, (255, 255, 255), 0.25))
        for wx in range(x0 + 2, x0 + w - 2, 4):  # windows, warm-lit
            for dy in (4, 5):
                put(img, wx, dy, (186, 160, 112))
                put(img, wx + 1, dy, (170, 144, 100))
    for x in range(W):
        for y in range(7, STREET):
            put(img, x, y, (72, 70, 70))
        put(img, x, STREET - 1, (120, 118, 112))  # the curb
        for y in range(STREET, H):
            put(img, x, y, (40, 42, 50))
        if x % 6 < 3:  # a dashed centerline
            put(img, x, 15, (150, 130, 60))
    for x in range(W):  # a string of tiny pennants along the rooftops
        if x % 2 == 0:
            put(img, x, 3, (jfx.RED, jfx.WHITE, jfx.BLUE)[(x // 2) % 3], 0.85)


def parade_float(img, x0, f):
    """The float: a deck on a pleated skirt (blue band, then red and white pleats), wheels peeking out, a big gold
    star on a post and two kids waving flags."""
    deck = 9
    for x in range(x0, x0 + FLOAT_W):
        if x in (x0, x0 + FLOAT_W - 1) and False:
            continue
        for y in range(deck, 15):
            if y == deck:
                c = (240, 240, 240)
            elif y == deck + 1:
                c = jfx.BLUE
            else:
                c = jfx.RED if ((x - x0) // 2) % 2 == 0 else jfx.WHITE
            put(img, x, y, c)
        if (x - x0) % 4 == 1:  # gold stars on the blue band
            put(img, x, deck + 1, jfx.GOLD_LIGHT)
    for wx in (x0 + 3, x0 + FLOAT_W - 5):  # wheels: a lit grey with a hub
        for dx in range(3):
            put(img, wx + dx, 15, (120, 122, 134))
        put(img, wx + 1, 15, (200, 200, 210) if (f // 2) % 2 else (150, 150, 160))
    # a big gold star on a post at the back of the deck
    sx, sy = x0 + 6, 0
    star = ("..Y..", "..Y..", "YYYYY", ".YYY.", ".Y.Y.")
    for v, row in enumerate(star):
        for u, ch in enumerate(row):
            if ch == "Y":
                put(img, sx + u, sy + v, jfx.GOLD_LIGHT if v < 3 else jfx.GOLD)
    for y in range(sy + 5, deck):
        put(img, sx + 2, y, (200, 200, 210))
    # two kids on the deck waving flags
    kid(img, x0 + 13, deck - 1, (255, 255, 255), jfx.HAIR[1], jfx.SKIN[0], f * 0.5)
    kid(img, x0 + 19, deck - 1, (255, 90, 90), jfx.HAIR[2], jfx.SKIN[2], f * 0.5 + 2.0)


CROWD = [(3, (90, 200, 255), 0, 0), (16, (255, 220, 80), 3, 2), (31, (120, 220, 120), 2, 1),
         (46, (255, 140, 200), 4, 3), (61, (255, 170, 60), 1, 2)]


def render():
    base = jfx.sky([(0, (70, 136, 226)), (3, (130, 180, 240))])
    storefronts(base)
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        for i, (x, shirt, hair, skin) in enumerate(CROWD):  # the kids on the far sidewalk
            excited = 0.45 if i % 2 else 0.6
            kid(img, x, STREET - 1, shirt, jfx.HAIR[hair], jfx.SKIN[skin], f * excited + i * 1.7)
        lead = -2 + f * SPEED
        for i, (spr, off) in enumerate(UNITS):
            x = lead + off
            step = ((f // 4) + i) % 2
            img_s = spr.img(step)
            blit(img, img_s, math.floor(x + 0.5), STREET - 6 + (0 if step == 0 else 0))
            if spr is MAJOR:  # the baton twirls above the drum major's raised hand
                a = f * 0.55
                hx, hy = math.floor(x + 0.5) + 5, STREET - 7
                for k in range(-2, 3):
                    c = jfx.GOLD if abs(k) == 2 else (220, 224, 236)
                    put(img, hx + k * math.cos(a), hy + k * math.sin(a) * 0.7, c)
            if spr is DRUM and step == 0:  # sticks hit the drum on the beat
                put(img, math.floor(x + 0.5) + 6, STREET - 3, (255, 255, 200))
        parade_float(img, math.floor(lead + FLOAT_GAP - FLOAT_W + 0.5), f)
        frames.append(img)
    return frames
