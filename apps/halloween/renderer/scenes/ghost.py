"""Scene: A Friendly Ghost. Green mist drifts through a little graveyard of cartoon tombstones (one says RIP, the
rest are blank). A friendly ghost rises from behind the big stone, floats out, blinks and waves: BOO! Two little
ghosts pop up to join it, and the three bob together before floating away into the night."""

import math

from busybar.canvas import FPS, H, W, blit, put, sec
from busybar.font import draw_text
from hfx import (NIGHT_TOP, frame_t, full_moon, gradient, in_moon, mist, quant, stars, tombstone)
from scenes.text import SCENE_TEXT
from sprites import GHOST, GHOST_BLINK, LITTLE_GHOST

NAME = "ghost"
TITLE = "A Friendly Ghost"
SECONDS = 15
KEYFRAMES = [(1.0, "A misty little graveyard"), (3.0, "Something rises..."), (5.4, "A friendly ghost"),
             (6.2, "It blinks"), (7.6, "BOO!"), (10.4, "Two little ghosts join in"), (13.8, "Floating away")]

MOON = (7.0, 3.5, 3.4)
STONES = [(1, 10, 6, 6, 0), (10, 11, 5, 5, 0), (17, 7, 13, 9, 0), (34, 11, 5, 5, -1), (43, 10, 7, 6, 0),
          (54, 11, 5, 5, 1), (63, 9, 7, 7, 0)]  # (x, y, w, h, tilt)
ENGRAVE = (36, 26, 56)
BIG = STONES[2]
RISE = (2.0, 4.2)
DRIFT = (4.2, 5.4)
HOME = (36, 2)
BLINK = (6.0, 6.25)
WAVE = (6.6, 8.6)
BOO = (7.0, 9.4)
LITTLE = [(9.4, STONES[1], (14, 4)), (9.9, STONES[5], (54, 4))]  # (pop-up second, stone, where it floats to)
AWAY = 12.6


def ghost_pos(t: float):
    sx = BIG[0] + (BIG[2] - GHOST.w) // 2
    if t < RISE[0]:
        return None
    if t < RISE[1]:
        u = (t - RISE[0]) / (RISE[1] - RISE[0])
        return sx, (BIG[1] + 1) - u * 7
    if t < DRIFT[1]:
        u = (t - DRIFT[0]) / (DRIFT[1] - DRIFT[0])
        e = 0.5 - 0.5 * math.cos(math.pi * u)
        return sx + (HOME[0] - sx) * e, (BIG[1] - 6) + (HOME[1] - (BIG[1] - 6)) * e
    bob = math.sin((t - DRIFT[1]) * 3.0) * 1.0
    if t > AWAY:
        return HOME[0] + (t - AWAY) * 3, HOME[1] + bob - (t - AWAY) * 4.5
    return HOME[0], HOME[1] + bob


def render():
    bg = gradient([(0, NIGHT_TOP), (8, (26, 10, 50)), (15, (30, 40, 60))])
    full_moon(bg, *MOON, halo=0.6)
    # an iron fence behind the stones
    for x in range(W):
        put(bg, x, 9, (44, 38, 66))
        if x % 4 == 1:
            for y in range(8, 15):
                put(bg, x, y, (44, 38, 66))
            put(bg, x, 7, (64, 56, 90))
    for i, (x, y, w, h, tilt) in enumerate(STONES):
        tombstone(bg, x, y, w, h, tilt, tone=(i + 1) % 3)
    text, fnt = SCENE_TEXT["tombstone"]
    draw_text(bg, text, BIG[0] + 1, BIG[1] + 2, ENGRAVE, font=fnt)
    for x in range(W):  # grass
        put(bg, x, 15, (44, 84, 48))
        if x % 4 == 1:
            put(bg, x, 14, (60, 110, 60))
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 41, 14, f, ymax=7, avoid=lambda x, y: in_moon(x, y, *MOON))
        p = ghost_pos(t)
        rising = p is not None and t < RISE[1]
        layer = img
        if rising:  # behind the big stone: draw the ghost, then the stone and its text on top again
            fr = (f // 4) % 2
            blit(layer, GHOST.img(fr), p[0], p[1])
            tombstone(layer, *BIG[:4], BIG[4], tone=0)
            draw_text(layer, text, BIG[0] + 1, BIG[1] + 2, ENGRAVE, font=fnt)
            for x in range(BIG[0], BIG[0] + BIG[2]):
                put(layer, x, 15, (44, 84, 48))
        for t0, st, (tx, ty) in LITTLE:
            if t < t0:
                continue
            u = min(1.0, (t - t0) / 0.8)
            sx = st[0] + (st[2] - LITTLE_GHOST.w) // 2
            x = sx + (tx - sx) * u
            y = st[1] + 1 + (ty - st[1] - 1) * u + math.sin((t - t0) * 3.4 + tx) * 0.8 * u
            if t > AWAY:
                x += (t - AWAY) * (2 if tx > 30 else -2)
                y -= (t - AWAY) * 4
            a = quant(min(1.0, (t - t0) / 0.4), 4)
            blit(img, LITTLE_GHOST.img((f // 4) % 2), x, y, alpha=a)
        if p is not None and not rising:
            if BLINK[0] <= t < BLINK[1]:
                spr = GHOST_BLINK.img(0)
            elif WAVE[0] <= t < WAVE[1]:
                spr = GHOST.img(2 if (f // 4) % 2 else 0)  # arms swap sides: a wave
            else:
                spr = GHOST.img((f // 4) % 2)
            blit(img, spr, p[0], p[1])
        if BOO[0] <= t < BOO[1]:
            a = quant(min((t - BOO[0]) / 0.3, (BOO[1] - t) / 0.3, 1.0), 4)
            word, bf = SCENE_TEXT["ghost"]
            draw_text(img, word, 50, 1, None, font=bf, gradient=((255, 255, 255), (160, 255, 200)),
                      shadow=(60, 14, 90), alpha=a)
        mist(img, f // 3, 14, seed=2, a=0.3, period=60)
        frames.append(img)
    return frames
