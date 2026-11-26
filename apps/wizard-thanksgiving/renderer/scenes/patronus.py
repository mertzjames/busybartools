"""Scene 5 (playlist #8): Pumpkin Patronus. A glowing silver turkey bursts from the green-and-silver witch's wand."""

import math
import random

from PIL import ImageFilter

from busybar.canvas import FPS, add, blit, lerp, phase, put, sec, tint, vgradient
from busybar.font import draw_text
from busybar.fx import Particles, Stars, puff
from cast import GREEN, STAND, WAND
from sprites import TURKEY

NAME = "patronus"
TITLE = "Pumpkin Patronus"
SECONDS = 15
KEYFRAMES = [(1.5, "A dark, misty wood"), (3.6, "Wand raised, light gathers"), (6.0, "A silver turkey bursts out"),
             (10.0, "...and gallops back"), (13.5, "EXPECTO PIE!")]

SILVER = (170, 215, 255)
CASTER = GREEN.sprite
CASTER_X, CASTER_Y = 2, 16 - CASTER.h
TIP = (CASTER_X + GREEN.tip[0], CASTER_Y + GREEN.tip[1])


def trees(img):
    for x, w in ((18, 2), (33, 1), (47, 2), (60, 1), (68, 2)):
        for xx in range(x, x + w):
            for y in range(0, 16):
                put(img, xx, y, (10, 18, 24))
        put(img, x - 1, 3 + x % 4, (10, 18, 24))
        put(img, x + w, 6 + x % 3, (10, 18, 24))


def glow_sprite(i: int, flip: bool):
    base = tint(TURKEY.img(i, flip=flip), SILVER)
    halo = base.filter(ImageFilter.GaussianBlur(1.2))
    return base, halo


def render():
    rng = random.Random(9)
    bg = vgradient((3, 6, 16), (10, 18, 30))
    trees(bg)
    stars = Stars(seed=9, n=8, ymax=5, period=FPS * 4, dim=0.05, bright=0.4)
    mist = Particles(seed=91)
    sp = Particles(seed=92)
    sprites_cache = {(i, fl): glow_sprite(i, fl) for i in range(4) for fl in (False, True)}
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        # low drifting mist bands
        for x in range(72):
            a = 0.10 + 0.07 * math.sin(x * 0.25 + t * 0.8) + 0.05 * math.sin(x * 0.6 - t * 1.3)
            add(img, x, 14, (90, 120, 150), a)
            add(img, x, 15, (90, 120, 150), a * 1.3)

        raised = 2.0 <= t < 13.0
        blit(img, CASTER.img(WAND if raised else STAND), CASTER_X, CASTER_Y)

        # light gathers at the wand tip 2.4-4.0s
        if 2.4 <= t < 13.0:
            k = phase(f, sec(2.4), sec(4.0))
            r = 0.6 + 2.0 * k + (0.4 * math.sin(t * 8) if t >= 4.0 else 0)
            if t >= 4.0:
                r *= 0.6
            puff(img, TIP[0], TIP[1], r, (220, 240, 255), 0.6)
            add(img, TIP[0], TIP[1], (255, 255, 255), 1.0)
        if 4.0 <= t < 4.2:
            sp.emit(TIP[0], TIP[1], 16, vx=(-1.5, 2.0), vy=(-1.2, 1.2), life=(8, 16), colors=(SILVER, (255, 255, 255)),
                    glow=True)

        # patronus: gallops right 4.0-8.6s, turns, gallops back left high 9.0-12.6s, dissolves into the wand
        pt = None
        if 4.0 <= t < 8.6:
            pt = (lerp(TIP[0] - 4, 76, phase(f, sec(4.0), sec(8.6))), 6, False)
        elif 9.0 <= t < 12.6:
            pt = (lerp(76, TIP[0] + 2, phase(f, sec(9.0), sec(12.6))), 3, True)
        if pt:
            px, py, flip = pt
            gf = (f // 2) % 4
            hop = -1.5 * abs(math.sin(t * 9))
            base, halo = sprites_cache[(gf, flip)]
            blit(img, halo, px, py + hop, alpha=0.45)
            blit(img, base, px, py + hop, alpha=1.0)
            if f % 1 == 0:
                tail_x = px + (11 if flip else 0)
                mist.emit(tail_x, py + 4 + rng.uniform(-2, 3), 1, vx=(-0.1, 0.1), vy=(-0.15, 0.0), life=(10, 20),
                          colors=(SILVER, (120, 170, 220)), glow=True)
        if 12.6 <= t < 12.8:
            sp.emit(TIP[0], TIP[1], 14, vx=(-1.2, 1.2), vy=(-1.0, 1.0), life=(8, 14),
                    colors=(SILVER, (255, 255, 255)), glow=True)
        mist.step_draw(img)
        sp.step_draw(img)

        if 12.8 <= t < 15.0:
            r = int(lerp(0, 48, phase(f, sec(12.8), sec(13.6))))
            fade = 1 - phase(f, sec(14.5), sec(15.0))
            draw_text(img, "EXPECTO PIE!", 18, 6, None, font="tiny", gradient=((235, 245, 255), SILVER),
                      shadow=(20, 40, 70), reveal=r, alpha=fade)
        frames.append(img)
    return frames
