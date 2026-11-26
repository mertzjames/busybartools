"""Scene: dawn over Galveston Bay. Quiet and slow (docs/DECISIONS.md D3).

The night sky lightens through three quantized stops to a warm horizon; the stars fade; a lighthouse on a spit of
land sweeps its beam until the day takes over; a two-masted ship drifts across the bay with its sails catching the
first light; gulls cross; and the sun's rim rises with a golden path on the water. No text: it is the morning
before the news.
"""

import math
import random

from busybar.canvas import H, W, add, blit, ease_in_out, mix, phase, put, sec
from busybar.fx import Stars

import jfx
from sprites import LIGHTHOUSE, SHIP

NAME = "dawn"
TITLE = "Dawn over Galveston Bay"
SECONDS = 14
KEYFRAMES = [(0.5, "Before dawn: the lighthouse sweeps the bay"), (4.0, "A ship drifts in"),
             (8.0, "The sky lightens; gulls cross"), (11.0, "The sun's rim rises"),
             (13.5, "Morning over the bay")]

HORIZON = 11  # first water row
SUN_X = 57

NIGHT = [(0, (6, 8, 30)), (6, (18, 18, 58)), (10, (52, 30, 70))]
DAY = [(0, (44, 76, 156)), (6, (150, 112, 150)), (10, (255, 168, 92))]


def sky_at(p: float):
    stops = [(y, jfx.qmix(a, b, p)) for (y, a), (_, b) in zip(NIGHT, DAY)]
    return jfx.sky(stops)


def render():
    stars = Stars(seed=61, n=16, ymax=8, period=sec(4), color=(220, 226, 255), dim=0.15, bright=0.8)
    rng = random.Random(62)
    ripples = [(rng.randrange(W), rng.randrange(HORIZON + 1, H), rng.choice((2, 3)), rng.random()) for _ in range(26)]
    frames = []
    cache = {}
    for f in range(sec(SECONDS)):
        p = ease_in_out(phase(f, sec(1.0), sec(12.5)))
        key = math.floor(p * 40 + 0.5)
        if key not in cache:
            cache[key] = sky_at(key / 40)
        img = cache[key].copy()
        # stars fade with the light
        if p < 0.7:
            stars.draw(img, f, alpha=1 - p / 0.7)
        # the sun's rim and its glow (steady glow, no flicker)
        sun = phase(f, sec(8.0), sec(13.5))
        if sun > 0:
            cy = HORIZON + 2.5 - 5.5 * ease_in_out(sun)
            jfx.glow(img, SUN_X, HORIZON - 1, 9, (120, 70, 20), 0.5 * sun, squash=1.6)
            for y in range(HORIZON):
                for x in range(SUN_X - 4, SUN_X + 5):
                    if (x - SUN_X) ** 2 + (y - cy) ** 2 <= 11.5:
                        put(img, x, y, (255, 236, 160) if y < cy else (255, 200, 90))
        # water: the sky's colors, darkened, then ripples
        top_c = img.getpixel((0, HORIZON - 1))[:3]
        for y in range(HORIZON, H):
            c = mix(jfx.qmix((10, 14, 40), (60, 70, 120), p), top_c, 0.35 - 0.06 * (y - HORIZON))
            for x in range(W):
                put(img, x, y, c)
        for x0, y, ln, ph in ripples:
            x = (x0 + f * 0.12 * (1 + (y - HORIZON) * 0.3)) % (W + 6) - 3
            k = 0.5 + 0.5 * math.sin(2 * math.pi * (f / sec(3) + ph))
            if k < 0.35:
                continue
            for dx in range(ln):
                add(img, x + dx, y, jfx.qmix((40, 50, 90), (255, 190, 120), p), 0.25 * k)
        if sun > 0:  # a golden path on the water under the sun
            for y in range(HORIZON, H):
                for dx in range(-2, 3):
                    x = SUN_X + dx + (1 if (y + f // 4) % 3 == 0 else 0)
                    if ((x * 7 + y * 3 + f // 3) % 4) < 2:
                        add(img, x, y, (255, 200, 100), sun * (0.55 - 0.1 * abs(dx)))
        # the ship drifts left to right, its sails warming with the light
        sx = -18 + 52 * f / sec(SECONDS)
        ship = SHIP.img(0)
        lit = ship.copy()
        px = lit.load()
        for yy in range(lit.height):
            for xx in range(lit.width):
                r, g, b, a = px[xx, yy]
                if a:
                    k = 0.35 + 0.65 * p if yy < 6 else 0.45 + 0.4 * p
                    c = mix((r, g, b), (40, 40, 70), 1 - k)
                    px[xx, yy] = c + (a,)
        blit(img, lit, sx, HORIZON - 9)
        for yy in range(5):  # a broken reflection of the sails
            for xx in range(lit.width):
                r, g, b, a = px[xx, 4 - yy]
                if a and (xx + yy + f // 5) % 3:
                    add(img, sx + xx, HORIZON + 1 + yy, (r, g, b), 0.22 - 0.035 * yy)
        # land and the lighthouse
        for x in range(0, 13):
            top = 12 if x < 9 else 13 + (x > 10)
            for y in range(top, H):
                put(img, x, y, jfx.qmix((24, 28, 30), (70, 66, 44), p) if y > top else jfx.qmix((34, 40, 38),
                                                                                              (96, 90, 56), p))
        lh = LIGHTHOUSE.img(0).copy()
        lpx = lh.load()
        for yy in range(lh.height):
            for xx in range(lh.width):
                r, g, b, a = lpx[xx, yy]
                if a and yy != 2:
                    lpx[xx, yy] = mix((r, g, b), (36, 36, 60), 0.55 * (1 - p)) + (a,)
        blit(img, lh, 3, 1)
        # the lamp's beam sweeps round (4 s a turn) and fades as the day comes
        beam = max(0.0, 1 - p * 1.4)
        if beam > 0:
            th = 2 * math.pi * f / sec(4)
            c = math.cos(th)
            jfx.glow(img, 5, 3, 3, (255, 210, 110), 0.45 * beam)
            if c > 0.15:
                for d in range(2, 34):
                    k = c * beam * (1 - d / 34) * 0.55
                    add(img, 5 + d, 3 + d * 0.06, (255, 220, 140), k)
                    add(img, 5 + d, 2 + d * 0.06, (255, 220, 140), k * 0.4)
                    add(img, 5 + d, 4 + d * 0.06, (255, 220, 140), k * 0.4)
            if math.sin(th) > 0.9:  # the beam faces us: a flash
                for dx in (-1, 0, 1):
                    add(img, 5 + dx, 3, (255, 240, 200), 0.6 * beam)
        # gulls: wings spread, flapping, crossing high
        for i, (t0, y0, speed) in enumerate(((sec(6.5), 3, 0.32), (sec(7.3), 5, 0.28))):
            age = f - t0
            if age < 0:
                continue
            gx = -3 + age * speed
            gy = y0 + math.sin(age * 0.08 + i) * 0.8
            up = (age // 4 + i) % 2 == 0
            gc = jfx.qmix((150, 150, 170), (236, 236, 240), p)
            put(img, gx, gy, gc)
            put(img, gx - 1, gy - (1 if up else 0), gc)
            put(img, gx + 1, gy - (1 if up else 0), gc)
            put(img, gx - 2, gy - (1 if up else -1) * (1 if up else 0), gc, 0.7)
            put(img, gx + 2, gy - (1 if up else -1) * (1 if up else 0), gc, 0.7)
        frames.append(img)
    return frames
