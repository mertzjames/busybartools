"""The Bunny's Garden: on a sunny spring morning the bunny hops in from the left. Three times it stops, sniffs the
grass and leaves a decorated egg hidden behind it (by a bush, among the tulips, by a bush), then hops away to the
right, and the hidden eggs twinkle."""

from busybar.canvas import W, blit, new, sec
from busybar.fx import sparkle

import efx
from sprites import BUNNY

NAME = "bunny_garden"
TITLE = "The Bunny's Garden"
SECONDS = 16
KEYFRAMES = [(0.5, "A sunny garden"), (2.6, "The bunny hops in"), (4.4, "It stops to hide an egg"),
             (6.4, "Off to the tulips"), (9.4, "A second egg"), (12.6, "And a third by the bush"),
             (15.4, "Three eggs hidden")]

GROUND = 14  # the bunny's feet and the eggs' bottoms sit on this row
SIT = 26  # frames per hiding stop
STOP = [("sit", 4, [0]), ("sit", 12, [3]), ("sit", 10, [0, 0, 3, 0])]
PLAN = [("start", -16), ("hop", 4), *STOP, ("hop", 3), *STOP, ("hop", 3), *STOP, ("hop", 5)]

# egg drops: (frame, x, color, pattern), at the bunny's tail when it lifts its head
DROPS = []


def _plan_drops():
    t, x = 0, PLAN[0][1]
    stops = 0
    for step in PLAN[1:]:
        if step[0] == "hop":
            t += step[1] * efx.HOP
            x += step[1] * efx.HOP_DX
        else:
            if step[2] == [3]:  # the sniff: the egg appears at its end
                color, pat = ((efx.PINK, "stripes"), (efx.LEMON, "zigzag"), (efx.LILAC, "dots"))[stops]
                DROPS.append((t + step[1] - 2, x - 3, color, pat))
                stops += 1
            t += step[1]


_plan_drops()

BUSHES = [(2, 7, 8), (44, 9, 6)]  # (x, w, h), drawn in front of the eggs
TULIPS = [(24, efx.PINK), (27, (255, 90, 90)), (30, efx.LILAC), (60, efx.PEACH), (64, efx.PINK), (68, (255, 90, 90))]


def background():
    img = new()
    efx.sky(img)
    efx.sun(img, 66, 2.5, r=2.6, rays=False)
    return img


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        efx.cloud(img, 8 + f / 30, 2)
        efx.cloud(img, 36 + f / 24, 4, w=7, alpha=0.85)
        efx.grass(img, GROUND - 1, seed=3)
        for x, c in TULIPS:
            efx.tulip(img, x, GROUND - 1, 5, c)
        # eggs that have been hidden so far
        for t0, x, c, pat in DROPS:
            if f >= t0:
                efx.egg(img, x, GROUND - 6, 5, 7, c, pat)
        for x, w, h in BUSHES:
            efx.bush(img, x, GROUND, w, h, seed=x)
        # the bunny
        bx, lift, fr = efx.bunny_path(f, PLAN)
        blit(img, BUNNY.img(fr), round(bx), GROUND - 12 + round(lift))
        # a pop of sparkle as each egg appears, then a slow twinkle at the end
        for k, (t0, x, c, pat) in enumerate(DROPS):
            age = f - t0
            if 0 <= age < 8:
                sparkle(img, x + 2, GROUND - 7, age, 1 - age / 8)
            if f > sec(13.6) and (f // 6 + k * 3) % 9 == 0:
                sparkle(img, x + 1, GROUND - 6, f, 0.8)
        frames.append(img)
    return frames
