"""Scene: The Parade. Bunting in green, white and orange hangs over a town street at dusk. The parade marches past: a flag bearer with the Irish tricolor, a piper in a saffron kilt (music notes rising
from the pipes), a drummer with a shamrock on the bass drum, and two children skipping along. Confetti rains down
at the end."""

import math
import random

from busybar.canvas import W, add, mix, put, sec, vgradient
from busybar.party import Confetti, line
from pfx import GOLD, GOLD_HI, ORANGE, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, WHITE, note, shamrock

NAME = "parade"
TITLE = "The Parade"
SECONDS = 16
KEYFRAMES = [(1.0, "Bunting over the street at dusk"), (3.4, "The flag bearer leads the way"),
             (6.4, "The piper plays"), (9.4, "The drummer keeps the beat"), (12.0, "Children skip along"),
             (14.6, "Confetti!")]

FEET = 14
SPEED = 0.45  # px per frame
STEP = 8  # frames per stride
# marchers: (kind, offset behind the leader in px)
MARCHERS = [("flag", 0), ("piper", -16), ("drummer", -31), ("kid", -44), ("kid2", -52)]
LEAD_START = -6
CONFETTI_T = sec(12.4)

SKIN = ((250, 200, 160), (214, 156, 112), (176, 116, 78), (236, 184, 140))
KILT = (232, 168, 52)  # saffron, the Irish pipers' kilt
KILT_DK = (190, 126, 34)
JACKET = (30, 120, 56)
JACKET_HI = (70, 170, 80)
CAP = (24, 100, 44)
STOCK = (232, 228, 214)
SHOE = (130, 76, 40)
TRICOLOR = (SHAMROCK, WHITE, ORANGE)


def background():
    """A town street at dusk: a deep-blue sky, dim slate rooftops with a few warm windows, a pavement, and bunting
    overhead. Kept dark and plain so the marchers' colors stand out."""
    img = vgradient((30, 52, 124), (104, 96, 150))
    rng = random.Random(12)
    x = 0
    while x < W:
        w = rng.randint(9, 14)
        top = rng.randint(5, 8)
        c = (24, 26, 46) if (x // 3) % 2 else (30, 30, 52)
        gable = rng.random() < 0.5
        for xx in range(x, min(W, x + w)):
            t = top
            if gable:
                t = top - min(xx - x, x + w - 1 - xx) // 2 + 1
            for yy in range(t, FEET + 1):
                put(img, xx, yy, c)
        for _ in range(2):
            wx, wy = x + rng.randint(1, max(1, w - 3)), rng.randint(top + 2, FEET - 4)
            put(img, wx, wy, (255, 200, 110), 0.55)
        x += w
    for xx in range(W):  # the road
        put(img, xx, FEET + 1, (80, 80, 94))
    # bunting: a sagging cord with pennants
    for xx in range(W):
        y = 0.5 + 1.5 * math.sin(math.pi * ((xx % 24) / 24))
        put(img, xx, y, (200, 200, 190), 0.5)
        if xx % 4 == 1:
            c = TRICOLOR[(xx // 4) % 3]
            put(img, xx, y + 1, c, 0.6)
            put(img, xx + 1, y + 1, c, 0.6)
            put(img, xx, y + 2, c, 0.6)
    return img


def legs(img, x: int, feet: int, f: int, phase_off: int = 0, short: bool = False) -> None:
    """Two legs in a marching stride (side view, facing right): stockings and shoes."""
    s = ((f + phase_off) // (STEP // 2)) % 4  # 0 apart, 1 together, 2 apart (other leg ahead), 3 together
    rows = 1 if short else 2
    for r in range(rows):
        y = feet - rows + r
        if s in (0, 2):
            put(img, x + (0 if r == 0 else -1), y, STOCK)
            put(img, x + (2 if r == 0 else 3), y, STOCK)
        else:
            put(img, x + 1, y, STOCK)
            put(img, x + 2 if r else x + 1, y, STOCK)
    if s in (0, 2):
        put(img, x - 1, feet, SHOE)
        put(img, x + 3, feet, SHOE)
        put(img, x + 4, feet, SHOE)
    else:
        put(img, x + 1, feet, SHOE)
        put(img, x + 2, feet, SHOE)


def body(img, x: int, top: int, skin, cap=CAP, jacket=JACKET, kilt=True, hair=None) -> None:
    """Head (3x3, hair or a tilted caubeen cap), a jacket and a kilt. (x, top) is the head's top-left."""
    for dy in range(3):
        for dx in range(3):
            put(img, x + dx, top + dy, skin)
    if hair:
        for dx in range(3):
            put(img, x + dx, top, hair)
        put(img, x, top + 1, hair)
    else:  # the caubeen, worn tilted, with a gold badge
        for dx in range(-1, 3):
            put(img, x + dx, top - 1, cap)
        put(img, x - 1, top, cap)
        put(img, x + 2, top - 1, GOLD)
    for dy in range(4):
        for dx in range(3):
            put(img, x + dx, top + 3 + dy, JACKET_HI if dx == 2 and dy < 3 else jacket)
    if kilt:
        for dx in range(-1, 4):
            put(img, x + dx, top + 7, KILT if dx < 3 else KILT_DK)
        for dx in range(-1, 4):
            put(img, x + dx, top + 8, KILT_DK if (dx % 2) else KILT)


def flag_bearer(img, x: int, f: int) -> None:
    top = FEET - 11
    legs(img, x, FEET, f)
    body(img, x, top + 1, SKIN[1], cap=(26, 26, 30), jacket=(40, 90, 150), kilt=False)
    # trousers instead of a kilt
    for dx in range(3):
        put(img, x + dx, top + 8, (40, 54, 90))
        put(img, x + dx, top + 9, (40, 54, 90))
    # a green hat instead of a cap: a low top hat
    for dx in range(-1, 4):
        put(img, x + dx, top, (34, 150, 60))
    for dx in range(0, 3):
        put(img, x + dx, top - 1, (34, 150, 60))
    put(img, x + 1, top - 1, GOLD)
    # the pole, held out in front, and the tricolor trailing behind it (green at the hoist), waving
    px = x + 4
    for y in range(-1, top + 7):
        put(img, px, y, (170, 130, 80))
    put(img, px - 1, top + 5, SKIN[1])
    put(img, px, -1, GOLD)
    for c in range(9):
        wave = round(0.8 * math.sin(c * 0.8 - f * 0.45))
        col = TRICOLOR[c // 3]
        for r in range(4):
            put(img, px - 1 - c, 0 + r + wave, col if r else mix(col, (255, 255, 255), 0.3))


def piper(img, x: int, f: int) -> None:
    top = FEET - 11
    legs(img, x, FEET, f, 3)
    # drones: three pipes rising back over the shoulder (ivory tips)
    for k, (dx, dy) in enumerate(((-3, -2), (-4, 0), (-2, -3))):
        line(img, x + 1, top + 4, x + dx, top + dy, (170, 120, 70))
        put(img, x + dx, top + dy, (240, 230, 200))
    body(img, x, top + 1, SKIN[0])
    # the bag under the arm (green tartan) and the chanter down in front
    for dx in range(3):
        for dy in range(2):
            put(img, x + dx, top + 5 + dy, (40, 140, 70) if (dx + dy) % 2 else (200, 60, 60))
    line(img, x + 3, top + 3, x + 5, top + 7, (190, 150, 100))
    put(img, x + 4, top + 5, SKIN[0])
    put(img, x + 5, top + 6, SKIN[0])


def drummer(img, x: int, f: int) -> None:
    top = FEET - 11
    legs(img, x, FEET, f, 5)
    body(img, x, top + 1, SKIN[2])
    # the bass drum, face toward us: white head, green rim, a gold shamrock in the middle
    cx, cy = x + 4, top + 6
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            d = dx * dx + dy * dy
            if d <= 11:
                put(img, cx + dx, cy + dy, (236, 236, 226) if d <= 5 else (40, 150, 70))
    shamrock(img, cx, cy, 0, (60, 190, 80), (150, 240, 130), (40, 140, 60))
    put(img, cx, cy - 1, GOLD)
    # beaters: one hits on every step
    beat = (f // STEP) % 2
    hit = f % STEP < 2
    for side in (0, 1):
        up = side != beat or not hit
        hx = cx - 4 if side == 0 else cx + 4
        hy = cy - (4 if up else 0)
        put(img, hx, hy, SKIN[2])
        put(img, hx + (1 if side == 0 else -1), hy + (1 if up else 0), (210, 180, 130))
    if hit:
        add(img, cx + (-2 if beat else 2), cy, (255, 255, 220), 0.6)


def kid(img, x: int, f: int, shirt, hair, skin, hop_off: int) -> None:
    hop = 1 if ((f + hop_off) // 5) % 2 else 0
    top = FEET - 8 - hop
    legs(img, x, FEET - hop, f, hop_off, short=True)
    for dy in range(3):
        for dx in range(3):
            put(img, x + dx, top + dy, skin)
    for dx in range(3):
        put(img, x + dx, top, hair)
    put(img, x, top + 1, hair)
    for dy in range(3):
        for dx in range(3):
            put(img, x + dx, top + 3 + dy, shirt)
    for dx in range(3):
        put(img, x + dx, top + 6, (60, 70, 120))
    # an arm up, waving a little shamrock
    put(img, x + 3, top + 3, skin)
    put(img, x + 4, top + 2, skin)
    shamrock(img, x + 4, top, 0, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK)


def render():
    bg = background()
    confetti = [Confetti(60 + i, CONFETTI_T + i * 6, x, -1, n=26, vx=(-0.6, 0.6), vy=(-0.3, 0.4),
                         fall=(0.08, 0.16), colors=(SHAMROCK_HI, WHITE, ORANGE, GOLD, GOLD_HI), spread=6)
                for i, x in enumerate((10, 34, 58, 22, 46))]
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        lead = LEAD_START + f * SPEED
        for kind, off in MARCHERS:
            x = int(round(lead + off))
            if not -14 <= x < W + 10:
                continue
            if kind == "flag":
                flag_bearer(img, x, f)
            elif kind == "piper":
                piper(img, x, f)
                for i in range(4):  # notes rise from the pipes
                    age = (f + i * 9) % 36
                    a = math.sin(math.pi * age / 36)
                    note(img, x - 2 - age * 0.2, 4 - age * 0.12 + i % 2, GOLD_HI, 0.85 * a, kind=i % 2)
            elif kind == "drummer":
                drummer(img, x, f)
            elif kind == "kid":
                kid(img, x, f, (50, 170, 70), (200, 100, 40), SKIN[3], 0)
            else:
                kid(img, x, f, (236, 236, 226), (96, 70, 60), SKIN[2], 3)
        if f >= CONFETTI_T:
            for c in confetti:
                c.draw(img, f, floor=FEET + 1)
        frames.append(img)
    return frames
