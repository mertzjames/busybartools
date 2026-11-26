"""Scene: a bald eagle soars over snowy mountains (docs/DECISIONS.md D3). It flies in from the left flapping, then
circles on the wind, banking into its turns, flaps again and climbs away toward the sun. Seen from below with its
wings spread: the white head and tail and the gold beak read against the blue."""

import math

from busybar.canvas import H, W, blit, ease_in, ease_out, phase, put, sec
from busybar.sprite import Sprite
from PIL import Image

import pfx

NAME = "eagle"
TITLE = "Eagle over the Mountains"
SECONDS = 14
KEYFRAMES = [(1.2, "A bald eagle flies in"), (4.5, "Circling on the wind"), (7.0, "Banking into a turn"),
             (10.0, "A few strong wingbeats"), (13.0, "Climbing toward the sun")]

# Wings are a lit brown (black is an unlit LED).
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

FAR = [(4, 7, 8), (18, 10, 10), (31, 7, 7), (45, 10, 10), (59, 8, 8), (72, 9, 9)]
MID = [(0, 4, 6), (11, 5, 6), (25, 4, 5), (37, 5, 6), (52, 5, 6), (66, 4, 5)]


def banked(sprite: Image.Image, bank: float) -> Image.Image:
    """Tilt the wings by shearing columns up on one side and down on the other (rotating pixel art mangles it)."""
    if abs(bank) < 0.5:
        return sprite
    w, h = sprite.size
    out = Image.new("RGBA", (w, h + 4), (0, 0, 0, 0))
    for x in range(w):
        dy = math.floor(bank * (x - (w - 1) / 2) / ((w - 1) / 2) + 0.5)
        col = sprite.crop((x, 0, x + 1, h))
        out.alpha_composite(col, (x, 2 + dy))
    return out


def render():
    base = pfx.sky([(0, (26, 56, 150)), (7, (56, 100, 192)), (12, (140, 174, 228))])
    pfx.glow(base, 63, 2, 9, (255, 240, 200), 0.55)
    for dx in (0, 1):
        for dy in (0, 1):
            put(base, 62 + dx, 1 + dy, (255, 250, 230))
    pfx.mountains(base, FAR, 15, (74, 82, 132), snow=(236, 240, 252), snowline=9, shade=(58, 64, 110))
    pfx.mountains(base, MID, 15, (44, 56, 92), snow=(170, 182, 214), snowline=12, shade=(34, 44, 76))
    for x in range(W):  # a near ridge of pines
        top = 14 - (1 if x % 5 in (1, 2) else 0) - (1 if x % 5 == 1 else 0)
        for y in range(top, H):
            put(base, x, y, (36, 92, 66) if y > top else (56, 120, 82))
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        # wisps of cloud drifting across the peaks
        for i, (x0, y, w) in enumerate(((10, 9, 10), (50, 7, 8), (90, 10, 12))):
            x = (x0 - f * 0.15) % 110 - 20
            for dx in range(w):
                put(img, x + dx, y, (220, 228, 246), 0.35 * math.sin(math.pi * (dx + 0.5) / w))
        t = f / 15
        bank = 0.0
        if f < sec(3):  # in from the left, flapping
            p = ease_out(phase(f, 0, sec(3)))
            x, y = -18 + (24 + 18) * p, 3 - 2 * p
        elif f < sec(10.5):  # a lazy loop, banking into the turns
            a = 2 * math.pi * (t - 3) / 7.5
            x, y = 24 + 14 * math.sin(a), 1 + 1.0 * (1 - math.cos(a))
            bank = 2.2 * math.sin(a)  # level at the start and end of the loop, steepest in the turns
        else:  # climb away toward the sun
            p = ease_in(phase(f, sec(10.5), sec(SECONDS)))
            x, y = 24 + 44 * p, 1 - 10 * p
        flapping = f < sec(2.4) or f >= sec(9.5)
        frame = FLAP[(f // 3) % 4] if flapping else 1
        spr = banked(EAGLE.img(frame), bank)
        blit(img, spr, x, y - (spr.height - 8) // 2)
        frames.append(img)
    return frames
