"""Scene: sparklers at dusk (docs/DECISIONS.md D3). Three kids, seen from behind on a lawn under a fading summer sky,
light sparklers and swing them in loops and figure eights that leave glowing trails. Then the middle one writes USA
in the air, letter by letter, and the letters hang there and fade as fireflies blink in the grass."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.party import hash01

import jfx

NAME = "sparklers"
TITLE = "Sparklers at Dusk"
SECONDS = 14
KEYFRAMES = [(0.6, "Dusk on the lawn"), (2.2, "Sparklers lit"), (4.6, "Loops and figure eights"),
             (8.4, "Writing in the air: U"), (10.6, "U S A"), (12.6, "The letters fade")]

LAND = 12
SPARK = (255, 236, 170)
TRAIL = (255, 190, 80)

# kids seen from behind: (center x, hair, shirt), lit mid-tone shirts so they read against the dusk (no dark clothes)
KIDS = [(12, (150, 96, 50), (220, 70, 80)), (35, (210, 160, 80), (90, 130, 230)), (59, (110, 70, 44), (236, 236, 236))]

# the letters USA as pen strokes on a 5x7 grid ((col, row) points, None lifts the pen), drawn at LETTER_X
STROKES = {
    "U": [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (1, 6), (2, 6), (3, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1),
          (4, 0)],
    "S": [(4, 1), (3, 0), (2, 0), (1, 0), (0, 1), (0, 2), (1, 3), (2, 3), (3, 3), (4, 4), (4, 5), (3, 6), (2, 6), (1, 6),
          (0, 5)],
    "A": [(0, 6), (0, 5), (0, 4), (0, 3), (0, 2), (1, 1), (2, 0), (3, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), None,
          (1, 4), (2, 4), (3, 4)],
}
WORD = "USA"
LETTER_X = 35 - 9  # 3 letters of 5 px with 2 px gaps = 19 px, centered over the middle kid
LETTER_Y = 1
WRITE0 = sec(7.6)
PTS_PER_FRAME = 0.8  # pen speed
LIT = sec(1.6)  # when the sparklers catch


def letter_path():
    """[(x, y, pen_down)] for the whole word, in writing order."""
    out = []
    for i, ch in enumerate(WORD):
        down = True
        for p in STROKES[ch]:
            if p is None:
                down = False
                continue
            out.append((LETTER_X + i * 7 + p[0], LETTER_Y + p[1], down))
            down = True
    return out


PATH = letter_path()


def tip(k: int, f: int):
    """Sparkler tip of kid k at frame f (float x, y)."""
    cx = KIDS[k][0]
    if k == 1 and f >= WRITE0:
        i = (f - WRITE0) * PTS_PER_FRAME
        if i < len(PATH) - 1:
            a, b = PATH[int(i)], PATH[int(i) + 1]
            u = i - int(i)
            return a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u
        return cx + 3, 6.0  # done: rests by the kid's shoulder
    t = max(0, f - LIT) / 15
    if k == 0:  # circles
        return cx + 4 + 3.0 * math.cos(5.0 * t), 4.5 + 2.6 * math.sin(5.0 * t)
    if k == 2:  # figure eights
        return cx - 4 + 4.0 * math.sin(3.2 * t), 4.5 + 2.4 * math.sin(6.4 * t)
    return cx + 3 + 3.5 * math.sin(3.6 * t), 4.0 + 1.5 * math.cos(5.8 * t)  # swoops, before writing


def kid(img, cx, hair, shirt, hand, glow):
    """A kid from behind: hair (no face), shoulders and back, one arm up to the sparkler's handle."""
    top = 8
    for dx in (-1, 0, 1):
        put(img, cx + dx, top, hair)
        put(img, cx + dx, top + 1, hair)
    put(img, cx, top - 1, hair)
    for y in range(top + 2, H):
        for dx in range(-2, 3):
            if y == top + 2 and abs(dx) == 2:
                continue
            put(img, cx + dx, y, mix(shirt, (40, 30, 60), 0.15 * (y - top - 2) / 6))
    if glow > 0:  # the sparkler's warm light on the hair and shoulders
        for dx in (-1, 0, 1):
            add(img, cx + dx, top - (1 if dx == 0 else 0), (255, 200, 120), 0.35 * glow)
    # the arm: from the shoulder to the hand
    sx, sy = cx + (2 if hand[0] >= cx else -2), top + 3
    n = 4
    for i in range(1, n + 1):
        u = i / n
        put(img, sx + (hand[0] - sx) * u, sy + (hand[1] - sy) * u, shirt if i == 1 else (220, 170, 130))


def sparks(img, x, y, f, seed):
    """The burning tip: a white-gold core and a few sparks flying out a pixel or two (only a handful of pixels per
    frame, so the file stays small)."""
    add(img, x, y, (255, 255, 230), 1.0)
    for j in range(5):
        if hash01(seed, f, j) < 0.55:
            a = 2 * math.pi * hash01(seed, f, j, 7)
            r = 1 + 1.6 * hash01(seed, f, j, 9)
            add(img, x + math.cos(a) * r, y + math.sin(a) * r, SPARK, 0.8)


def render():
    sky = jfx.sky([(0, (14, 18, 62)), (5, (50, 36, 104)), (9, (140, 66, 96)), (11, (236, 134, 70))])
    for x in range(W):  # the lawn and a soft line of far bushes, a lit deep green
        top = LAND - (1 if 0.5 + 0.5 * math.sin(x * 0.35) + 0.4 * math.sin(x * 0.9) > 0.9 else 0)
        for y in range(top, H):
            put(sky, x, y, (24, 54, 44) if y < LAND + 1 else (30, 70, 50))
    base = sky
    flies = [(5 + (i * 13) % 62, LAND + 1 + (i * 5) % 3, i) for i in range(7)]
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        for x, y, i in flies:  # fireflies blink on and off
            k = math.sin(2 * math.pi * (f / 45 + i * 0.37))
            if k > 0.6:
                put(img, x, y, (200, 255, 110), (k - 0.6) / 0.4)
        # the letters: every point written so far glows, then the word fades after it is done
        if f >= WRITE0:
            done = (f - WRITE0) * PTS_PER_FRAME
            fade = 1 - phase(f, sec(11.6), sec(13.6))
            for j, (x, y, down) in enumerate(PATH[:int(done) + 1]):
                age = (done - j) / PTS_PER_FRAME
                k = max(0.8, 1 - age / 30) * fade
                c = mix(TRAIL, (255, 250, 220), max(0.0, 1 - age / 6))
                if j > 0 and down:  # fill between points, so diagonal strokes join
                    px_, py_ = PATH[j - 1][0], PATH[j - 1][1]
                    if abs(px_ - x) + abs(py_ - y) > 1:
                        put(img, (px_ + x) / 2, (py_ + y) / 2, c, k)
                put(img, x, y, c, k)
        for k, (cx, hair, shirt) in enumerate(KIDS):
            lit = f >= LIT + k * 3
            tx, ty = tip(k, f)
            hand = (cx + max(-3, min(3, round((tx - cx) * 0.5))), 7 + max(-2, min(1, round((ty - 5) * 0.4))))
            if lit and not (k == 1 and f >= WRITE0):  # trails behind the swinging tips
                for j in range(1, 13):
                    px_, py_ = tip(k, f - j)
                    add(img, px_, py_, TRAIL, 0.95 * (1 - j / 13))
            kid(img, cx, hair, shirt, hand, 1.0 if lit else 0.0)
            # the stick, from the hand to the tip
            for i in range(1, 4):
                u = i / 4
                put(img, hand[0] + (tx - hand[0]) * u, hand[1] + (ty - hand[1]) * u, (150, 150, 160), 0.8)
            if lit:
                sparks(img, tx, ty, f, k)
            else:
                put(img, tx, ty, (120, 120, 130))
        frames.append(img)
    return frames
