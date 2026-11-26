"""Scene: a cherry tree in blossom with a hatchet leaning on its trunk, a folklore nod kept light: the tree is
fine, the hatchet is resting, and a cherry pie cools on a stump (docs/DECISIONS.md D3). Petals drift on the
breeze, a robin drops in, and a gust at 9 s sends up a flurry of petals."""

import math
import random

from busybar.canvas import H, W, add, blit, ease_out, phase, put, sec
from busybar.sprite import Sprite

import pfx

NAME = "cherry_tree"
TITLE = "The Cherry Tree"
SECONDS = 14
KEYFRAMES = [(1.0, "A cherry tree in blossom"), (4.0, "The hatchet rests against it"),
             (7.5, "A robin drops in beside the pie"), (10.0, "A gust of petals"), (13.0, "A cherry pie cools on the stump")]

TRUNK_X = 30
CANOPY = (30, 3.6, 13.0, 4.4)  # center x, center y, radius x, radius y

HATCHET = Sprite("hatchet", {"S": "#D2D8EA", "s": "#FFFFFF", "W": "#E0A460", "w": "#B07840"}, """
sSSW.
sSSW.
..SW.
...W.
....W
....W
""")

ROBIN = Sprite("robin", {"B": "#8C7A6E", "b": "#6C5E58", "O": "#F07038", "Y": "#FFC040", "W": "#E8E0D8"}, """
..BB.
bBBBY
.OOB.
..Y..
""", """
.bb..
bBBBY
.OO..
.....
""", """
.....
bBBBY
.OOBb
...b.
""")

PIE = Sprite("pie", {"C": "#E8B464", "c": "#C88C40", "R": "#D82838", "r": "#A01828", "T": "#C8CCD8"}, """
.CRCRC.
CcRcRcC
TTTTTTT
""")


def blossoms():
    """Fixed blossom pixels of the canopy: (dx, dy, color), relative to the canopy center."""
    rng = random.Random(7)
    cx, cy, rx, ry = CANOPY
    out = []
    for y in range(0, 9):
        for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            edge = 1 + 0.25 * math.sin(x * 1.3 + y * 0.7)
            if d > edge:
                continue
            r = rng.random()
            if d > 0.75 * edge and r < 0.35:
                continue  # a ragged edge
            c = (255, 214, 228) if r < 0.3 else (250, 160, 196) if r < 0.75 else (226, 104, 150)
            if rng.random() < 0.08 and d < 0.7:
                c = (120, 74, 54)  # a branch peeking through
            out.append((x - cx, y - cy, c))
    return out


class Petal:
    def __init__(self, rng, t0, x, y, speed):
        self.t0, self.x, self.y, self.speed = t0, x, y, speed
        self.ph = rng.uniform(0, 6.28)
        self.fall = rng.uniform(0.03, 0.07)
        self.c = rng.choice(((255, 214, 228), (250, 160, 196), (255, 236, 242)))

    def draw(self, img, f, wind):
        age = f - self.t0
        if age < 0:
            return
        x = self.x + age * self.speed * wind + 1.2 * math.sin(age * 0.18 + self.ph)
        y = self.y + age * self.fall + 0.8 * math.sin(age * 0.11 + self.ph)
        if 0 <= x < W and y < 13:
            put(img, x, y, self.c, 0.9)


def render():
    base = pfx.sky([(0, (84, 136, 218)), (12, (160, 196, 238))])
    # rolling grass
    for x in range(W):
        top = 13 - (1 if 44 < x < 66 else 0)
        for y in range(top, H):
            put(base, x, y, (86, 156, 70) if y == top else (60, 124, 56))
    # a white picket fence on the left
    for x in range(0, 17):
        put(base, x, 10, (220, 222, 230))
        if x % 3 == 1:
            for y in range(8, 13):
                put(base, x, y, (238, 240, 246))
            put(base, x, 7, (238, 240, 246), 0.6)
    # the trunk and the lower branches
    for y in range(7, 13):
        for dx in (0, 1):
            put(base, TRUNK_X + dx, y, (128, 82, 50) if dx == 0 else (100, 64, 42))
    put(base, TRUNK_X - 1, 12, (100, 64, 42))
    put(base, TRUNK_X + 2, 12, (100, 64, 42))
    pfx.line(base, TRUNK_X, 8, TRUNK_X - 6, 5, (110, 72, 48))
    pfx.line(base, TRUNK_X + 1, 8, TRUNK_X + 7, 4, (110, 72, 48))
    # the stump and the pie
    for x in range(53, 60):
        put(base, x, 11, (176, 132, 84))
        put(base, x, 12, (126, 84, 52))
    put(base, 56, 11, (204, 160, 104))
    blooms = blossoms()

    rng = random.Random(11)
    petals = [Petal(rng, rng.randint(-60, sec(SECONDS)), rng.uniform(16, 40), rng.uniform(1, 9), rng.uniform(0.12, 0.25))
              for _ in range(26)]
    gust0 = sec(9)
    petals += [Petal(rng, gust0 + rng.randint(0, 20), rng.uniform(18, 42), rng.uniform(0, 9), rng.uniform(0.4, 0.7))
               for _ in range(30)]

    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        gust = math.sin(math.pi * phase(f, gust0, sec(12)))
        sway = 0.5 * math.sin(2 * math.pi * f / 45) + 1.4 * gust
        cx, cy, _, _ = CANOPY
        for dx, dy, c in blooms:
            lean = sway * (1 - (dy + 6) / 12)  # the top of the canopy moves most
            put(img, cx + dx + math.floor(lean + 0.5), cy + dy, c)
        # the hatchet leans on the trunk, its blade catching the light now and then
        blit(img, HATCHET.img(0), TRUNK_X - 1, 8)
        g = max(0.0, math.sin(2 * math.pi * (f - sec(3)) / sec(5)))
        if g > 0.9:
            add(img, TRUNK_X, 8, (255, 255, 255), (g - 0.9) * 8)
        # the pie and its steam
        blit(img, PIE.img(0), 53, 8)
        for i in range(3):
            age = (f + i * 13) % 40
            x = 55 + i * 1.5 + 0.7 * math.sin((f + i * 9) * 0.2)
            put(img, x, 7 - age / 8, (240, 240, 250), 0.5 * (1 - age / 40))
        # the robin flies in from the right and lands on a branch
        land = sec(7)
        if f >= sec(5):
            p = ease_out(phase(f, sec(5), land))
            rx = 74 + (46 - 74) * p
            ry = -3 + (9 - -3) * p - 2.5 * math.sin(math.pi * p)
            hop = f >= land and (f // 20) % 4 == 3  # a peck at the grass now and then
            fr = (f // 2) % 2 + 1 if f < land else 0
            blit(img, ROBIN.img(fr, flip=True), round(rx), round(ry) + (1 if hop else 0))
        for pt in petals:
            pt.draw(img, f, 1.0 + 1.5 * gust)
        frames.append(img)
    return frames
