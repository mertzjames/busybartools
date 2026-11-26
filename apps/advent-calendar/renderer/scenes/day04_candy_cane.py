"""Dec 4: Candy Cane. A giant candy cane's stripes spin like a barber pole while peppermints roll past."""

import math

from busybar.canvas import FPS, add, ease_out, lerp, phase, put, sec
from busybar.fx import SPARKLE, Particles

from common import sky

NAME = "day04"
TITLE = "Candy Cane"
SECONDS = 8
KEYFRAMES = [(0.6, "A candy cane swings in"), (2.6, "Its stripes start to spin"),
             (4.6, "Peppermints roll by"), (7.0, "A sugary shine")]

RED = (232, 30, 46)
WHITE = (250, 246, 246)
PINK = (255, 160, 170)
MINT = (60, 200, 120)


def cane_path():
    """Centerline points of the cane: a hook at the top-left, a straight shaft down the right."""
    pts = []
    for i in range(0, 41):
        a = math.pi + math.pi * i / 40  # left (pi) over the top to the right (2pi); radius 5, center (0, 6)
        pts.append((5 * math.cos(a), 6 + 5 * math.sin(a)))
    for i in range(1, 25):
        pts.append((5, 6 + i * 0.4))
    return pts


def draw_cane(img, cx, cy, spin, angle):
    ca, sa = math.cos(angle), math.sin(angle)
    path = cane_path()
    s = 0.0
    for i, (x, y) in enumerate(path):
        if i:
            s += math.hypot(x - path[i - 1][0], y - path[i - 1][1])
        j0, j1 = max(0, i - 1), min(len(path) - 1, i + 1)
        tx, ty = path[j1][0] - path[j0][0], path[j1][1] - path[j0][1]
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n
        for off in (-1, 0, 1):
            px, py = x + off * nx, y + off * ny
            rx, ry = px * ca - py * sa, px * sa + py * ca
            # diagonal stripes: shift the stripe phase across the tube's thickness
            stripe = int(math.floor((s + off * 0.9 + spin) / 1.7)) % 2
            c = RED if stripe == 0 else WHITE
            if off == -1 and stripe == 1:
                c = PINK
            put(img, cx + rx, cy + ry, c)


def peppermint(img, x, y, rot):
    for dy in range(-2, 3):
        for dx in range(-2, 3):
            if dx * dx + dy * dy > 5:
                continue
            a = math.atan2(dy, dx) + rot
            c = RED if int(math.floor(a / (math.pi / 3))) % 2 == 0 else WHITE
            if dx == 0 and dy == 0:
                c = WHITE
            put(img, x + dx, y + dy, c)


def render():
    bg = sky(((8, 40, 30), (14, 70, 44)))
    sp = Particles(seed=44)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # snowy sparkle field
        for i in range(14):
            x, y = (i * 37) % 72, (i * 11) % 16
            put(img, x, y, (200, 255, 220), 0.25 + 0.25 * math.sin(f * 0.3 + i))
        swing = (1 - ease_out(phase(f, 0, sec(1.6)))) * 0.9 * math.cos(t * 6)
        spin = 0 if t < 2.2 else (t - 2.2) * 8
        # peppermints roll across in both directions, behind the cane
        if t > 3.6:
            k = phase(f, sec(3.6), sec(7.6))
            peppermint(img, lerp(-4, 76, k), 13, -k * 20)
            peppermint(img, lerp(78, -6, phase(f, sec(4.2), sec(8.0))), 9, k * 20)
        draw_cane(img, 34, 0, spin, swing * 0.3)
        # shine: a sweep down the shaft and sparkles
        if t > 6.2:
            k = phase(f, sec(6.2), sec(7.2))
            add(img, 39, lerp(6, 15, k), (255, 255, 255), 0.9 * (1 - k))
            if f % 3 == 0:
                sp.emit(36 + (f * 7) % 9 - 4, 3 + (f * 5) % 12, 1, vy=(-0.3, -0.1), life=(6, 12), colors=SPARKLE,
                        glow=True)
        sp.step_draw(img)
        frames.append(img)
    return frames
