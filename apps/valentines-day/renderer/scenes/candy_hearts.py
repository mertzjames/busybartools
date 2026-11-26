"""Scene: Candy Hearts (the finale). Pastel candy hearts tumble down and stack up at both ends of the screen. BE MINE
stamps in between them, then XOXO, and the show ends with heart-shaped fireworks in pink, red and gold."""

import math

from busybar.canvas import FPS, H, W, add, ease_in, put, sec
from busybar.party import glitter
from vfx import (BERRY, CANDY, GOLD, GOLD_LIGHT, INK, PINK, PLUM, RED, ROSE, WARM_WHITE, HeartBurst, caption,
                 dim_rect, gradient, heart, twinkle)

NAME = "candy_hearts"
TITLE = "Candy Hearts"
SECONDS = 16
KEYFRAMES = [(1.6, "Candy hearts tumble down"), (4.6, "They stack up at the ends"), (6.4, "BE MINE"),
             (10.0, "XOXO"), (12.9, "Heart fireworks"), (15.2, "The grand finale")]

# (rest x, rest y, drop second, candy color index): a little pyramid of three at each end, bottom row first. They
# stay within columns 0-15 and 56-71, clear of the 37 px BE MINE between them.
STACKS = [(0, 8, 0.3, 0), (63, 8, 0.8, 2), (7, 8, 1.3, 1), (56, 8, 1.8, 3), (3, 1, 2.5, 4), (60, 1, 3.1, 5)]
FALL = 0.55  # seconds to fall from above the screen
STAMP, SWAP, BURSTS = 5.2, 8.9, 11.8
TEXT_TOP = ((255, 236, 240), (255, 104, 150), (130, 10, 52))


def candy(img, x: float, y: float, ci: int, a: float = 1.0) -> None:
    """A 9 px candy heart: pastel body, darker rim, and ink dashes suggesting a printed word."""
    body, rim = CANDY[ci]
    x, y = int(math.floor(x + 0.5)), int(math.floor(y + 0.5))
    heart(img, x, y, 9, body, a, shade=False, rim=rim)
    for xx in (2, 3, 5, 6):
        put(img, x + xx, y + 3, INK, 0.8 * a)
    for xx in (3, 4, 5):
        put(img, x + xx, y + 5, INK, 0.8 * a)
    put(img, x + 1, y + 1, WARM_WHITE, 0.7 * a)


def candy_y(t: float, rest_y: float, t0: float) -> float | None:
    """Falling with gravity, then a small bounce, then at rest."""
    if t < t0:
        return None
    age = t - t0
    if age < FALL:
        return -10 + (rest_y + 10) * ease_in(age / FALL)
    age -= FALL
    if age < 0.3:
        return rest_y - 2.5 * math.sin(math.pi * age / 0.3)
    return rest_y


def render():
    bg = gradient([(0, (18, 2, 22)), (8, PLUM), (15, BERRY)])
    bursts = [
        HeartBurst(sec(BURSTS + 0.4), 36, 6.5, 7.5, (ROSE, PINK), seed=1),
        HeartBurst(sec(BURSTS + 1.3), 27, 5.5, 6, (GOLD, GOLD_LIGHT), seed=2),
        HeartBurst(sec(BURSTS + 1.9), 45, 6, 6, (RED, ROSE), seed=3),
        HeartBurst(sec(BURSTS + 2.8), 36, 6.5, 8.5, (PINK, GOLD_LIGHT, ROSE), n=34, life=36, seed=4),
    ]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        for b in bursts:
            b.draw(img, f)
        if t > BURSTS + 3.0:
            glitter(img, 6, f, n=14, period=40, colors=(GOLD_LIGHT, (255, 200, 220)), area=(19, 0, 53, 16))
        # the text in the middle
        if STAMP <= t < BURSTS:
            word = "BE MINE" if t < SWAP else "XOXO"
            start = STAMP if t < SWAP else SWAP
            k = min(1.0, (t - start) / 0.35)
            out = min(1.0, max(0.0, (BURSTS - t) / 0.4)) if t > SWAP else min(1.0, max(0.0, (SWAP - t) / 0.3))
            dim_rect(img, 17, 3, 54, 12, 0.5 * k)
            caption(img, word, 4, *TEXT_TOP, a=min(k, out))
            if t - start < 0.25:  # the stamp's flash
                for x in range(20, 52):
                    add(img, x, 3, WARM_WHITE, 0.4 * (1 - (t - start) / 0.25))
                    add(img, x, 12, WARM_WHITE, 0.4 * (1 - (t - start) / 0.25))
            for i, (x, y) in enumerate(((20, 2), (51, 13), (51, 2), (20, 13))):
                twinkle(img, x, y, f, GOLD_LIGHT, 0.8, period=20, ph=i / 4)
        # the candy stacks (drawn last: they sit in front)
        beat = 0
        if t > STAMP:
            u = (t - STAMP) % 1.6
            beat = 1 if u < 0.12 or 0.26 <= u < 0.36 else 0
        for i, (x, y, t0, ci) in enumerate(STACKS):
            cy = candy_y(t, y, t0)
            if cy is None:
                continue
            candy(img, x, cy - (beat if i % 2 == (int(t / 1.6) % 2) else 0), ci)
        frames.append(img)
    return frames
