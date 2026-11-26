"""Growing together: a parent and child work along a garden bed on a sunny spring day. The child drops seeds, the
parent waters them, and sprouts shoot up behind them and open into tulips, daisies, roses and lavender. A butterfly
visits at the end (docs/DECISIONS.md D3)."""

import math

from busybar.canvas import H, W, add, ease_out, lerp, mix, phase, put, sec

import mfx

NAME = "garden"
TITLE = "Growing Together"
SECONDS = 16
N = sec(SECONDS)
KEYFRAMES = [(0.6, "A spring morning in the garden"), (3.0, "Seeds and a watering can"),
             (6.5, "Sprouts come up behind them"), (10.5, "The bed fills with flowers"),
             (14.0, "A butterfly visits")]

GROUND = 13  # the figures' feet; the bed is rows 14-15 in front of them
SPOTS = [3, 8, 13, 18, 23, 28, 33, 38, 43, 48, 53]  # flower columns
KINDS = [("tulip", mfx.PINK), ("daisy", mfx.WHITE), ("rose", mfx.ROSE), ("lavender", None),
         ("tulip", mfx.YELLOW), ("daisy", mfx.WHITE), ("tulip", mfx.LAVENDER), ("rose", mfx.PINK),
         ("daisy", mfx.WHITE), ("tulip", mfx.CORAL), ("lavender", None)]
HEADS = [7, 8, 6, 8, 7, 9, 6, 7, 8, 6, 8]  # head top rows
WALK0, WALK1 = sec(0.8), sec(11.0)
PARENT0, PARENT1 = -6, 57
CHILD_AHEAD = 7
GROW = sec(2.2)
PARENT = dict(skin=mfx.SKIN[0], shirt=mfx.CORAL, legs_c=(70, 100, 200), hair=mfx.PINK, style="hat")
CHILD = dict(skin=mfx.SKIN[2], shirt=mfx.GREEN_HI, legs_c=(200, 120, 60), hair=mfx.HAIR_DARK, style="long",
             child=True)


def backdrop():
    img = mfx.sky([(0, (56, 112, 196)), (11, (120, 170, 226)), (12, (120, 170, 226))])
    mfx.glow(img, 66, 2, 9, (120, 100, 40), 0.9)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if abs(dx) + abs(dy) < 2:
                put(img, 66 + dx, 2 + dy, mfx.YELLOW_HI)
    for x in range(W):  # a far hedge, then the lawn
        h = 11 + (1 if math.sin(x * 0.7) + math.sin(x * 0.31) > 0.6 else 0)
        for y in range(h, 13):
            put(img, x, y, (40, 120, 60))
        put(img, x, 13, mfx.GREEN)
    return img


def cloud(img, x: float, y: int) -> None:
    for dx, dy in ((0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 1), (4, 1), (3, 0)):
        put(img, x + dx, y + dy, (232, 240, 255), 0.85)


def bed(img) -> None:
    for x in range(W):
        for y in (14, 15):
            put(img, x, y, mfx.SOIL if (x + y) % 3 else mfx.SOIL_DK)


def parent_x(f: int) -> int:
    return int(round(lerp(PARENT0, PARENT1, phase(f, WALK0, WALK1))))


def watered(spot: int) -> int:
    """The frame the parent's can reaches spot column x (the can is 4 px right of the parent)."""
    for f in range(N):
        if parent_x(f) + 5 >= spot:
            return f
    return N


def render():
    base = backdrop()
    water_at = [watered(x) for x in SPOTS]
    frames = []
    for f in range(N):
        img = base.copy()
        cloud(img, 10 + f * 0.04, 2)
        cloud(img, 38 + f * 0.03, 4)
        walking = WALK0 <= f < WALK1
        step = 1 if walking and (f // 4) % 2 else 0
        px = parent_x(f)
        cx = px + CHILD_AHEAD
        # flowers behind the figures? No: the bed is in front; draw figures first
        hands = mfx.person(img, px, GROUND, arms=(0.0, 0.22), legs=step, **PARENT)
        # the watering can at the parent's right hand, tipped while walking
        hx, hy = hands["r"]
        can = (90, 196, 210)
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put(img, hx + dx, hy - 1 + dy, can)
        put(img, hx + 2, hy - 1, mix(can, mfx.WHITE, 0.3))
        put(img, hx - 1, hy - 1, mix(can, (0, 0, 0), 0.3))
        if walking:  # water drops from the spout to the soil
            for k in range(3):
                age = ((f + k * 3) % 9) / 9
                put(img, hx + 3 + age * 1.5, hy + age * (GROUND + 1 - hy), (170, 220, 255), 0.9)
        # the child, a step ahead, dropping seeds
        ch_step = 1 if walking and ((f + 2) // 4) % 2 else 0
        chands = mfx.person(img, cx, GROUND, arms=(0.06, 0.18 if walking else 0.0), legs=ch_step, **CHILD)
        if walking and (f % 10) < 6:
            sx, sy = chands["r"]
            put(img, sx, sy + 1 + (f % 10) // 2, (226, 190, 120))
        if f >= WALK1 + sec(1.2):  # they look back at the garden: the child waves
            wave = 0.4 + 0.08 * math.sin(f * 0.8)
            mfx.person(img, cx, GROUND, arms=(0.06, wave), **CHILD)
        bed(img)
        # flowers grow where they were watered
        for i, x in enumerate(SPOTS):
            t0 = water_at[i] + sec(0.3)
            if f < t0:
                continue
            g = phase(f, t0, t0 + GROW)
            top = HEADS[i]
            stem_top = int(round(lerp(GROUND + 1, top + 2, ease_out(min(1.0, g * 1.6)))))
            for y in range(stem_top, 16):
                put(img, x, y, mfx.GREEN)
            if g > 0.35:
                put(img, x - 1, 12, mfx.GREEN_HI)
                put(img, x + 1, 11, mfx.GREEN_HI) if g > 0.5 else None
            kind, color = KINDS[i]
            mfx.bloom(img, kind, x, top, color, grow=max(0.0, (g - 0.45) / 0.55) if g < 1 else 1.0)
        # a butterfly flits over the finished bed
        if f >= sec(12):
            q = (f - sec(12)) / sec(4)
            bx = lerp(6, 50, q)
            by = 5 + 2.5 * math.sin(q * 9)
            mfx.butterfly(img, bx, by, f, mfx.YELLOW)
        frames.append(img)
    return frames
