"""Scene: fishing at dawn. A parent and child sit on the end of a dock as the sun comes up over a still lake. The
child holds the rod; the bobber twitches, then dips, the rod bends, and a small sunfish comes up on the line. The
parent cheers, the fish gets a moment in the sunrise, and then it is let go with a splash and spreading ripples."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.party import hash01

import ffx

NAME = "fishing"
TITLE = "Fishing at Dawn"
SECONDS = 14
KEYFRAMES = [(1.0, "Sunrise on the lake"), (4.0, "The bobber twitches"), (5.6, "A bite! The rod bends"),
             (7.6, "A little sunfish"), (9.2, "A cheer"), (10.9, "Let go with a splash"), (13.0, "Ripples")]

HORIZON = 8  # the far shore; water from row 9
SUN_X = 57
DOCK_END = 16
KID_X, DAD_X = 15, 8
TIP = (31.0, 1.0)  # the rod tip at rest
BOB_X = 44  # where the bobber floats

FISH = ["GG.", "GGO", "GGO", ".G.", "T.T"]  # hanging head-up from the line (row 0 = the mouth)
FISH_PAL = {"G": (120, 206, 150), "O": (255, 170, 70), "T": (90, 170, 130)}

WATER_TOP = (150, 112, 146)
WATER_BOTTOM = (24, 46, 98)


def fish(img, x: int, y: int, f: int, flip: bool = False) -> None:
    """The sunfish, 3x5, hanging from (x+0, y); its tail flicks."""
    rows = FISH[::-1] if flip else FISH
    wiggle = (f // 2) % 2
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch == ".":
                continue
            xx = x + dx + (wiggle if ch == "T" else 0) - 1
            put(img, xx, y + dy, FISH_PAL[ch])


def ripple(img, cx: float, y: int, age: int, life: int = 30, strength: float = 0.8) -> None:
    """An expanding ring on the water, seen edge-on: two bright points moving apart, fading."""
    if not (0 <= age < life):
        return
    r = 0.8 + age * 0.22
    k = strength * (1 - age / life)
    for s in (-1, 1):
        add(img, cx + s * r, y, (200, 210, 240), k)
        add(img, cx + s * (r - 1), y, (200, 210, 240), k * 0.4)
    if age > 6:
        rr = r * 0.5
        for s in (-1, 1):
            add(img, cx + s * rr, y + 1, (170, 190, 230), k * 0.4)


def splash(img, cx: float, y0: float, age: int, life: int = 12, seed: int = 0) -> None:
    """Droplets thrown up and falling back."""
    if not (0 <= age < life):
        return
    for i in range(6):
        vx = (hash01(seed, i) - 0.5) * 0.7
        vy = -0.55 - 0.4 * hash01(seed, i, 7)
        x = cx + vx * age
        y = y0 + vy * age + 0.06 * age * age
        if y < y0 + 0.5:
            put(img, x, y, (226, 236, 255), 1 - age / life)


def base_frame(sun_y: int):
    img = ffx.sky([(0, (16, 26, 80)), (4, (52, 50, 120)), (6, (170, 100, 130)), (7, (246, 150, 110)),
                   (HORIZON, (255, 196, 120))])
    ffx.sun(img, SUN_X, sun_y, 3.0, halo=0.4)
    # far shore: a low treeline, a lit blue-green
    for x in range(W):
        h = 1 + (1 if math.sin(x * 0.7) + math.sin(x * 0.23 + 1) > 0.9 else 0)
        for y in range(HORIZON - h + 1, HORIZON + 1):
            put(img, x, y, (44, 70, 84) if (x + y) % 4 else (52, 82, 92))
    # water, and the sun's reflection as a steady warm column
    for y in range(HORIZON + 1, H):
        c = mix(WATER_TOP, WATER_BOTTOM, (y - HORIZON - 1) / (H - HORIZON - 2))
        for x in range(W):
            put(img, x, y, c)
        half = 1 + (y - HORIZON) // 2
        for x in range(SUN_X - half, SUN_X + half + 1):
            if (y - HORIZON) % 2 == 1:  # broken horizontal dashes, wider further down
                add(img, x + (y % 3) - 1, y, (230, 140, 50), 0.75 * (1 - abs(x - SUN_X) / (half + 2)))
    # reeds on the right
    for x, top in ((66, 9), (68, 7), (69, 10), (71, 8)):
        for y in range(top, H):
            put(img, x, y, (60, 130, 70) if y > top else (130, 90, 50))
    # the dock: planks on rows 11-12, posts into the water
    for x in range(0, DOCK_END + 1):
        put(img, x, 11, ffx.WOOD_HI if x % 4 else ffx.WOOD)
        put(img, x, 12, ffx.WOOD_DK)
    for x in (2, 9, DOCK_END - 1):
        for y in range(13, H):
            put(img, x, y, (92, 60, 38))
    return img


def rod(img, hand, tip, bend: float) -> None:
    """The rod from the hand to the tip, bowed down by `bend` rows at the tip end."""
    hx, hy = hand
    tx, ty = tip
    n = 24
    for i in range(n + 1):
        t = i / n
        x = hx + (tx - hx) * t
        y = hy + (ty - hy) * t + bend * t * t
        put(img, x, y, (150, 96, 60) if t < 0.2 else (236, 210, 150))


def fishing_line(img, a, b, sag: float = 0.0) -> None:
    ax, ay = a
    bx, by = b
    n = int(max(abs(bx - ax), abs(by - ay))) + 2
    for i in range(n + 1):
        t = i / n
        put(img, ax + (bx - ax) * t, ay + (by - ay) * t + sag * 4 * t * (1 - t), (226, 214, 222), 0.55)


def render():
    frames = []
    bases = {}
    for f in range(sec(SECONDS)):
        sun_y = 9 - int(5 * phase(f, 0, sec(SECONDS)) + 0.5)
        if sun_y not in bases:
            bases[sun_y] = base_frame(sun_y)
        img = bases[sun_y].copy()
        s = f / 15

        # the story beats
        bite = phase(f, sec(5.0), sec(5.4))
        reel = phase(f, sec(5.8), sec(7.2))
        drop = phase(f, sec(10.2), sec(10.8))
        bend = 0.0
        if 5.0 <= s < 10.2:
            bend = 3.0 * (1 - 0.6 * reel) + (0.6 * math.sin(f * 0.9) if s < 7.2 else 0.0)
        tip = (TIP[0] - (1.5 if 5.0 <= s < 10.2 else 0), TIP[1] + bend * 0.6)

        # the people (the child on the dock end, the parent beside), seated facing the lake
        cheer = 8.4 <= s < 9.8
        dad_arms = (0.45, 0.45) if cheer else (0.05, 0.22)
        if cheer and (f // 4) % 2:
            dad_arms = (0.5, 0.5)
        ffx.figure(img, DAD_X, 14, ffx.SKIN_DEEP, (206, 74, 60), (196, 164, 110), cap=(40, 150, 150), facing=1,
                   beard=ffx.HAIR_DARK, arms=dad_arms, seated=True)
        kid_r = 0.32 if s < 10.2 else (0.32 if s < 11.6 else (0.4 if (f // 5) % 2 else 0.28))
        hands = ffx.figure(img, KID_X, 13, ffx.SKIN_DEEP, (246, 204, 64), (70, 120, 200), hair=ffx.HAIR_DARK,
                           style="curly", kid=True, arms=(0.25, kid_r), facing=1, seated=True)
        hand = (hands["r"][0] + 0.5, hands["r"][1])
        rod(img, hand, tip, bend * 0.4)

        # the bobber, the line and the fish
        if s < 5.0:
            bob_y = 9 + (1 if 3.4 <= s < 3.6 or 4.2 <= s < 4.4 else 0)
            fishing_line(img, tip, (BOB_X, bob_y - 0.5), sag=1.0)
            put(img, BOB_X, bob_y, (236, 50, 50))
            if bob_y == 9:
                put(img, BOB_X, 10, (236, 236, 236), 0.8)
            for t0 in (3.4, 4.2):
                ripple(img, BOB_X, 10, f - sec(t0), 16, 0.6)
        elif s < 5.8:
            fishing_line(img, tip, (BOB_X, 11), sag=0.0)  # the bobber is pulled under
            ripple(img, BOB_X, 10, f - sec(5.0), 24)
            splash(img, BOB_X, 9, f - sec(5.0), 10, seed=3)
        elif s < 10.2:
            # the fish comes up out of the water and swings in under the rod tip
            e = 1 - (1 - reel) ** 2
            fx_ = BOB_X + (tip[0] + 1 - BOB_X) * e
            fy = 10 + (tip[1] + 4 - 10) * e - 3 * math.sin(math.pi * e)
            if s >= 7.2:
                fx_ += math.sin((f - sec(7.2)) * 0.25) * 0.8  # a little swing
            fishing_line(img, tip, (fx_, fy - 1))
            put(img, BOB_X + (fx_ - BOB_X), fy - 2, (236, 50, 50))  # the bobber rides up the line
            fish(img, ffx.rnd(fx_), ffx.rnd(fy), f)
            splash(img, BOB_X, 9, f - sec(5.8), 12, seed=5)
            ripple(img, BOB_X, 10, f - sec(5.8), 26)
            if 8.0 <= s < 9.8:  # a glint of sunrise on its side
                k = 0.5 + 0.5 * math.sin((f - sec(8.0)) * 0.5)
                add(img, ffx.rnd(fx_), ffx.rnd(fy) + 1, (255, 240, 200), 0.7 * k)
        else:
            # let go: the fish falls head-first back into the water
            land_x = tip[0] + 2
            e = drop * drop
            fy = (tip[1] + 4) + (10 - (tip[1] + 4)) * e
            fishing_line(img, tip, (tip[0] + 1, tip[1] + 3))
            put(img, tip[0] + 1, tip[1] + 2, (236, 50, 50))
            if drop < 1:
                fish(img, ffx.rnd(land_x), ffx.rnd(fy), f, flip=True)
            splash(img, land_x, 9, f - sec(10.8), 14, seed=9)
            for k, t0 in enumerate((10.8, 11.4, 12.1)):
                ripple(img, land_x, 10 + (k == 2), f - sec(t0), 40, 0.8 - 0.2 * k)

        # a few slow glints on the water
        for i in range(5):
            gx = int(hash01(11, i) * 60) + 20
            gy = 11 + int(hash01(12, i) * 4)
            k = max(0.0, math.sin(2 * math.pi * (f / 45 + hash01(13, i))))
            if k > 0.7:
                add(img, gx, gy, (200, 170, 140), 0.5 * (k - 0.7) / 0.3)
        frames.append(img)
    return frames
