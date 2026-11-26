"""Scene: Trick or Treat! Four trick-or-treaters (a sheet ghost, a little witch, a pumpkin and a caped hero) walk
down the street to a house with a glowing jack-o'-lantern on the step. TRICK OR TREAT! The door opens, candy flies
into each bucket (each kid hops for joy), the door closes, and they hurry off to the next house."""

import math

from busybar.canvas import FPS, H, W, add, blit, mix, put, sec
from busybar.font import draw_text, text_width
from hfx import (NIGHT_MID, NIGHT_TOP, candy_corn, dim_rect, frame_t, glow, gradient, pumpkin, pumpkin_glow, quant,
                 stars)
from scenes.text import SCENE_TEXT
from sprites import GHOST_KID, HERO_KID, PUMPKIN_KID, WITCH_KID

NAME = "trick"
TITLE = "Trick or Treat!"
SECONDS = 16
KEYFRAMES = [(1.5, "Trick-or-treaters on the way"), (5.5, "Up to the door"), (6.8, "TRICK OR TREAT!"),
             (8.4, "Candy for everyone"), (9.6, "A hop for joy"), (12.5, "Off to the next house")]

CAPTION = SCENE_TEXT["trick"][0]
GROUND = 15  # the sidewalk row (the kids stand on it)
KIDS = [GHOST_KID, WITCH_KID, PUMPKIN_KID, HERO_KID]
TARGETS = (39, 29, 19, 9)  # where each kid stops (sprite left edge)
SPEED_IN = 8.0  # px/s
ARRIVE = 6.0
DOOR_X, DOOR_W, DOOR_TOP = 50, 5, 6
OPEN = (6.6, 10.6)  # door open..closed
LEAVE = 11.0
SPEED_OUT = 12.0
CANDY_T = (7.6, 8.1, 8.6, 9.1)  # each kid's candy lands at this second
CANDY_COLORS = ((255, 60, 90), (90, 220, 255), (255, 220, 60), (160, 255, 80), (255, 140, 220))


def kid_x(i: int, t: float) -> float:
    if t < LEAVE:
        return min(TARGETS[i], TARGETS[i] - (ARRIVE - t) * SPEED_IN)
    return TARGETS[i] + (t - LEAVE) * SPEED_OUT


def walking(i: int, t: float) -> bool:
    return t < ARRIVE or t >= LEAVE


def hop(i: int, t: float) -> float:
    u = t - CANDY_T[i] - 0.1
    return 2.0 * math.sin(math.pi * u / 0.45) if 0 <= u < 0.45 else 0.0


BUCKET = ((6, 6), (5, 7), (6, 5), (6, 6))  # each sprite's bucket (or bag) top-left


def bucket_pos(i: int, t: float):
    spr = KIDS[i]
    return kid_x(i, t) + BUCKET[i][0], H - spr.h + BUCKET[i][1]


def render():
    bg = gradient([(0, NIGHT_TOP), (8, NIGHT_MID), (14, (60, 20, 76))])
    # the house front at the right: lit violet clapboard, a door with a porch light and a step
    for x in range(44, W):
        for y in range(2, GROUND):
            c = (74, 50, 96) if y % 3 else (60, 40, 80)
            put(bg, x, y, c)
        put(bg, x, 1, (100, 80, 130))
        put(bg, x, 0, (52, 36, 72))
    for y in range(1, GROUND):
        put(bg, 44, y, (110, 90, 140))
    for x in range(DOOR_X - 1, DOOR_X + DOOR_W + 1):
        put(bg, x, DOOR_TOP - 1, (150, 120, 170))
    for y in range(DOOR_TOP - 1, GROUND):
        put(bg, DOOR_X - 1, y, (150, 120, 170))
        put(bg, DOOR_X + DOOR_W, y, (150, 120, 170))
    for x in range(64, 69):  # a window with warm light
        for y in range(4, 8):
            put(bg, x, y, (255, 200, 90) if (x != 66 and y != 6) else (140, 100, 70))
    glow(bg, 58, 4, 6, (110, 80, 20), 0.8)  # porch light
    put(bg, 58, 3, (255, 240, 170))
    put(bg, 58, 4, (255, 250, 210))
    put(bg, 58, 2, (120, 100, 90))
    pumpkin_glow(bg, 58, 9, 7, 6, 0.7)
    # sidewalk and a picket fence on the left
    for x in range(W):
        put(bg, x, GROUND, (96, 84, 118))
    for x in range(0, 43):
        if x % 3 == 0:
            for y in range(9, GROUND):
                put(bg, x, y, (70, 56, 90))
            put(bg, x, 8, (90, 74, 110))
        put(bg, x, 10, (62, 50, 82))
        put(bg, x, 13, (62, 50, 82))
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 9, 14, f, ymax=7, avoid=lambda x, y: x >= 43)
        # the door: closed panel, or warm light when open
        k = 0.0
        if OPEN[0] <= t < OPEN[1]:
            k = quant(min((t - OPEN[0]) / 0.4, (OPEN[1] - t) / 0.4, 1.0), 4)
        for y in range(DOOR_TOP, GROUND):
            for dx in range(DOOR_W):
                closed = (150, 60, 40) if dx not in (0, DOOR_W - 1) else (120, 46, 32)
                put(img, DOOR_X + dx, y, mix(closed, (255, 196, 90), k))
        put(img, DOOR_X + DOOR_W - 2, 10, (255, 220, 120), 1 - k)  # door knob
        if k > 0:
            glow(img, DOOR_X + 2, GROUND - 1, 7, (100, 60, 10), 0.6 * k)
        pumpkin(img, 58, 9, 7, 6, "happy", lit=1.0, f=f, seed=5, small=True)
        # candy: flies from the door in an arc into each bucket
        for i in range(4):
            land = CANDY_T[i]
            for j in range(3):
                t0 = land - 0.6 + j * 0.08
                u = (t - t0) / 0.6
                if 0 <= u < 1:
                    bx, by = bucket_pos(i, land)
                    sx, sy = DOOR_X + 1, 9
                    x = sx + (bx + 0.5 - sx) * u
                    y = sy + (by - sy) * u - 5 * math.sin(math.pi * u)
                    put(img, x, y, CANDY_COLORS[(i + j) % len(CANDY_COLORS)])
        for i in reversed(range(4)):
            spr = KIDS[i]
            x = kid_x(i, t)
            fr = (f // 3) % 2 if walking(i, t) else 0
            y = H - spr.h - hop(i, t)
            blit(img, spr.img(fr), x, y)
            if t > CANDY_T[i]:  # a candy peeks out of the bucket
                put(img, x + BUCKET[i][0] + 1, y + BUCKET[i][1] - 1, CANDY_COLORS[i])
        if 6.6 <= t < 9.6:  # the caption, over a darkened band of sky
            a = quant(min((t - 6.6) / 0.3, (9.6 - t) / 0.3, 1.0), 4)
            dim_rect(img, 0, 0, text_width(CAPTION, "tiny") + 2, 5, 0.7 * a)
            draw_text(img, CAPTION, 1, 0, None, font="tiny", gradient=((255, 238, 150), (255, 130, 20)),
                      shadow=(40, 4, 50), alpha=a)
        frames.append(img)
    return frames
