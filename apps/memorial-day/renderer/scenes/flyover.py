"""Scene: The Missing Man. Four aircraft fly across a calm evening sky in formation. Over the middle of the field the
third pulls up and climbs away alone, leaving a gap in the formation, while the others fly on. The planes are plain
grey with no markings, insignia or national emblems."""

import math

from busybar.canvas import FPS, H, W, phase, put, sec
from busybar.sprite import Sprite
from mdfx import sky

NAME = "flyover"
TITLE = "The Missing Man"
SECONDS = 14
KEYFRAMES = [(2.5, "Four aircraft in formation"), (5.6, "The third pulls up"),
             (7.4, "And climbs away alone"), (11.0, "The others fly on, leaving a gap")]

PAL = {"L": "#A8B0C0", "H": "#D4DAE6", "W": "#7C8698", "C": "#9CC4E8"}
LEVEL = Sprite("level", PAL, """
H.......
HLLLLC..
LLLLLLLH
..WWW...
""").img()
PITCH = Sprite("pitch", PAL, """
.......H
.....LH.
..HLLC..
HLLLL...
LWW.....
""").img()
CLIMB = Sprite("climb", PAL, """
...H
..LH
..LC
.LL.
HLL.
LW..
L...
""").img()

SPEED = 9.0  # px per second across the field
# formation slots behind the lead: (columns behind, top row)
SLOTS = [(0, 3), (10, 6), (20, 3), (30, 6)]
MISSING = 2
PULL_T = 5.4  # seconds: the missing man starts to pull up

SKY = [(0, (20, 34, 88)), (8, (44, 64, 124)), (13, (92, 92, 136))]
CLOUDS = [(10, 2, 14), (44, 9, 10), (60, 3, 8)]


def backdrop():
    img = sky(SKY)
    for cx, cy, n in CLOUDS:  # still, soft clouds: the planes are the only motion
        for i in range(n):
            a = 0.3 * (1 - abs(i - n / 2) / (n / 2 + 1))
            put(img, cx + i, cy, (150, 150, 180), a)
            if 2 <= i <= n - 3:
                put(img, cx + i, cy - 1, (150, 150, 180), a * 0.5)
    for x in range(W):
        h = max(1, min(3, 1 + int(1.4 + 1.2 * math.sin(x * 0.31 + 2) + 0.7 * math.sin(x * 1.1))))
        for y in range(14 - h, 14):
            put(img, x, y, (30, 54, 54))
        put(img, x, 14, (44, 84, 50))
        put(img, x, 15, (32, 66, 40))
    return img


def missing_path(t: float):
    """Position and sprite of the missing man after it pulls up at PULL_T (None while still in formation)."""
    dt = t - PULL_T
    if dt < 0:
        return None
    x0 = lead_x(PULL_T) - SLOTS[MISSING][0]
    y0 = SLOTS[MISSING][1]
    if dt < 0.5:
        return x0 + SPEED * dt, y0 - 1.5 * dt, LEVEL
    if dt < 1.1:
        return x0 + SPEED * dt, y0 - 0.75 - 4 * (dt - 0.5), PITCH
    vy = 4 + 7 * (dt - 1.1)  # climbing faster and faster
    return x0 + SPEED * 1.1 + 2.5 * (dt - 1.1), y0 - 3.2 - vy * (dt - 1.1), CLIMB


def lead_x(t: float) -> float:
    return -9 + SPEED * (t - 0.4)


def render():
    base = backdrop()
    frames = []
    trail: list[tuple[int, int, float]] = []  # contrail points: (x, y, time laid)
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = base.copy()
        mp = missing_path(t)
        if mp and mp[2] is CLIMB:
            trail.append((int(mp[0] + 0.5), int(mp[1] + 0.5) + CLIMB.height, t))
        for x, y, t0 in trail:  # a faint trail that thins out over two seconds
            a = 0.45 * (1 - phase(int(t * 100), int(t0 * 100), int((t0 + 2.0) * 100)))
            if a > 0 and 0 <= y < H:
                put(img, x, y, (230, 234, 242), a)
                put(img, x + 1, y, (230, 234, 242), a * 0.4)
        for k, (back, top) in enumerate(SLOTS):
            if k == MISSING and mp:
                continue
            x = int(math.floor(lead_x(t) - back + 0.5))
            paste(img, LEVEL, x, top)
        if mp:
            spr = mp[2]
            paste(img, spr, int(math.floor(mp[0] + 0.5)), int(math.floor(mp[1] + 0.5)))
        frames.append(img)
    return frames


def paste(img, spr, x: int, y: int) -> None:
    """Draw a sprite clipped to the frame."""
    px = spr.load()
    for yy in range(spr.height):
        for xx in range(spr.width):
            if px[xx, yy][3]:
                put(img, x + xx, y + yy, px[xx, yy][:3])

