"""Scene: Skeleton Dance (the finale). The spotlights come up on a little stage and three skeletons dance to a beat
(two a second): arm pumps, then a can-can kick that ripples down the line, then the middle one's skull hops up off
its neck and lands back on, while the dance floor flashes. They jump together, and Halloween confetti and candy corn rain down."""

import math

from busybar.canvas import FPS, H, W, add, mix, put, sec
from busybar.party import Confetti
from hfx import BONE, candy_corn, frame_t, glow, gradient, quant

NAME = "skeletons"
TITLE = "Skeleton Dance"
SECONDS = 15
KEYFRAMES = [(0.6, "A dark stage"), (1.4, "Spotlights up"), (3.2, "Arm pumps to the beat"),
             (7.0, "A can-can kick down the line"), (9.9, "The middle skull hops up"),
             (12.6, "Jump!"), (13.8, "Confetti and candy corn")]

BEAT = 0.5  # seconds per beat (120 bpm)
XS = (16, 36, 56)
FEET = 14  # feet on row 14; the dance floor is row 15
LIGHTS_ON = (0.9, 1.5)
PUMP = (1.5, 6.0)
CANCAN = (6.0, 9.0)
HOP = (9.0, 12.0)
JUMP = (12.0, 13.0)
CONFETTI_AT = 12.6
SOCKET = (70, 230, 90)  # lit green eye sockets (black would be an unlit hole)
FLOOR = ((255, 120, 20), (150, 60, 220), (110, 230, 60))
CURTAIN = (110, 24, 60)
CANDY = ((8, 0.0, 9.0), (25, 0.5, 7.5), (45, 0.2, 8.5), (62, 0.7, 7.0), (31, 1.1, 9.5), (52, 1.3, 8.0))  # (x, delay s, rows/s)


def line(img, x0, y0, x1, y1, c) -> None:
    n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
    for i in range(n + 1):
        u = i / n
        put(img, math.floor(x0 + (x1 - x0) * u + 0.5), math.floor(y0 + (y1 - y0) * u + 0.5), c)


def limb(img, x, y, a1, a2, l1, l2) -> None:
    """Two bones from (x, y): angles in degrees from straight down (positive = toward +x)."""
    r1, r2 = math.radians(a1), math.radians(a2)
    x1, y1 = x + math.sin(r1) * l1, y + math.cos(r1) * l1
    x2, y2 = x1 + math.sin(r2) * l2, y1 + math.cos(r2) * l2
    line(img, x, y, x1, y1, BONE)
    line(img, x1, y1, x2, y2, BONE)


def skeleton(img, cx: int, pose: dict) -> None:
    """A 7x13 skeleton standing with its feet on FEET: a skull with lit sockets and a jaw, an oval rib cage
    around the spine, a pelvis and two-bone limbs. pose: arms (l_shoulder, l_elbow, r_shoulder, r_elbow), legs
    (l_hip, l_knee, r_hip, r_knee), lift (whole body up), head (skull up, for the hop)."""
    top = FEET - 12 - pose.get("lift", 0)
    hy = top - pose.get("head", 0)
    for dx, dy in ((-1, 0), (0, 0), (1, 0), (-2, 1), (-1, 1), (0, 1), (1, 1), (2, 1), (-2, 2), (0, 2), (2, 2),
                   (-1, 3), (0, 3), (1, 3)):
        put(img, cx + dx, hy + dy, BONE)
    put(img, cx - 1, hy + 2, SOCKET)
    put(img, cx + 1, hy + 2, SOCKET)
    put(img, cx - 1, top + 4, (200, 196, 180))  # jaw: two teeth
    put(img, cx + 1, top + 4, (200, 196, 180))
    for dx in (-1, 0, 1):  # an oval rib cage around the spine
        put(img, cx + dx, top + 5, BONE)
        put(img, cx + dx, top + 7, BONE)
    for dx in (-2, 0, 2):
        put(img, cx + dx, top + 6, BONE)
    put(img, cx, top + 8, BONE)  # spine, then the pelvis
    for dx in (-1, 0, 1):
        put(img, cx + dx, top + 9, BONE)
    la, le, ra, re = pose["arms"]
    limb(img, cx - 2, top + 5, -la, -le, 2.2, 2.2)
    limb(img, cx + 2, top + 5, ra, re, 2.2, 2.2)
    lh, lk, rh, rk = pose["legs"]
    limb(img, cx - 1, top + 10, -lh, -lk, 1.2, 1.6)
    limb(img, cx + 1, top + 10, rh, rk, 1.2, 1.6)


STAND = {"arms": (20, 10, 20, 10), "legs": (8, 0, 8, 0)}


def pose_at(i: int, t: float) -> dict:
    beat = t / BEAT
    n = int(beat)
    ph = beat - n
    bob = 1 if ph < 0.3 else 0
    if PUMP[0] <= t < PUMP[1]:
        up = n % 2 == 0
        arms = (135, 165, 35, 15) if up else (35, 15, 135, 165)
        return {"arms": arms, "legs": (12, 0, 12, 0), "lift": 0, "head": bob}
    if CANCAN[0] <= t < CANCAN[1]:
        k = (n + i) % 4  # the kick ripples down the line
        legs = {0: (70, 90, 6, 0), 2: (6, 0, 70, 90)}.get(k, (10, 0, 10, 0))
        return {"arms": (50, -40, 50, -40), "legs": legs, "head": bob}  # hands on hips
    if HOP[0] <= t < HOP[1]:
        if i == 1:
            u = ((t - HOP[0]) % 1.5) / 1.5
            head = int(math.floor(2 * math.sin(math.pi * min(1.0, u / 0.7)) + 0.5)) if u < 0.7 else 0
            return {"arms": (60, 120, 60, 120), "legs": (10, 0, 10, 0), "head": head}
        clap = n % 2 == 0
        return {"arms": (70, 140, 70, 140) if clap else (40, 90, 40, 90), "legs": (10, 0, 10, 0), "head": bob}
    if JUMP[0] <= t < JUMP[1]:
        u = (t - JUMP[0]) / (JUMP[1] - JUMP[0])
        lift = int(math.floor(2 * math.sin(math.pi * u) + 0.5))
        return {"arms": (140, 165, 140, 165), "legs": (25, -15, 25, -15), "lift": lift}
    if t >= JUMP[1]:
        wave = n % 2 == 0
        return {"arms": (135, 165, 35, 15) if (wave ^ (i == 1)) else (35, 15, 135, 165), "legs": (10, 0, 10, 0),
                "head": bob}
    return STAND


def render():
    dark = gradient([(0, (10, 2, 20)), (10, (24, 6, 40)), (15, (34, 10, 50))])
    lit = dark.copy()
    # two spotlights from the top corners: steady soft cones of green and purple, pooling on the floor
    for (sx, color) in ((10, (40, 110, 30)), (62, (90, 40, 130))):
        for y in range(H):
            half = 1.5 + y * 0.9
            cx = sx + (36 - sx) * y / 30
            for x in range(int(cx - half) - 1, int(cx + half) + 2):
                d = abs(x - cx) / half
                if d < 1:
                    add(lit, x, y, color, 0.55 * (1 - d))
    glow(lit, 36, 15, 20, (60, 30, 50), 0.6)
    for img in (dark, lit):  # curtains at both sides: lit velvet folds
        for y in range(H):
            for x in list(range(0, 4)) + list(range(68, W)):
                fold = (x % 2 == 0)
                put(img, x, y, mix(CURTAIN, (160, 40, 90), 0.4 if fold else 0.0))
        for x in range(4, 68):
            put(img, x, 0, (130, 30, 70) if x % 3 else (180, 50, 90))
    confetti = Confetti(seed=13, t0=sec(CONFETTI_AT), x=36, y=-2, n=46, vx=(-2.4, 2.4), vy=(-0.4, 0.6),
                        fall=(0.12, 0.22), colors=((255, 120, 20), (150, 60, 220), (110, 230, 60), (255, 236, 150),
                                                   (255, 255, 255)), spread=24, stagger=6)
    frames = []
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        k = quant((t - LIGHTS_ON[0]) / (LIGHTS_ON[1] - LIGHTS_ON[0]), 6)
        img = dark.copy() if k <= 0 else (lit.copy() if k >= 1 else _blend(dark, lit, k))
        # the dance floor: tiles flash on each beat once the music starts
        n = int(t / BEAT)
        on = t >= PUMP[0]
        for x in range(4, 68):
            tile = (x - 4) // 4
            c = FLOOR[(tile + n) % 3] if on else (60, 40, 70)
            bright = 1.0 if on and (tile + n) % 2 == 0 else 0.45
            put(img, x, 15, tuple(int(v * bright) for v in c))
        for i, x in enumerate(XS):
            skeleton(img, x, pose_at(i, t))
        if t >= CONFETTI_AT:
            confetti.draw(img, f)
            for j, (cx, t0, v) in enumerate(CANDY):  # candy corn tumbles down with the confetti
                age = t - CONFETTI_AT - t0
                if age >= 0:
                    candy_corn(img, cx + math.floor(0.8 * math.sin(age * 3 + j) + 0.5), math.floor(-3 + age * v + 0.5))
        frames.append(img)
    return frames


def _blend(a, b, k):
    from PIL import Image
    return Image.blend(a, b, k)
