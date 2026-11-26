"""The Egg Hunt: two kids walk through the garden. One spots the eggs peeking out from behind the bushes and in the
tulips, picks each one up and tosses it into the basket the other is carrying, which fills up egg by egg. With
four found, they jump and cheer."""

import math

from busybar.canvas import mix, new, put, sec
from busybar.fx import sparkle

import efx

NAME = "egg_hunt"
TITLE = "The Egg Hunt"
SECONDS = 16
KEYFRAMES = [(0.6, "Two kids with a basket"), (2.2, "An egg by the bush!"), (3.0, "Into the basket"),
             (6.5, "Another one"), (10.4, "A third"), (13.2, "One in the tulips"), (15.2, "A full basket: hooray!")]

GROUND = 14
SPEED = 0.6  # px per frame while walking
STOP = 26  # frames per find: bend 0-5, hold 6-9, toss 10-21, stand 22-25
GAP = 12  # the basket carrier walks this far behind the finder

FINDER = {"shirt": (100, 220, 150), "hair": (236, 186, 80), "skin": (178, 118, 78), "pants": (96, 80, 200)}
CARRIER = {"shirt": (255, 120, 150), "hair": (150, 80, 46), "skin": (246, 196, 160), "pants": (60, 110, 210)}

# eggs: (x, color, pattern); the finder stops with its hand just in front of each
EGGS = [(20, efx.PINK, "zigzag"), (37, efx.LEMON, "stripes"), (53, efx.LILAC, "dots"), (66, efx.PEACH, "band")]
BUSHES = [(23, 8, 7), (40, 8, 6), (56, 7, 6)]
TULIPS = [(64, (255, 90, 90)), (71, efx.LILAC), (6, efx.LEMON), (10, efx.PINK)]


def schedule():
    """[(start frame, end frame, kind, x0, x1, egg index)] for the finder."""
    plan, f, x = [], 0, -6.0
    for i, (ex, _, _) in enumerate(EGGS):
        target = ex - 5
        n = int(math.ceil((target - x) / SPEED))
        plan.append((f, f + n, "walk", x, float(target), i))
        f += n
        x = float(target)
        plan.append((f, f + STOP, "find", x, x, i))
        f += STOP
    plan.append((f, sec(SECONDS), "cheer", x, x, -1))
    return plan


PLAN = schedule()


def state(f):
    for t0, t1, kind, x0, x1, i in PLAN:
        if t0 <= f < t1:
            u = (f - t0) / max(1, t1 - t0)
            return kind, x0 + (x1 - x0) * u, f - t0, i
    return "cheer", PLAN[-1][3], f - PLAN[-1][0], -1


def found_by(f):
    """Indices of eggs already in the basket at frame f, and the egg in the air (index, progress) if any."""
    done, flying = [], None
    for t0, t1, kind, x0, x1, i in PLAN:
        if kind != "find":
            continue
        if f >= t0 + 22:
            done.append(i)
        elif f >= t0 + 10:
            flying = (i, (f - t0 - 10) / 12)
    return done, flying


def background():
    img = new()
    efx.sky(img)
    efx.sun(img, 46, 2, r=2.4, rays=False)
    return img


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        efx.cloud(img, 14 + f / 28, 1)
        efx.cloud(img, 28 + f / 40, 3, w=7, alpha=0.85)
        efx.grass(img, GROUND - 1, seed=8)
        kind, fx_, age, cur = state(f)
        done, flying = found_by(f)
        # eggs still hiding (the one being picked up rides in the finder's hand)
        for i, (ex, c, pat) in enumerate(EGGS):
            picked = i in done or (flying and flying[0] == i) or (kind == "find" and cur == i and age >= 6)
            if not picked:
                efx.egg(img, ex, GROUND - 6, 5, 7, c, pat)
        for x, w, h in BUSHES:
            efx.bush(img, x, GROUND, w, h, seed=x + 1, blossoms=(255, 220, 240))
        for x, c in TULIPS:
            efx.tulip(img, x, GROUND - 1, 5, c)
        # the kids
        fx_ = round(fx_)
        walking = kind == "walk"
        step = (f // 4) % 2 if walking else 0
        cheer = kind == "cheer"
        jump = cheer and (age // 6) % 2 == 0 and age > 3
        bend = 1.0 if (kind == "find" and age < 10) else 0.0
        cx = fx_ - GAP
        lift = 1 if jump else 0
        hop = 1 if cheer and (age // 6) % 2 == 1 else 0  # the carrier hops on the other beat
        efx.kid(img, cx, GROUND, step=step, lift=hop, **CARRIER)
        # the carrier's basket, held out in front, filling up
        bx, by = cx + 5, GROUND - 2 - hop
        efx.basket(img, bx, by, 6, 3, 3, back=True, front=False)
        for k, i in enumerate(done):
            c = EGGS[i][1]
            put(img, bx + 1 + (k % 4), by - 3 - (k // 4), c)
            put(img, bx + 1 + (k % 4), by - 2, mix(c, efx.ACCENT[c], 0.5))
        efx.basket(img, bx, by, 6, 3)
        hand = efx.kid(img, fx_, GROUND, step=(step + 1) % 2 if walking else 0, bend=bend, arms_up=cheer and jump,
                       lift=lift, **FINDER)
        # the egg in the finder's hand, then tossed in an arc into the basket
        if kind == "find" and 6 <= age < 10:
            ex, c, pat = EGGS[cur]
            efx.egg(img, hand[0] - 1, hand[1] - 3, 3, 4, c, "stripes", shine=False)
        if flying:
            i, u = flying
            c = EGGS[i][1]
            sx, sy = fx_ + 4, GROUND - 6
            tx, ty = bx + 2, by - 3
            x = sx + (tx - sx) * u
            y = sy + (ty - sy) * u - 7 * math.sin(math.pi * u)
            efx.egg(img, round(x) - 1, round(y) - 2, 3, 4, c, "stripes", shine=False)
        # a sparkle when each egg lands
        for t0, t1, k_, x0, x1, i in PLAN:
            if k_ == "find" and 0 <= f - (t0 + 22) < 8:
                a = f - (t0 + 22)
                sparkle(img, bx + 3, by - 4, a, 1 - a / 8)
        if cheer:
            for k in range(3):
                if (f // 3 + k * 2) % 5 == 0:
                    sparkle(img, bx + 1 + 2 * k, by - 6 - k % 2, f, 0.8, color=(255, 240, 160))
        frames.append(img)
    return frames
