"""Scene: a field of poppies. A green field under a warm afternoon sky; red poppies open across it from left to
right, then sway as a slow breeze passes over, and a few petals drift. The red poppy is a symbol of remembrance
and of Veterans Day (docs/DECISIONS.md D3, D10)."""

import math
import random

from busybar.canvas import H, W, mix, phase, put, sec

from vfx import POPPY, STEM, bud, poppy, sky

NAME = "poppies"
TITLE = "A Field of Poppies"
SECONDS = 14
KEYFRAMES = [(0.5, "A green field of buds"), (3.0, "The poppies open"), (6.5, "A field of red"),
             (9.5, "A slow breeze"), (13.0, "Petals drift")]

SKY = [(0, (80, 130, 206)), (4, (160, 194, 232)), (6, (250, 222, 172))]
HILL = (98, 132, 120)
FIELD_TOP = (84, 140, 70)
FIELD_BOTTOM = (40, 92, 44)
HALO = (30, 64, 34)

# rows of flowers, back to front: (head row, size, spacing, stem length)
ROWS = [(8, 1, 3, 0), (9, 1, 3, 0), (10, 2, 4, 1), (12, 3, 6, 2), (14, 4, 9, 2)]


def layout():
    rng = random.Random(1111)
    flowers = []
    for r, (y, size, gap, stem) in enumerate(ROWS):
        slots = list(range(rng.randrange(gap), W, gap))
        for x in slots:
            x = x + rng.choice((-1, 0, 0, 1)) if size >= 3 else x
            flowers.append({"x": x, "y": y + (rng.choice((0, 1)) if size <= 2 else 0), "size": size, "stem": stem,
                            "open": sec(1.0) + int((x / W) * sec(5.0)) + rng.randrange(sec(0.8)) + r * 2})
    return flowers


def base():
    img = sky(SKY)
    for x in range(W):  # low hills along the horizon
        top = 6 + (1 if math.sin(x / 9.0) + 0.5 * math.sin(x / 4.0 + 1) > 0.3 else 0)
        for y in range(top, 8):
            put(img, x, y, HILL)
        for y in range(8, H):
            put(img, x, y, mix(FIELD_TOP, FIELD_BOTTOM, (y - 8) / (H - 9)))
    return img


CLOUDS = [(6, 1, ("..WWW....", ".WWWWWW..", "WWWWWWWWW")), (44, 2, ("...WW...", ".WWWWWW.", "WWWWWWWW"))]


def clouds(img, f: int) -> None:
    """Two soft clouds drifting right, one pixel every second (so most frames repeat the last)."""
    for x0, y0, rows in CLOUDS:
        x = x0 + f // 15
        for dy, row in enumerate(rows):
            for dx, ch in enumerate(row):
                if ch == "W":
                    put(img, (x + dx) % (W + 12) - 6, y0 + dy, (250, 248, 240), 0.55 + 0.15 * dy)


def render():
    n = sec(SECONDS)
    bg = base()
    flowers = layout()
    rng = random.Random(11)
    petals = [(rng.uniform(0, W), rng.uniform(0, 1), sec(rng.uniform(6.5, 10.0))) for _ in range(4)]
    frames = []
    for f in range(n):
        img = bg.copy()
        clouds(img, f)
        q = (f // 3) * 3  # the breeze moves in steps of 3 frames: calmer, and a smaller .anim
        for fl in flowers:
            x, y, size = fl["x"], fl["y"], fl["size"]
            breeze = math.sin(2 * math.pi * (x / 48.0 - q / sec(5.0)))
            sway = 1 if size >= 3 and f > sec(7.5) and breeze > 0.55 else 0
            for k in range(1, fl["stem"] + 2):
                put(img, x + (sway if k == 1 else 0), y + (1 if size >= 4 else 0) + k, STEM)
            p = phase(f, fl["open"], fl["open"] + sec(0.6))
            if p <= 0:
                if size >= 2:
                    bud(img, x, y + (1 if size >= 4 else 0))
                continue
            grow = max(1, min(size, int(1 + (size - 1) * p + 0.5)))
            poppy(img, x + sway, y, grow, halo=HALO if grow >= 3 else None)
        for px, ph, t0 in petals:  # a few petals lift off and drift on the breeze
            if f < t0:
                continue
            t = (f - t0) / sec(6.0)
            if t > 1:
                continue
            x = px + 30 * t
            y = 12 - 9 * math.sin(math.pi * t) + 2 * math.sin(2 * math.pi * (2 * t + ph))
            put(img, x % W, y, POPPY, 1 - t * 0.5)
        frames.append(img)
    return frames
