"""Dec 25: Christmas Morning (the finale). The tree glows over the presents, the sleigh flies past, fireworks of
stardust burst, and HO HO HO! rings out."""

import math

from busybar.canvas import FPS, blit, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles

from common import LIGHTS, TEXT_GOLD, TEXT_SHADOW, glow
from props import STAR, draw_sleigh_team, draw_star_glow, draw_tree, gift

NAME = "day25"
TITLE = "Christmas Morning"
SECONDS = 10
KEYFRAMES = [(0.8, "Christmas morning"), (2.6, "The sleigh flies past"), (4.6, "Fireworks of stardust"),
             (7.0, "HO HO HO!"), (9.4, "Merry Christmas")]

CX, TOP, BASE = 12, 4, 13
BURSTS = [(3.8, 34, 4, 0), (4.4, 56, 3, 1), (5.0, 45, 6, 2), (5.6, 64, 5, 3), (6.0, 28, 3, 4)]
GIFTS = [(2, 4, 3, (214, 30, 46), (255, 214, 92)), (16, 5, 3, (40, 150, 80), (250, 250, 255)),
         (21, 3, 2, (250, 200, 50), (214, 30, 46))]


def render():
    bg = vgradient((12, 10, 40), (40, 20, 50))
    sp = Particles(seed=25)
    fw = Particles(seed=250)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        for x in range(72):
            put(img, x, 15, (110, 66, 34))
        glow(img, CX, 8, 10, (255, 190, 90), 0.15)
        draw_tree(img, CX, TOP, BASE, f, lights=1, ornaments=1, tinsel=1, twinkle=True)
        blit(img, STAR.img(), CX - 2, TOP - 4)
        draw_star_glow(img, CX, TOP - 3, f)
        for x, w, h, body, rib in GIFTS:
            gift(img, x, 15 - h, w, h, body, rib)
        # sleigh flies across the top 1.4-4.0 s
        k = phase(f, sec(1.4), sec(4.0))
        if 0 < k < 1:
            x = lerp(-34, 74, k)
            y = 1 + 0.8 * math.sin(t * 5)
            draw_sleigh_team(img, x, y, f)
            sp.emit(x, y + 8, 2, vx=(-0.5, -0.1), vy=(-0.1, 0.3), life=(10, 20), colors=SPARKLE, glow=True)
        # stardust fireworks
        for t0, bx, by, ci in BURSTS:
            if t0 <= t < t0 + 0.07:
                c = LIGHTS[ci % len(LIGHTS)]
                for i in range(18):
                    a = i / 18 * 2 * math.pi
                    v = 1.1 + (i % 3) * 0.25
                    fw.items.append({"x": bx, "y": by, "vx": v * math.cos(a), "vy": v * math.sin(a) * 0.7,
                                     "life": 16 + i % 5, "age": 0, "c": c if i % 4 else (255, 255, 255),
                                     "g": 0.05, "drag": 0.9, "glow": True})
            if t0 - 0.5 <= t < t0:  # rising rocket trail
                ry = lerp(16, by, (t - (t0 - 0.5)) / 0.5)
                put(img, bx, ry, (255, 220, 160))
        # HO HO HO! with the scene dimmed behind it
        txt = "HO HO HO!"
        if t >= 6.4:
            dim = 0.55 * phase(f, sec(6.4), sec(6.9))
            rect(img, 0, 0, 72, 16, (0, 0, 0), dim)
            # the tree keeps glowing through the dim
            blit(img, STAR.img(), CX - 2, TOP - 4)
            w = text_width(txt)
            reveal = int((w + 1) * phase(f, sec(6.6), sec(7.4)))
            tx = 24 + (46 - w) // 2
            bounce = [round(-1.0 * max(0.0, math.sin((t - 7.4) * 6 - i))) if t > 7.4 else 0 for i in range(3)]
            # draw word by word so each HO bounces in turn
            x0 = tx
            for i, word in enumerate(txt.split(" ")):
                ww = text_width(word)
                rv = max(0, min(ww, reveal - (x0 - tx)))
                draw_text(img, word, x0, 4 + bounce[i], None, gradient=TEXT_GOLD, shadow=TEXT_SHADOW, reveal=rv)
                x0 += ww + text_width(" ") + 2
            if f % 2 == 0 and t > 7.0:
                sp.emit(tx + (f * 7) % w, 4 + (f * 3) % 7, 1, vy=(-0.4, -0.1), life=(6, 12), colors=SPARKLE,
                        glow=True)
        fw.step_draw(img)
        sp.step_draw(img)
        frames.append(img)
    return frames
