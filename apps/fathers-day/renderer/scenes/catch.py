"""Scene: playing catch on a summer morning. A parent and a child stand across a mowed lawn under a blue sky and toss a
ball back and forth: a big lob, a bouncing throw back, then a high one that sends the child backing up to make the
catch. Both cheer, and they keep playing."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec

import ffx

NAME = "catch"
TITLE = "Playing Catch"
SECONDS = 14
KEYFRAMES = [(0.6, "A summer morning in the yard"), (1.8, "A big lob"), (2.6, "Caught!"), (4.4, "A bouncer back"),
             (7.0, "A high one"), (8.2, "Backing up... got it!"), (9.0, "A cheer"), (11.0, "And again")]

LAWN = 11  # the lawn starts on this row
DAD_X = 13
KID_X0 = 56

BALL = (255, 238, 70)  # a yellow softball: white vanished against the pale sky
BALL_SHADE = (214, 176, 30)

# throws: (start s, end s, from, to, peak height in rows above the straight line, bounce at fraction or None)
DAD_HAND = (13.0, 6.0)


def kid_x(s: float) -> float:
    if s < 6.6:
        return KID_X0
    if s < 7.9:
        return KID_X0 + 4 * phase(int(s * 15), sec(6.6), sec(7.9))
    if s < 10.5:
        return KID_X0 + 4
    return KID_X0 + 4 - 4 * phase(int(s * 15), sec(10.5), sec(11.5))


def arc(a, b, t: float, h: float):
    x = a[0] + (b[0] - a[0]) * t
    y = a[1] + (b[1] - a[1]) * t - h * 4 * t * (1 - t)
    return x, y


def base_frame():
    img = ffx.sky([(0, (60, 128, 214)), (6, (106, 176, 238)), (LAWN - 1, (160, 206, 244))])
    # far trees along the back of the yard
    for x in range(W):
        top = LAWN - 2 - (1 if math.sin(x * 0.45) + math.sin(x * 0.17 + 2) > 0.6 else 0)
        for y in range(top, LAWN):
            put(img, x, y, (54, 120, 70) if (x + y) % 3 else (66, 136, 80))
    # the lawn, mowed in stripes
    for y in range(LAWN, H):
        for x in range(W):
            band = ((x + (y - LAWN)) // 6) % 2
            put(img, x, y, mix(ffx.GRASS, ffx.GRASS_HI, 0.35) if band else ffx.GRASS)
    # a shade tree at the left edge and a bush on the right
    ffx.tree(img, 2, 0, r=4.5, base=12, seed=2)
    for x in range(67, W):
        for y in range(8, 12):
            if (x - 69) ** 2 + (y - 11) ** 2 * 2 <= 9:
                put(img, x, y, ffx.GRASS_DK if (x + y) % 3 else ffx.GRASS)
    return img


def render():
    base = base_frame()
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        s = f / 15
        # two drifting clouds (whole-pixel steps every few frames)
        ffx.cloud(img, 24 + f // 12, 1, 8)
        ffx.cloud(img, 48 + f // 18, 3, 6, a=0.8)

        kx = kid_x(s)
        kid_hand = (kx - 2.5, 8.0)
        dad_catch = (DAD_X + 3.0, 7.0)
        throws = [
            (1.0, 2.4, DAD_HAND, kid_hand, 6.5, None),
            (3.4, 5.2, (KID_X0 - 2.5, 9.0), dad_catch, 2.0, 0.55),
            (6.2, 7.9, DAD_HAND, (KID_X0 + 1.5, 6.0), 10.0, None),
            (10.0, 11.5, (KID_X0 + 1.5, 9.0), dad_catch, 4.0, None),
            (12.6, 14.2, DAD_HAND, kid_hand, 6.5, None),
        ]
        ball = None
        for t0, t1, a, b, h, bounce in throws:
            if t0 <= s < t1:
                t = (s - t0) / (t1 - t0)
                if bounce is None:
                    ball = arc(a, b, t, h)
                else:  # down to the grass, then a bounce up to the catcher
                    g = (a[0] + (b[0] - a[0]) * bounce, 13.0)
                    ball = arc(a, g, t / bounce, h) if t < bounce else arc(g, b, (t - bounce) / (1 - bounce), 3.0)
                trail = [arc(a, b, max(0.0, t - d / (t1 - t0) / 15), h) if bounce is None else None for d in (2, 4)]
                for k, p in enumerate(trail):
                    if p:
                        put(img, p[0], p[1], BALL, 0.4 - 0.15 * k)
        # who holds the ball between throws
        holding = None
        if s < 1.0 or 5.2 <= s < 6.2 or 11.5 <= s < 12.6:
            holding = "dad"
        elif 2.4 <= s < 3.4 or 7.9 <= s < 10.0:
            holding = "kid"

        # the parent: winds up and throws, catches in front
        dad_arms = (0.06, 0.06)
        for t0 in (1.0, 6.2, 12.6):
            if t0 - 0.6 <= s < t0:
                dad_arms = (0.1, 0.5)  # wind-up, arm high
            elif t0 <= s < t0 + 0.4:
                dad_arms = (0.1, 0.32)  # follow-through
        if 4.7 <= s < 6.2 or 11.0 <= s < 12.6:
            dad_arms = (0.18, 0.3)  # hands out to catch
        cheer = 8.4 <= s < 9.8
        if cheer:
            dad_arms = (0.45, 0.45) if (f // 4) % 2 else (0.5, 0.5)
        hands = ffx.figure(img, DAD_X, 14, ffx.SKIN_LIGHT, (244, 122, 40), (62, 96, 160), hair=ffx.HAIR_BROWN,
                           cap=(214, 40, 48), facing=1, arms=dad_arms)
        if holding == "dad":
            ball = hands["r"]

        # the child: catches up high, backs up for the long one, jumps for joy
        kid_arms = (0.08, 0.08)
        if 2.0 <= s < 3.0 or 7.4 <= s < 8.4:
            kid_arms = (0.42, 0.38)  # reaching up
        for t0 in (3.4, 10.0):
            if t0 - 0.5 <= s < t0:
                kid_arms = (0.1, 0.48) if t0 == 10.0 else (0.48, 0.1)
        jump = 0
        if cheer:
            kid_arms = (0.5, 0.5)
            jump = 1 if (f // 4) % 2 else 0
        walking = 6.6 <= s < 7.9 or 10.5 <= s < 11.5
        legs = 1 if walking and (f // 3) % 2 else 0
        khands = ffx.figure(img, ffx.rnd(kx), 14 - jump, ffx.SKIN_TAN, (186, 92, 226), (60, 90, 150),
                            hair=ffx.HAIR_AUBURN, style="pony", kid=True, facing=-1, arms=kid_arms, legs=legs)
        if holding == "kid":
            ball = khands["l"] if not (9.5 <= s < 10.0) else khands["r"]
        if 7.9 <= s < 8.6:  # the catch sparkles
            k = 1 - (s - 7.9) / 0.7
            bx, by = khands["l"]
            for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1), (0, -2)):
                add(img, bx + dx * (1 + (1 - k)), by + dy * (1 + (1 - k)), ffx.GOLD_HI, 0.8 * k)

        if ball is not None:
            bx, by = ball
            if by < 13.5:  # its shadow on the lawn
                put(img, bx, 15, (30, 90, 34), 0.5)
            bx, by = ffx.rnd(bx - 0.5), ffx.rnd(by - 0.5)  # a 2x2 ball: one pixel was too easy to miss
            for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
                put(img, bx + dx, by + dy, BALL if dx + dy < 2 else BALL_SHADE)
        frames.append(img)
    return frames
