"""Dec 15: Toy Soldier. A wind-up toy drummer marches in, beats a drum roll with sparks, salutes and marches on."""

import math

from busybar.canvas import FPS, add, blit, lerp, phase, put, sec, vgradient
from busybar.fx import SPARKLE, Particles
from busybar.sprite import Sprite

NAME = "day15"
TITLE = "Toy Soldier"
SECONDS = 8
KEYFRAMES = [(1.0, "A toy drummer marches in"), (3.2, "Rat-a-tat-tat!"), (5.6, "A smart salute"),
             (7.4, "And off he marches")]

_S = {"K": "#3A3A8E", "k": "#5A5AB8", "Y": "#FFD24A", "S": "#F6C79C", "B": "#4A8CFF", "p": "#FF8A9A",
      "R": "#D8202E", "r": "#9A1222", "W": "#F4F4FF", "T": "#2A2A6A", "P": "#FF3040"}
SOLDIER = Sprite("toy_soldier", _S, """
...P...
..KKK..
.KkKKK.
.KKYKK.
.KKKKK.
.SSSSS.
.SBSBS.
.SpSpS.
YRWRWRY
RRRWRRR
.RWRWR.
.RRYRR.
.WW.WW.
.WW.WW.
.TT.TT.
""", """
...P...
..KKK..
.KkKKK.
.KKYKK.
.KKKKK.
.SSSSS.
.SBSBS.
.SpSpS.
YRWRWRY
RRRWRRR
.RWRWR.
.RRYRR.
.WW.WW.
.WW..WW
.TT..TT
""", """
...P...
..KKK..
.KkKKK.
.KKYKK.
.KKKKK.
.SSSSS.
.SBSBS.
.SpSpS.
YRWRWRY
RRRWRRR
.RWRWR.
.RRYRR.
.WW.WW.
WW..WW.
TT..TT.
""")
SALUTE = Sprite("toy_soldier_salute", _S, """
...P....
..KKK...
.KkKKKR.
.KKYKKR.
.KKKKKR.
.SSSSSR.
.SBSBSR.
.SpSpRR.
YRWRWR..
RRRWRR..
.RWRWR..
.RRYRR..
.WW.WW..
.WW.WW..
.TT.TT..
""")
DRUM = Sprite("drum", {"W": "#F4F4FF", "R": "#E8283A", "Y": "#FFD24A"}, """
YYYYY
RWRWR
WRWRW
YYYYY
""")


def render():
    bg = vgradient((14, 30, 30), (24, 56, 50))
    # toy shelf / floorboards
    for x in range(72):
        put(bg, x, 15, (140, 90, 40))
        put(bg, x, 14, (180, 120, 60) if x % 12 else (120, 70, 30))
    # wallpaper stripes
    for x in range(0, 72, 6):
        for y in range(14):
            put(bg, x, y, (30, 70, 60))
    sp = Particles(seed=15)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        step = [1, 0, 2, 0][(f // 3) % 4]
        drumming = False
        if t < 2.2:
            x = lerp(-8, 32, phase(f, 0, sec(2.2)))
            frame = step
        elif t < 5.0:
            x, frame, drumming = 32, 0, True
        elif t < 6.4:
            x, frame = 32, None
        else:
            x = lerp(32, 76, phase(f, sec(6.4), sec(8.0)))
            frame = step
        bob = -1 if frame in (1, 2) else 0
        if frame is None:
            blit(img, SALUTE.img(), x, -1)
        else:
            blit(img, SOLDIER.img(frame), x, -1 + bob)
            blit(img, DRUM.img(), x + 1, 10 + bob)
            # drumsticks
            up = (f // 2) % 2 if drumming else 0
            for side, sx in ((0, x + 1), (1, x + 5)):
                hit = drumming and up == side
                sy = 8 + bob if not hit else 9 + bob
                put(img, sx, sy, (230, 200, 150))
                put(img, sx + (1 if side == 0 else -1), sy + 1, (230, 200, 150))
                if hit and drumming:
                    add(img, sx + (1 if side == 0 else -1), 10 + bob, (255, 255, 200), 0.6)
            if drumming and f % 2 == 0:
                sp.emit(x + 3, 9, 2, vx=(-0.9, 0.9), vy=(-0.9, -0.2), life=(5, 10), colors=SPARKLE, glow=True)
            # wind-up key on the back
            ky = 9 + bob
            put(img, x - 1, ky, (255, 214, 92))
            turn = (f // 2) % 2
            put(img, x - 2, ky - 1 + turn * 2, (255, 214, 92))
        sp.step_draw(img)
        frames.append(img)
    return frames
