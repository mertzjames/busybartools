"""A bouquet assembles stem by stem: tulips, roses, daisies and lavender swing in from both sides and gather into a
bunch, a paper wrap rises around the stems, and a ribbon bow ties it (docs/DECISIONS.md D3)."""

from busybar.canvas import H, ease_in_out, ease_out, lerp, phase, put, sec
from busybar.party import glitter

import mfx

NAME = "bouquet"
TITLE = "A Bouquet for Mom"
SECONDS = 14
N = sec(SECONDS)
KEYFRAMES = [(0.5, "The first tulip swings in"), (3.5, "Roses and daisies gather"),
             (7.6, "Lavender and the last tulips"), (9.4, "A paper wrap rises"), (11.0, "Tied with a ribbon"),
             (13.0, "Ready for Mom")]

TIE = (36, 12)  # where every stem meets, under the bow
# (head column, head top row, kind, color), in the order they arrive (alternating sides)
FLOWERS = [
    (36, 1, "tulip", mfx.PINK), (32, 2, "rose", mfx.ROSE), (40, 2, "rose", mfx.PINK_DK),
    (28, 4, "daisy", mfx.WHITE), (44, 4, "daisy", mfx.WHITE), (34, 5, "tulip", mfx.YELLOW),
    (38, 5, "tulip", mfx.LAVENDER), (30, 6, "lavender", None), (42, 6, "lavender", None),
    (25, 6, "tulip", mfx.CORAL), (47, 6, "tulip", mfx.PINK),
]
ARRIVE0, GAP, FLIGHT = sec(0.3), sec(0.7), sec(1.0)
WRAP0, WRAP1 = sec(8.4), sec(9.6)
BOW0, BOW1 = sec(10.0), sec(11.0)


def flower_pos(i: int, f: int):
    """Head position and stem base of flower i at frame f (None before it starts)."""
    x, y, _, _ = FLOWERS[i]
    t0 = ARRIVE0 + i * GAP
    if f < t0:
        return None
    p = ease_out(phase(f, t0, t0 + FLIGHT))
    side = -1 if i % 2 == 0 else 1
    if i == 0:
        side = -1
    sx, sy = (x - 34 if side < 0 else x + 34), y + 5
    # an arc: the head rises a little mid-flight
    hx = lerp(sx, x, p)
    hy = lerp(sy, y, p) - 2.5 * (4 * p * (1 - p))
    bx = lerp(sx + side * -3, TIE[0], p)
    by = lerp(H + 2, TIE[1], p)
    return hx, hy, bx, by


def draw_bunch_stems(img, f: int) -> None:
    """The bundle below the tie: three stems once the first flower has landed."""
    if f < ARRIVE0 + FLIGHT:
        return
    for dx, x0 in ((-1, 35), (0, 36), (1, 37)):
        for y in range(TIE[1], H):
            put(img, x0 + dx * (y - TIE[1]) // 3, y, mfx.GREEN_DK if dx else mfx.GREEN)


# half-widths of the paper wrap, rows 9..15: wide at the top, gathered at the waist (row 13), flared below
WRAP_HALF = (9, 7, 5, 3, 2, 3, 4)


def wrap(img, f: int) -> None:
    """The paper wrap: cream with a pink edge and fold lines, rising from below."""
    if f < WRAP0:
        return
    rise = ease_out(phase(f, WRAP0, WRAP1))
    off = int(round((1 - rise) * 8))
    for r, half in enumerate(WRAP_HALF):
        y = 9 + r + off
        for x in range(36 - half, 36 + half + 1):
            if r == 0:  # a scalloped top edge
                if x % 2 == 0:
                    put(img, x, y, mfx.PINK_HI)
                continue
            edge = abs(x - 36) == half
            fold = (x - 36 + r) % 4 == 0 and r < 4
            put(img, x, y, mfx.PINK if edge else mfx.mix_paper(fold))


def bow(img, f: int) -> None:
    """A rose-red satin ribbon at the wrap's waist: the knot first, then the loops, then the tails."""
    if f < BOW0:
        return
    p = phase(f, BOW0, BOW1)
    cx, cy = TIE[0], 13
    hi, c, dk = mfx.ROSE_HI, mfx.ROSE, mfx.ROSE_DK
    for dx in (-1, 0, 1):
        put(img, cx + dx, cy, c)
    put(img, cx, cy, hi)
    if p > 0.25:  # loops
        for dx in (-1, 1):
            put(img, cx + 2 * dx, cy - 1, c)
            put(img, cx + 3 * dx, cy - 1, hi)
            put(img, cx + 4 * dx, cy, c)
            put(img, cx + 3 * dx, cy + 1, dk)
            put(img, cx + 2 * dx, cy, dk)
    if p > 0.6:  # tails
        put(img, cx - 1, cy + 1, c)
        put(img, cx - 1, cy + 2, dk)
        put(img, cx + 1, cy + 1, c)
        put(img, cx + 2, cy + 2, dk)


def render():
    bg = mfx.sky([(0, (24, 10, 38)), (15, (50, 18, 50))])
    mfx.glow(bg, 36, 6, 20, (60, 26, 56), 0.7, squash=1.8)
    frames = []
    for f in range(N):
        img = bg.copy()
        draw_bunch_stems(img, f)
        placed = [flower_pos(i, f) for i in range(len(FLOWERS))]
        for i, pos in enumerate(placed):  # stems first, so the heads cover them
            if pos:
                hx, hy, bx, by = pos
                mfx.line(img, hx, hy + 3, bx, by, mfx.GREEN)
        for lx, ly, side in ((31, 9, -1), (41, 9, 1)):  # two leaves once the middle has filled
            if f >= ARRIVE0 + 6 * GAP + FLIGHT:
                put(img, lx, ly, mfx.GREEN_HI)
                put(img, lx + side, ly - 1, mfx.GREEN)
        for i, pos in enumerate(placed):
            if pos:
                hx, hy, _, _ = pos
                _, _, kind, color = FLOWERS[i]
                mfx.bloom(img, kind, int(round(hx)), int(round(hy)), color)
        wrap(img, f)
        bow(img, f)
        if f >= BOW1:
            k = ease_in_out(phase(f, BOW1, BOW1 + sec(1)))
            glitter(img, seed=11, f=f, n=10, period=sec(2), colors=(mfx.YELLOW_HI, mfx.PINK_HI),
                    area=(22, 0, 51, 9), strength=1.0 * k)
            for hx0, t0 in ((14, BOW1), (58, BOW1 + sec(0.8))):
                if f >= t0:
                    q = phase(f, t0, t0 + sec(2.5))
                    mfx.heart(img, hx0, 12 - 12 * q, 5, mfx.PINK, alpha=min(1.0, 3 * (1 - q)))
        frames.append(img)
    return frames
