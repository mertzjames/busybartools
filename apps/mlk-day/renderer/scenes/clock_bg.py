"""Clock card backdrop: a seamless 4 s loop of a calm night sky before dawn: a few faint stars along the top, a
low city skyline along the bottom with a handful of warm windows, and the first gold glow on the horizon
(docs/DECISIONS.md D7). The live time and date are drawn over the middle, which stays dark and still."""

import math

from busybar.canvas import W, add, put, sec, vgradient
from busybar.fx import Stars

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

# roof heights of a low skyline (rows from the bottom), left to right
ROOFS = [2, 2, 3, 3, 3, 2, 2, 1, 1, 2, 2, 2, 3, 3, 1, 1, 1, 2, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
         1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 1, 1, 3, 3, 3, 2, 2, 1, 1, 2, 2, 3, 3, 3, 2, 2, 1, 1]
WINDOWS = [(3, 14), (12, 14), (57, 14), (66, 14), (19, 15)]


def render():
    bg = vgradient((4, 8, 30), (12, 16, 50))
    for x in range(W):  # the first light along the horizon
        for y in (14, 15):
            add(bg, x, y, (120, 60, 40), 0.35 if y == 14 else 0.6)
        for k in range(ROOFS[x]):
            put(bg, x, 15 - k, (26, 28, 60))
    stars = Stars(seed=21, n=10, ymax=2, period=LOOP, color=(210, 220, 255), dim=0.08, bright=0.55)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for i, (x, y) in enumerate(WINDOWS):
            k = 0.75 + 0.25 * math.sin(2 * math.pi * (f / LOOP + i / 5))
            put(img, x, y, (255, 200, 110), 0.85 * k)
        frames.append(img)
    return frames
