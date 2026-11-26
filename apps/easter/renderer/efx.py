"""App-local Easter props and effects: decorated eggs, spring flowers, grass, a morning sky, the sun, a basket, a
nest, kids for the egg hunt, and a darkened box for captions.

Everything is seeded or a pure function of the frame number, so builds are byte-identical. These build on the shared
render kit (busybar.canvas / busybar.party) and stay in this app until another app needs them (repo R2).

Pastels stay LIT and saturated (docs/DECISIONS.md D4): every egg color keeps one channel high and at least one well
below it, so it reads as a color on the LEDs, not as white, and every pattern uses a deeper accent of the same hue
or a contrasting pastel.
"""

from __future__ import annotations

import math

from busybar.canvas import H, W, add, mix, put
from busybar.party import hash01

# --- palette (linear colors; the build's tone curve lifts them) ------------------------------------------------

PINK = (255, 140, 196)
BLUE = (120, 180, 255)
MINT = (100, 226, 160)
LEMON = (255, 226, 90)
LILAC = (186, 140, 255)
PEACH = (255, 170, 104)
WHITE = (255, 250, 240)

# deeper accents of each pastel, for stripes, dots and zigzags
ACCENT = {
    PINK: (226, 50, 140),
    BLUE: (40, 100, 226),
    MINT: (20, 156, 92),
    LEMON: (236, 150, 20),
    LILAC: (120, 66, 216),
    PEACH: (232, 96, 40),
}
PASTELS = (PINK, BLUE, MINT, LEMON, LILAC, PEACH)

GRASS = (70, 176, 60)
GRASS_HI = (120, 214, 80)
GRASS_DK = (34, 120, 44)
LEAF = (56, 156, 64)
LEAF_DK = (30, 104, 40)
SUN = (255, 214, 60)
SUN_HI = (255, 246, 170)
STRAW = (214, 168, 80)
STRAW_HI = (246, 210, 120)
STRAW_DK = (150, 104, 44)
WICKER = (176, 112, 52)
WICKER_HI = (220, 156, 82)
WICKER_DK = (122, 72, 30)

# Morning sky: a clear spring blue, lighter at the horizon (never so pale that white or cream reads as sky)
SKY_TOP = (56, 120, 226)
SKY_BOTTOM = (116, 178, 244)


# --- eggs -------------------------------------------------------------------------------------------------------

def egg_mask(w: int, h: int) -> list[tuple[int, int]]:
    """Pixels (dx, dy) of an egg w wide and h tall: an ellipse, narrower at the top."""
    out = []
    cx = (w - 1) / 2
    for dy in range(h):
        v = (dy + 0.5) / h  # 0 top .. 1 bottom
        # half-width: the widest point sits below the middle, like an egg
        yy = (v - 0.58) / (0.58 if v < 0.58 else 0.42)
        half = (w / 2) * math.sqrt(max(0.0, 1 - yy * yy))
        half *= 0.86 + 0.14 * v
        for dx in range(w):
            if abs(dx - cx) <= half - 0.05 or (abs(dx - cx) < 0.6 and half > 0.3):
                out.append((dx, dy))
    return out


def pattern_color(pattern: str, base, accent, dx: int, dy: int, w: int, h: int, reveal: float = 1.0, alt=None):
    """The color of one egg pixel. reveal (0..1) paints the pattern in from left to right."""
    if pattern == "plain" or dx > reveal * (w + 1) - 1:
        return base
    alt = alt or WHITE
    if pattern == "stripes":  # two bands across the middle
        if dy in (h // 3, (2 * h) // 3):
            return accent
    elif pattern == "band":  # one wide band with a white line through it
        mid = h // 2
        if dy == mid:
            return alt
        if dy in (mid - 1, mid + 1):
            return accent
    elif pattern == "dots":
        if (dx + 2 * dy) % 3 == 0 and 0 < dy < h - 1:
            return accent if (dx + dy) % 2 else alt
    elif pattern == "zigzag":
        mid = h // 2
        z = mid + (1 if (dx % 4) in (1, 3) else (0 if dx % 4 == 2 else 2)) - 1
        if dy == z:
            return accent
        if dy == z + 2 and h >= 8:
            return alt
    elif pattern == "split":  # two-tone: top half the accent
        if dy < h // 2:
            return accent
    elif pattern == "hearts":  # a row of small diamonds
        mid = h // 2
        k = dx % 3
        if (k == 1 and dy in (mid - 1, mid + 1)) or (k != 1 and dy == mid):
            return accent
    return base


def egg(img, x: int, y: int, w: int, h: int, base, pattern: str = "plain", accent=None, alpha: float = 1.0,
        reveal: float = 1.0, alt=None, shine: bool = True, top_cut: int = 0) -> None:
    """A decorated egg with its top-left at (x, y). top_cut hides that many top rows (for a cracked-open shell)."""
    accent = accent or ACCENT.get(tuple(base), mix(base, (0, 0, 0), 0.35))
    for dx, dy in egg_mask(w, h):
        if dy < top_cut:
            continue
        c = pattern_color(pattern, base, accent, dx, dy, w, h, reveal, alt)
        # soft shading: the lower-right edge a touch deeper
        if dx >= w - 1 - (1 if dy > h // 2 else 0) and w >= 4:
            c = mix(c, accent, 0.25)
        put(img, x + dx, y + dy, c, alpha)
    if shine and w >= 4 and h >= 5 and top_cut <= 1:
        put(img, x + 1, y + 1 + (h >= 7), mix(base, WHITE, 0.7), alpha)


def small_egg(img, x: int, y: int, base, alpha: float = 1.0, accent=None) -> None:
    """A 3x4 egg (tiny eggs in the grass): a pastel with one accent stripe."""
    accent = accent or ACCENT.get(tuple(base), base)
    for dx, dy in ((1, 0), (0, 1), (1, 1), (2, 1), (0, 2), (1, 2), (2, 2), (1, 3), (0, 3), (2, 3)):
        if dy == 3 and dx != 1:
            continue
        put(img, x + dx, y + dy, accent if dy == 2 else base, alpha)
    put(img, x + 1, y + 3, base, alpha)


def crack(img, x: int, y: int, w: int, row: int, color=(120, 44, 80), progress: float = 1.0) -> None:
    """A zigzag crack across an egg at `row` (relative), drawn in from the middle outwards. A stepped line (two
    pixels up, two down), so it reads as one jagged line on the LEDs rather than a checkerboard."""
    cx = (w - 1) / 2
    for dx in range(w):
        if abs(dx - cx) > progress * (w / 2 + 0.5):
            continue
        dy = row - (1 if dx % 4 in (1, 2) else 0)
        put(img, x + dx, y + dy, color)


# --- scenery ----------------------------------------------------------------------------------------------------

def grass(img, top: int, seed: int = 1, f: int = 0, sway: float = 0.0, color=GRASS, hi=GRASS_HI, dk=GRASS_DK) -> list:
    """A grass band from row `top` down, with blades poking above it. Returns the grass top per column."""
    tops = []
    for x in range(W):
        h = top
        r = hash01(seed, x)
        if r > 0.55:
            h -= 1
        if r > 0.88:
            h -= 1
        tops.append(h)
        for y in range(h, H):
            c = color if (x + y) % 3 else dk
            if y == h:
                c = hi if r > 0.3 else color
            put(img, x, y, c)
    return tops


def sky(img, top=SKY_TOP, bottom=SKY_BOTTOM, rows: int = H) -> None:
    for y in range(rows):
        c = mix(top, bottom, y / max(1, rows - 1))
        for x in range(W):
            put(img, x, y, c)


def sun(img, cx: float, cy: float, r: float = 3.2, f: int = 0, rays: bool = True, alpha: float = 1.0) -> None:
    """A round sun with a soft halo and slowly turning rays."""
    for y in range(int(cy - r - 5), int(cy + r + 6)):
        for x in range(int(cx - r - 5), int(cx + r + 6)):
            d = math.hypot(x - cx, y - cy)
            if d <= r:
                put(img, x, y, mix(SUN_HI, SUN, d / r), alpha)
            elif d <= r + 4:
                k = 1 - (d - r) / 4
                ang = math.atan2(y - cy, x - cx)
                ray = 0.5 + 0.5 * math.cos(8 * ang - 2 * math.pi * f / 90) if rays else 0.5
                add(img, x, y, (255, 200, 60), alpha * k * k * (0.25 + 0.4 * ray ** 3))


def cloud(img, x: float, y: float, w: int = 9, alpha: float = 1.0, color=(250, 252, 255)) -> None:
    """A small puffy cloud: a flat bottom and two bumps."""
    for dx in range(w):
        put(img, x + dx, y + 2, color, alpha)
        put(img, x + dx, y + 1, color, alpha * (0.95 if 0 < dx < w - 1 else 0.5))
    for dx in range(2, min(w - 1, 6)):
        put(img, x + dx, y, color, alpha * (0.9 if 2 < dx < 5 else 0.6))
    for dx in range(5, w - 2):
        put(img, x + dx, y, color, alpha * 0.7)
    for dx in range(3, 5):
        put(img, x + dx, y - 1, color, alpha * 0.8)


def bush(img, x: int, base: int, w: int = 9, h: int = 6, seed: int = 0, color=LEAF, dk=LEAF_DK,
         blossoms=None) -> None:
    """A rounded bush standing on row `base`, x is its left edge. blossoms: an optional flower color."""
    cx = x + (w - 1) / 2
    for y in range(base - h + 1, base + 1):
        for xx in range(x, x + w):
            ny = (base - y + 0.5) / h
            nx = (xx - cx) / (w / 2)
            if nx * nx + (ny * 1.0) ** 2 * 0.85 <= 1.0 or (y >= base - 1 and abs(nx) <= 1):
                r = hash01(seed, xx, y)
                c = dk if r < 0.3 else (mix(color, (160, 230, 110), 0.35) if r > 0.85 and ny > 0.5 else color)
                put(img, xx, y, c)
                if blossoms and r > 0.9 and ny > 0.3:
                    put(img, xx, y, blossoms)


def stem(img, x: int, base: int, h: int, color=LEAF, lean: float = 0.0) -> tuple[float, int]:
    """A stem from row `base` up h rows; returns the top (x, y)."""
    xx = float(x)
    for k in range(h):
        xx = x + lean * k / max(1, h)
        put(img, round(xx), base - k, color)
    return xx, base - h + 1


def tulip(img, x: int, base: int, h: int, color, open_: float = 1.0, alpha: float = 1.0) -> None:
    """A tulip on a stem: a closed bud (open_=0) that opens into a cup with three petal tips."""
    if h <= 0:
        return
    top = base - h + 1
    for k in range(h):
        put(img, x, base - k, LEAF, alpha)
    if h >= 4:  # a leaf
        put(img, x - 1, base - 1, LEAF_DK, alpha)
        put(img, x - 1, base - 2, LEAF, alpha)
    deep = ACCENT.get(tuple(color), mix(color, (0, 0, 0), 0.3))
    if open_ <= 0.01:
        return
    if open_ < 0.5:  # a bud
        put(img, x, top - 1, deep, alpha)
        put(img, x, top - 2, color, alpha * min(1.0, open_ * 4))
        return
    # the cup: 3 wide, 2 tall; open adds petal tips at the corners
    for dx in (-1, 0, 1):
        put(img, x + dx, top - 1, deep if dx == 0 else color, alpha)
        put(img, x + dx, top - 2, color, alpha)
    if open_ >= 0.8:
        put(img, x - 1, top - 3, color, alpha)
        put(img, x + 1, top - 3, color, alpha)
        put(img, x, top - 3, mix(color, WHITE, 0.4), alpha * 0.6)


def daffodil(img, x: int, base: int, h: int, open_: float = 1.0, alpha: float = 1.0, petals=(255, 240, 150),
             trumpet=(255, 160, 30)) -> None:
    """A daffodil facing right: pale petals around an orange trumpet; a closed bud bends on its stem first."""
    if h <= 0:
        return
    top = base - h + 1
    for k in range(h):
        put(img, x, base - k, LEAF, alpha)
    if h >= 4:
        put(img, x + 1, base - 1, LEAF_DK, alpha)
    if open_ <= 0.01:
        return
    if open_ < 0.5:
        put(img, x + 1, top - 1, (200, 220, 120), alpha)
        return
    hx, hy = x + 1, top - 2
    k = min(1.0, (open_ - 0.5) * 2)
    for dx, dy in ((0, -1), (-1, 0), (0, 1), (1, -1), (1, 1), (-1, -1), (-1, 1)):
        put(img, hx + dx, hy + dy, petals, alpha * k)
    put(img, hx, hy, trumpet, alpha)
    put(img, hx + 1, hy, trumpet, alpha * k)
    put(img, hx, hy + 2, LEAF, alpha)  # the neck


def lily(img, x: int, base: int, h: int, open_: float = 1.0, alpha: float = 1.0, flip: bool = False) -> None:
    """An Easter lily: a white trumpet flower nodding sideways off its stem, a bell with petal tips curling out
    and gold stamens. A pale green bud first (open_ < 0.5)."""
    if h <= 0:
        return
    s = -1 if flip else 1
    top = base - h + 1
    for k in range(h):
        put(img, x, base - k, LEAF, alpha)
    put(img, x - s, base - 2, LEAF, alpha)
    put(img, x - s * 2, base - 3, LEAF_DK, alpha)
    if open_ <= 0.01:
        return
    white, shade, neck = (252, 252, 240), (214, 226, 200), (170, 220, 150)
    if open_ < 0.5:
        put(img, x + s, top, neck, alpha)
        put(img, x + s * 2, top, (230, 240, 210), alpha * open_ * 2)
        return
    k = min(1.0, (open_ - 0.5) * 2)
    # a trumpet opening sideways: neck, a 3-tall bell, then petal tips curling out above and below
    put(img, x + s, top, neck, alpha)
    put(img, x + s * 2, top, shade, alpha)
    for dy in (-1, 0, 1):
        put(img, x + s * 3, top + dy, white, alpha)
    put(img, x + s * 4, top, (255, 196, 50), alpha * k)  # the gold stamens
    put(img, x + s * 4, top - 2, white, alpha * k)
    put(img, x + s * 4, top + 2, white, alpha * k)
    put(img, x + s * 2, top - 1, shade, alpha * k * 0.7)
    put(img, x + s * 2, top + 1, shade, alpha * k * 0.7)


def butterfly(img, x: float, y: float, f: int, colors=((255, 150, 210), (255, 220, 240)), body=(110, 60, 90),
              speed: int = 2, alpha: float = 1.0) -> None:
    """A tiny butterfly (3 px across) that flaps every `speed` frames: wings open, then folded up."""
    a, b = colors
    xi, yi = round(x), round(y)
    up = (f // speed) % 2
    put(img, xi, yi, body, alpha)
    if up:
        put(img, xi - 1, yi - 1, a, alpha)
        put(img, xi + 1, yi - 1, a, alpha)
    else:
        put(img, xi - 1, yi, a, alpha)
        put(img, xi + 1, yi, a, alpha)
        put(img, xi - 1, yi + 1, b, alpha * 0.8)
        put(img, xi + 1, yi + 1, b, alpha * 0.8)


def basket(img, x: int, base: int, w: int = 12, h: int = 4, handle: int = 5, back: bool = False,
           front: bool = True) -> None:
    """A woven wicker basket: x is its left edge, `base` its bottom row. Draw the back (handle) first, then the
    contents, then the front (the woven body), so eggs sit inside."""
    if back:
        cx = x + (w - 1) / 2
        rx = (w - 3) / 2
        for k in range(0, 41):
            a = math.pi * k / 40
            put(img, cx - rx * math.cos(a), base - h - handle * math.sin(a) + 0.5, WICKER_HI)
    if front:
        top = base - h + 1
        for y in range(top, base + 1):
            inset = 1 if y == base else 0
            for xx in range(x + inset, x + w - inset):
                weave = (xx + (y - top)) % 2 == 0
                c = WICKER_HI if y == top else (WICKER if weave else WICKER_DK)
                put(img, xx, y, c)


def nest(img, cx: int, base: int, w: int = 20, h: int = 3) -> None:
    """A straw nest: a shallow bowl of crossing straws."""
    x0 = cx - w // 2
    for y in range(base - h + 1, base + 1):
        for x in range(x0, x0 + w):
            k = (y - (base - h + 1))
            inset = (h - 1 - k) * 0 + (1 if y == base else 0)
            if x < x0 + inset or x >= x0 + w - inset:
                continue
            r = hash01(31, x, y)
            c = STRAW_HI if r > 0.7 else (STRAW_DK if r < 0.3 else STRAW)
            put(img, x, y, c)
    for x in range(x0 - 1, x0 + w + 1, 3):  # a few stray straws
        put(img, x, base - h + (x % 2), STRAW_HI, 0.8)


def kid(img, x: int, feet: int, shirt, hair, skin, pants=(70, 96, 190), shoes=(236, 236, 250), facing: int = 1,
        bend: float = 0.0, step: int = 0, arms_up: bool = False, lift: int = 0, alpha: float = 1.0) -> tuple[int, int]:
    """A small child in profile, 4 px wide and 10 rows tall, feet on row `feet` (minus `lift` when jumping).
    No face detail: a hair cap and a plain lit skin profile (docs/DECISIONS.md D5). x is the left edge of the body.
    bend 0..1 leans forward to pick something up; step 0/1 alternates the legs; arms_up cheers.
    Returns the front hand's (x, y)."""
    s = facing
    F = feet - lift
    front = x + 3 if s > 0 else x  # body column on the facing side
    back = x + 1 if s > 0 else x + 2
    lean = 1 if bend > 0.5 else 0
    # shoes and legs
    legs = (x + 1, x + 2) if step == 0 else (x, x + 3)
    for lx in legs:
        put(img, lx, F, shoes, alpha)
        put(img, lx, F - 1, pants, alpha)
        put(img, lx, F - 2, pants, alpha)
    # shirt: 3 wide, 4 rows, leaning forward at the top when bending
    for dy in range(4):
        sh = s * lean if dy < 2 else 0
        for dx in range(3):
            put(img, x + (1 if s > 0 else 0) + dx + sh - (1 if s < 0 else 0) + (0 if s > 0 else 1), F - 3 - dy, shirt,
                alpha)
    # head: 3x3, hair on top and at the back of the head
    hx = x + 1 + s * (2 * lean)
    hy = F - 9 + lean
    for dy in range(3):
        for dx in range(3):
            back_col = dx == (0 if s > 0 else 2)
            c = hair if dy == 0 or (back_col and dy == 1) else skin
            put(img, hx + dx, hy + dy, c, alpha)
    put(img, hx + (0 if s > 0 else 2), hy + 2, hair, alpha)  # hair down the back
    # the front arm
    if arms_up:
        ax = front + s
        put(img, ax, F - 6, shirt, alpha)
        put(img, ax, F - 7, skin, alpha)
        put(img, ax, F - 8, skin, alpha)
        bx = back - s
        put(img, bx, F - 7, skin, alpha)
        put(img, bx, F - 8, skin, alpha)
        return ax, F - 8
    if lean:
        ax = front + s * 2
        put(img, ax - s, F - 4, shirt, alpha)
        put(img, ax, F - 3, skin, alpha)
        put(img, ax, F - 2, skin, alpha)
        return ax, F - 1
    put(img, front + s, F - 5, shirt, alpha)
    put(img, front + s, F - 4, skin, alpha)
    return front + s, F - 3


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 0) -> None:
    """Darken the box x0..x1, y0..y1 by k (0..1) so a caption reads over busy art; `feather` fades the edge out over
    that many pixels on every side. (From Kwanzaa's kfx.dim_rect, extended to feather all four sides.)"""
    if k <= 0:
        return
    px = img.load()
    for y in range(max(0, y0 - feather), min(img.height, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(img.width, x1 + feather + 1)):
            d = max(x0 - x, x - x1, y0 - y, y - y1, 0)
            kk = k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - kk)), int(g * (1 - kk)), int(b * (1 - kk)), a)


# --- the bunny's hop ----------------------------------------------------------------------------------------------

HOP = 10  # frames per hop: crouch 2, airborne 6, land 2
HOP_DX = 7  # pixels per hop


def hop_pose(k: int, height: float = 2.0) -> tuple[int, float, float]:
    """Pose within one hop at frame k (0..HOP-1): (sprite frame, dx fraction 0..1, dy lift in px)."""
    if k < 2:
        return 1, 0.0, 0.0
    if k < 8:
        u = (k - 1) / 7
        return 2, u, -height * math.sin(math.pi * u)
    return 1, 1.0, 0.0


def bunny_path(f: int, plan) -> tuple[float, float, int]:
    """Where the bunny is at frame f, following plan = [("hop", n) | ("sit", frames, [sprite frames...]), ...] from a
    starting x given as plan[0] = ("start", x). Returns (x, lift, sprite frame)."""
    x = plan[0][1]
    t = 0
    for step in plan[1:]:
        if step[0] == "hop":
            n = step[1]
            if f < t + n * HOP:
                i, k = divmod(f - t, HOP)
                fr, u, dy = hop_pose(k)
                return x + (i + u) * HOP_DX, dy, fr
            x += n * HOP_DX
            t += n * HOP
        else:
            _, frames, poses = step
            if f < t + frames:
                return x, 0.0, poses[(f - t) * len(poses) // frames]
            t += frames
    return x, 0.0, 0
