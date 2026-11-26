"""Spring Flowers: the sun shines on a bare patch of garden. Shoots push up one after another and open into tulips
and daffodils across the whole bed, and two butterflies flutter in; one settles on a tulip."""

import math
import random

from busybar.canvas import new, sec
from busybar.fx import sparkle

import efx

NAME = "flowers"
TITLE = "Spring Flowers"
SECONDS = 15
KEYFRAMES = [(0.4, "A sunny, bare garden"), (2.4, "The first shoots"), (4.6, "Tulips open"),
             (7.0, "Daffodils too"), (9.4, "Butterflies arrive"), (12.0, "One lands on a tulip"),
             (14.4, "A garden in bloom")]

GROUND = 14
TULIP_COLORS = (efx.PINK, (255, 86, 86), efx.LILAC, efx.PEACH, (255, 120, 200))


def plan():
    """[(x, kind, color, height, start frame)] for every flower, grown in a shuffled order across the bed."""
    rng = random.Random(42)
    xs = list(range(3, 70, 4))
    order = xs[:]
    rng.shuffle(order)
    out = []
    for k, x in enumerate(xs):
        kind = "daffodil" if k % 3 == 1 else "tulip"
        color = TULIP_COLORS[k % len(TULIP_COLORS)]
        h = rng.choice((5, 6, 7)) if kind == "tulip" else rng.choice((6, 7))
        start = 18 + order.index(x) * 7
        out.append((x, kind, color, h, start))
    return out


FLOWERS = plan()
LAND = FLOWERS[7]  # the tulip the first butterfly settles on


def background():
    img = new()
    efx.sky(img)
    efx.sun(img, 8, 3, r=3.0, rays=False)
    return img


def butterfly_path(f, k):
    """Two butterflies: in from the right on wavy paths; the first lands on a tulip at about 11 s."""
    t0 = sec(7.6) + k * 20
    age = f - t0
    if age < 0:
        return None
    if k == 0:
        lx, lk, lc, lh, _ = LAND
        land_at = sec(3.4)
        tx, ty = lx, GROUND - 1 - lh - 4
        if age < land_at:
            u = age / land_at
            x = 74 + (tx - 74) * u
            y = ty - 3 + 3 * u + 1.6 * math.sin(age * 0.35)
            return x, y, True
        return tx, ty, (age // 10) % 3 == 0  # resting, wings opening slowly now and then
    x = 76 - age * 0.32
    y = 5 + 2.2 * math.sin(age * 0.22)
    if x < -3:
        return None
    return x, y, True


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        efx.cloud(img, 30 + f / 36, 2, w=8)
        efx.grass(img, GROUND, seed=11)
        for x, kind, color, h, start in FLOWERS:
            age = f - start
            if age < 0:
                continue
            grow = min(1.0, age / 16)
            hh = max(1, round(h * grow))
            open_ = 0.0 if grow < 1 else min(1.0, (age - 16) / 12)
            if kind == "tulip":
                efx.tulip(img, x, GROUND, hh, color, open_ if grow >= 1 else 0.3 * (grow > 0.6))
            else:
                efx.daffodil(img, x, GROUND, hh, open_ if grow >= 1 else 0.3 * (grow > 0.6))
            if 28 <= age < 34:
                sparkle(img, x, GROUND - h - 2, age, (34 - age) / 6, color=(255, 250, 200))
        for k, colors in enumerate((((255, 150, 210), (255, 220, 240)), ((150, 200, 255), (220, 236, 255)))):
            p = butterfly_path(f, k)
            if p:
                x, y, flap = p
                efx.butterfly(img, x, y, f if flap else 1, colors=colors, speed=2)
        frames.append(img)
    return frames
