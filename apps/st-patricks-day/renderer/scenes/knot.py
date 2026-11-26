"""Scene: The Celtic Knot. Two cords, one gold and one green, weave themselves around the edge of the display, over
and under each other in turn, until they close into an unbroken knotwork border. ERIN GO BRAGH ("Ireland forever")
appears inside it between two shamrocks, and a gleam of light runs around the knot.

The knot is an original two-cord plait on a rounded-rectangle path: the cords cross every half period, and at each
crossing the one underneath breaks for a pixel on either side, alternating gold-over-green and green-over-gold
(docs/DECISIONS.md D6)."""

import math

from busybar.canvas import W, add, ease_in_out, ease_out, mix, phase, put, sec, vgradient
from busybar.font import draw_text, text_width
from pfx import GOLD, GOLD_DK, GOLD_HI, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, glow, shamrock, sparkle4

NAME = "knot"
TITLE = "The Celtic Knot"
SECONDS = 14
KEYFRAMES = [(1.4, "Two cords begin to weave"), (4.0, "Over and under, around the edge"),
             (6.8, "The knot closes"), (8.8, "ERIN GO BRAGH"), (11.6, "A gleam runs around the knot")]

X0, Y0, X1, Y1 = 1.5, 1.5, 70.5, 14.5  # the centerline of the border
R = 2.5  # corner radius
AMP = 1.25  # how far each cord swings from the centerline
WEAVE = (sec(0.6), sec(7.0))
WORDS = sec(7.6)
GLEAM = (sec(9.4), sec(13.6))
TEXT = "ERIN GO BRAGH"

STRAIGHT = (X1 - X0 - 2 * R, Y1 - Y0 - 2 * R)
LENGTH = 2 * (STRAIGHT[0] + STRAIGHT[1]) + 2 * math.pi * R
PERIODS = 16
P = LENGTH / PERIODS
CORD = {0: (GOLD, GOLD_HI, GOLD_DK), 1: ((60, 200, 90), (150, 250, 150), (30, 130, 60))}
BG_TOP, BG_BOTTOM = (6, 30, 16), (10, 44, 22)


def path(s: float):
    """Point and outward normal on the rounded-rectangle centerline, s from the top-left, clockwise."""
    s %= LENGTH
    a, b = STRAIGHT
    q = math.pi * R / 2
    segs = [  # (length, kind, data)
        (a, "line", ((X0 + R, Y0), (1, 0), (0, -1))),
        (q, "arc", ((X1 - R, Y0 + R), -math.pi / 2)),
        (b, "line", ((X1, Y0 + R), (0, 1), (1, 0))),
        (q, "arc", ((X1 - R, Y1 - R), 0.0)),
        (a, "line", ((X1 - R, Y1), (-1, 0), (0, 1))),
        (q, "arc", ((X0 + R, Y1 - R), math.pi / 2)),
        (b, "line", ((X0, Y1 - R), (0, -1), (-1, 0))),
        (q, "arc", ((X0 + R, Y0 + R), math.pi)),
    ]
    for ln, kind, data in segs:
        if s <= ln:
            if kind == "line":
                (px, py), (dx, dy), n = data
                return px + dx * s, py + dy * s, n
            (cx, cy), a0 = data
            ang = a0 + s / R
            return cx + R * math.cos(ang), cy + R * math.sin(ang), (math.cos(ang), math.sin(ang))
        s -= ln
    return X0 + R, Y0, (0, -1)


def cord_pixels():
    """For each cord, the pixels it covers in drawing order: [(s, x, y, under, over)]. Near a crossing, `under`
    pixels are left out (the other cord passes over there) and `over` pixels are drawn on top."""
    out = {0: [], 1: []}
    seen = {0: set(), 1: set()}
    n = int(LENGTH * 10)
    for i in range(n):
        s = i / 10
        x, y, (nx, ny) = path(s)
        w = math.sin(2 * math.pi * s / P)
        k = round(2 * s / P)  # nearest crossing
        near = abs(s - k * P / 2) < 0.95
        for c, sign in ((0, 1), (1, -1)):
            px, py = int(math.floor(x + nx * sign * AMP * w + 0.5)), int(math.floor(y + ny * sign * AMP * w + 0.5))
            if (px, py) in seen[c]:
                continue
            seen[c].add((px, py))
            over = (k % 2 == 0) == (c == 0)  # gold over at even crossings, green over at odd
            out[c].append((s, px, py, near and not over, near and over))
    return out


def render():
    pix = cord_pixels()
    frames = []
    tw = text_width(TEXT, "tiny")
    for f in range(sec(SECONDS)):
        img = vgradient(BG_TOP, BG_BOTTOM)
        head = LENGTH * ease_in_out(phase(f, *WEAVE))
        gleam = phase(f, *GLEAM)
        layer = {}
        for c in (1, 0):
            base, hi, dk = CORD[c]
            for s, x, y, under, over in pix[c]:
                if s > head or under or ((x, y) in layer and layer[(x, y)][1] and not over):
                    continue
                col = mix(base, hi, 0.5) if (int(s * 2) % 3 == 0) else base
                if 0 < gleam < 1:  # the gleam: two bright spots chasing around
                    for g in (gleam, gleam + 0.5):
                        d = abs(((s / LENGTH - g * 2) % 1.0) - 0.5)
                        if d > 0.47:
                            col = mix(col, (255, 255, 230), (d - 0.47) / 0.03)
                layer[(x, y)] = (col, over)
        for (x, y), (col, _) in layer.items():
            put(img, x, y, col)
        # the weaving heads: a sparkle where each cord is being laid
        if 0 < head < LENGTH:
            for c, sign in ((0, 1), (1, -1)):
                x, y, (nx, ny) = path(head)
                w = math.sin(2 * math.pi * head / P)
                sparkle4(img, x + nx * sign * AMP * w, y + ny * sign * AMP * w, 1.0, (255, 255, 230))
        if WEAVE[1] <= f < WEAVE[1] + 6:  # the knot closes: a soft flash
            k = 1 - (f - WEAVE[1]) / 6
            for x in range(W):
                for y in (1, 14):
                    add(img, x, y, (120, 110, 60), 0.5 * k)
        if f >= WORDS:
            a = ease_out(phase(f, WORDS, WORDS + sec(1.0)))
            glow(img, 36, 8, 14, (40, 90, 40), 0.5 * a)
            draw_text(img, TEXT, (W - tw) // 2, 6, None, font="tiny", gradient=(GOLD_HI, (255, 176, 40)),
                      shadow=(4, 30, 12), alpha=a)
            sa = ease_out(phase(f, WORDS + sec(0.6), WORDS + sec(1.4)))
            for cx in (7, 64):
                shamrock(img, cx, 7, 0, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK, alpha=sa)
        frames.append(img)
    return frames
