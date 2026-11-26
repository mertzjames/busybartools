"""Scene: The Shamrock Field. The view drifts across a meadow of shamrocks nodding in the breeze, gusts rolling
through in waves. The drift slows, and one clover catches the light: it has four leaves. It rises up, big and
glowing, and LUCKY! appears beside it."""

import math
import random

from busybar.canvas import W, ease_in_out, ease_out, mix, phase, put, sec, vgradient
from busybar.font import text_width
from busybar.party import hash01
from pfx import GOLD_HI, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, caption, dim_rect, glow, shamrock, sparkle4

NAME = "shamrocks"
TITLE = "The Shamrock Field"
SECONDS = 15
KEYFRAMES = [(1.0, "A meadow of shamrocks in the breeze"), (5.0, "Gusts roll through"),
             (7.8, "One clover catches the light"), (9.4, "It has four leaves"), (12.5, "LUCKY!")]

PAN_END = sec(7.4)
GLINT = (sec(7.4), sec(8.6))
RISE = (sec(8.6), sec(10.2))
WORD = sec(10.4)
CLOVER = (18, 7)  # where the found clover settles
# layers: (row, size, speed px/frame, spacing, colors, seed)
LAYERS = [
    (6, 0, 0.14, 5, ((30, 120, 50), (80, 170, 90), (18, 80, 34)), 1),
    (12, 1, 0.42, 11, (SHAMROCK, SHAMROCK_HI, SHAMROCK_DK), 3),
]
FIND_LAYER = 1
FIND_SCREEN_X = 40  # where the four-leaf clover stops when the drift ends


def pan(f: int) -> float:
    """How far the view has drifted (in front-layer pixels): constant speed, easing to a stop at PAN_END."""
    slow = sec(2.0)
    if f < PAN_END - slow:
        return f
    if f < PAN_END:
        u = (f - (PAN_END - slow)) / slow
        return PAN_END - slow + slow * (u - u * u / 2)
    return PAN_END - slow / 2


def plants(layer: int):
    row, size, speed, spacing, colors, seed = LAYERS[layer]
    rng = random.Random(seed)
    span = int(W + pan(sec(15)) * speed + 20)
    out = []
    x = -8.0
    while x < span:
        out.append((x, row + rng.choice((0, 0, 1)), rng.random()))
        x += spacing + rng.uniform(-1.0, 1.0)
    return out


def background():
    img = vgradient((70, 120, 196), (16, 54, 22))
    for y in range(0, 4):  # a pale sky band at the top
        for x in range(W):
            put(img, x, y, mix((86, 140, 214), (170, 206, 230), y / 3))
    for x in range(W):  # the far edge of the meadow, then dark soil-green so the leaves stand out
        top = 4 + (1 if math.sin(x * 0.3) > 0.6 else 0)
        for y in range(top, 16):
            put(img, x, y, mix((22, 64, 28), (6, 24, 10), (y - top) / 6))
    return img


def render():
    bg = background()
    layers = [plants(i) for i in range(len(LAYERS))]
    end = pan(sec(SECONDS))
    # the four-leaf clover: the front-layer plant nearest to where it should stop
    fx = FIND_SCREEN_X + end * LAYERS[FIND_LAYER][2]
    find = min(range(len(layers[FIND_LAYER])), key=lambda i: abs(layers[FIND_LAYER][i][0] - fx))
    _, fy0, _ = layers[FIND_LAYER][find]
    layers[FIND_LAYER][find] = (fx, fy0, 0.5)
    # keep its neighbours clear of it, so it stands alone when the drift stops
    keep = [(i, p) for i, p in enumerate(layers[FIND_LAYER]) if i == find or abs(p[0] - fx) >= 10]
    find = [i for i, _ in keep].index(find)
    layers[FIND_LAYER] = [p for _, p in keep]
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        p = pan(f)
        rise = ease_in_out(phase(f, *RISE))
        for li, plist in enumerate(layers):
            row, size, speed, spacing, (c, hi, stem), seed = LAYERS[li]
            for i, (x0, y0, ph) in enumerate(plist):
                x = x0 - p * speed
                if not -6 <= x < W + 6:
                    continue
                # the breeze: a wave rolling left to right, with stronger gusts now and then
                gust = 0.6 + 0.4 * math.sin(f * 0.05)
                w = math.sin(x * 0.25 - f * 0.32 + ph * 2) * gust
                sway = 1 if w > 0.45 else (-1 if w < -0.75 else 0)
                four = li == FIND_LAYER and i == find
                if four and f >= RISE[0]:
                    continue
                shamrock(img, x, y0, size, c, hi, stem, four=four, sway=0 if four and f >= GLINT[0] else sway)
        if f >= GLINT[0]:
            sx, sy = FIND_SCREEN_X, fy0
            if f < RISE[0]:
                k = phase(f, *GLINT)
                glow(img, sx, sy, 5, (255, 236, 140), 0.5 * math.sin(math.pi * min(1.0, k * 1.3)))
                sparkle4(img, sx + 2, sy - 3, max(0.0, math.sin(math.pi * k * 2)), (255, 255, 230))
            else:
                dim_rect(img, 0, 0, W - 1, 15, 0.65 * rise)
                cx = sx + (CLOVER[0] - sx) * rise
                cy = sy + (CLOVER[1] - sy) * rise
                glow(img, cx, cy, 4 + 4 * rise, (255, 220, 120), 0.3 * rise)
                if rise < 0.5:
                    shamrock(img, cx, cy, 1, four=True)
                else:
                    shamrock(img, cx, cy, 2, four=True)
        if f >= RISE[1]:
            # sparkles circling the clover, and the word
            for i in range(6):
                a = 2 * math.pi * (i / 6 + (f - RISE[1]) / sec(4))
                k = 0.5 + 0.5 * math.sin(f * 0.4 + i * 1.7)
                sparkle4(img, CLOVER[0] + 9 * math.cos(a), CLOVER[1] + 6.5 * math.sin(a), k, GOLD_HI)
            k = ease_out(phase(f, WORD, WORD + sec(0.8)))
            w = text_width("LUCKY!", "big")
            caption(img, "LUCKY!", 4, k, x=34 + (38 - w) // 2, back=0.3)
            for i in range(5):
                tw = hash01(31, i, (f - WORD) // 4)
                if tw > 0.7 and f > WORD + 8:
                    sparkle4(img, 36 + i * 7, 2 + (i % 2) * 10, tw, GOLD_HI)
        frames.append(img)
    return frames
