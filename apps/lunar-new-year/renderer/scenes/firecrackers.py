"""Firecrackers: a long string of red firecrackers hangs from a bamboo pole by a red door. The Nian, the folklore
beast that fears red and loud noise, sneaks up the street; the fuse is lit right above it and it flees. The spark
races along the string, and every cracker pops with a flash, a puff of smoke and red paper that settles on the
street like a carpet. At the end the Nian peeks back in, sees all that red, and ducks away (docs/DECISIONS.md D2).
"""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, blit, ease_in, ease_in_out, mix, phase, put, sec, vgradient
from busybar.fx import puff
from busybar.party import glitter

import lnyfx as fx
import sprites

NAME = "firecrackers"
TITLE = "Firecrackers"
SECONDS = 12
KEYFRAMES = [(0.8, "The Nian sneaks up the street"), (2.0, "The fuse is lit: the Nian jumps"),
             (4.6, "Pop, pop, pop!"), (7.4, "The last ones go off"), (10.6, "The Nian peeks back in"),
             (11.6, "Too much red: it ducks away")]

N = sec(SECONDS)
STREET = 15
LIT = sec(1.6)  # the fuse is lit at the right end
SPEED = 9.5 / 15  # px per frame the spark travels left
X0, X1 = 8, 69  # the string runs from the pole (left) to the right end


def cord_y(x: float) -> float:
    u = (x - X0) / (X1 - X0)
    return 2 + 4.5 * math.sin(math.pi * u)


def crackers():
    """Every cracker: (x, y, pop frame, side). Pops come a little early or late, so it sounds ragged."""
    rng = random.Random(17)
    out = []
    for i, x in enumerate(range(X1 - 1, X0 + 1, -3)):
        y = int(round(cord_y(x))) + 1
        pop = LIT + int((X1 - x) / SPEED) + rng.randint(-2, 3)
        out.append((x, y, pop, i % 2))
    return out


def door(img) -> None:
    """A red door with gold studs and a lit lantern-red frame, on the left behind the pole."""
    for y in range(4, STREET):
        for x in range(0, 7):
            put(img, x, y, fx.RED_DARK if x in (0, 6) or y == 4 else (120, 18, 24))
    for y in (6, 8, 10, 12):
        put(img, 2, y, fx.GOLD_DARK)
        put(img, 4, y, fx.GOLD_DARK)


def nian(img, f: int) -> None:
    """The Nian's two appearances: sneaking in and fleeing, then peeking back at the end."""
    spr = sprites.NIAN
    y = STREET - spr.h
    if f < sec(3.2):
        if f < LIT + 2:  # sneaking toward the door, facing left
            x = W - (W - 54) * ease_in_out(phase(f, 0, LIT))
            blit(img, spr.img((f // 4) % 2, flip=True), x, y)
        else:  # startled: a hop, then it runs off to the right
            t = f - LIT - 2
            hop = max(0.0, math.sin(math.pi * t / 6)) * 3 if t < 6 else 0
            x = 54 + 26 * ease_in(phase(f, LIT + 6, sec(3.2)))
            blit(img, spr.img((f // 2) % 2), x, y - hop)
    elif sec(9.8) <= f < sec(12):
        out = ease_in_out(phase(f, sec(9.8), sec(10.6))) - ease_in_out(phase(f, sec(11.3), sec(11.9)))
        x = W - 7 * out
        blit(img, spr.img(0, flip=True), x, y)
        if sec(10.8) <= f < sec(11.3) and (f // 3) % 2:
            put(img, x + 2, y + 2, (40, 170, 160))  # a blink


def render():
    bg = vgradient((10, 6, 22), (34, 10, 26))
    fx.rooftops(bg, base=13, color=(26, 22, 38), edge=(80, 56, 50), wall=(46, 12, 18), seed=31, lit=0.3)
    door(bg)
    for x in range(W):
        put(bg, x, STREET, (64, 54, 60))
    items = crackers()
    rng = random.Random(23)
    bits = []  # red paper: (pop, x, y, vx, vy, color)
    for x, y, pop, _ in items:
        for _ in range(3):
            bits.append((pop, x, y, rng.uniform(-0.9, 0.9), rng.uniform(-1.2, -0.2),
                         rng.choice((fx.RED, fx.RED, (255, 90, 80), fx.GOLD))))
    frames = []
    for f in range(N):
        img = bg.copy()
        # the bamboo pole
        for y in range(1, STREET):
            put(img, 7, y, (180, 160, 80) if y % 4 else (120, 110, 50))
        put(img, 8, 1, (180, 160, 80))
        # smoke behind everything that's left
        for x, y, pop, _ in items:
            age = f - pop
            if 0 <= age < sec(3.2):
                k = age / sec(3.2)
                puff(img, x + 2 * k + math.sin(age * 0.1 + x), y - 1 - 6 * k, 1.0 + 1.8 * k, fx.SMOKE,
                     0.45 * (1 - k))
        # the cord (it burns away behind the spark)
        spark_x = X1 - (f - LIT) * SPEED if f >= LIT else X1 + 1
        for x in range(X0, X1 + 1):
            if x < spark_x:
                put(img, x, cord_y(x), (150, 40, 40))
        # the crackers still waiting
        for x, y, pop, side in items:
            if f < pop:
                fx.firecracker(img, x - side, y + side)
        # the spark
        if LIT <= f and spark_x > X0:
            sy = cord_y(spark_x)
            add(img, spark_x, sy, (255, 250, 220), 1.0)
            add(img, spark_x + 1, sy - 1, fx.GOLD, 0.8 * (f % 2))
            add(img, spark_x - 1, sy + 1, fx.GOLD_LIGHT, 0.6 * ((f + 1) % 2))
        if LIT - sec(0.6) <= f < LIT:  # a match touches the fuse
            put(img, X1 + 1, cord_y(X1) - 1 + (LIT - f) // 3, fx.GOLD_LIGHT)
        # the pops
        for x, y, pop, side in items:
            age = f - pop
            if 0 <= age < 4:
                fx.flash(img, x - side, y + side + 1, 1 - age / 4)
        # red paper flies and settles on the street
        for pop, x, y, vx, vy, c in bits:
            age = f - pop
            if age < 0:
                continue
            px = x + vx * min(age, 25) * 0.8
            py = y + vy * age + 0.035 * age * age
            if py >= STREET - 1:
                py = STREET - 1 + (1 if int(px * 7) % 3 == 0 else 0)
                c = mix(c, (120, 20, 24), 0.35)
            put(img, px, min(py, H - 1), c)
        nian(img, f)
        if f > sec(9.5):
            glitter(img, seed=4, f=f, n=8, period=40, area=(10, 13, 70, 16), strength=0.5, colors=(fx.GOLD,))
        frames.append(img)
    return frames
