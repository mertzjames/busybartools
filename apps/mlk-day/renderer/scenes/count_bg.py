"""Countdown and word card backdrop: a seamless 4 s loop of first light: a deep-blue sky, a gold dawn band low on
the horizon that breathes slowly, and faint rays fanning up from the hidden sun (docs/DECISIONS.md D7). The text
band in the middle stays dark, so gold words read clearly."""

import math

from busybar.canvas import H, W, add, mix, sec, vgradient

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

SUN_X, SUN_Y = 36, 20


def render():
    bg = vgradient((6, 10, 36), (26, 24, 70))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        breathe = 0.5 + 0.5 * math.cos(2 * math.pi * f / LOOP)
        for y in range(H):
            for x in range(W):
                dx, dy = x - SUN_X, SUN_Y - y
                d = math.hypot(dx, dy * 2.2)
                # horizon glow, strongest at the bottom center
                g = max(0.0, 1 - d / 34) ** 2
                add(img, x, y, mix((255, 120, 60), (255, 180, 90), g), (0.5 + 0.1 * breathe) * g)
                # soft rays, rotating slowly, faded out in the text band
                ang = math.atan2(dy, dx)
                ray = 0.5 + 0.5 * math.cos(9 * ang + 2 * math.pi * f / LOOP)
                fade = 1.0 if y >= 13 or y <= 1 else 0.25
                add(img, x, y, (255, 170, 80), 0.07 * ray ** 4 * fade * max(0.0, 1 - d / 40))
        frames.append(img)
    return frames
