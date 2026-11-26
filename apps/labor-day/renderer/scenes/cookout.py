"""Scene: the backyard cookout. Over a white picket fence the afternoon turns to dusk. A cook at a red kettle grill
flips burgers, smoke curls up, two friends at a gingham-covered picnic table (watermelon, lemonade, corn) raise their
cups, string lights come on and fireflies blink in the grass (docs/DECISIONS.md D3, D10)."""

from __future__ import annotations

import math

from busybar.canvas import H, W, add, ease_in_out, mix, phase, put, sec
from busybar.fx import puff
from busybar.party import string_lights

import lfx

NAME = "cookout"
TITLE = "Backyard Cookout"
SECONDS = 14
KEYFRAMES = [(1.0, "Burgers on the grill"), (3.4, "A flip"), (6.4, "Watermelon and lemonade"),
             (9.6, "The string lights come on"), (12.6, "Cheers, and fireflies")]

DAY = [(0, (84, 148, 232)), (5, (168, 176, 226)), (9, (255, 196, 150))]
DUSK = [(0, (34, 36, 104)), (5, (104, 76, 148)), (9, (236, 118, 96))]
GRILL_X = 21
FLIPS = (sec(2.8), sec(6.8), sec(10.4))
FLIP_LEN = sec(0.9)
LIGHTS0 = sec(8.0)
CHEERS = sec(11.2)


def fence(img, k: float) -> None:
    """A wooden privacy fence (lit planks, pointed tops), dimming with the dusk."""
    for x in range(W):
        plank = (x // 3) % 3
        c = ((182, 122, 70), (166, 108, 60), (174, 116, 66))[plank]
        c = mix(c, (96, 66, 70), k * 0.8)
        top = 7 if x % 3 == 1 else 8
        for y in range(top, 14):
            put(img, x, y, c if y != 11 else mix(c, (0, 0, 0), 0.15))
    g = mix((70, 170, 70), (34, 90, 50), k)
    for x in range(W):
        put(img, x, 14, g)
        put(img, x, 15, mix(g, (0, 0, 0), 0.2))


def grill(img, f: int, lid_glow: float) -> None:
    x0 = GRILL_X
    lfx.grid(img, x0 - 3, 9, [
        "RRRRRRR",
        ".RRRRR.",
        "..rrr..",
        "..l.l..",
        ".l...l.",
        "l.....l",
    ], {"R": lfx.RED, "r": lfx.RED_DK, "l": lfx.STEEL})
    for dx in range(-3, 4):
        put(img, x0 + dx, 8, lfx.STEEL_HI)  # the grate
    for dx in range(-2, 3):
        add(img, x0 + dx, 9, (255, 120, 30), 0.3 + 0.2 * lid_glow)  # coals glowing under the grate


def patty(img, x: float, y: float, flipped: bool) -> None:
    put(img, x, y, (170, 92, 48) if flipped else (140, 74, 40))
    put(img, x + 1, y, (150, 80, 42))


def table(img) -> None:
    for x in range(38, 66):  # gingham cloth
        put(img, x, 10, lfx.RED if (x // 2) % 2 == 0 else lfx.WHITE)
        put(img, x, 11, lfx.WHITE if (x // 2) % 2 == 0 else (240, 140, 140))
    for x in (40, 63):
        for y in range(12, 15):
            put(img, x, y, lfx.WOOD)
    lfx.grid(img, 44, 8, ["rrrr", "gggg"], {"r": (255, 70, 90), "g": (60, 170, 70)})  # watermelon slice
    put(img, 45, 8, (250, 240, 220))  # a seed (lit, not black)
    lfx.grid(img, 52, 7, ["c.", "yy", "yy"], {"c": (230, 240, 255), "y": (255, 230, 80)})  # lemonade
    lfx.grid(img, 57, 8, ["yYy", "ggg"], {"y": (255, 220, 70), "Y": (255, 246, 160), "g": (110, 180, 70)})  # corn


def render():
    frames = []
    smoke_k = 0
    for f in range(sec(SECONDS)):
        k = lfx.quant(phase(f, sec(3.0), sec(13.0)), 32)
        img = lfx.sky(lfx.blend_stops(DAY, DUSK, k))
        fence(img, k)
        # the cook: dark skin, a ball cap and an apron; the spatula comes up for each flip
        flip = None
        for t0 in FLIPS:
            if t0 - sec(0.3) <= f < t0 + FLIP_LEN:
                flip = (f - t0) / FLIP_LEN
        arm_r = 0.3 if flip is not None and flip < 0.4 else 0.18
        hands = lfx.person(img, 13, 14, lfx.SKIN[0], (70, 120, 220), (90, 96, 120), hat="cap", hat_c=lfx.RED,
                           apron=lfx.WHITE, arms=(0.04, arm_r))
        hx, hy = hands["r"]
        put(img, hx + 1, hy, lfx.STEEL_HI)  # the spatula
        put(img, hx + 2, hy, lfx.STEEL_HI)
        grill(img, f, k)
        # smoke curls up from the grate
        for i in range(4):
            age = (f + i * 9) % 36
            sx = GRILL_X - 1 + 1.5 * math.sin((f + i * 9) / 7) + age * 0.05
            puff(img, sx, 7 - age * 0.2, 0.5 + age * 0.02, (226, 222, 230), 0.35 * (1 - age / 36))
        # two patties; the left one is flipped each time
        if flip is not None and flip >= 0:
            lift = math.sin(math.pi * min(1.0, flip))
            patty(img, GRILL_X - 2, 7 - round(3 * lift), flip > 0.5)
        else:
            done = sum(1 for t0 in FLIPS if f >= t0 + FLIP_LEN)
            patty(img, GRILL_X - 2, 7, done % 2 == 1)
        patty(img, GRILL_X + 1, 7, False)
        # friends at the picnic table (seated: the table hides their legs)
        cheers = f >= CHEERS
        lfx.person(img, 48, 14, lfx.SKIN[3], (236, 90, 170), lfx.DENIM, hair=lfx.HAIR_BLOND, hat="long",
                   arms=(0.04, 0.4 if cheers else 0.1), seated=True)
        lfx.person(img, 60, 14, lfx.SKIN[1], (60, 190, 170), lfx.DENIM, hair=lfx.HAIR_GREY,
                   arms=(0.4 if cheers else 0.1, 0.04), seated=True)
        if cheers:
            put(img, 51, 4, (255, 230, 80))  # raised cups of lemonade
            put(img, 57, 4, (255, 230, 80))
        table(img)
        # string lights come on as it gets dark
        if f >= LIGHTS0:
            on = ease_in_out(phase(f, LIGHTS0, LIGHTS0 + sec(1.2)))
            layer = img.copy()
            string_lights(layer, f, y0=0, sag=2.0, spacing=6, period=30)
            from PIL import Image
            img = Image.blend(img, layer, on) if on < 1 else layer
        # fireflies in the dusk
        if f >= sec(10.0):
            for i in range(6):
                t = (f + i * 11) % 30
                if t < 12:
                    x = (i * 23 + 7) % 34 + 26 * (i % 2)
                    y = 3 + (i * 5) % 5
                    add(img, x + t // 6, y, (220, 255, 120), 0.9 * math.sin(math.pi * t / 12))
        frames.append(img)
        smoke_k += 1
    return frames
