"""Dec 6: Ornaments. Three glass baubles swing from a pine bough; a glint runs across each and the lights twinkle."""

import math

from busybar.canvas import FPS, add, mix, phase, put, sec, vgradient

from common import LIGHTS, PINE, PINE_DARK

NAME = "day06"
TITLE = "Ornaments"
SECONDS = 8
KEYFRAMES = [(0.5, "Baubles on a pine bough"), (2.5, "A glint runs across them"),
             (4.8, "They swing in the warm light"), (7.2, "The bough's lights twinkle")]

BAUBLES = [  # x, string length, body color, band color, swing phase
    (17, 5, (220, 30, 50), (255, 214, 92), 0.0),
    (36, 3, (40, 110, 230), (240, 240, 255), 1.4),
    (55, 6, (240, 170, 30), (220, 30, 50), 2.6),
]
CAP = (210, 200, 170)
THREAD = (230, 190, 90)


def bauble(img, cx, cy, body, band, t, glint_x):
    """Round bauble of radius 3.4: shaded body, a band, a cap; glint_x is the glint's column offset (-5..5)."""
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = math.hypot(dx + 0.2, dy + 0.2)
            if d > 3.6:
                continue
            light = 0.35 + 0.65 * max(0.0, 1 - math.hypot(dx + 1.2, dy + 1.4) / 5.5)
            c = mix((0, 0, 0), body, 0.45 + 0.75 * light)
            if dy == 0:
                c = band
            put(img, cx + dx, cy + dy, c)
    put(img, cx - 1, cy - 2, (255, 255, 255), 0.9)  # highlight
    for dx in (-1, 0, 1):
        put(img, cx + dx, cy - 4, CAP)
    if -4 <= glint_x <= 4:
        for dy in range(-3, 4):
            add(img, cx + glint_x - dy * 0.3, cy + dy, (255, 255, 255), 0.45 * (1 - abs(dy) / 4))


def bough(img):
    for x in range(72):
        yc = 1 + 0.8 * math.sin(x * 0.09 + 0.5)
        for y in range(0, int(yc) + 2):
            put(img, x, y, PINE_DARK if (x + y) % 3 else PINE)
        # needles poking down
        if x % 2 == 0:
            put(img, x, int(yc) + 2, PINE, 0.9)
        if x % 4 == 1:
            put(img, x, int(yc) + 3, PINE_DARK, 0.9)


def render():
    bg = vgradient((40, 14, 10), (70, 30, 16))
    # warm bokeh behind
    bokeh = [(8, 10, (255, 160, 60)), (28, 13, (255, 90, 90)), (46, 9, (255, 200, 90)), (65, 12, (120, 160, 255)),
             (60, 5, (255, 150, 60)), (4, 4, (255, 210, 120))]
    for x, y, c in bokeh:
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                d = math.hypot(dx, dy)
                if d < 2.6:
                    add(bg, x + dx, y + dy, c, 0.18 * (1 - d / 2.8))
    bough(bg)
    lights = [(x, int(round(2 + 0.8 * math.sin(x * 0.09 + 0.5)))) for x in range(5, 72, 9)]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        amp = 0.25 + 0.25 * phase(f, sec(3.5), sec(4.5))
        for i, (x, length, body, band, ph) in enumerate(BAUBLES):
            ang = amp * math.sin(t * 2.2 + ph)
            top = 3
            ln = length + 4  # pivot to bauble center
            cx = x + ln * math.sin(ang)
            cy = top + ln * math.cos(ang)
            for k in range(length + 1):
                put(img, x + k * math.sin(ang), top + k * math.cos(ang), THREAD, 0.8)
            # the glint sweeps each bauble in turn, twice
            g = ((t - 1.6 - i * 0.35) % 3.2) * 10 - 5
            bauble(img, round(cx), round(cy), body, band, t, round(g))
        tw = phase(f, sec(6.0), sec(6.6))
        for j, (x, y) in enumerate(lights):
            on = 0.55 + 0.45 * math.sin(f * 0.35 + j * 1.9) if tw > 0 else 0.5
            put(img, x, y, LIGHTS[j % len(LIGHTS)], on)
            if tw > 0:
                add(img, x, y + 1, LIGHTS[j % len(LIGHTS)], 0.25 * tw)
        frames.append(img)
    return frames
