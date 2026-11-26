"""Scene: Many Hands. A row of people of every skin tone stands facing the dawn, seen from behind. One after another
they raise their arms and join hands with their neighbors, until one chain crosses the whole display. A warm light
passes along the joined hands; then the chain lowers its hands, still joined, and the word UNITY appears."""

import math

from busybar.canvas import FPS, H, add, ease_in_out, lerp, phase, put, sec, vgradient
from mfx import HAIR, SKIN, TOPS, caption, glow

NAME = "hands"
TITLE = "Many Hands"
SECONDS = 15
KEYFRAMES = [(1.0, "People stand together, facing the dawn"), (3.6, "One by one, they raise their hands"),
             (7.6, "Joined hands; light runs along the chain"), (13.0, "UNITY")]

N = 6
SPACING = 12
SHOULDER_Y = 12
PEAK_Y = 4
LOW_Y = 13
# (skin, hair, shirt): seen from behind, so a head is just hair (no faces)
PEOPLE = [(SKIN[2], HAIR[0], TOPS[0]), (SKIN[5], HAIR[5], TOPS[3]), (SKIN[0], HAIR[4], TOPS[2]),
          (SKIN[3], HAIR[2], TOPS[1]), (SKIN[1], HAIR[3], TOPS[6]), (SKIN[4], HAIR[1], TOPS[5])]
RISE_START, RISE_STEP, RISE_LEN = 1.2, 0.8, 1.8
WAVE_START, WAVE_STEP = 7.0, 0.35
LOWER = (9.8, 11.4)


def shoulder_x(i: int) -> float:
    return 6 + SPACING * i


def person(img, sx: float, hair, shirt) -> None:
    """Head (hair only, from behind) and shoulders along the bottom edge."""
    x = round(sx)
    for y in range(SHOULDER_Y - 3, SHOULDER_Y):
        for dx in (-1, 0, 1):
            if not (y == SHOULDER_Y - 3 and dx != 0) or True:
                put(img, x + dx, y, hair)
    for y in range(SHOULDER_Y, H):
        for dx in range(-3, 4):
            if y == SHOULDER_Y and abs(dx) == 3:
                continue
            put(img, x + dx, y, shirt)


def arm(img, ax: float, ay: float, hx: float, hy: float, skin, sleeve) -> None:
    """A 1 px arm from the shoulder (ax, ay) to the hand (hx, hy), a sleeve near the shoulder."""
    n = int(max(abs(hx - ax), abs(hy - ay)) * 2) + 1
    for i in range(n + 1):
        u = i / n
        put(img, round(ax + (hx - ax) * u), round(ay + (hy - ay) * u), sleeve if u < 0.25 else skin)


def hand(img, hx: float, hy: float, skin) -> None:
    put(img, round(hx), round(hy), skin)
    put(img, round(hx), round(hy) - 1, skin)


def render():
    bg = vgradient((10, 12, 44), (14, 14, 38))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        dawn = ease_in_out(phase(f, sec(6), sec(12)))
        glow(img, 36, -4, 30, (255, 150, 80), 0.18 + 0.22 * dawn)
        low = ease_in_out(phase(f, sec(LOWER[0]), sec(LOWER[1])))
        rise = [phase(f, sec(RISE_START + i * RISE_STEP), sec(RISE_START + i * RISE_STEP + RISE_LEN)) for i in range(N)]
        joins = []
        for i, (skin, hair, shirt) in enumerate(PEOPLE):
            sx = shoulder_x(i)
            person(img, sx, hair, shirt)
            for side in (-1, 1):
                ax = round(sx) + 3 * side
                px = sx + side * SPACING / 2  # the meeting point with the neighbor
                neighbor = i + side
                both = rise[i] >= 1 and (neighbor < 0 or neighbor >= N or rise[neighbor] >= 1)
                e = ease_in_out(rise[i])
                top = lerp(PEAK_Y, LOW_Y, low)
                hy = lerp(H + 1, top, e)
                hx = lerp(ax + side, px - side * (0 if both else 1), e)
                arm(img, ax, SHOULDER_Y, hx, hy, skin, shirt)
                hand(img, hx, hy, skin)
        for k in range(N + 1):
            joins.append(shoulder_x(k) - SPACING / 2)
        # light runs along the joined hands, then they keep a soft glow
        y = lerp(PEAK_Y, LOW_Y, low) - 0.5
        for k, x in enumerate(joins):
            w = math.exp(-((t - WAVE_START - k * WAVE_STEP) / 0.4) ** 2)
            steady = 0.4 * phase(f, sec(WAVE_START + k * WAVE_STEP), sec(WAVE_START + k * WAVE_STEP + 0.8))
            a = max(w, steady)
            if a > 0.01:
                glow(img, x, y, 6, (255, 190, 100), 0.9 * a)
                add(img, x, y, (255, 240, 200), 0.8 * w)
                add(img, x, y - 1, (255, 240, 200), 0.8 * w)
        a = ease_in_out(phase(f, sec(11.4), sec(13.2))) * (1 - phase(f, sec(14.4), sec(15)))
        caption(img, "UNITY", 1, a, font="big", back=False)
        frames.append(img)
    return frames
