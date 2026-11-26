"""Scene: fixing the bike, then the first ride. In a sunny driveway a parent kneels by a bike and tightens the back
wheel with a wrench while the child waits in a helmet. A spin of the wheel, a happy hop, and the child climbs on. The
parent jogs alongside holding the seat, lets go, and cheers as the child rides off on their own."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec

import ffx

NAME = "bike"
TITLE = "The First Ride"
SECONDS = 14
KEYFRAMES = [(1.0, "A wobbly back wheel"), (2.4, "Tightened with a wrench"), (4.6, "A spin: good as new"),
             (6.8, "Climbing on"), (8.4, "Holding the seat..."), (10.0, "...and letting go"),
             (12.0, "Riding off on their own"), (13.4, "A big cheer")]

GROUND = 14  # feet and tire bottoms; the driveway is rows 14-15
BIKE_X0 = 28  # the rear hub's column at the start
FRAME = (236, 56, 64)
TIRE = (70, 70, 86)  # a lit charcoal: grey tires vanished against the pale sky
SPOKE = (214, 214, 226)
CHROME = (226, 226, 236)

DAD = dict(skin=ffx.SKIN_BROWN, shirt=(250, 250, 244), pants=(64, 82, 132), hair=ffx.HAIR_DARK, style="buzz")
KID = dict(skin=ffx.SKIN_BROWN, shirt=(60, 206, 226), pants=(232, 160, 48), cap=(255, 196, 40), kid=True)


def wheel(img, cx: float, cy: float, angle: float) -> None:
    """A 5x5 wheel: a grey tire ring, a hub, and two spokes at `angle` (turns)."""
    cx, cy = ffx.rnd(cx), ffx.rnd(cy)
    for dx, dy in ((-1, -2), (0, -2), (1, -2), (-2, -1), (2, -1), (-2, 0), (2, 0), (-2, 1), (2, 1), (-1, 2), (0, 2),
                   (1, 2)):
        put(img, cx + dx, cy + dy, TIRE)
    put(img, cx, cy, CHROME)
    a = 2 * math.pi * angle
    for k in (0, math.pi):
        put(img, cx + ffx.rnd(math.cos(a + k)), cy + ffx.rnd(math.sin(a + k)), SPOKE, 0.8)


def bike(img, bx: float, angle: float, crank: float) -> dict:
    """The bike, facing right, rear hub at column bx and front hub 9 px ahead, so the frame sits between the wheels
    instead of on top of them. Returns the seat and the handlebar points."""
    x = ffx.rnd(bx)
    cy = GROUND - 2
    wheel(img, x, cy, angle)
    wheel(img, x + 9, cy, angle)
    # an open step-through frame (a filled diamond read as a red blob at this size)
    ffx.line(img, x + 1, cy, x + 4, cy, FRAME)  # chain stay
    ffx.line(img, x + 3, cy - 1, x + 3, cy - 4, FRAME)  # seat tube
    ffx.line(img, x + 4, cy, x + 7, cy - 3, FRAME)  # down tube
    put(img, x + 8, cy - 4, CHROME)  # head tube and fork
    put(img, x + 8, cy - 3, CHROME)
    put(img, x + 8, cy - 2, CHROME)
    put(img, x + 9, cy - 1, CHROME)
    put(img, x + 2, cy - 5, (84, 84, 100))  # the saddle (a lit charcoal)
    put(img, x + 3, cy - 5, (110, 110, 126))
    put(img, x + 4, cy - 5, (84, 84, 100))
    put(img, x + 8, cy - 5, (84, 84, 100))  # handlebars
    put(img, x + 7, cy - 5, (84, 84, 100))
    a = 2 * math.pi * crank  # the pedal crank
    put(img, x + 4 + ffx.rnd(1.2 * math.cos(a)), cy + ffx.rnd(1.2 * math.sin(a)), (250, 250, 250))
    return {"seat": (x + 3, cy - 5), "bars": (x + 7, cy - 5)}


def base_frame():
    img = ffx.sky([(0, (70, 150, 230)), (7, (120, 190, 246)), (GROUND - 1, (180, 220, 250))])
    ffx.sun(img, 60, 2, 2.2, halo=0.25)
    ffx.cloud(img, 36, 2, 9)
    # the house and its open garage on the left
    for y in range(4, GROUND):
        for x in range(0, 19):
            put(img, x, y, (238, 222, 184) if (y % 3) else (226, 208, 170))
    for y, (x0, x1) in zip(range(0, 4), ((0, 14), (0, 16), (0, 18), (0, 20))):
        for x in range(x0, x1 + 1):
            put(img, x, y, (170, 74, 60) if (x + y) % 4 else (150, 62, 50))
    for y in range(6, GROUND):  # the garage: warm, lit inside, with a shelf of paint cans
        for x in range(3, 15):
            put(img, x, y, mix((112, 92, 80), (84, 70, 64), (y - 6) / 7))
    for x, c in ((5, (220, 80, 80)), (7, (80, 140, 220)), (9, (240, 200, 70)), (12, (120, 200, 120))):
        put(img, x, 8, c)
    for x in range(4, 14):
        put(img, x, 9, (150, 110, 80))
    for x in range(3, 15):
        put(img, x, 5, (250, 250, 244))  # the door rolled up
    # a tree on the right, grass, then the driveway and the sidewalk
    ffx.tree(img, 66, 1, r=5, base=GROUND - 1, seed=5)
    for y in range(GROUND - 4, GROUND):  # a lawn strip behind the driveway, so the wheels read against green
        for x in range(19, W):
            put(img, x, y, ffx.GRASS if (x + y) % 5 else ffx.GRASS_HI)
    for y in (GROUND, GROUND + 1):
        for x in range(W):
            c = (150, 150, 156) if y == GROUND else (128, 128, 136)
            if x % 12 == 0:
                c = (110, 110, 118)  # the cracks between slabs
            put(img, x, y, c)
    return img


def render():
    base = base_frame()
    frames = []
    angle = 0.0
    crank = 0.0
    for f in range(sec(SECONDS)):
        img = base.copy()
        s = f / 15

        # the bike's position and the wheel speed
        ride = phase(f, sec(6.8), sec(9.6))
        solo = phase(f, sec(9.6), sec(12.6))
        bx = BIKE_X0 + 16 * ride + 34 * solo * solo
        speed = 0.0
        if 4.2 <= s < 6.0:
            speed = 0.25 * (1 - (s - 4.2) / 1.8)  # the spin, slowing down
        elif 6.8 <= s:
            speed = 0.08 + 0.12 * solo
        elif 1.0 <= s < 1.6:
            speed = 0.02
        angle += speed
        if s >= 6.8:
            crank += 0.06 + 0.06 * solo
        wob = 0
        if s < 1.6 and (f // 3) % 2:
            wob = 1  # the loose wheel wobbles
        pts = bike(img, bx, angle, crank)
        if wob:
            put(img, ffx.rnd(bx) - 1, GROUND - 2, TIRE, 0.7)

        # the parent: kneels with a wrench, spins the wheel, then jogs alongside and lets go
        if s < 6.0:
            arms = (0.12, 0.25)
            if 1.6 <= s < 4.2:
                arms = (0.12, 0.25 + 0.04 * math.sin(f * 0.8))
            elif 4.2 <= s < 4.6:
                arms = (0.12, 0.4)
            hands = ffx.figure(img, BIKE_X0 - 4, GROUND, facing=1, kneel=True, arms=arms, **DAD)
            if 1.6 <= s < 4.2:  # the wrench, turning on the hub
                a = 2 * math.pi * (s - 1.6) * 0.8
                hx, hy = BIKE_X0 + 0.0, GROUND - 2.0
                ex, ey = hx - 1.6 * math.cos(a) - 1, hy - 1.6 * abs(math.sin(a)) - 0.5
                ffx.line(img, hx - 0.5, hy - 0.5, ex, ey, CHROME)
                for t0 in (2.4, 3.4):
                    if t0 <= s < t0 + 0.35:
                        k = 1 - (s - t0) / 0.35
                        for dx, dy in ((0, -2), (2, 0), (-2, 0), (1, -1), (-1, -1)):
                            add(img, hx + dx, hy - 2 + dy, ffx.GOLD_HI, 0.9 * k)
        else:
            jog = 6.8 <= s < 9.6
            if s < 6.8:
                dad_x = BIKE_X0 - 4
            elif jog:
                dad_x = bx - 3
            else:
                dad_x = BIKE_X0 + 16 - 3 + 2 * phase(f, sec(9.6), sec(10.2))
            if s < 9.6:
                arms = (0.06, 0.25 if jog else 0.06)  # one hand on the seat
            else:
                arms = (0.5, 0.5) if (f // 4) % 2 else (0.44, 0.44)
            hop = 1 if s >= 10.4 and (f // 4) % 2 else 0
            ffx.figure(img, ffx.rnd(dad_x), GROUND - hop, facing=1, legs=1 if jog and (f // 3) % 2 else 0, arms=arms,
                       **DAD)

        # the child: waits, hops at the spin, walks over and rides
        if s < 6.8:
            kx = 48 - (8 * phase(f, sec(5.8), sec(6.8)))
            hop = 1 if 4.6 <= s < 5.6 and (f // 3) % 2 else 0
            karms = (0.45, 0.45) if hop else (0.06, 0.06)
            ffx.figure(img, ffx.rnd(kx), GROUND - hop, facing=-1, arms=karms,
                       legs=1 if 5.8 <= s and (f // 3) % 2 else 0, **KID)
        else:
            sx, sy = pts["seat"]
            # seated on the saddle; arms forward to the handlebars
            ffx.figure(img, sx, sy + 1, facing=1, seated=True, arms=(0.3, 0.3), **KID)
        frames.append(img)
    return frames
