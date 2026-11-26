"""Scene: The Black Cat. A black cat (deep violet-grey with a moonlit rim and glowing yellow-green eyes) pads
along the top of a wooden fence and stops in front of the full moon. A bat flits by: the cat arches its back and
puffs up its tail. Then it settles down, sits, and gives a slow, smug blink. A jack-o'-lantern glows on a post."""

import math

from busybar.canvas import FPS, H, W, add, blit, put, sec
from hfx import (NIGHT_MID, NIGHT_TOP, cobweb, frame_t, full_moon, gradient, in_moon, pumpkin, pumpkin_glow,
                 stars)
from sprites import BAT, CAT

NAME = "cat"
TITLE = "The Black Cat"
SECONDS = 14
KEYFRAMES = [(1.6, "A black cat on the fence"), (4.6, "It stops by the moon"), (6.0, "A bat flits past"),
             (6.8, "Arched back, puffed tail"), (9.6, "It sits down"), (11.2, "A slow blink"),
             (13.0, "Glowing eyes")]

MOON = (50.0, 6.0, 6.2)
RAIL = 11  # the fence's top rail; the cat's feet stand on row RAIL - 1
STOP_X = 42
WALK = (0.0, 4.6)
BAT_T = (5.2, 7.0)
ARCH = (5.9, 8.6)
SIT = 8.9
BLINKS = ((11.0, 11.35), (12.6, 12.9))
POST_X = 63


def cat_state(t: float):
    """(x, frame index)."""
    if t < WALK[1]:
        u = t / WALK[1]
        x = -16 + u * (STOP_X + 16)
        return x, (int(t * FPS) // 3) % 2
    if ARCH[0] <= t < ARCH[1]:
        return STOP_X, 2
    if t >= SIT:
        blink = any(a <= t < b for a, b in BLINKS)
        return STOP_X, 4 if blink else 3
    return STOP_X, 0


def render():
    bg = gradient([(0, NIGHT_TOP), (9, NIGHT_MID), (15, (60, 20, 76))])
    full_moon(bg, *MOON, halo=0.8)
    cobweb(bg, "tl", 6, a=0.5)
    # the fence: a top rail, boards with gaps, and a taller post holding a jack-o'-lantern
    for x in range(W):
        put(bg, x, RAIL, (150, 112, 84))
        put(bg, x, RAIL + 1, (104, 76, 60))
        for y in range(RAIL + 2, H):
            if x % 4 != 3:
                put(bg, x, y, (92, 66, 56) if x % 4 else (110, 80, 64))
    for y in range(8, H):
        for dx in range(3):
            put(bg, POST_X + 2 + dx, y, (120, 88, 68) if dx < 2 else (88, 64, 52))
    pumpkin_glow(bg, POST_X, 2, 7, 6, 0.8)
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 51, 16, f, ymax=9, avoid=lambda x, y: in_moon(x, y, *MOON) or (x < 7 and y < 7) or x >= POST_X)
        pumpkin(img, POST_X, 2, 7, 6, "classic", lit=1.0, f=f, seed=9, small=True)
        if BAT_T[0] <= t < BAT_T[1]:  # a bat flits right to left above the cat
            u = (t - BAT_T[0]) / (BAT_T[1] - BAT_T[0])
            blit(img, BAT.img((f // 2) % len(BAT), flip=True), W - u * (W + 10), 1 + 1.5 * math.sin(u * 9))
        x, fr = cat_state(t)
        jitter = 1 if fr == 2 and (f // 2) % 4 == 0 and t < ARCH[0] + 0.8 else 0
        blit(img, CAT.img(fr), x + jitter, RAIL - CAT.h)
        if fr in (2, 3) or (fr == 0 and t >= WALK[1]):  # glowing eyes: a soft lime halo
            ey = RAIL - CAT.h + (3 if fr in (0, 2) else 2)
            ex = x + jitter + (13 if fr in (0, 2) else 11)
            k = 0.5 if fr == 2 else 0.25
            for dx, dy in ((-1, 0), (3, 0), (1, -1), (1, 1)):
                add(img, ex + dx, ey + dy, (90, 140, 20), k)
        frames.append(img)
    return frames
