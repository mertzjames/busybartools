"""Dec 24: The Star. On Christmas Eve a star rises in a spiral of sparkles and settles on top of the tree."""

import math

from busybar.canvas import FPS, blit, ease_in_out, lerp, phase, put, sec, vgradient
from busybar.fx import SPARKLE, Particles

from common import glow
from props import STAR, draw_star_glow, draw_tree, gift

NAME = "day24"
TITLE = "The Star"
SECONDS = 9
KEYFRAMES = [(0.6, "Christmas Eve: the tree waits"), (2.4, "A star rises..."), (4.4, "...and spirals up"),
             (5.6, "It lands on top!"), (8.0, "The tree glows")]

CX, TOP, BASE = 36, 4, 13


def render():
    bg = vgradient((10, 8, 30), (34, 16, 40))
    for x in range(72):
        put(bg, x, 15, (110, 66, 34))
    sp = Particles(seed=24)
    frames = []
    landed = 5.4
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        after = phase(f, sec(landed), sec(landed + 1.2))
        if after > 0:
            glow(img, CX, 7, 14, (255, 190, 90), 0.18 * after)
        draw_tree(img, CX, TOP, BASE, f, lights=1, ornaments=1, tinsel=1, twinkle=True)
        for x, w, h, body, rib in ((27, 5, 3, (214, 30, 46), (255, 214, 92)),
                                   (41, 4, 3, (60, 110, 230), (240, 240, 255))):
            gift(img, x, 15 - h, w, h, body, rib)
        # the star: rises from the bottom-left in a spiral, lands on the tip at 5.4 s
        if t < landed:
            k = ease_in_out(phase(f, sec(1.2), sec(landed)))
            if k > 0:
                r = 14 * (1 - k)
                ang = k * math.pi * 3
                sx = CX - 2 + r * math.cos(ang) - 2
                sy = lerp(16, TOP - 4, k) + r * 0.25 * math.sin(ang)
                blit(img, STAR.img(), sx, sy)
                sp.emit(sx + 2, sy + 2, 2, vx=(-0.3, 0.3), vy=(-0.1, 0.4), life=(8, 16), colors=SPARKLE,
                        glow=True)
        else:
            blit(img, STAR.img(), CX - 2, TOP - 4)
            draw_star_glow(img, CX, TOP - 3, f, strength=min(1.0, (t - landed) * 2))
            if t - landed < 0.1:
                sp.emit(CX, TOP - 3, 30, vx=(-2.0, 2.0), vy=(-1.2, 1.6), life=(10, 24), colors=SPARKLE,
                        glow=True)
        sp.step_draw(img)
        frames.append(img)
    return frames
