"""Scene 3 (playlist #5): Great Hall Feast. Floating candles; the yellow-and-black witch levitates the turkey."""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, lerp, phase, put, sec, vgradient
from busybar.font import draw_text
from busybar.fx import SPARKLE, Particles, Stars, sparkle
from cast import WALK, WAND, YELLOW
from sprites import CANDLE, ROAST

NAME = "great_hall"
TITLE = "Great Hall Feast"
SECONDS = 18
KEYFRAMES = [(1.0, "Candles float over the feast"), (3.5, "A witch walks in"), (7.0, "Wand up, sparkles fly"),
             (10.5, "LEVIOSA! The turkey floats"), (16.5, "...and lands safely")]

CANDLES = [(4, 0.0), (15, 1.3), (27, 2.1), (39, 0.7), (50, 1.9), (62, 2.8), (69, 0.4)]
TABLE_Y = 13
CASTER_STOP = 5
TURKEY_X, TURKEY_Y = 54, 5
CASTER = YELLOW.sprite
CASTER_Y = 16 - CASTER.h


def table(img):
    for x in range(72):
        put(img, x, TABLE_Y, (150, 92, 44))
        put(img, x, TABLE_Y + 1, (98, 56, 26))
        put(img, x, TABLE_Y + 2, (70, 38, 18))
    # plates and goblets
    for x in (20, 34, 44, 66):
        put(img, x, TABLE_Y - 1, (230, 230, 236))
        put(img, x + 1, TABLE_Y - 1, (230, 230, 236))
    for x in (24, 38, 48, 70):
        put(img, x, TABLE_Y - 1, (242, 181, 21))
        put(img, x, TABLE_Y - 2, (242, 181, 21))


def render():
    ceiling = vgradient((6, 8, 30), (22, 14, 40))
    stars = Stars(seed=5, n=20, ymax=11, period=FPS * 4, dim=0.1, bright=0.6)
    sp = Particles(seed=51)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = ceiling.copy()
        stars.draw(img, f)
        for i, (cx, ph) in enumerate(CANDLES):
            cy = 1 + round(math.sin(t * 1.6 + ph * 2) * 1.0)
            blit(img, CANDLE.img((f // 3 + i) % 4), cx - 1, cy)
            add(img, cx, cy, (255, 180, 60), 0.25)
            add(img, cx, cy + 1, (255, 160, 40), 0.15)
        table(img)

        # turkey: levitate 8.0-10.5s up, hover, float back down 14.0-16.0s
        if t < 8.0:
            ty = TURKEY_Y
        elif t < 10.5:
            ty = lerp(TURKEY_Y, 1.0, ease_in_out(phase(f, sec(8.0), sec(10.5))))
        elif t < 14.0:
            ty = 1.0 + math.sin((t - 10.5) * 3) * 0.8
        elif t < 16.0:
            ty = lerp(1.0, TURKEY_Y, ease_in_out(phase(f, sec(14.0), sec(16.0))))
        else:
            ty = TURKEY_Y
        lifted = 7.6 <= t < 16.0
        if lifted:
            for k in range(10):
                add(img, TURKEY_X + k, ty + 3, (255, 240, 170), 0.12)
        blit(img, ROAST.img(), TURKEY_X, ty)
        if lifted and f % 3 == 0:
            sp.emit(TURKEY_X + (f * 7) % 10, ty + 8, 1, vy=(0.1, 0.3), life=(6, 10), colors=SPARKLE, glow=True)

        # the witch walks in, raises the wand 6-16s
        if t < 5.0:
            wx = lerp(-10, CASTER_STOP, phase(f, sec(0.8), sec(5.0)))
            wf = WALK[(f // 3) % 4] if t > 0.8 else WALK[0]
        else:
            wx, wf = CASTER_STOP, (WAND if 6.0 <= t < 16.2 else WALK[0])
        blit(img, CASTER.img(wf), wx, CASTER_Y)
        tip = (CASTER_STOP + YELLOW.tip[0], CASTER_Y + YELLOW.tip[1])
        if 6.2 <= t < 8.0:
            # sparkle stream along an arc from wand tip to the turkey
            k = phase(f, sec(6.2), sec(8.0))
            for j in range(4):
                kk = max(0.0, k - j * 0.06)
                x = lerp(tip[0], TURKEY_X + 4, kk)
                y = lerp(tip[1], TURKEY_Y + 2, kk) - 5 * math.sin(math.pi * kk)
                add(img, x, y, (255, 245, 190), 1.0 - j * 0.22)
            sp.emit(tip[0], tip[1], 1, vx=(-0.3, 0.3), vy=(-0.3, 0.2), life=(5, 9), colors=SPARKLE, glow=True)
        if 6.0 <= t < 16.2 and f % 4 == 0:
            sparkle(img, tip[0], tip[1] - 1, f, 0.7)

        if 9.0 <= t < 14.0:
            reveal = int(lerp(0, 33, phase(f, sec(9.0), sec(9.6))))
            fade = 1 - phase(f, sec(13.5), sec(14.0))
            draw_text(img, "LEVIOSA!", 18, 6, None, font="tiny",
                      gradient=((255, 245, 200), (255, 200, 80)), shadow=(80, 40, 0), reveal=reveal, alpha=fade)
        sp.step_draw(img)
        frames.append(img)
    return frames
