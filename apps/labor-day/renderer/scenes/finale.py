"""Scene: the finale. At night the tower from "Topping Out" stands finished, its windows lit and its flag on the roof.
A crowd of workers, seen from behind in hard hats and caps, watches fireworks burst over the city and cheers. Bunting
drops in along the top and the words THANK YOU, then WORKERS, light up (docs/DECISIONS.md D3, D6)."""

from __future__ import annotations

import random

from busybar.canvas import H, W, ease_out, phase, put, sec
from busybar.font import draw_text, text_width
from busybar.party import Firework

import lfx

NAME = "finale"
TITLE = "Thank You, Workers"
SECONDS = 14
KEYFRAMES = [(1.4, "Fireworks over the finished tower"), (4.0, "The crowd watches"), (7.0, "A gold willow"),
             (10.4, "THANK YOU"), (13.0, "WORKERS")]

FW_RED = (255, 56, 66)
FW_WHITE = (255, 255, 255)
FW_BLUE = (90, 130, 255)
FW_GOLD = (255, 200, 70)
FW_ORANGE = (255, 140, 40)

BUNTING0 = sec(8.6)
WORD1 = sec(9.4)
WORD2 = sec(11.8)
CHEER0 = sec(9.6)
CAPTION_Y = 3
SKYLINE = (44, 48, 92)  # a lit navy-grey (black would be unlit)
WINDOW = (255, 214, 120)

# the crowd, left to right: (x, skin, shirt, hair, hat, hat color)
CROWD = [
    (3, lfx.SKIN[2], lfx.DENIM, lfx.HAIR_DARK, "hard", lfx.SAFETY),
    (11, lfx.SKIN[0], (226, 70, 70), lfx.HAIR_GREY, "cap", (60, 120, 230)),
    (19, lfx.SKIN[4], lfx.TEAL, lfx.HAIR_BLOND, "", None),
    (27, lfx.SKIN[1], lfx.ORANGE, lfx.HAIR_DARK, "hard", lfx.WHITE),
    (35, lfx.SKIN[3], (150, 110, 230), lfx.HAIR_AUBURN, "puff", None),
    (43, lfx.SKIN[0], (110, 146, 200), lfx.HAIR_DARK, "hard", lfx.ORANGE),
    (51, lfx.SKIN[2], (90, 180, 90), lfx.HAIR_BROWN, "cap", lfx.RED),
    (59, lfx.SKIN[4], lfx.DENIM, lfx.HAIR_GREY, "hard", lfx.SAFETY),
    (67, lfx.SKIN[1], (236, 90, 170), lfx.HAIR_DARK, "puff", None),
]


def skyline(img) -> None:
    rng = random.Random(3)
    x = 0
    while x < W:  # low buildings
        w, h = rng.randint(4, 8), rng.randint(3, 6)
        for xx in range(x, min(W, x + w)):
            for yy in range(H - h, H):
                put(img, xx, yy, SKYLINE)
        for yy in range(H - h + 1, H, 2):
            for xx in range(x + 1, min(W, x + w) - 1, 2):
                if rng.random() < 0.35:
                    put(img, xx, yy, WINDOW, 0.7)
        x += w + 1
    for xx in range(44, 53):  # the finished tower, windows lit floor by floor
        for yy in range(5, H):
            put(img, xx, yy, (52, 56, 104))
            if xx in (45, 47, 49, 51) and yy % 2 == 0 and yy > 5:
                put(img, xx, yy, WINDOW, 0.85)
    for xx in range(45, 52):
        put(img, xx, 4, (70, 74, 124))
    lfx.tiny_flag(img, 48, 1)


def render():
    base = lfx.sky([(0, (6, 8, 34)), (8, (16, 16, 56)), (15, (34, 24, 72))])
    skyline(base)
    shows = [
        Firework(1, sec(0.9), 20, 4, (FW_RED,), "peony", n=26),
        Firework(2, sec(1.7), 58, 3, (FW_WHITE,), "ring"),
        Firework(3, sec(2.6), 34, 5, (FW_BLUE, FW_WHITE), "peony", n=30),
        Firework(4, sec(3.6), 10, 4, (FW_GOLD, FW_ORANGE), "palm"),
        Firework(5, sec(4.3), 64, 5, (FW_BLUE,), "peony", n=24),
        Firework(6, sec(5.2), 28, 3, (FW_WHITE, FW_RED), "ring"),
        Firework(7, sec(6.4), 48, 3, None, "willow"),
        Firework(8, sec(7.3), 16, 5, (FW_BLUE, FW_RED), "peony", n=28),
        Firework(9, sec(7.9), 60, 4, (FW_RED,), "ring"),
        # behind the words: small bursts at the edges only
        Firework(10, sec(10.6), 5, 6, (FW_GOLD,), "peony", n=14, speed=0.55),
        Firework(11, sec(11.6), 67, 6, (FW_BLUE, FW_WHITE), "peony", n=14, speed=0.55),
        Firework(12, sec(12.8), 5, 5, (FW_RED,), "peony", n=14, speed=0.55),
    ]
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        for fw in shows:
            fw.draw(img, f, 1.0)
        word = "THANK YOU" if f < WORD2 else "WORKERS"
        k = phase(f, WORD1, WORD1 + sec(0.6)) if f < WORD2 else phase(f, WORD2, WORD2 + sec(0.6))
        if f >= WORD1:
            out = 1.0 - phase(f, WORD2 - sec(0.4), WORD2) if f < WORD2 else 1.0
            tw = text_width(word, "big")
            x = (W - tw) // 2
            lfx.dim_rect(img, x - 1, CAPTION_Y, x + tw, CAPTION_Y + 7, 0.8 * max(k, 0.6 if f >= WORD2 else 0),
                         feather=2)
        if f >= BUNTING0:
            lfx.bunting(img, -5 + 4 * ease_out(phase(f, BUNTING0, BUNTING0 + sec(0.7))), period=24)
        if f >= WORD1:
            draw_text(img, word, x, CAPTION_Y, None, font="big", gradient=(lfx.GOLD_LIGHT, lfx.GOLD),
                      shadow=(70, 30, 10), alpha=k * out)
        for i, (cx, skin, shirt, hair, hat, hat_c) in enumerate(CROWD):
            cheer = f >= CHEER0 and ((f - CHEER0) // 6 + i) % 3 != 0
            jump = 1 if (f >= CHEER0 and ((f - CHEER0) // 6 + i) % 4 == 0) else 0
            top = 11 - jump
            lfx.back_view(img, cx, top, skin, shirt, hair, hat, hat_c or lfx.SAFETY)
            if cheer:  # a raised arm
                side = 3 if i % 2 else -3
                put(img, cx + side, top + 2, shirt)
                put(img, cx + side, top + 1, skin)
        frames.append(img)
    return frames
