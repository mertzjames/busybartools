"""Scene: a bald eagle soars past a waving flag (docs/DECISIONS.md D3, D5). The flag flies from a brass pole on the
left of a bright summer sky: thirteen one-row stripes, red at the top and bottom, and a blue canton over the top
seven with the stars as a dense checker of dots. An eagle glides in from the right, circles on the breeze banking
into its turns, then beats its wings and climbs away as a gust snaps the flag out."""

import math

from PIL import Image

from busybar.canvas import H, W, blit, ease_in, ease_out, phase, put, sec
from busybar.sprite import Sprite

import jfx

NAME = "eagle_flag"
TITLE = "Eagle and Flag"
SECONDS = 14
KEYFRAMES = [(0.6, "The flag in a summer breeze"), (2.4, "An eagle glides in"), (5.4, "Circling on the wind"),
             (8.0, "Banking into a turn"), (11.0, "A few strong wingbeats"), (13.2, "Climbing away")]

POLE_X = 3
FLAG_W = 30
CANTON_W = 12
TOP = 1

# The eagle seen from below, wings spread (the same design as Presidents' Day's). Wings are a lit brown (black is an
# unlit LED); the white head and tail and the gold beak read against the blue.
EAGLE_PAL = {"B": "#94603A", "b": "#74482C", "W": "#F6F6F6", "T": "#E6E6EA", "Y": "#FFC830"}
EAGLE = Sprite("eagle", EAGLE_PAL, """
b...............b
bb.............bb
.bB....WWW....Bb.
..bBB..WYW..BBb..
....bBBBBBBBb....
.......BBB.......
.......TTT.......
......TTTTT......
""", """
.................
.................
.......WWW.......
bb.....WYW.....bb
.bBBBBBBBBBBBBBb.
...bbBBBBBBBbb...
.......TTT.......
......TTTTT......
""", """
.................
.................
.......WWW.......
.......WYW.......
...bBBBBBBBBBb...
.bbBB..BBB..BBbb.
bb.....TTT.....bb
b.....TTTTT.....b
""")
FLAP = (0, 1, 2, 1)


def banked(sprite: Image.Image, bank: float) -> Image.Image:
    """Tilt the wings by shifting columns up on one side and down on the other (rotating pixel art mangles it)."""
    if abs(bank) < 0.5:
        return sprite
    w, h = sprite.size
    out = Image.new("RGBA", (w, h + 4), (0, 0, 0, 0))
    for x in range(w):
        dy = math.floor(bank * (x - (w - 1) / 2) / ((w - 1) / 2) + 0.5)
        out.alpha_composite(sprite.crop((x, 0, x + 1, h)), (x, 2 + dy))
    return out


def clouds(img, f):
    """Soft summer clouds drifting left, behind everything."""
    for x0, y, w, speed in ((20, 3, 10, 0.06), (58, 1, 12, 0.045), (96, 5, 9, 0.07)):
        x = (x0 - f * speed) % 110 - 20
        for dx in range(w):
            k = math.sin(math.pi * (dx + 0.5) / w)
            put(img, x + dx, y, (226, 236, 252), 0.45 * k)
            put(img, x + dx, y + 1, (206, 220, 246), 0.6 * k)
            if 1 < dx < w - 2:
                put(img, x + dx, y - 1, (236, 242, 255), 0.35 * k)


def render():
    base = jfx.sky([(0, (40, 96, 206)), (9, (80, 140, 226)), (13, (150, 190, 240))])
    for x in range(W):  # distant green treetops along the bottom
        top = 14 - (1 if math.sin(x * 0.45) + 0.6 * math.sin(x * 1.3) > 0.5 else 0)
        for y in range(top, H):
            put(base, x, y, (40, 116, 64) if y > top else (64, 146, 80))
    frames = []
    t = 0.0
    for f in range(sec(SECONDS)):
        img = base.copy()
        clouds(img, f)
        jfx.pole(img, POLE_X, 0, 15)
        gust = math.sin(math.pi * phase(f, sec(10.0), sec(13.0)))
        t += 1 / (32 - 10 * gust)
        jfx.draw_flag(img, POLE_X + 1, TOP, FLAG_W, t, cw=CANTON_W, amp=1.1 + 0.4 * gust, wavelength=16)
        # the eagle: in from the right, a loop over the right half of the sky, then wingbeats and away
        tt = f / 15
        bank = 0.0
        if f < sec(3.5):
            p = ease_out(phase(f, sec(0.8), sec(3.5)))
            x, y = 76 - (76 - 48) * p, 2 + 1 * p
        elif f < sec(10.5):
            a = 2 * math.pi * (tt - 3.5) / 7.0
            x, y = 48 - 10 * math.sin(a), 3 - 1.5 * (1 - math.cos(a))
            bank = -2.2 * math.sin(a)
        else:
            p = ease_in(phase(f, sec(10.5), sec(SECONDS)))
            x, y = 48 + 30 * p, 3 - 12 * p
        flapping = f < sec(1.8) or f >= sec(10.0)
        frame = FLAP[(f // 3) % 4] if flapping else 1
        spr = banked(EAGLE.img(frame), bank)
        blit(img, spr, math.floor(x - 8 + 0.5), math.floor(y + 0.5) - (spr.height - 8) // 2)
        frames.append(img)
    return frames
