"""Scene: a hammock nap at sunset. A granddad naps in a striped hammock between two trees, a straw hat over his face
and a lemonade in the grass. The hammock sways, the Z's drift up, the sun sinks, and a leaf twirls down and lands on
his belly. It rides his breathing for a moment, the Z's pause, then carry on."""

import math

from busybar import font
from busybar.canvas import H, W, add, mix, phase, put, sec

import ffx

NAME = "hammock"
TITLE = "Hammock Nap"
SECONDS = 14
KEYFRAMES = [(1.0, "A hammock at sunset"), (3.2, "Z z z"), (6.4, "A leaf lets go"), (8.6, "...and lands on his belly"),
             (10.0, "A snort"), (12.6, "Z z z")]

GROUND = 12
LEFT, RIGHT = 16, 56  # where the ropes tie to the trunks (row ANCHOR_Y)
ANCHOR_Y = 6
MID = 36
SAG = 5.0

SKIN = ffx.SKIN_MEDIUM
SHIRT = (240, 96, 64)
SHIRT_DOT = (255, 150, 100)
PANTS = (196, 164, 112)
SHOES = (150, 76, 50)
HAT = (236, 204, 120)
HAT_BAND = (200, 60, 60)
FABRIC = ((70, 140, 214), (96, 170, 236))  # one calm blue: stripes made the napper unreadable
ROPE = (226, 210, 170)
LEAF = (190, 236, 70)
LEAF_DK = (120, 190, 50)


def curve(x: float, sway: float = 0.0) -> float:
    """Row of the hammock's bed at column x."""
    u = (x - MID - sway) / ((RIGHT - LEFT) / 2)
    return ANCHOR_Y + SAG * max(0.0, 1 - u * u) + (0 if abs(u) <= 1 else 0)


def base_frame(sun_y: int):
    img = ffx.sky([(0, (40, 36, 100)), (3, (130, 66, 112)), (6, (240, 130, 80)), (7, (255, 176, 90))])
    ffx.sun(img, MID + 6, sun_y, 3.0, core=(255, 226, 150), rim=(255, 170, 70), halo=0.35)
    # far hills in shadow: a dark band behind the hammock, so the napper reads (the bright sunset swallowed him)
    for x in range(W):
        top = 7 - (1 if math.sin(x * 0.2 + 1) > 0.4 else 0)
        for y in range(top, GROUND):
            put(img, x, y, mix((40, 56, 70), (26, 60, 44), (y - top) / 5))
        put(img, x, top, (200, 110, 70), 0.5)  # rim light along the ridge
    for y in range(GROUND, H):  # the lawn: a lit green, warmed by the sunset
        for x in range(W):
            put(img, x, y, (54, 116, 52) if (x * 3 + y) % 7 else (66, 132, 58))
    for cx, top, seed in ((10, 0, 3), (62, 0, 8)):
        ffx.tree(img, cx, top, r=6.0, base=GROUND, leaf=(36, 100, 50), leaf_hi=(70, 140, 60), trunk=(120, 76, 46),
                 seed=seed)
        for y in range(5, GROUND):  # a thicker trunk
            put(img, cx + 1, y, (96, 60, 38))
    # the lemonade in the grass by the left tree
    for y in (11, 12, 13):
        put(img, 21, y, (255, 230, 90) if y > 11 else (250, 250, 240))
        put(img, 22, y, (240, 210, 70) if y > 11 else (250, 250, 240))
    put(img, 22, 10, (120, 220, 90))  # a mint sprig
    return img


def lie(img, sway: float, breath: int) -> dict:
    """The hammock and the napper on it. Returns the belly-top point."""
    # ropes from the trunks to the hammock's ends
    ffx.line(img, LEFT + 0.0, ANCHOR_Y, LEFT + 4 + sway, curve(LEFT + 4, sway) - 0.4, ROPE)
    ffx.line(img, RIGHT + 0.0, ANCHOR_Y, RIGHT - 4 + sway, curve(RIGHT - 4, sway) - 0.4, ROPE)
    # the striped bed (two rows deep)
    for x in range(LEFT + 4, RIGHT - 3):
        y = ffx.rnd(curve(x, sway))
        put(img, x, y, FABRIC[1])
        put(img, x, y + 1, FABRIC[0])
    # the napper, head on the left: hat over the face, shirt, belly, legs, feet up
    hx = ffx.rnd(MID - 11 + sway)
    yb = lambda x: ffx.rnd(curve(x, sway))  # noqa: E731
    for x in range(hx - 1, hx + 4):  # head under a wide straw hat: the brim, a red band, the crown
        put(img, x, yb(x) - 1, HAT)
    for x in range(hx, hx + 3):
        put(img, x, yb(x) - 2, HAT_BAND)
        put(img, x, yb(x) - 3, HAT)
    put(img, hx - 2, yb(hx - 2) - 1, ffx.HAIR_GREY)  # grey hair peeking out
    put(img, hx + 4, yb(hx + 4) - 1, ffx.HAIR_GREY)  # and a grey beard
    for x in range(hx + 4, hx + 13):  # the shirt, two rows, with a pattern
        for r in (1, 2):
            put(img, x, yb(x) - r, SHIRT_DOT if r == 2 and x % 3 == 0 else SHIRT)
    belly = (hx + 9, yb(hx + 9) - 3)
    for x in range(hx + 7, hx + 12):  # the belly, rising with each breath
        if breath or x in (hx + 8, hx + 9, hx + 10):
            put(img, x, yb(x) - 3, SHIRT)
    if breath:
        belly = (belly[0], belly[1] - 1)
        for x in (hx + 8, hx + 9, hx + 10):
            put(img, x, yb(x) - 4, SHIRT)
    for x in range(hx + 13, hx + 22):  # legs
        put(img, x, yb(x) - 1, PANTS)
    put(img, hx + 22, yb(hx + 22) - 1, SHOES)  # feet up
    put(img, hx + 22, yb(hx + 22) - 2, SHOES)
    ax = hx + 6  # one arm hanging over the edge
    put(img, ax, yb(ax) + 2, SKIN)
    put(img, ax, yb(ax) + 3, SKIN)
    return {"belly": belly}


def zee(img, x: float, y: float, big: bool, a: float) -> None:
    if big:
        font.draw_text(img, "Z", ffx.rnd(x), ffx.rnd(y), (236, 230, 255), font="tiny", alpha=a)
    else:
        for dx, dy in ((0, 0), (1, 0), (1, 1), (0, 2), (1, 2)):
            put(img, ffx.rnd(x) + dx, ffx.rnd(y) + dy, (226, 220, 250), a)


def render():
    frames = []
    bases = {}
    snort = (9.6, 10.4)
    for f in range(sec(SECONDS)):
        s = f / 15
        sun_y = 4 + int(3 * phase(f, 0, sec(SECONDS)) + 0.5)
        if sun_y not in bases:
            bases[sun_y] = base_frame(sun_y)
        img = bases[sun_y].copy()
        sway = round(math.sin(2 * math.pi * s / 4.6) * 1.0)
        breath = 1 if (s % 3.0) < 1.4 else 0
        if snort[0] <= s < snort[1]:
            breath = 1
        pts = lie(img, sway, breath)

        # the Z's: a slow chain drifting up and to the right from the hat; they pause after the leaf lands
        hx = MID - 11 + sway
        for i in range(4):
            age = (s - i * 0.9) % 3.6
            if 8.6 <= s < 11.2:
                continue
            if s < 1.0 or (11.2 <= s < 12.0):
                continue
            t = age / 3.6
            zee(img, hx + 1 + 7 * t + math.sin(age * 2) * 0.8, ANCHOR_Y + 2 - 8 * t, i % 2 == 0,
                min(1.0, 3 * t) * (1 - t))

        # the leaf: lets go of the right tree, twirls down and lands on the belly; the snort bounces it
        leaf = phase(f, sec(6.2), sec(8.6))
        if leaf > 0:
            bx, by = pts["belly"]
            if leaf < 1:
                lx = 58 + (bx - 58) * leaf + 3.0 * math.sin(leaf * math.pi * 3)
                ly = 3 + (by - 1 - 3) * leaf
                flip = (f // 3) % 2
            else:
                lx, ly = bx, by - 1
                flip = 0
                if snort[0] <= s < snort[1]:
                    ly -= 2 * math.sin(math.pi * (s - snort[0]) / (snort[1] - snort[0]))
            put(img, lx, ly, LEAF)  # lime: an orange leaf vanished on the orange shirt
            put(img, lx + (1 if flip else -1), ly, LEAF_DK)
        if snort[0] <= s < snort[0] + 0.5:  # a big Z for the snort
            zee(img, hx + 2, ANCHOR_Y - 3, True, 1.0)
        frames.append(img)
    return frames
