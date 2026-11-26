"""Dec 8: Penguin. A penguin waddles onto the ice, belly-slides across in a spray of snow, and flaps happily."""

import math

from busybar.canvas import FPS, blit, ease_in_out, lerp, phase, put, sec, vgradient
from busybar.fx import Particles
from busybar.sprite import Sprite

from common import Snow

NAME = "day08"
TITLE = "Penguin"
SECONDS = 8
KEYFRAMES = [(1.0, "A penguin waddles in"), (2.8, "Hop..."), (4.4, "Wheee! A belly slide"),
             (7.2, "Flap flap!")]

_P = {"K": "#26305E", "k": "#4A5C96", "W": "#F4F6FF", "O": "#FF9A1E", "e": "#FFFFFF", "c": "#FFC0C8"}
PENGUIN = Sprite("penguin", _P, """
...kKK..
..KKKKK.
..KKeKOO
..KKKKc.
.kKKWWK.
KKKWWWK.
.KKWWWK.
..KWWWK.
..KKKK..
..OO.O..
""", """
...kKK..
..KKKKK.
..KKeKOO
..KKKKc.
.kKKWWK.
KKKWWWK.
.KKWWWK.
..KWWWK.
..KKKK..
...O.OO.
""")
FLAP = Sprite("penguin_flap", _P, """
...kKK...
..KKKKK..
..KKeKOO.
..KKKKc..
K.KKWWK.K
.KKWWWKK.
..KWWWK..
..KWWWK..
..KKKK...
..OO.OO..
""", """
...kKK...
..KKKKK..
..KKeKOO.
..KKKKc..
..KKWWK..
.KKWWWKK.
K.KWWWK.K
..KWWWK..
..KKKK...
..OO.OO..
""")
SLIDE = Sprite("penguin_slide", _P, """
.....kKKKK....
..kKKKKKKKKe..
KKKKKKKKKKKKOO
.OOWWWWWWWWK..
""")


def render():
    bg = vgradient((50, 100, 186), (120, 162, 222))
    # distant icebergs
    for x in range(72):
        h = 9 - (2.5 * max(0, 1 - abs(x - 12) / 9) + 3.5 * max(0, 1 - abs(x - 58) / 7))
        for y in range(int(h), 12):
            put(bg, x, y, (150, 190, 235) if y > h + 0.5 else (235, 244, 255))
    for x in range(72):
        put(bg, x, 12, (240, 248, 255))
        for y in range(13, 16):
            put(bg, x, y, (176, 202, 240) if (x + y * 3) % 11 else (130, 168, 224))
    snow = Snow(seed=88, n=14, speed=(0.1, 0.25), ymax=12)
    sp = Particles(seed=8)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        snow.draw(img, f, alpha=0.9)
        if t < 2.4:  # waddle in
            x = lerp(-9, 18, phase(f, 0, sec(2.4)))
            tilt = 1 if (f // 3) % 2 else 0
            blit(img, PENGUIN.img((f // 3) % 2), x, 2 + tilt * 0)
        elif t < 3.2:  # hop
            k = phase(f, sec(2.4), sec(3.2))
            blit(img, PENGUIN.img(0), 18 + k * 3, 2 - 3 * math.sin(math.pi * k))
        elif t < 6.2:  # belly slide
            k = ease_in_out(phase(f, sec(3.2), sec(6.2)))
            x = lerp(19, 52, k)
            blit(img, SLIDE.img(), x, 8)
            if k < 0.95 and f % 1 == 0:
                sp.emit(x, 11, 2, vx=(-1.2, -0.3), vy=(-0.9, -0.2), life=(6, 12), colors=((255, 255, 255),
                        (210, 230, 255)), gravity=0.12)
        else:  # pop up and flap
            blit(img, FLAP.img((f // 2) % 2), 54, 2)
            if (f // 2) % 4 == 0:
                put(img, 60, 1, (255, 255, 255), 0.7)
        sp.step_draw(img)
        frames.append(img)
    return frames
