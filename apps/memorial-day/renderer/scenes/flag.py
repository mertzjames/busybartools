"""Scene: the flag, in two variants (docs/DECISIONS.md D5).

- flag_half, "The Flag at Half-Staff" (the morning of Memorial Day): following the custom, the flag is first at the
  peak, then lowered slowly to half-staff, where it flies against a calm morning sky.
- flag_full, "The Flag at Full Staff" (from noon on Memorial Day, and every other day): the flag flies at the peak
  against a clear afternoon sky.

The app's playlist picks the variant from the bar's clock (app/shared/memorial.ts, halfStaff()).
"""

import math
from types import SimpleNamespace

from busybar.canvas import FPS, W, ease_in_out, mix, phase, put, sec
from mdfx import draw_flag, pole, sky

SECONDS = 14
POLE_X = 26
POLE_TOP = 0
FULL_Y = 1  # flag top row at the peak
HALF_Y = 5  # flag top row at half-staff (its bottom stripe just above the grass)
FLAG_W = 17  # 17 x 9: about 1.9 : 1, a real flag's proportions (D11)
WAVE_PERIOD = 2.6  # seconds per wave cycle: a slow, steady breeze

MORNING = [(0, (40, 62, 128)), (7, (78, 104, 166)), (12, (168, 150, 160))]
AFTERNOON = [(0, (36, 74, 156)), (7, (70, 116, 192)), (12, (124, 160, 210))]

# slow clouds: (x at t=0, row, length, speed px/s)
CLOUDS = [(4, 3, 9, 0.55), (52, 1, 12, 0.45), (40, 5, 6, 0.6)]


def clouds(img, f: int, tint) -> None:
    for x0, y, n, v in CLOUDS:
        x = int((x0 + v * f / FPS) % (W + 20)) - 12
        for i in range(n):
            a = 0.35 * (1 - abs(i - n / 2) / (n / 2 + 1))
            put(img, x + i, y, tint, a)
            if 2 <= i <= n - 3:
                put(img, x + i, y - 1, tint, a * 0.6)


def ground(img, morning: bool) -> None:
    trees = (30, 58, 56) if morning else (34, 72, 54)
    for x in range(W):
        h = 1 + int(1.6 + 1.4 * math.sin(x * 0.37) + 0.8 * math.sin(x * 1.3))  # a low, uneven tree line
        h = max(1, min(3, h))
        for y in range(14 - h, 14):
            put(img, x, y, trees)
        put(img, x, 14, (58, 112, 58))
        put(img, x, 15, (42, 88, 46))


def make(half: bool):
    def render():
        frames = []
        stops = MORNING if half else AFTERNOON
        base = sky(stops)
        ground(base, half)
        if half:  # a soft, low morning light on the right
            for x in range(W):
                for y in range(9, 14):
                    c = base.getpixel((x, y))[:3]
                    k = max(0.0, 1 - abs(x - 62) / 20) * (y - 8) / 6 * 0.35
                    put(base, x, y, mix(c, (255, 206, 150), k))
        for f in range(sec(SECONDS)):
            img = base.copy()
            clouds(img, f, (240, 236, 236) if half else (246, 248, 255))
            if half:
                k = ease_in_out(phase(f, sec(1.5), sec(7.5)))
                y = int(FULL_Y + (HALF_Y - FULL_Y) * k + 0.5)
            else:
                y = FULL_Y
            pole(img, POLE_X, POLE_TOP, 15)
            draw_flag(img, POLE_X + 1, y, FLAG_W, f / (FPS * WAVE_PERIOD), amp=0.9, wavelength=18.0)
            frames.append(img)
        return frames

    if half:
        return SimpleNamespace(
            NAME="flag_half", TITLE="The Flag at Half-Staff", SECONDS=SECONDS, render=render,
            KEYFRAMES=[(0.5, "The flag at the peak"), (4.5, "Lowered slowly"),
                       (10.0, "At half-staff until noon")])
    return SimpleNamespace(
        NAME="flag_full", TITLE="The Flag at Full Staff", SECONDS=SECONDS, render=render,
        KEYFRAMES=[(1.0, "The flag at full staff"), (7.0, "A steady breeze"), (12.0, "A clear afternoon sky")])


HALF = make(True)
FULL = make(False)
