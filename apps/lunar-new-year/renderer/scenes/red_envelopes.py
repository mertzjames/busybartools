"""Red Envelopes: a child visits a grandparent and bows with a New Year wish; the grandparent hands over a red
envelope, the child jumps for joy, and red envelopes and gold coins shower down (docs/DECISIONS.md D2).
Simple figures only: no faces beyond a lit skin tone and hair.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import W, ease_in_out, ease_out, mix, phase, put, sec, vgradient
from busybar.party import glitter

import lnyfx as fx

NAME = "red_envelopes"
TITLE = "Red Envelopes"
SECONDS = 12
KEYFRAMES = [(1.2, "A child comes to visit"), (3.2, "A bow and a New Year wish"),
             (5.0, "A red envelope from grandma"), (6.6, "A jump for joy"), (9.5, "Red envelopes shower down"),
             (11.5, "Gold coins and glints")]

N = sec(SECONDS)
FLOOR = 15
SKIN = (240, 190, 150)
CHILD_X = 38
ELDER_X = 54


def doufang(img, cx: int, cy: int) -> None:
    """A diamond-shaped New Year paper (red with a gold edge and a gold dot)."""
    for dy in range(-3, 4):
        w = 3 - abs(dy)
        for dx in range(-w, w + 1):
            edge = abs(dx) == w
            put(img, cx + dx, cy + dy, fx.GOLD_DARK if edge else fx.RED)
    put(img, cx, cy, fx.GOLD)


def elder(img, x: int, f: int, reach: float, cheer: bool) -> None:
    """A grandparent: silver hair in a bun, a jade jacket, dark trousers; `reach` extends the arm to the left."""
    top = FLOOR - 10
    put(img, x, top, (220, 220, 235))
    put(img, x + 1, top, (220, 220, 235))  # bun
    put(img, x, top + 1, (220, 220, 235))
    put(img, x - 1, top + 1, (220, 220, 235))
    put(img, x - 1, top + 2, SKIN)
    put(img, x, top + 2, SKIN)
    jacket = (40, 160, 120)
    for y in range(top + 3, top + 8):
        for dx in (-1, 0, 1):
            put(img, x + dx, y, jacket if y < top + 7 else mix(jacket, (20, 90, 70), 0.4))
    put(img, x, top + 4, fx.GOLD)  # a knot button
    for y in range(top + 8, FLOOR):
        put(img, x - 1, y, (70, 60, 90))
        put(img, x + 1, y, (70, 60, 90))
    if cheer:
        put(img, x - 2, top + 2, SKIN)
        put(img, x + 2, top + 2, SKIN)
    else:
        n = int(round(reach))
        for k in range(n):
            put(img, x - 2 - k, top + 5, jacket)
        put(img, x - 2 - n, top + 5, SKIN)


def child(img, x: float, f: int, walking: bool, bow: float, arms_up: bool, hop: float) -> None:
    """A child in a gold jacket; `bow` 0..1 bends forward (hands together), `hop` lifts the whole figure."""
    x = int(round(x))
    ground = FLOOR - int(round(hop))
    top = ground - 7
    if bow > 0.5:  # bowing: head and shoulders forward and down, hands together in front
        put(img, x + 2, top + 2, (70, 50, 60))
        put(img, x + 2, top + 3, SKIN)
        for dx in (0, 1):
            put(img, x + dx, top + 3, (255, 190, 60))
        for y in (top + 4,):
            for dx in (-1, 0, 1):
                put(img, x + dx, y, (255, 190, 60))
        put(img, x + 2, top + 4, SKIN)
    else:
        put(img, x, top, (70, 50, 60))
        put(img, x + 1, top, (70, 50, 60))
        put(img, x, top + 1, SKIN)
        for y in range(top + 2, top + 5):
            for dx in (-1, 0, 1):
                put(img, x + dx, y, (255, 190, 60))
    if arms_up:
        put(img, x - 1, top, SKIN)
        put(img, x + 1, top - 1, SKIN)
    legs = (60, 80, 170)
    step = (f // 3) % 2 if walking else 0
    for y in range(top + 5, ground):
        if step:
            put(img, x, y, legs)
        else:
            put(img, x - 1, y, legs)
            put(img, x + 1, y, legs)


def render():
    bg = vgradient((70, 18, 24), (40, 10, 14))
    for x in range(W):  # a wooden floor and a skirting rail
        put(bg, x, FLOOR, (140, 84, 44) if x % 6 else (110, 64, 34))
        put(bg, x, 11, (90, 26, 30))
    doufang(bg, 8, 5)
    doufang(bg, 22, 5)
    # a round window with a lattice on the right wall
    for y in range(1, 10):
        for x in range(60, 71):
            if (x - 65) ** 2 + (y - 5) ** 2 <= 16:
                lattice = (x - 65) % 3 == 0 or (y - 5) % 3 == 0
                put(bg, x, y, (150, 90, 50) if lattice else (40, 30, 80))
    rng = random.Random(9)
    shower = [{"t0": sec(rng.uniform(7.6, 10.5)), "x": rng.uniform(1, W - 5), "v": rng.uniform(0.18, 0.3),
               "amp": rng.uniform(1, 2.5), "ph": rng.uniform(0, 6.3), "coin": rng.random() < 0.35}
              for _ in range(30)]
    frames = []
    for f in range(N):
        img = bg.copy()
        t = f / 15
        walk = ease_in_out(phase(f, 0, sec(2.4)))
        cx = -3 + (CHILD_X + 3) * walk
        bow = 0.0
        if 2.6 <= t < 4.2:
            bow = 1.0 if ((t - 2.6) % 0.8) < 0.5 else 0.0  # two bows
        reach = 3 * ease_out(phase(f, sec(4.2), sec(5.0))) * (1 - phase(f, sec(5.6), sec(5.9)))
        has = t >= 5.6
        hop = 0.0
        if 6.0 <= t < 8.0:
            hop = 3 * abs(math.sin(math.pi * (t - 6.0) / 0.5))
        arms_up = has and t >= 6.0
        elder(img, ELDER_X, f, reach, cheer=t >= 8.5)
        child(img, cx, f, walking=walk < 1, bow=bow, arms_up=arms_up, hop=hop)
        # the envelope: in grandma's hand, then the child's, then held up high
        if 4.2 <= t < 5.6:
            fx.envelope(img, ELDER_X - 3 - reach - 3, FLOOR - 6)
        elif has:
            if arms_up:
                fx.envelope(img, cx, FLOOR - 13 - hop)
            else:
                fx.envelope(img, cx + 1, FLOOR - 8)
        if 6.0 <= t < 7.4:  # a sparkle burst from the envelope
            k = phase(f, sec(6.0), sec(7.4))
            for i in range(8):
                a = i * math.pi / 4
                r = 2 + 5 * ease_out(k)
                put(img, cx + 2 + r * math.cos(a), FLOOR - 10 - hop + r * math.sin(a) * 0.7, fx.GOLD_LIGHT,
                    1 - k)
        for e in shower:
            age = f - e["t0"]
            if age < 0:
                continue
            y = -6 + age * e["v"] * 2.2
            if y > FLOOR:
                continue
            x = e["x"] + e["amp"] * math.sin(age * 0.12 + e["ph"])
            if e["coin"]:
                fx.coin(img, x, y + 4, f, int(e["ph"] * 10))
            else:
                fx.envelope(img, x, y, edge=(age // 5 + int(e["ph"])) % 4 == 0)
        if t > 8.5:
            glitter(img, seed=12, f=f, n=12, period=40, strength=0.7)
        frames.append(img)
    return frames
