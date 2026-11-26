"""Countdown, greeting and candy-phrase backdrop: a seamless 4 s loop. Two pastel candy hearts sit at the ends,
beating gently, over a deep plum night with faint rising hearts (docs/DECISIONS.md D7). The candy hearts fill rows
1-9 at columns 1-9 and 62-70, so the big line (rows 1-8 or 4-11, at most 48 px wide) fits between them and the
tiny line (rows 10-15) runs underneath."""

import math

from busybar.canvas import add, put, sec
from vfx import BERRY, CANDY, CRIMSON, INK, PINK, PLUM, ROSE, Drift, gradient, heart, heart_glow

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

LEFT, RIGHT = (1, 1), (62, 1)


def candy(img, x: int, y: int, body, rim, k: float) -> None:
    """A 9 px candy heart: pastel body, darker rim, a tiny printed word suggested by two ink dashes."""
    heart(img, x, y, 9, body, 1.0, shade=False, rim=rim)
    for xx in (2, 3, 5, 6):
        put(img, x + xx, y + 3, INK, 0.8)
    for xx in (3, 4, 5):
        put(img, x + xx, y + 5, INK, 0.8)
    put(img, x + 1, y + 1, (255, 255, 255), 0.5 + 0.4 * k)


def text_mask(x: float, y: float) -> float:
    return 0.25 if 10 <= x <= 61 else 0.7


def render():
    bg = gradient([(0, (20, 2, 20)), (8, PLUM), (15, BERRY)])
    drift = Drift(seed=41, n=12, period=LOOP, sizes=(3, 3, 5), colors=(ROSE, PINK, CRIMSON), alpha=(0.4, 0.7),
                  x_range=(10, 62))
    # steady glows behind the candies (glows that change every frame make the file much larger)
    for cx in (LEFT[0] + 4, RIGHT[0] + 4):
        heart_glow(bg, cx, 4.5, 7, (120, 20, 70), 0.6)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        drift.draw(img, f, mask=text_mask)
        # a double heartbeat once per loop: brighter highlight on each beat
        t = f / LOOP
        beat = max(0.0, math.cos(2 * math.pi * (t * 1.0)) ) ** 8 + 0.6 * max(0.0, math.cos(2 * math.pi * (t - 0.12))) ** 8
        candy(img, *LEFT, *CANDY[0], beat)
        candy(img, *RIGHT, *CANDY[2], beat)
        if beat > 0.3:
            for cx in (LEFT[0] + 4, RIGHT[0] + 4):
                add(img, cx, 9, (255, 150, 190), 0.3 * beat)
        frames.append(img)
    return frames
