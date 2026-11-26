"""Dec 1: First Snow. A big snowflake crystal drifts down, sparkles, and the first snow settles on the hills."""

import math

from busybar.canvas import FPS, add, blit, ease_out, lerp, phase, put, sec
from busybar.fx import Stars
from busybar.sprite import Sprite

from common import SNOW, Snow, ground_heights, pine, sky, snow_ground

NAME = "day01"
TITLE = "First Snow"
SECONDS = 8
KEYFRAMES = [(0.8, "A single snowflake drifts down"), (3.2, "It sparkles in the night"),
             (5.5, "Snow begins to fall"), (7.6, "The hills turn white")]

FLAKE = Sprite("big_flake", {"W": "#F4F8FF", "b": "#9CC8FF", "c": "#FFFFFF"}, """
....W....
.b..W..b.
..b.W.b..
...bWb...
WWWWcWWWW
...bWb...
..b.W.b..
.b..W..b.
....W....
""")


def render():
    bg = sky(((2, 6, 26), (16, 28, 64)))
    stars = Stars(seed=101, n=16, ymax=9, period=FPS * 4, dim=0.1, bright=0.7)
    light = Snow(seed=11, n=34, speed=(0.15, 0.4))
    hills_bare = ground_heights(1, 13.5, 1.2, 0.11)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f, alpha=1.0 - 0.6 * phase(f, sec(4), sec(6)))
        # hills: dark until the snow settles, then whitening from the top down
        cover = phase(f, sec(5.0), sec(7.6))
        for x, h in enumerate(hills_bare):
            top = int(round(h))
            for y in range(top, 16):
                dark = (20, 34, 40) if y > top else (36, 54, 60)
                white = SNOW if y == top else ((150, 170, 210) if y - top < 2 else (96, 116, 160))
                k = max(0.0, min(1.0, cover * 3 - (y - top) * 0.5 - (x % 5) * 0.08))
                put(img, x, y, tuple(int(lerp(dark[i], white[i], k)) for i in range(3)))
        for cx, base, hh in ((8, 13, 7), (15, 14, 5), (60, 13, 8), (67, 14, 5)):
            pine(img, cx, base, hh, snow=cover > 0.5)
        # snowfall builds up from 4.5 s
        density = phase(f, sec(4.5), sec(6.0))
        if density > 0:
            light.draw(img, f, alpha=density, below=lambda x: hills_bare[x])
        # the big flake: drift in (0-2.6 s), hover and sparkle (2.6-5 s), then sink behind the hill and fade
        if t < 2.6:
            k = ease_out(phase(f, 0, sec(2.6)))
            fx, fy = 36 + 6 * math.sin(t * 2.2) * (1 - k), lerp(-10, 3, k)
        else:
            fx, fy = 36, 3 + 0.6 * math.sin((t - 2.6) * 3)
        fade = 1.0 - phase(f, sec(5.2), sec(6.4))
        if fade > 0:
            blit(img, FLAKE.img(), fx - 4, fy, alpha=fade)
            if 2.4 <= t < 5.4:
                # glints travel around the six tips
                tips = [(0, -4), (3, -3), (4, 0), (3, 3), (0, 4), (-3, 3), (-4, 0), (-3, -3)]
                dx, dy = tips[(f // 2) % len(tips)]
                add(img, fx + dx, fy + 4 + dy, (255, 255, 255), 0.9)
                add(img, fx, fy + 4, (180, 220, 255), 0.4 + 0.3 * math.sin(f * 0.5))
        frames.append(img)
    return frames
