"""Scene: the Juneteenth flag is raised on a bright morning and waves (docs/DECISIONS.md D3, D5).

The official design, drawn by hand for 14 rows: a white five-point star inside a white outlined nova, centered on
a field split by a broad arc (a new horizon), blue above and red below. People below watch it go up, cheer when
it reaches the top, and wave small flags of their own; a gust at 9 s makes it snap out.
"""

import math

from busybar.canvas import H, W, ease_in_out, phase, put, sec

import jfx

NAME = "flag"
TITLE = "The Juneteenth Flag"
SECONDS = 14
KEYFRAMES = [(0.6, "A flagpole on a bright morning"), (3.0, "The Juneteenth flag goes up"),
             (6.0, "At the top: a cheer"), (9.8, "A gust snaps it out"), (12.5, "Small flags wave below")]

POLE_X = 12
FLAG_W = 21
FLAG_H = 14
TOP = 1

CROWD = [  # x, skin, shirt, style, hat, height, raise time (s), small flag
    (36, jfx.SKIN[1], (236, 232, 220), "puff", None, 10, 5.2, False),
    (43, jfx.SKIN[3], (230, 70, 80), "wrap", (250, 200, 60), 10, 5.4, True),
    (50, jfx.SKIN[0], (90, 170, 110), "short", None, 10, 5.3, False),
    (57, jfx.SKIN[4], (250, 210, 90), "buns", None, 8, 5.5, True),
    (66, jfx.SKIN[2], (120, 150, 230), "cap", (210, 40, 50), 10, 5.6, False),
]


def clouds(img, f):
    """Soft clouds drifting right to left (seamless over the scene)."""
    for x0, y, w, speed in ((20, 3, 9, 0.10), (52, 1, 12, 0.07), (80, 5, 8, 0.12), (106, 2, 10, 0.09)):
        x = (x0 - f * speed) % 116 - 22
        for dx in range(w):
            k = math.sin(math.pi * (dx + 0.5) / w)
            put(img, x + dx, y, (214, 226, 246), 0.35 * k)
            put(img, x + dx, y + 1, (196, 212, 240), 0.55 * k)
            if 1 < dx < w - 2:
                put(img, x + dx, y - 1, (220, 230, 248), 0.3 * k)


def render():
    base = jfx.sky([(0, (64, 120, 210)), (8, (112, 160, 228)), (13, (170, 200, 240))])
    jfx.glow(base, 66, 2, 7, (255, 240, 190), 0.6)
    for dx in (0, 1):
        for dy in (0, 1):
            put(base, 66 + dx, 2 + dy, (255, 250, 226))
    frames = []
    t = 0.0
    for f in range(sec(SECONDS)):
        img = base.copy()
        clouds(img, f)
        for x in range(W):  # grass
            put(img, x, 14, jfx.GRASS if x % 3 else jfx.GRASS_HI)
            put(img, x, 15, jfx.GRASS_DK)
        jfx.pole(img, POLE_X, 0, 15)
        rise = ease_in_out(phase(f, sec(0.8), sec(5.0)))
        y0 = round(H - (H - TOP) * rise)
        gust = math.sin(math.pi * phase(f, sec(8.8), sec(11.5)))
        t += 1 / (32 - 12 * gust)
        unfurl = 0.55 + 0.45 * ease_in_out(phase(f, sec(0.8), sec(5.4)))
        jfx.draw_flag(img, POLE_X + 1, y0, FLAG_W, FLAG_H, t, amp=0.9 + 0.5 * gust, unfurl=unfurl)
        # the crowd: watching, then a cheer, then waving
        for i, (x, skin, shirt, style, hat, hgt, up, small) in enumerate(CROWD):
            lift = ease_in_out(phase(f, sec(up), sec(up + 0.5)))
            wave = math.sin(2 * math.pi * (f / 12 + i * 0.27))
            if small and f > sec(7.0):
                arms = (0.04, 0.38 + 0.06 * wave)
            else:
                arms = (0.42 * lift + 0.04 * wave * lift, 0.42 * lift - 0.04 * wave * lift)
            hop = -1 if lift > 0.9 and f < sec(7.5) and (f // 3 + i) % 4 == 0 else 0
            hands = jfx.person(img, x, 15 + hop, skin, shirt, None, style=style, hat=hat, arms=arms, height=hgt)
            if small and f > sec(7.0):
                hx, hy = hands["r"]
                for yy in range(0, hy + 1):  # a stick held high, the little flag above everyone's heads
                    put(img, hx, yy, (200, 170, 120))
                ft = f / 10 + i * 0.4
                jfx.draw_flag(img, hx + 1, 0, 7, 5, ft, amp=0.8, wavelength=8.0, nova=3)
        frames.append(img)
    return frames
