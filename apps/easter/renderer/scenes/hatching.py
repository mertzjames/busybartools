"""Chicks Hatching: three pastel eggs sit in a straw nest in the warm light of a spring evening. One by one they
wobble, crack along a zigzag, pop their tops and a fluffy chick pokes out, blinking and cheeping. At the end all
three cheep together."""

import math

from busybar.canvas import blit, mix, new, put, sec, vgradient
from busybar.fx import sparkle

import efx
from sprites import CHICK

NAME = "hatching"
TITLE = "Chicks Hatching"
SECONDS = 15
KEYFRAMES = [(0.5, "Three eggs in a nest"), (1.6, "The first one wobbles"), (2.4, "Crack!"),
             (3.2, "Hello, chick"), (6.6, "The second hatches"), (10.3, "And the third"),
             (13.6, "Three chicks cheeping")]

EW, EH = 7, 9  # egg size
EY = 5  # egg top row (bottoms on row 13, behind the nest's rim)
EGGS = [(22, efx.BLUE, 15), (32, (255, 236, 200), 70), (42, efx.PINK, 125)]  # (x, color, hatch start frame)
CUT = 4  # the crack runs across egg row 4; the top 4 rows pop off


def background():
    img = vgradient((34, 20, 58), (74, 40, 70))
    # a soft warm sunbeam from the upper left
    for y in range(16):
        for x in range(72):
            u = x - 10 - y * 1.4
            if 0 <= u < 14:
                put(img, x, y, (255, 200, 120), 0.10 * math.sin(math.pi * u / 14))
    # straw on the floor
    for x in range(72):
        put(img, x, 15, efx.STRAW_DK if x % 3 else efx.STRAW, 0.8)
    return img


def shell_top(img, x, y, color):
    """The popped-off cap: the top rows of the egg with a jagged lower edge."""
    for dx, dy in efx.egg_mask(EW, EH):
        if dy < CUT - (1 if dx % 4 in (1, 2) else 0):
            put(img, x + dx, y + dy, color)


def render():
    bg = background()
    efx.nest(bg, 36, 15, 34, 3)
    nest_front = bg.crop((0, 13, 72, 16))  # redrawn over the eggs so they sit inside
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        for i, (x, c, t0) in enumerate(EGGS):
            age = f - t0
            accent = efx.ACCENT.get(c, (200, 150, 110))
            if age < 24:  # waiting, then wobbling and cracking
                wob = 0
                if 0 <= age < 24 and (age // 3) % 2 == 0 and age % 12 < 6:
                    wob = 1 if (age // 6) % 2 else -1
                if f > EGGS[-1][2] + 60:
                    wob = 0
                efx.egg(img, x + wob, EY, EW, EH, c)
                if age >= 8:
                    efx.crack(img, x + wob, EY, EW, CUT, color=mix(accent, (90, 20, 60), 0.6),
                              progress=min(1.0, (age - 8) / 8))
                continue
            # hatched: the chick rises out of the lower shell
            rise = min(1.0, (age - 24) / 6)
            cy = round(EY + 5 - 6 * rise)
            fr = 0
            if age > 34:
                beat = (f + i * 7) % 30
                fr = 1 if beat < 5 else (2 if 15 <= beat < 19 else 0)
            if f > EGGS[-1][2] + 60:  # the finale: all three cheep in turn
                beat = (f - i * 6) % 18
                fr = 1 if beat < 6 else 0
            blit(img, CHICK.img(fr), x - 1 + (1 if i == 2 else 0), cy)
            efx.egg(img, x, EY, EW, EH, c, top_cut=CUT, shine=False)
            efx.crack(img, x, EY, EW, CUT, color=mix(c, (255, 255, 255), 0.4))  # the broken rim, lit
            # the cap flies up and off to the side, then is gone
            if age < 40:
                u = (age - 24) / 16
                side = -1 if i == 0 else 1
                shell_top(img, round(x + side * 10 * u), round(EY - 7 * math.sin(math.pi * min(1, u * 1.2)) + 12 * u * u),
                          c)
            if 24 <= age < 32:
                sparkle(img, x + 3, EY - 1, age, 1 - (age - 24) / 8, color=(255, 246, 180))
        img.paste(nest_front, (0, 13), None)
        # the nest front covers egg bottoms; the straw itself is opaque in that band
        frames.append(img)
    return frames
