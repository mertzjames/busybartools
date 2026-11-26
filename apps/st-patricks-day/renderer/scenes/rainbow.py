"""Scene: Rainbow's End. A spring shower falls over green hills; the clouds part, the sun comes out, and a rainbow
arcs across the sky to land behind an old iron pot on the hill. A glint slides down the rainbow, the pot overflows
and gold coins tumble out in a glittering pile, and the leprechaun peeks out from behind it to tip his hat."""

import math
import random

from busybar.canvas import H, W, ease_in_out, ease_out, mix, phase, put, sec, vgradient
from busybar.fx import puff
from busybar.party import glitter
from pfx import (GOLD, GOLD_DK, GOLD_HI, SHAMROCK_DK, SHAMROCK_HI, coin, glow, leprechaun, pot, rainbow, shamrock,
                 sparkle4)

NAME = "rainbow"
TITLE = "Rainbow's End"
SECONDS = 15
KEYFRAMES = [(1.0, "A spring shower over the hills"), (4.5, "The clouds part"), (6.6, "A rainbow arcs across"),
             (8.4, "A glint slides down to the pot"), (10.4, "The pot overflows with gold"),
             (13.4, "The leprechaun peeks out and tips his hat")]

POT_X, POT_BASE = 53, 14
RB = dict(cx=29.0, cy=16.0, rx=25.0, ry=16.0)
CLEAR = (sec(2.8), sec(5.4))
ARC = (sec(5.0), sec(7.8))
GLINT = (sec(7.8), sec(9.0))
SPILL = sec(9.0)
PEEK = (sec(11.6), sec(12.4))
TIP = sec(12.8)

CLOUDS = [(6, 2, 4.0), (14, 1, 5.0), (24, 3, 4.5), (34, 1, 5.0), (44, 2, 4.0), (54, 1, 4.5), (64, 3, 5.0)]


def hills(img) -> list[int]:
    tops = []
    for x in range(W):
        top = 12.6 + 1.2 * math.sin(x * 0.09 + 0.4) + 0.5 * math.sin(x * 0.31)
        if abs(x - POT_X) < 9:
            top = min(top, 13.0)  # the pot's hill, a little flatter
        tops.append(int(top))
        for y in range(int(top), H):
            put(img, x, y, mix((50, 170, 64), (26, 112, 44), (y - top) / 3))
    return tops


def coins():
    """Coins flung out of the pot: (launch frame, x0, vx, vy, landing row)."""
    rng = random.Random(41)
    out = []
    for i in range(26):
        t0 = SPILL + int(i * 2.2) + rng.randint(0, 2)
        vx = rng.uniform(-1.0, 0.9)
        out.append((t0, POT_X + rng.uniform(-3, 3), vx, rng.uniform(-1.3, -0.7), rng.choice((14, 15, 15))))
    return out


def render():
    flying = coins()
    rain_rng = random.Random(5)
    drops = [(rain_rng.uniform(0, W), rain_rng.uniform(0, H), rain_rng.uniform(0.9, 1.3)) for _ in range(40)]
    frames = []
    for f in range(sec(SECONDS)):
        clear = ease_in_out(phase(f, *CLEAR))
        img = vgradient(mix((40, 46, 70), (34, 84, 186), clear), mix((70, 80, 100), (130, 184, 236), clear))
        if clear > 0:
            glow(img, 66, 2, 9 * clear, (255, 230, 150), 0.6 * clear)
        # the rainbow, drawn from the left foot over the top to the pot
        reveal = ease_out(phase(f, *ARC))
        if reveal > 0:
            rainbow(img, RB["cx"], RB["cy"], RB["rx"], RB["ry"], reveal=reveal, alpha=0.9)
        tops = hills(img)
        for x, y in ((8, 14), (20, 15), (33, 14), (44, 15)):
            shamrock(img, x, y, 0, SHAMROCK_HI, (190, 255, 160), SHAMROCK_DK)
        # rain, fading as the sky clears
        rain = 1 - phase(f, sec(2.4), sec(4.4))
        if rain > 0:
            for i, (x0, y0, v) in enumerate(drops):
                y = (y0 + f * v) % (H + 2) - 1
                x = (x0 - f * 0.25) % W
                if y < tops[int(x) % W]:
                    put(img, x, y, (180, 206, 255), 0.8 * rain)
                    put(img, x - 0.25, y - 1, (180, 206, 255), 0.35 * rain)
        # clouds drift apart and up
        for i, (cx, cy, r) in enumerate(CLOUDS):
            side = -1 if cx < 36 else 1
            x = cx + side * 30 * clear
            y = cy - 6 * clear
            puff(img, x, y, r, mix((150, 156, 176), (230, 236, 244), clear), 0.95 * (1 - clear * 0.6))
        # the leprechaun, behind the pot
        if f >= PEEK[0]:
            p = ease_out(phase(f, *PEEK))
            hat = int(round(2 * ease_in_out(phase(f, TIP, TIP + sec(0.4))) *
                            (1 - ease_in_out(phase(f, sec(14.0), sec(14.4))))))
            leprechaun(img, POT_X + 4, POT_BASE + 1 - 13 + int(round(8 * (1 - p))),
                       "stand", "out_up" if hat else "hips", hat_lift=hat, blink=(f // 3) % 17 == 0)
        # the pot of gold: heaped up as the gold arrives
        heap = 0.35 + 0.65 * ease_out(phase(f, GLINT[1] - 4, SPILL + 12))
        pot(img, POT_X, POT_BASE, gold=heap, f=f)
        # a glint slides down the rainbow's right half into the pot
        if GLINT[0] <= f < GLINT[1]:
            u = phase(f, *GLINT)
            ang = math.pi / 2 * (1 - u)  # from the top to the right foot
            gx = RB["cx"] + RB["rx"] * 0.86 * math.cos(ang)
            gy = RB["cy"] - RB["ry"] * 0.86 * math.sin(ang)
            sparkle4(img, gx, gy, 1.0, (255, 255, 230))
        if GLINT[1] - 2 <= f < GLINT[1] + 6:
            glow(img, POT_X, POT_BASE - 7, 6, (255, 220, 120), 0.8 * (1 - (f - GLINT[1] + 2) / 8))
        # coins tumble out and settle on the grass
        for i, (t0, x0, vx, vy, land) in enumerate(flying):
            age = f - t0
            if age < 0:
                continue
            x = x0 + vx * age
            y = POT_BASE - 8 + vy * age + 0.12 * age * age
            if y >= land:  # landed: lying flat, glinting now and then
                # solve for the landing time to find where it came down
                a, b, c = 0.12, vy, (POT_BASE - 8) - land
                tl = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)
                lx = int(round(x0 + vx * tl))
                if 0 <= lx < W and abs(lx - POT_X) > 6:
                    put(img, lx, land, GOLD if i % 3 else GOLD_DK)
                    put(img, lx + 1, land, GOLD_DK if i % 3 else GOLD)
                continue
            coin(img, x, y, f, seed=i)
        if f >= SPILL:
            k = phase(f, SPILL, SPILL + 10)
            glitter(img, 23, f, n=14, period=sec(2), colors=(GOLD_HI, (255, 255, 230)), area=(42, 4, 72, 16),
                    strength=0.9 * k)
        frames.append(img)
    return frames

