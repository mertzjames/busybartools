"""Scene: a log cabin at dusk in the February snow, a nod to Lincoln without a face (docs/DECISIONS.md D3, D5): a
tall stovepipe hat stands in the warm open doorway, with a stack of books by the door and a lantern on the step.
The lantern is lit, smoke curls from the chimney and snow falls; a flake settles on the hat's crown."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.fx import Stars
from busybar.party import Snowfall

import pfx

NAME = "log_cabin"
TITLE = "The Log Cabin"
SECONDS = 14
KEYFRAMES = [(0.8, "A log cabin at dusk"), (4.5, "The lantern is lit"), (8.0, "A hat in the open doorway"),
             (11.0, "Books by the door, smoke from the chimney"), (13.2, "A snowflake settles on the hat")]

CABIN_X0, CABIN_X1 = 17, 47
LOG_A, LOG_B = (140, 90, 54), (112, 70, 42)
DOOR_X0, DOOR_X1 = 30, 36
HAT_X, HAT_Y = 32, 8  # top-left of the crown
LANTERN = (39, 10)  # top of the lantern body


def pine(img, cx: int, top: int, half: int) -> None:
    for y in range(top, 14):
        w = int((y - top) * half / (14 - top) + 0.5)
        for x in range(cx - w, cx + w + 1):
            put(img, x, y, (30, 72, 54) if (x + y) % 3 else (40, 88, 64))
        put(img, cx - w, y, (200, 210, 236), 0.7)  # snow on the branch tips
    put(img, cx, top - 1, (210, 220, 240))


def render():
    base = pfx.sky([(0, (14, 16, 56)), (11, (64, 52, 112))])
    pfx.glow(base, 62, 3, 7, (230, 230, 255), 0.35)  # the moon, steady
    for x, y in ((61, 2), (62, 2), (61, 3), (62, 3), (63, 3), (62, 4), (61, 4)):
        put(base, x, y, (244, 240, 220))
    for x in range(W):  # snow on the ground
        for y in range(13, H):
            put(base, x, y, mix((196, 206, 236), (150, 162, 206), (y - 13) / 2))
    pine(base, 6, 3, 5)
    pine(base, 12, 6, 3)
    pine(base, 56, 4, 5)
    pine(base, 67, 2, 5)
    # the cabin: logs, protruding log ends at the corners, a snowy roof and a stone chimney
    for y in range(4, 13):
        for x in range(CABIN_X0, CABIN_X1 + 1):
            put(base, x, y, LOG_A if y % 2 == 0 else LOG_B)
        for x in (CABIN_X0 - 1, CABIN_X1 + 1):
            put(base, x, y, (190, 140, 88) if y % 2 == 0 else (160, 116, 72))
    for y, (x0, x1) in zip(range(0, 4), ((24, 40), (21, 43), (18, 46), (15, 49))):  # a sloped, snowy roof
        for x in range(x0, x1 + 1):
            put(base, x, y, (130, 100, 92) if (x + 2 * y) % 5 else (112, 86, 80))
        put(base, x0, y, (226, 232, 248))
        put(base, x1, y, (226, 232, 248))
    for x in range(24, 41):
        put(base, x, 0, (226, 232, 248))  # snow along the ridge
    for x in (41, 42):  # the chimney, poking up from the roof's slope
        put(base, x, 1, (140, 130, 136) if x % 2 else (118, 110, 118))
        put(base, x, 0, (220, 226, 244))
    # the open door: warm light inside, the door swung in on the left
    for y in range(6, 13):
        for x in range(DOOR_X0, DOOR_X1 + 1):
            put(base, x, y, mix((250, 196, 110), (206, 132, 66), (y - 6) / 6))
        put(base, DOOR_X0 - 1, y, (90, 58, 36))
        put(base, DOOR_X1 + 1, y, (90, 58, 36))
    for x in range(DOOR_X0 - 1, DOOR_X1 + 2):
        put(base, x, 5, (90, 58, 36))
    for x in range(DOOR_X0 - 3, DOOR_X1 + 4):  # the split-log step
        put(base, x, 13, (176, 130, 84))
    for x in range(DOOR_X0, DOOR_X1 + 1):
        add(base, x, 14, (255, 170, 80), 0.25)  # door light on the snow
    # the window, lit
    for y in range(6, 10):
        for x in range(19, 25):
            frame = x in (19, 24) or y in (6, 9)
            put(base, x, y, (90, 58, 36) if frame else (255, 206, 110))
    for x in range(19, 25):
        add(base, x, 13, (255, 180, 80), 0.2)
    # the books, stacked on the snow (red, navy, green with cream page edges)
    for y, (c, w0, w1) in zip((10, 11, 12), (((190, 40, 50), 24, 27), ((54, 70, 150), 23, 27), ((50, 120, 70), 24, 28))):
        for x in range(w0, w1 + 1):
            put(base, x, y, c)
        put(base, w1, y, (240, 220, 160))

    stars = Stars(seed=9, n=12, ymax=5, period=sec(7), color=(220, 224, 255), dim=0.1, bright=0.7)
    snow = Snowfall(seed=13, n=22, period=sec(SECONDS), color=(232, 236, 255), alpha=(0.45, 0.9))
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        stars.draw(img, f)
        # the lantern: a frame, a glowing glass and a handle; a steady glow, only the flame flickers
        lit = round(phase(f, sec(3.6), sec(4.4)) * 8) / 8
        lx, ly = LANTERN
        if lit > 0:
            pfx.glow(img, lx + 0.5, ly + 1.5, 4, (255, 170, 70), 0.4 * lit)
        put(img, lx, ly - 1, (150, 140, 120))
        put(img, lx + 1, ly - 1, (150, 140, 120))
        for y in range(ly, ly + 3):
            put(img, lx, y, mix((80, 70, 70), (255, 214, 120), lit))
            put(img, lx + 1, y, mix((70, 60, 60), (255, 190, 90), lit))
        if lit > 0:
            k = 0.8 + 0.2 * math.sin(f * 1.3) * math.sin(f * 0.41)
            put(img, lx, ly + 1, (255, 246, 200), k * lit)
        for x in (lx - 1, lx + 2):
            put(img, x, ly + 3, (110, 100, 96))
        # the stovepipe hat, silhouetted in the lit doorway: a tall charcoal crown (lit, never black) with a sheen,
        # a darker band and a wide brim, rim-lit on the right by the lantern
        for y in range(HAT_Y, HAT_Y + 4):
            for x in range(HAT_X, HAT_X + 3):
                c = (64, 60, 78)
                if x == HAT_X:
                    c = (104, 100, 122)  # the sheen
                if y == HAT_Y + 3:
                    c = (40, 38, 50) if x != HAT_X else (70, 66, 84)  # the band
                put(img, x, y, c)
            if lit > 0:
                put(img, HAT_X + 2, y, mix((64, 60, 78), (190, 140, 96), 0.5 * lit))
        for x in range(HAT_X - 1, HAT_X + 4):
            put(img, x, HAT_Y + 4, (84, 80, 100))
        if f >= sec(10.4):  # the settled snowflake
            put(img, HAT_X + 1, HAT_Y - 1, (236, 240, 255))
        # smoke curls up from the chimney and drifts right
        for i in range(5):
            age = (f + i * 9) % 45
            sx = 41.5 + age * 0.12 + 0.8 * math.sin((f + i * 11) * 0.15)
            put(img, sx, -age / 30, (170, 166, 190), 0.5 * (1 - age / 45))
        snow.draw(img, f)
        frames.append(img)
    return frames
