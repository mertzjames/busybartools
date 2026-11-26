"""Scene: the fireworks finale over the bay (docs/DECISIONS.md D3, D4).

Night over the water. A crowd seen from behind (hair and shoulders, a warm glow behind them so they read) watches
red, white, blue and gold fireworks (busybar.party) burst and reflect in the bay. Then HAPPY / JUNETEENTH, and
FREEDOM DAY, with a last volley.
"""

import math

from busybar.canvas import H, W, add, phase, put, sec
from busybar.party import GOLD, GOLD_LIGHT, WHITE, Firework, glitter

import jfx
from scenes.text import FINALE_BOTTOM, FINALE_MID, FINALE_TOP, RED, STARLIGHT, look

NAME = "finale"
TITLE = "Freedom Day Fireworks"
SECONDS = 16
KEYFRAMES = [(2.0, "Fireworks over the bay"), (4.6, "Red, white and blue bursts"), (7.5, "HAPPY JUNETEENTH"),
             (13.0, "FREEDOM DAY"), (15.3, "A last volley")]

WATER = 13
RED_C = (255, 64, 72)
BLUE_C = (96, 140, 255)
FW_COLORS = ((RED_C, WHITE), (BLUE_C, WHITE), (RED_C,), (BLUE_C,), (GOLD, GOLD_LIGHT), (RED_C, BLUE_C, WHITE))

SHOTS = [  # time (s), x, y, kind, colors
    (0.9, 18, 5, "peony", 0), (1.8, 50, 4, "ring", 1), (2.6, 34, 3, "willow", 4), (3.2, 62, 6, "peony", 2),
    (3.8, 10, 4, "palm", 3), (4.4, 42, 5, "peony", 5), (5.0, 26, 4, "ring", 0), (5.6, 58, 3, "willow", 4),
    (7.0, 6, 3, "peony", 1), (8.4, 66, 4, "peony", 0), (10.0, 5, 5, "ring", 2), (11.0, 66, 3, "ring", 3),
    (12.4, 14, 3, "peony", 5), (12.9, 58, 4, "peony", 1),
    (14.0, 20, 4, "ring", 0), (14.2, 52, 5, "ring", 1), (14.5, 36, 3, "willow", 4), (14.8, 10, 6, "peony", 2),
    (15.0, 62, 6, "peony", 3),
]

CROWD = [  # x (head center), hair color, shirt color, raises an arm at (s)
    (3, (84, 56, 44), (150, 60, 70), 1.0), (10, (70, 48, 40), (60, 80, 150), 4.5), (17, (96, 62, 46), (70, 120, 80), 2.0),
    (24, (64, 44, 40), (150, 120, 60), 5.1), (31, (88, 58, 44), (110, 70, 140), 3.0), (38, (76, 50, 42), (60, 110, 140), 1.9),
    (45, (92, 60, 46), (150, 80, 60), 4.4), (52, (68, 46, 40), (90, 90, 150), 2.7), (59, (84, 56, 44), (140, 60, 90), 3.6),
    (66, (74, 50, 42), (80, 120, 90), 5.4),
]


def backdrop():
    img = jfx.sky([(0, (6, 6, 28)), (8, (14, 12, 46)), (12, (30, 20, 60))])
    for x in range(W):  # the far shore, then the water
        put(img, x, WATER - 1, (34, 30, 58))
        for y in range(WATER, H):
            put(img, x, y, (12, 16, 44))
    jfx.glow(img, 36, 14, 40, (60, 40, 50), 0.35, squash=2.4)  # warm light behind the crowd
    return img


def render():
    bg = backdrop()
    shots = [Firework(500 + i, sec(t), x, y, colors=FW_COLORS[c], kind=kind, n=28, life=26)
             for i, (t, x, y, kind, c) in enumerate(SHOTS)]
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        for fw in shots:
            fw.draw(img, f)
        # reflections: mirror the sky's bright pixels into the water, broken by ripples
        px = img.load()
        for y in range(WATER, H):
            src = 2 * WATER - y - 2
            for x in range(W):
                if (x + y + f // 3) % 3 == 0:
                    continue
                r, g, b, _ = px[x, max(0, src)]
                if max(r, g, b) > 90:
                    add(img, x + (1 if (y + f // 4) % 2 else 0), y, (r, g, b), 0.3)
        # the crowd from behind: heads of hair and shoulders, a few arms raised when bursts go off
        for i, (x, hair, shirt, up) in enumerate(CROWD):
            dy = 1 if i % 3 == 1 else 0
            for ddx in (-1, 0, 1):
                put(img, x + ddx, 11 + dy, hair)
                put(img, x + ddx, 12 + dy, hair)
            put(img, x, 10 + dy, hair)
            for ddx in (-2, -1, 0, 1, 2):
                for yy in range(13 + dy, H):
                    put(img, x + ddx, yy, shirt)
            raised = (f - sec(up)) % sec(6) < sec(1.6)
            if raised:
                side = 1 if i % 2 else -1
                for k in range(4):
                    put(img, x + side * (2 + (k > 1)), 12 + dy - k, shirt if k < 2 else (150, 100, 70))
        # the greetings
        t1 = phase(f, sec(6.0), sec(6.8)) - phase(f, sec(11.2), sec(11.8))
        if t1 > 0:
            jfx.dim_rect(img, 0, 0, W - 1, H - 1, 0.55 * t1, feather=0)
            jfx.caption(img, FINALE_TOP, 0, look(RED), alpha=t1)
            jfx.caption(img, FINALE_BOTTOM, 8, look(STARLIGHT), alpha=t1)
        t2 = phase(f, sec(12.0), sec(12.8)) - phase(f, sec(15.2), sec(15.9))
        if t2 > 0:
            jfx.dim_rect(img, 0, 2, W - 1, 12, 0.55 * t2, feather=2)
            jfx.caption(img, FINALE_MID, 4, look(STARLIGHT), alpha=t2)
            glitter(img, 77, f, n=8, period=sec(2), colors=(GOLD_LIGHT, WHITE), area=(2, 1, 70, 3), strength=0.6)
        frames.append(img)
    return frames
