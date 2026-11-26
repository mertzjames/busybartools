"""Tea in a sunny window: a quiet moment. A teacup steams on the windowsill beside a potted geranium and a little vase
of tulips, clouds drift past, a butterfly visits the window, and the steam curls into a heart
(docs/DECISIONS.md D3)."""

import math

from busybar.canvas import W, add, ease_in_out, lerp, mix, phase, put, sec

import mfx

NAME = "tea"
TITLE = "Tea in the Sunny Window"
SECONDS = 12
N = sec(SECONDS)
KEYFRAMES = [(0.6, "A cup of tea in the sun"), (4.0, "Clouds drift by"), (6.5, "A butterfly visits"),
             (9.4, "The steam curls into a heart")]

WIN_X0, WIN_X1, WIN_Y1 = 7, 38, 9  # the window opening (inclusive), rows 0..WIN_Y1
SILL = 11
CUP_X = 45  # the cup's left column: in front of the darker wall, so the white cup and its steam read
BAR_X = 23
POT_X = 15
VASE_X = 65
HEART0, HEART1 = sec(8.4), sec(11.2)
WALL = (66, 36, 52)
WALL_DK = (52, 28, 44)


def backdrop():
    img = mfx.sky([(0, WALL), (15, WALL_DK)])
    # outside: a bright spring sky, the sun in the upper right pane, a green treetop far below
    for y in range(0, WIN_Y1 + 1):
        for x in range(WIN_X0, WIN_X1 + 1):
            put(img, x, y, mix((90, 160, 240), (170, 214, 255), y / WIN_Y1))
    mfx.glow(img, 32, 2, 7, (120, 110, 60), 0.9)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1), (-1, 0), (0, -1), (2, 1), (1, 2), (-1, 1), (1, -1)):
        put(img, 32 + dx, 2 + dy, mfx.YELLOW_HI)
    for x in range(WIN_X0, WIN_X1 + 1):  # far hills along the bottom of the view
        put(img, x, WIN_Y1, (110, 190, 130))
        if math.sin(x * 0.4) > 0.2:
            put(img, x, WIN_Y1 - 1, (130, 204, 150))
    return img


def frame_and_room(img):
    """The window frame and bars, the curtains and the sill (drawn over the sky and clouds)."""
    for y in range(0, WIN_Y1 + 1):
        put(img, WIN_X0 - 1, y, mfx.CREAM)
        put(img, WIN_X1 + 1, y, mfx.CREAM)
        put(img, BAR_X, y, mfx.CREAM)
    for x in range(WIN_X0, WIN_X1 + 1):
        put(img, x, 5, mfx.CREAM)
    for x in range(2, 70):  # the sill
        put(img, x, SILL, mfx.CREAM)
        put(img, x, SILL + 1, (220, 190, 160))
    # curtains, gathered at the sides
    for y in range(0, SILL):
        w = 3 if y < 7 else 2
        for k in range(w):
            c = mfx.PINK if (k + y // 3) % 2 else mfx.PINK_DK
            put(img, WIN_X0 - 2 - k + (1 if y >= 7 else 0), y, c)
            put(img, WIN_X1 + 2 + k - (1 if y >= 7 else 0), y, c)


def still_life(img):
    """The cup and saucer, the vase of tulips and the potted geranium on the sill."""
    # saucer and cup (white with a pink band and a pink heart), handle on the right
    for x in range(CUP_X - 1, CUP_X + 6):
        put(img, x, SILL - 1, (232, 226, 236) if CUP_X <= x < CUP_X + 5 else (200, 194, 210))
    for y in range(SILL - 5, SILL - 1):
        for x in range(CUP_X, CUP_X + 5):
            band = y == SILL - 4
            put(img, x, y, mfx.PINK if band else mfx.WHITE)
    put(img, CUP_X + 2, SILL - 3, mfx.ROSE)  # a tiny heart on the cup
    put(img, CUP_X, SILL - 2, mix(mfx.WHITE, (150, 140, 170), 0.3))
    put(img, CUP_X + 4, SILL - 2, mix(mfx.WHITE, (150, 140, 170), 0.3))
    for dy in (0, 1, 2):  # the handle
        put(img, CUP_X + 5 + (1 if dy == 1 else 0), SILL - 5 + dy, mfx.WHITE)
    for x in range(CUP_X + 1, CUP_X + 4):  # tea showing at the rim
        put(img, x, SILL - 5, (196, 120, 64))
    # a small framed picture on the wall: a heart
    for y in range(1, 7):
        for x in range(54, 60):
            edge = y in (1, 6) or x in (54, 59)
            put(img, x, y, (226, 180, 96) if edge else (250, 230, 220))
    mfx.heart(img, 57, 2, 3, mfx.ROSE)
    # the vase of tulips, left
    v = VASE_X
    for y in (SILL - 3, SILL - 2, SILL - 1):
        put(img, v, y, (120, 170, 255))
        put(img, v + 1, y, (160, 200, 255))
    for x, top, c in ((v - 1, 3, mfx.YELLOW), (v + 2, 2, mfx.PINK)):
        for y in range(top + 3, SILL - 3):
            put(img, min(max(x, v), v + 1), y, mfx.GREEN)
        mfx.tulip(img, x, top, c)
    # the potted geranium, right
    for y, half in ((SILL - 3, 3), (SILL - 2, 2), (SILL - 1, 2)):
        for x in range(POT_X - half, POT_X + half + 1):
            put(img, x, y, (206, 104, 60) if y != SILL - 3 else (232, 130, 80))
    for dx, dy in ((-2, -1), (-1, -1), (0, -1), (1, -1), (2, -1), (-3, -2), (-1, -2), (1, -2), (3, -2), (0, -2),
                   (-2, -3), (2, -3), (0, -3)):
        put(img, POT_X + dx, SILL - 3 + dy, mfx.GREEN if (dx + dy) % 2 else mfx.GREEN_DK)
    for cx, cy in ((POT_X - 2, SILL - 7), (POT_X + 2, SILL - 6), (POT_X, SILL - 8)):
        for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
            put(img, cx + dx, cy + dy, mfx.ROSE if (dx + dy) % 2 else mfx.ROSE_HI)
        put(img, cx, cy + 2, mfx.GREEN)


def sunbeam(img):
    """Soft light falling through the window onto the sill (steady)."""
    for y in range(0, 16):  # a broad shaft from the window down to the right, across the cup
        for x in range(W):
            d = x - (WIN_X1 + 1) - (y - 0) * 1.2
            if WIN_X1 < x and 0 <= d <= 14:
                add(img, x, y, (70, 52, 24), 0.6 * (1 - d / 15))


STEAM_HEART = [(-2, 0), (-1, -1), (0, 0), (1, -1), (2, 0), (2, 1), (1, 2), (0, 3), (-1, 2), (-2, 1)]


def steam(img, f: int):
    cx = CUP_X + 2
    fade = 1.0
    if HEART0 - sec(0.6) <= f < HEART1:
        fade = 0.3
    for i in range(2):
        for k in range(4):
            age = (f / 22 + k / 4 + i * 0.12) % 1.0
            y = SILL - 6 - age * 6
            x = cx + (i - 0.5) * 1.2 + 1.1 * math.sin(2 * math.pi * (age * 1.2 + i * 0.4))
            put(img, x, y, (240, 236, 246), 0.8 * (1 - age) * fade)
    if HEART0 <= f < HEART1:  # the steam curls into a heart that rises and fades
        q = phase(f, HEART0, HEART1)
        a = min(1.0, q * 5) * (1 - ease_in_out(max(0.0, (q - 0.55) / 0.45)))
        hy = lerp(3.0, 0.0, q)
        for dx, dy in STEAM_HEART:
            put(img, cx + 0.5 + dx, hy + dy, (250, 240, 250), 0.85 * a)


def render():
    base = backdrop()
    frames = []
    for f in range(N):
        img = base.copy()
        for x0, y, sp in ((12, 1, 0.05), (34, 3, 0.035)):  # clouds drift right, wrapping inside the window
            x = WIN_X0 + ((x0 + f * sp) % (WIN_X1 - WIN_X0 + 6)) - 5
            for dx, dy in ((0, 1), (1, 0), (1, 1), (2, 0), (2, 1), (3, 1), (4, 1), (3, 0)):
                xx = int(round(x + dx))
                if WIN_X0 <= xx <= WIN_X1 and y + dy < 8:
                    put(img, xx, y + dy, (240, 246, 255), 0.9)
        frame_and_room(img)
        sunbeam(img)
        still_life(img)
        steam(img, f)
        if sec(5.4) <= f < sec(8.6):  # a butterfly flutters to the geranium, rests, and leaves
            q = phase(f, sec(5.4), sec(8.6))
            if q < 0.35:
                bx, by = lerp(30, POT_X + 2, q / 0.35), lerp(1, 3.0, q / 0.35) + math.sin(q * 30)
            elif q < 0.7:
                bx, by = POT_X + 2, 3.0
            else:
                r = (q - 0.7) / 0.3
                bx, by = lerp(POT_X + 2, -4, r), 3.0 - 3 * r + math.sin(r * 12)
            mfx.butterfly(img, bx, by, f if q < 0.35 or q >= 0.7 else f // 3, mfx.YELLOW)
        frames.append(img)
    return frames
