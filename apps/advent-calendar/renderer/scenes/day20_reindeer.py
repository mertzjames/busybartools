"""Dec 20: Reindeer. A reindeer prances across a moonlit field, takes a run-up, and lifts off into the sky."""

import math

from busybar.canvas import FPS, blit, ease_in_out, lerp, phase, put, sec
from busybar.fx import SPARKLE, Particles, Stars
from busybar.sprite import Sprite

from common import SNOW, SNOW_SHADE, ground_heights, pine, sky, snow_ground

NAME = "day20"
TITLE = "Reindeer"
SECONDS = 8
KEYFRAMES = [(1.2, "A reindeer prances in"), (3.0, "A running start..."), (4.4, "...and lift-off!"),
             (6.4, "Sparkling across the sky")]

_R = {"B": "#A8683A", "b": "#E0B888", "y": "#F0D8A8", "e": "#FFFFFF", "n": "#7A4A2A", "w": "#FFFFFF",
      "Y": "#FFD24A", "R": "#E8283A"}
REINDEER = Sprite("reindeer", _R, """
..........y.y.
..........yyy.
...........y..
..........BBB.
..........BeBB
.........RBBBn
.BBBBBBBBRY...
wBBBBBBBBB....
.BbbbbbbbB....
.B.B....B.B...
.B.B....B.B...
""", """
..........y.y.
..........yyy.
...........y..
..........BBB.
..........BeBB
.........RBBBn
.BBBBBBBBRY...
wBBBBBBBBB....
.BbbbbbbbB....
..BB...BB.....
.B..B.B..B....
""", """
..........y.y.
..........yyy.
...........y..
..........BBB.
..........BeBB
.........RBBBn
.BBBBBBBBRY...
wBBBBBBBBB....
.BbbbbbbbB....
B..B....B..B..
B...B..B...B..
""")
FLYING = Sprite("reindeer_fly", _R, """
..........y.y.
..........yyy.
...........y..
..........BBB.
..........BeBB
.........RBBBn
.BBBBBBBBRY...
wBBBBBBBBB....
BBbbbbbbbBBB..
B..........B..
..............
""")


def render():
    bg = sky(((4, 8, 34), (20, 32, 74)))
    stars = Stars(seed=200, n=24, ymax=10, period=FPS * 4, dim=0.1, bright=0.8)
    hills = ground_heights(20, 13.5, 0.8, 0.09)
    sp = Particles(seed=20)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        # big moon
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                d = math.hypot(dx, dy)
                if d <= 4.2:
                    put(img, 60 + dx, 4 + dy, (250, 244, 210) if d < 3.4 else (200, 196, 170))
        put(img, 59, 3, (220, 214, 180))
        put(img, 61, 6, (220, 214, 180))
        snow_ground(img, hills)
        for cx, base, hh in ((5, 14, 6), (12, 14, 4), (68, 14, 5)):
            pine(img, cx, base, hh)
        gallop = (f // 2) % 3
        if t < 2.4:  # prance in
            x = lerp(-15, 20, phase(f, 0, sec(2.4)))
            y = 3 - abs(math.sin(t * 7)) * 1.2
            blit(img, REINDEER.img(gallop), x, y)
        elif t < 3.6:  # run-up
            x = lerp(20, 34, phase(f, sec(2.4), sec(3.6)))
            blit(img, REINDEER.img(gallop), x, 3 - abs(math.sin(t * 10)) * 0.8)
        else:  # lift-off and arc away over the moon
            k = ease_in_out(phase(f, sec(3.6), sec(7.6)))
            x = lerp(34, 80, k)
            y = 3 - 9 * math.sin(math.pi * k * 0.75) + 2 * k
            blit(img, FLYING.img(), x, y)
            if f % 1 == 0:
                sp.emit(x + 1, y + 8, 2, vx=(-0.6, -0.1), vy=(-0.1, 0.3), life=(8, 18), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        frames.append(img)
    return frames
