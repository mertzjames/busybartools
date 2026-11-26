"""Dec 18: Nutcracker. A wooden nutcracker toy opens wide, a walnut drops in, and CRACK! Twice, then a proud grin."""

import math

from busybar.canvas import FPS, add, ease_in, lerp, phase, put, rect, sec, vgradient
from busybar.fx import Particles

from common import LIGHTS

NAME = "day18"
TITLE = "Nutcracker"
SECONDS = 8
KEYFRAMES = [(0.6, "A wooden nutcracker"), (1.8, "Open wide..."), (2.9, "CRACK!"), (5.2, "Another one"),
             (7.2, "A proud grin")]

HAT = (200, 24, 40)
HAT_D = (140, 14, 28)
GOLD = (255, 210, 80)
SKIN = (246, 200, 160)
HAIR = (244, 244, 255)
EYE = (60, 120, 255)
NOSE = (255, 140, 150)
MOUTH = (110, 16, 30)
COAT = (40, 90, 200)
COAT_D = (26, 60, 150)
NUT = (230, 160, 70)
NUT_D = (170, 104, 40)
X = 36  # center column


def head(img, jaw, blink, grin):
    # tall hat with a gold band and plume
    rect(img, X - 3, 0, 7, 3, HAT)
    for y in range(0, 3):
        put(img, X + 3, y, HAT_D)
    for dx in range(-4, 5):
        put(img, X + dx, 3, GOLD)
    put(img, X, 1, GOLD)
    # face
    rect(img, X - 3, 4, 7, 3, SKIN)
    for y in range(4, 10):
        put(img, X - 4, y, HAIR)
        put(img, X + 4, y, HAIR)
    if not blink:
        put(img, X - 2, 5, EYE)
        put(img, X + 2, 5, EYE)
    else:
        put(img, X - 2, 5, SKIN)
        put(img, X + 2, 5, SKIN)
    put(img, X, 6, NOSE)
    # mustache
    for dx in range(-3, 4):
        put(img, X + dx, 7, HAIR)
    # mouth gap (dark red, lit) between mustache and jaw
    for j in range(jaw):
        for dx in range(-2, 3):
            put(img, X + dx, 8 + j, MOUTH)
    if grin:
        put(img, X - 2, 7, HAIR)
        put(img, X - 3, 6, HAIR)
        put(img, X + 3, 6, HAIR)
    # jaw + beard (moves down)
    jy = 8 + jaw
    for dx in range(-3, 4):
        put(img, X + dx, jy, SKIN)
    for dx in range(-3, 4):
        put(img, X + dx, jy + 1, HAIR)
    for dx in range(-2, 3):
        put(img, X + dx, jy + 2, HAIR)
    # coat below
    for y in range(jy + 3, 16):
        for dx in range(-4, 5):
            put(img, X + dx, y, COAT if abs(dx) < 3 else COAT_D)
        put(img, X, y, GOLD if y % 2 == 0 else COAT)
    for y in range(jy + 3, 16):
        put(img, X - 5, y, (240, 240, 255))  # white cuffs/arms
        put(img, X + 5, y, (240, 240, 255))


def nut(img, x, y):
    for dx, dy, c in ((0, 0, NUT), (1, 0, NUT), (-1, 1, NUT), (0, 1, NUT_D), (1, 1, NUT), (2, 1, NUT_D),
                      (0, 2, NUT_D), (1, 2, NUT)):
        put(img, x + dx - 0.5, y + dy, c)


def render():
    bg = vgradient((12, 40, 26), (20, 64, 40))
    for y in range(16):
        for x in range(0, 72, 4):
            put(bg, x + (y % 2) * 2, y, (26, 76, 48))
    sp = Particles(seed=18)
    frames = []
    cycles = [(1.2, 2.9), (4.0, 5.6)]  # open at, snap at
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # fairy lights along both sides
        for i, y in enumerate(range(1, 16, 3)):
            for x in (6, 66):
                put(img, x + (i % 2), y, LIGHTS[(i + f // 8 + x) % len(LIGHTS)], 0.8)
        jaw = 0
        for t_open, t_snap in cycles:
            if t_open <= t < t_snap:
                jaw = round(3 * phase(f, sec(t_open), sec(t_open + 0.5)))
                # walnut drops into the mouth
                k = ease_in(phase(f, sec(t_open + 0.6), sec(t_snap - 0.2)))
                ny = lerp(-3, 8, k)
                if 0 < k < 1:
                    nut(img, X, ny)
            if t_snap <= t < t_snap + 0.05:
                sp.emit(X, 9, 14, vx=(-1.8, 1.8), vy=(-1.4, 0.4), life=(8, 16), colors=(NUT, NUT_D, (230, 200, 150)),
                        gravity=0.12)
        blink = (f % 50) in (0, 1, 2)
        grin = t > 6.4
        head(img, jaw, blink, grin)
        # the nut sits in the open mouth until the snap
        for t_open, t_snap in cycles:
            if t_snap - 0.2 <= t < t_snap:
                nut(img, X, 8)
        for t_open, t_snap in cycles:
            if t_snap <= t < t_snap + 0.25:
                a = 1 - (t - t_snap) / 0.25
                for r in (6, 8):
                    for ang in range(0, 360, 30):
                        add(img, X + r * math.cos(math.radians(ang)), 9 + r * 0.5 * math.sin(math.radians(ang)),
                            (255, 250, 200), a * 0.8)
        if grin:
            # proud sparkle in the eyes
            if (f // 3) % 4 == 0:
                add(img, X - 2, 5, (255, 255, 255), 0.7)
                add(img, X + 2, 5, (255, 255, 255), 0.7)
        sp.step_draw(img)
        frames.append(img)
    return frames
