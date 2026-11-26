"""Scene: Hearts Afloat. Little hearts of every pink and red rise and sway through a plum night, more and more of
them, until one grows in the middle into a big heart that beats twice, then again, with a ring of gold twinkles."""

import math
import random

from busybar.canvas import FPS, H, W, sec
from vfx import (BERRY, BLUSH, CRIMSON, GOLD_LIGHT, PINK, PLUM, RED, ROSE, WARM_WHITE, gradient, heart, heart_c,
                 heart_glow, heart_size, twinkle)

NAME = "floating_hearts"
TITLE = "Hearts Afloat"
SECONDS = 14
KEYFRAMES = [(1.5, "The first hearts rise"), (5.0, "More and more of them"), (7.6, "One grows in the middle"),
             (9.4, "A big heart beats"), (12.6, "Gold twinkles ring it")]

CX, CY = 35.5, 7.5
GROW_AT = 7.0  # seconds
GROW = (3, 5, 7, 9, 11, 13, 15)  # widths, one step every GROW_STEP s
GROW_STEP = 0.2


def rising(seed: int = 3):
    """The rising hearts: launch times spread over the scene (more later), columns taken from shuffled slots so
    neighbors rarely overlap, and none launched up the middle once the big heart is coming."""
    rng = random.Random(seed)
    items = []
    n = 34
    slots = []
    for i in range(n):
        if not slots:
            slots = list(range(9))
            rng.shuffle(slots)
        t0 = (i / n) ** 0.85 * 12.5 - 1.5  # some already on screen at the start
        slot = slots.pop()
        if t0 > GROW_AT - 3.5 and 3 <= slot <= 5:  # keep the middle clear for the big heart
            slot = rng.choice((0, 1, 2, 6, 7, 8))
        w = rng.choice((3, 5, 5, 7, 7, 9))
        items.append({
            "t0": t0, "x": slot * 8 + rng.uniform(-1, 1), "v": rng.uniform(2.4, 4.0), "w": w,
            "amp": rng.uniform(0.5, 1.2), "sw": rng.uniform(0.5, 1.1), "sp": rng.uniform(0, 6.28),
            # small hearts are the deeper reds (they read as farther away); big ones the brighter pinks
            "c": rng.choice({3: (CRIMSON, (150, 20, 60)), 5: (CRIMSON, RED, ROSE), 7: (RED, ROSE, PINK),
                             9: (ROSE, PINK, BLUSH)}[w]),
        })
    return items


def big_width(t: float) -> int:
    """The center heart's width at time t (0 before it appears), with a double beat every 1.6 s."""
    if t < GROW_AT:
        return 0
    k = int((t - GROW_AT) / GROW_STEP)
    if k < len(GROW):
        return GROW[k]
    u = (t - GROW_AT - len(GROW) * GROW_STEP) % 1.6
    return 17 if (0.0 <= u < 0.14 or 0.3 <= u < 0.42) else 15


def render():
    bg = gradient([(0, (18, 2, 22)), (7, PLUM), (15, BERRY)])
    items = rising()
    rings = [(CX + 13 * math.cos(a), CY + 6.5 * math.sin(a), i / 10) for i, a in
             enumerate(2 * math.pi * k / 10 + 0.3 for k in range(10))]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        bw = big_width(t)
        show_big = bw > 0
        if show_big:  # a steady glow, stronger once it is full size
            heart_glow(img, CX, CY + 0.5, 6 + bw * 0.55, (110, 10, 50), 0.7)
        for it in items:
            age = t - it["t0"]
            if age < 0:
                continue
            hw, hh = heart_size(it["w"])
            y = H + 1 - it["v"] * age
            if y < -hh:
                continue
            x = it["x"] + it["amp"] * math.sin(it["sw"] * age * 2 + it["sp"])
            heart(img, x, y, it["w"], it["c"], halo=(30, 3, 26))
        if show_big:
            heart_c(img, CX, CY + (0.5 if bw >= 15 else 0), bw, RED, halo=(40, 2, 24))
            if t > GROW_AT + len(GROW) * GROW_STEP + 2.6:
                for x, y, ph in rings:
                    twinkle(img, x, y, f, GOLD_LIGHT, 0.9, period=24, ph=ph)
        frames.append(img)
    return frames
