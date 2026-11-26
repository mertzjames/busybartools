"""Dec 14: Snowman. A snowball rolls in and grows, the head drops on, then a hat, a carrot nose, and a wave."""

import math

from busybar.canvas import FPS, ease_in, ease_out, lerp, phase, put, sec

from common import SNOW, Snow, sky

NAME = "day14"
TITLE = "Snowman"
SECONDS = 8
KEYFRAMES = [(1.0, "A snowball rolls in"), (2.6, "The head drops on"), (3.8, "A hat!"),
             (4.8, "Carrot nose and a scarf"), (6.6, "Hello!")]

SHADE = (170, 190, 230)
HAT = (110, 116, 170)
HAT_BAND = (220, 30, 50)
CARROT = (255, 130, 30)
EYE = (40, 50, 110)
STICK = (140, 90, 40)
SCARF = (220, 30, 50)
SCARF2 = (255, 200, 60)
X = 36


def ball(img, cx, cy, r, rot=0.0):
    ri = int(math.ceil(r))
    for y in range(int(cy) - ri, int(cy) + ri + 1):
        for x in range(int(cx) - ri, int(cx) + ri + 1):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                lit = (x - cx) + (y - cy) > r * 0.6
                c = SHADE if lit else SNOW
                if rot and int((math.atan2(y - cy, x - cx) + rot) * 2) % 5 == 0 and d > r * 0.5:
                    c = SHADE
                put(img, x, y, c)


def render():
    snow = Snow(seed=14, n=24, speed=(0.12, 0.3), ymax=15)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky(((10, 16, 44), (30, 46, 90)))
        for x in range(72):
            put(img, x, 15, SNOW)
        snow.draw(img, f, alpha=0.8)
        # bottom ball: rolls in from the left and grows
        k = ease_out(phase(f, 0, sec(1.8)))
        r = lerp(1.2, 3.3, k)
        bx = lerp(-3, X, k)
        ball(img, bx, 14.6 - r, r, rot=0 if k >= 1 else -bx * 0.6)
        if k < 1:  # trail of packed snow
            for x in range(0, int(bx) - 2):
                put(img, x, 14, SHADE, 0.6)
        # head drops 2.0-2.6
        if t >= 2.0:
            hy = lerp(-4, 6.6, ease_in(phase(f, sec(2.0), sec(2.6))))
            if 2.6 <= t < 2.8:
                hy = 6.6 + 0.4 * math.sin((t - 2.6) * 15)
            ball(img, X, hy, 2.2)
            if t >= 2.6:
                for dx in (-2, -1, 1, 2):
                    put(img, X + dx, 9, SHADE)
        # scarf + face + arms after 4.2
        if t >= 4.2:
            a = phase(f, sec(4.2), sec(4.5))
            for dx in range(-2, 3):
                put(img, X + dx, 9, SCARF, a)
            put(img, X + 2, 10, SCARF, a)
            put(img, X + 2, 11, SCARF2, a)
            put(img, X - 1, 6, EYE, a)
            put(img, X + 1, 6, EYE, a)
            put(img, X, 7, CARROT, a)
            put(img, X + 1, 7, CARROT, a)
            for by in (11, 13):
                put(img, X, by, HAT_BAND, a)
        if t >= 4.6:
            # left arm still, right arm waves from 5.6
            for i in range(4):
                put(img, X - 4 - i, 11 - i * 0.6, STICK)
            wave = math.sin((t - 5.6) * 9) if t >= 5.6 else 0.0
            ang = -0.5 - 0.5 * max(0.0, wave) if t >= 5.6 else 0.3
            for i in range(5):
                put(img, X + 4 + i * math.cos(ang), 11 + i * math.sin(ang), STICK)
        # hat drops 3.4-3.8
        if t >= 3.4:
            hy = lerp(-6, 0, ease_in(phase(f, sec(3.4), sec(3.8))))
            for dx in range(-1, 2):
                for yy in range(3):
                    put(img, X + dx, hy + yy, HAT)
                put(img, X + dx, hy + 3, HAT_BAND)
            put(img, X - 1, hy, (160, 166, 220))
            for dx in range(-2, 3):
                put(img, X + dx, hy + 4, HAT)
        frames.append(img)
    return frames
