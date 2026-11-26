"""Out of season: Winter Night. A cabin among snowy pines; smoke curls from the chimney and snow falls softly.
Shown before Dec 1 between "N DAYS / TO ADVENT" cards (docs/DECISIONS.md D5)."""

import math

from busybar.canvas import FPS, put, rect, sec
from busybar.fx import Stars, moon

from common import Snow, glow, ground_heights, pine, sky, snow_ground

NAME = "winter"
TITLE = "Winter Night"
SECONDS = 8
KEYFRAMES = [(0.5, "A cabin in the snowy woods"), (4.0, "Smoke curls from the chimney"),
             (7.5, "Waiting for December")]


def render():
    bg = sky(((4, 8, 30), (22, 30, 70)))
    stars = Stars(seed=300, n=22, ymax=9, period=FPS * 4, dim=0.1, bright=0.8)
    hills = ground_heights(30, 13.0, 0.9, 0.1)
    snow = Snow(seed=30, n=34, speed=(0.12, 0.3))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        moon(img, 8, 1)
        snow_ground(img, hills)
        for cx, base, hh in ((20, 14, 8), (26, 14, 6), (52, 14, 9), (59, 14, 6), (66, 15, 8), (3, 15, 5)):
            pine(img, cx, base, hh)
        # cabin
        rect(img, 33, 8, 12, 6, (120, 64, 34))
        for y in range(8, 14):
            if y % 2 == 0:
                for x in range(33, 45):
                    put(img, x, y, (96, 50, 26))
        for i in range(8):
            for x in range(31 + i, 47 - i):
                put(img, x, 7 - i * 0.6, (240, 246, 255) if i == 0 or x in (31 + i, 46 - i) else (200, 210, 235))
        rect(img, 41, 2, 2, 4, (110, 70, 60))
        flick = 0.85 + 0.15 * math.sin(f * 0.9)
        rect(img, 35, 10, 3, 2, (255, 200, 90), flick)
        rect(img, 41, 10, 2, 4, (150, 80, 40))
        glow(img, 36, 11, 4, (255, 170, 70), 0.3 * flick)
        for k in range(6):
            age = (t * 1.5 + k * 0.8) % 4.8
            put(img, 42 + math.sin(age * 1.7) * 1.2 + age * 0.6, 1.5 - age * 0.3 + 0,
                (210, 210, 230), 0.45 * (1 - age / 4.8))
        snow.draw(img, f, below=lambda x: hills[x])
        frames.append(img)
    return frames
