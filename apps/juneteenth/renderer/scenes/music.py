"""Scene: music and dancing in the park at sunset (docs/DECISIONS.md D3, D6).

String lights twinkle over a small bandstand: a drummer, a saxophone and a bass guitar. Music notes float up,
and in the park neighbors dance to the beat with arms up and little hops. The sunset sky is darkened and the
grass is a dark band, so the small figures stand out instead of dissolving into the glow.
"""

import math

from busybar.canvas import H, W, add, put, sec
from busybar.party import GOLD, PINK, CYAN, LIME, string_lights

import jfx

NAME = "music"
TITLE = "Music in the Park"
SECONDS = 14
KEYFRAMES = [(1.0, "A band plays under string lights"), (5.0, "Neighbors start to dance"),
             (9.0, "Arms up on the beat"), (12.5, "Notes float over the park")]

BEAT = 8  # frames per beat (about 112 beats a minute)
GROUND = 14

NOTE = [".#", ".#", "##"]  # a note: stem and head (2 x 3)

DANCERS = [  # x, skin, shirt, pants, style, hat, dress, height, phase
    (29, jfx.SKIN[2], (255, 120, 60), (60, 70, 130), "puff", None, False, 11, 0),
    (37, jfx.SKIN[0], (250, 220, 90), None, "wrap", (60, 200, 140), True, 11, 1),
    (45, jfx.SKIN[4], (110, 200, 255), (230, 230, 230), "cap", (240, 240, 240), False, 11, 2),
    (52, jfx.SKIN[3], (255, 110, 170), None, "buns", None, False, 8, 3),
    (58, jfx.SKIN[5], (150, 230, 120), (70, 60, 110), "short", None, False, 11, 1),
    (65, jfx.SKIN[1], (200, 140, 255), None, "long", None, True, 11, 0),
]


def backdrop():
    img = jfx.sky([(0, (22, 20, 66)), (6, (78, 38, 96)), (10, (160, 74, 70))])
    for x in range(W):  # a dark tree line, then the grass
        top = 10 - (1 if (x // 5) % 3 == 0 else 0)
        for y in range(top, 12):
            put(img, x, y, (22, 40, 34))
        for y in range(12, H):
            put(img, x, y, (30, 70, 40) if (x + y) % 3 else (36, 84, 46))
    for x in range(0, 25):  # the bandstand floor
        put(img, x, 14, jfx.WOOD_HI)
        put(img, x, 15, jfx.WOOD)
    return img


def note(img, x: float, y: float, c, a: float) -> None:
    for dy, row in enumerate(NOTE):
        for dx, ch in enumerate(row):
            if ch == "#":
                put(img, x + dx, y + dy, c, a)


def render():
    bg = backdrop()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        string_lights(img, f, y0=0, sag=2.0, spacing=6, colors=(GOLD, PINK, CYAN, LIME), period=30)
        beat = (f % BEAT) / BEAT
        on = beat < 0.35
        bar = f // BEAT
        # the drummer behind a bass drum, sticks up and down on the beat, a cymbal flashing
        jfx.person(img, 2, GROUND, jfx.SKIN[3], (240, 240, 236), None, style="short",
                   arms=(0.3 if on else 0.18, 0.18 if on else 0.3), seated=True, height=11)
        for y in range(10, 14):
            for x in range(1, 8):
                d = math.hypot(x - 4, (y - 11.5) * 1.4)
                if d < 3.2:
                    put(img, x, y, jfx.FLAG_RED if d > 2.2 else (236, 236, 240))
        put(img, 9, 8, GOLD)
        put(img, 10, 8, GOLD)
        put(img, 9, 9, (150, 150, 160))
        for y in range(10, 14):
            put(img, 9, y, (150, 150, 160))
        if on and bar % 2 == 0:
            add(img, 9, 7, (255, 240, 170), 0.6)
            add(img, 10, 7, (255, 240, 170), 0.6)
        # the saxophone player, swaying, horn up
        sway = 1 if (bar % 4) in (1, 2) else 0
        sx = 11 + sway
        jfx.person(img, sx, GROUND - 1, jfx.SKIN[0], (90, 90, 200), (50, 50, 90), style="brim", hat=(240, 220, 160),
                   arms=(0.12, 0.12))
        cx = sx + 2
        for px, py in ((cx + 1, 6), (cx + 2, 7), (cx + 2, 8), (cx + 2, 9), (cx + 2, 10), (cx + 3, 10), (cx + 4, 9),
                       (cx + 4, 8)):
            put(img, px, py, GOLD)
        put(img, cx + 4, 7, (255, 236, 150))
        # the bass player
        jfx.person(img, 19, GROUND - 1, jfx.SKIN[2], (240, 180, 70), (60, 60, 90), style="puff", arms=(0.1, 0.15))
        for px, py in ((20, 9), (21, 9), (21, 10), (22, 10), (20, 10)):
            put(img, px, py, (200, 120, 60))
        for k in range(4):
            put(img, 23 + k, 8 - k, (170, 130, 96))
        # notes float up from the band and drift over the park, above everyone's heads
        for k in range(6):
            age = (f + k * 13) % 78
            x = 10 + (k % 3) * 4 + age * 0.55
            y = 3.5 - age * 0.05 + math.sin(age * 0.2 + k) * 0.8
            a = min(1.0, age / 8) * (1 - age / 78)
            note(img, x, y - 1, (GOLD, (255, 255, 255), CYAN)[k % 3], a)
        # dancers: arms up and down on the beat, little hops, a step side to side
        start = [sec(1.5), sec(2.3), sec(3.0), sec(3.6), sec(4.2), sec(4.8)]
        for i, (x, skin, shirt, pants, style, hat, dress, hgt, ph) in enumerate(DANCERS):
            dancing = f >= start[i]
            b = (bar + ph) % 4
            if not dancing:
                arms, hop, step, legs = (0.03, 0.03), 0, 0, 0
            elif f > sec(8.5):  # all together: arms up, swaying
                swing = 0.06 if (bar + ph) % 2 else -0.06
                arms, hop, step, legs = (0.45 + swing, 0.45 - swing), (-1 if on and b % 2 == 0 else 0), 0, 1
            else:
                arms = ((0.45, 0.1), (0.1, 0.45), (0.3, 0.3), (0.2, 0.05))[b]
                hop = -1 if on and b in (0, 2) else 0
                step = (0, 1, 0, -1)[b]
                legs = 1 if b % 2 == 0 else 0
            jfx.person(img, x + step, GROUND + hop, skin, shirt, pants, style=style, hat=hat, arms=arms, legs=legs,
                       height=hgt, dress=dress)
        frames.append(img)
    return frames
