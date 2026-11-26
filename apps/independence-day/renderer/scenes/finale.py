"""Scene: the finale (docs/DECISIONS.md D3). Volleys of red, white and blue fireworks fill the night sky, three at a
time like a flag; a big gold ring bursts in the middle and its flash spells out HAPPY / 4TH OF JULY, which glitters
as red, white and blue confetti drifts down behind it."""

import math

from busybar.canvas import W, mix, phase, put, sec
from busybar.font import draw_text, text_width
from busybar.party import Confetti, Firework, glitter

import jfx
from jfx import FW_BLUE, FW_GOLD, FW_RED, FW_WHITE

NAME = "finale"
TITLE = "Happy 4th!"
SECONDS = 14
KEYFRAMES = [(1.4, "Red, white and blue"), (3.4, "Three at a time"), (5.4, "Faster and faster"),
             (6.9, "A big gold ring"), (8.4, "HAPPY 4TH OF JULY"), (12.6, "Confetti and glitter")]

BOOM = sec(6.6)  # the gold ring that writes the greeting
HEAD, SUB = "HAPPY", "4TH OF JULY"
HEAD_Y, SUB_Y = 0, 8


def shells():
    s = []
    seed = 1
    # flag volleys: red, white and blue side by side, three times, quicker each time
    for k, (t0, y) in enumerate(((0.8, 5), (2.6, 4), (4.2, 6))):
        cx = (20, 50, 34)[k]
        for j, c in enumerate((FW_RED, FW_WHITE, FW_BLUE)):
            s.append(Firework(seed, sec(t0) + j * 3, cx - 14 + 14 * j, y + (j % 2), (c,), "peony", n=22, speed=0.75))
            seed += 1
    for t0, x, y, cols, kind in ((1.8, 62, 4, (FW_GOLD,), "palm"), (3.6, 8, 4, None, "willow"),
                                 (5.2, 56, 3, (FW_RED, FW_WHITE), "ring"), (5.5, 14, 5, (FW_BLUE, FW_WHITE), "ring"),
                                 (5.9, 36, 3, (FW_RED,), "peony"), (6.1, 66, 6, (FW_BLUE,), "peony")):
        s.append(Firework(seed, sec(t0), x, y, cols, kind, n=24))
        seed += 1
    s.append(Firework(99, BOOM, 36, 7, (FW_GOLD, (255, 236, 160)), "ring", speed=1.6, life=30))
    return s


def render():
    base = jfx.sky([(0, (4, 6, 28)), (9, (12, 12, 46)), (15, (30, 14, 50))])
    fws = shells()
    confetti = Confetti(21, BOOM + sec(1.0), 36, -1, n=60, vx=(-2.4, 2.4), vy=(-0.4, 0.6),
                        colors=(FW_RED, FW_WHITE, FW_BLUE, FW_RED, FW_WHITE, FW_BLUE, FW_GOLD), spread=34, stagger=30)
    hx = (W - text_width(HEAD)) // 2
    sx = (W - text_width(SUB)) // 2
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        for fw in fws:
            fw.draw(img, f)
        # the greeting is revealed outward from the gold ring's center as the ring expands
        r = (f - BOOM) * 2.4
        if r > 0:
            cap = min(1.0, r / 60)
            jfx.dim_rect(img, sx - 1, 0, sx + text_width(SUB), 15, 0.6 * cap, feather=2)
            confetti.draw(img, f, 0.8)  # behind the words, over the dimmed sky
            for text, x0, y0, grad in ((HEAD, hx, HEAD_Y, (jfx.GOLD_LIGHT, jfx.GOLD)),
                                       (SUB, sx, SUB_Y, ((255, 232, 232), (255, 96, 104)))):
                layer = base.copy()
                layer.paste((0, 0, 0, 0), (0, 0, W, 16))
                draw_text(layer, text, x0, y0, None, font="big", gradient=grad, shadow=(30, 10, 40))
                px = layer.load()
                for y in range(16):
                    for x in range(W):
                        if px[x, y][3] and math.hypot(x - 36, (y - 7) * 2) <= r:
                            put(img, x, y, px[x, y][:3])
            if f >= BOOM + sec(1.6):  # glints run across the words
                glitter(img, 8, f, n=10, period=40, colors=((255, 255, 255), jfx.GOLD_LIGHT), area=(sx, 0, sx + 61, 15),
                        strength=0.7)
        frames.append(img)
    return frames
