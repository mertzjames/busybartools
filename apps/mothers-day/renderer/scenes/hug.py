"""A hug under a blooming tree: the blossoms open across a cherry tree on a spring evening while a child runs in from
one side and a grandmother walks in from the other. They meet in a hug, a heart rises, and petals drift over them
(docs/DECISIONS.md D3)."""

import math
import random

from busybar.canvas import W, ease_out, lerp, mix, phase, put, sec

import mfx

NAME = "hug"
TITLE = "A Hug Under the Blossoms"
SECONDS = 15
N = sec(SECONDS)
KEYFRAMES = [(0.6, "A cherry tree in bud"), (3.5, "Blossoms open; here they come"), (6.4, "Almost there"),
             (8.0, "A big hug"), (12.0, "Petals drift over them")]

GROUND = 13
MEET = sec(7.2)
CHILD0, CHILD1 = -4, 31
GRAN0, GRAN1 = 76, 34
CHILD = dict(skin=mfx.SKIN[1], shirt=mfx.YELLOW, legs_c=(90, 130, 230), hair=mfx.HAIR_DARK, style="short",
             child=True)
GRAN = dict(skin=mfx.SKIN[4], shirt=mfx.LAVENDER, legs_c=mfx.PINK_DK, hair=mfx.HAIR_GREY, style="bun", skirt=True)
BLOSSOM = (mfx.PINK, mfx.PINK_HI, (255, 140, 190), (255, 200, 222))


def canopy():
    """Blossom pixels of the tree's crown: [(x, y, color, open frame)]."""
    rng = random.Random(42)
    out = []
    blobs = [(58, 3, 9, 3.2), (49, 4, 6, 2.6), (66, 4, 6, 3.0), (56, 0, 8, 2.2)]
    for y in range(0, 9):
        for x in range(38, W):
            inside = any(((x - bx) / rx) ** 2 + ((y - by) / ry) ** 2 <= 1 for bx, by, rx, ry in blobs)
            if inside and rng.random() < 0.8:
                out.append((x, y, rng.choice(BLOSSOM), sec(0.6) + int(rng.random() ** 0.8 * sec(5.5))))
    return out


def backdrop():
    img = mfx.sky([(0, (18, 20, 64)), (8, (46, 34, 84)), (12, (78, 46, 88))])
    mfx.glow(img, 30, 10, 24, (160, 100, 54), 1.0, squash=1.2)  # the low sun, right behind where they meet
    for x in range(W):
        h = 12 + (1 if math.sin(x * 0.18) > 0.3 else 0)
        for y in range(h, 16):
            put(img, x, y, (40, 120, 60) if y < 14 else (30, 96, 48))
    # trunk and branches (lit brown)
    trunk, hi = (128, 76, 50), (160, 100, 66)
    for y in range(5, 15):
        put(img, 57, y, trunk)
        put(img, 58, y, hi if y > 8 else trunk)
    put(img, 56, 14, trunk)
    put(img, 59, 14, trunk)
    for bx, by, d, n in ((56, 6, -1, 7), (59, 6, 1, 6), (57, 4, -1, 4), (58, 4, 1, 4)):
        for k in range(n):
            put(img, bx + d * k, by - k // 2, trunk)
    return img


def render():
    base = backdrop()
    crown = canopy()
    rng = random.Random(7)
    petals = [(rng.uniform(38, 74), rng.uniform(0, 1), rng.uniform(0.5, 1.0), rng.choice(BLOSSOM[:3]))
              for _ in range(16)]
    frames = []
    for f in range(N):
        img = base.copy()
        for x, y, c, t0 in crown:
            if f >= t0:
                put(img, x, y, c)
            elif f >= t0 - sec(1.5) and (x + y) % 3 == 0:
                put(img, x, y, (170, 110, 120), 0.8)  # a bud
        # the two walk toward each other, then hug
        if f < MEET:
            p = phase(f, sec(1.2), MEET)
            cx = int(round(lerp(CHILD0, CHILD1, ease_out(p) if p < 1 else 1)))
            gx = int(round(lerp(GRAN0, GRAN1, p)))
            run = (f // 3) % 2
            walk = (f // 5) % 2
            mfx.person(img, gx, GROUND, arms=(0.1 + 0.15 * (p > 0.7), 0.06), legs=walk, **GRAN)
            mfx.person(img, cx, GROUND, arms=(0.12 * run, 0.2 if p > 0.6 else 0.12 * (1 - run)), legs=run, **CHILD)
        else:
            sway = 1 if ((f - MEET) // sec(1.6)) % 2 and f > MEET + sec(2) else 0
            gx, cx = GRAN1 + sway, CHILD1 + sway
            mfx.person(img, gx, GROUND, **GRAN)
            mfx.person(img, cx, GROUND, **CHILD)
            for x in range(cx - 1, gx - 1):  # Grandma's arm around the child's shoulders
                put(img, x, 9, GRAN["skin"])
            put(img, gx - 2, 8, GRAN["shirt"])
            for x in range(cx + 2, gx + 3):  # the child's arm around Grandma's waist
                put(img, x, 10, CHILD["skin"])
            if f >= MEET + sec(0.5):  # a heart rises over them
                q = phase(f, MEET + sec(0.5), MEET + sec(3.5))
                y = lerp(5, 0, ease_out(q))
                mfx.heart(img, cx - 6, y, 5 if q < 1 else 7 if (f // 8) % 2 else 5, mfx.ROSE,
                          alpha=1.0)
        # petals drift down and to the left once the tree is in bloom
        if f >= sec(4):
            k = min(1.0, (f - sec(4)) / sec(2))
            for i, (x0, ph, speed, c) in enumerate(petals):
                if i / len(petals) > k:
                    continue
                age = ((f - sec(4)) * speed / sec(5) + ph) % 1.0
                x = x0 - age * 40 + 1.5 * math.sin(age * 12 + i)
                y = 3 + age * 11
                mfx.petal(img, x, y, f + i, c)
        frames.append(img)
    return frames
