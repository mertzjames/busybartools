"""Dec 12: Wreath. A wreath on a red front door; its lights chase round, the lanterns glow and snow drifts down."""

import math

from busybar.canvas import FPS, add, phase, put, rect, sec, vgradient

from common import LIGHTS, PINE, PINE_DARK, Snow, glow

NAME = "day12"
TITLE = "Wreath"
SECONDS = 8
KEYFRAMES = [(0.5, "A wreath on the front door"), (2.0, "Its lights switch on"), (4.5, "They chase around"),
             (7.0, "Everything twinkles")]

CX, CY = 36, 7


def ring():
    pts = []
    for y in range(16):
        for x in range(26, 47):
            d = math.hypot((x - CX) * 1.0, (y - CY) * 1.05)
            if 3.4 <= d <= 6.4:
                pts.append((x, y, d, math.atan2(y - CY, x - CX)))
    return pts


def render():
    bg = vgradient((30, 26, 40), (44, 36, 52))
    # stone wall
    for y in range(16):
        for x in range(72):
            if y % 4 == 0 or (x + (y // 4) * 3) % 7 == 0:
                put(bg, x, y, (60, 52, 70))
    # door
    rect(bg, 25, 0, 23, 16, (150, 20, 32))
    for y in range(16):
        put(bg, 25, y, (220, 180, 90))
        put(bg, 47, y, (220, 180, 90))
    for (x0, y0) in ((28, 2), (38, 2), (28, 11), (38, 11)):
        for x in range(x0, x0 + 7):
            put(bg, x, y0, (120, 12, 24))
        for y in range(y0, min(16, y0 + 4)):
            put(bg, x0, y, (120, 12, 24))
    put(bg, 44, 9, (255, 214, 92))  # knob
    # wreath body
    pts = ring()
    for x, y, d, a in pts:
        put(bg, x, y, (40, 170, 80) if (x * 7 + y * 3) % 5 else PINE_DARK)
    for x, y, d, a in pts:
        if (x * 13 + y * 7) % 29 == 0:
            put(bg, x, y, (220, 30, 40))
    # bow at the bottom
    for dx, dy, c in ((-2, 12, 1), (-1, 12, 0), (0, 12, 0), (1, 12, 0), (2, 12, 1), (-2, 13, 1), (2, 13, 1),
                      (-1, 14, 1), (1, 14, 1), (0, 13, 0)):
        put(bg, CX + dx, dy, (250, 50, 60) if c else (190, 20, 36))
    bulbs = [(round(CX + 4.9 * math.cos(k * math.pi / 6)), round(CY + 5.0 * math.sin(k * math.pi / 6)))
             for k in range(12)]
    snow = Snow(seed=12, n=26, speed=(0.15, 0.32))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # lanterns either side
        for lx in (17, 55):
            for y in range(4, 9):
                put(img, lx - 1, y, (40, 40, 50))
                put(img, lx + 1, y, (40, 40, 50))
            put(img, lx, 3, (40, 40, 50))
            fl = 0.8 + 0.2 * math.sin(f * 1.1 + lx)
            for y in range(5, 8):
                put(img, lx, y, (255, 200, 90), fl)
            glow(img, lx, 6, 5, (255, 160, 60), 0.3 * fl)
        on = phase(f, sec(1.4), sec(2.0))
        for i, (x, y) in enumerate(bulbs):
            if on <= 0:
                put(img, x, y, (90, 90, 90))
                continue
            if t < 3.0:
                a = on
            elif t < 6.2:
                a = 1.0 if (i - int((t - 3.0) * 8)) % 4 == 0 else 0.35  # chase
            else:
                a = 0.5 + 0.5 * math.sin(f * 0.6 + i * 2.1)
            put(img, x, y, LIGHTS[i % len(LIGHTS)], max(0.3, a))
            if a > 0.8:
                add(img, x, y, (255, 255, 255), 0.25)
        snow.draw(img, f)
        frames.append(img)
    return frames
