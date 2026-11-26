"""Disco Fever: a mirror ball drops in, spins, and throws colored spots around the room while two guests dance."""

import math

from busybar.canvas import FPS, add, blit, ease_out, phase, put, sec, vgradient
from party import CYAN, GOLD, LIME, PINK, SILVER, VIOLET, WHITE, dim, hash01
from sprites import GUESTS

NAME = "disco_ball"
TITLE = "Disco Fever"
SECONDS = 14
KEYFRAMES = [(0.8, "The mirror ball drops in"), (3.0, "It starts to spin"), (6.5, "Spots sweep the room"),
             (9.5, "Two guests hit the floor"), (13.0, "Disco fever")]

CX = 36
R = 4.6
SPOT_COLORS = (PINK, CYAN, GOLD, LIME, VIOLET, WHITE)
TILE_COLORS = (PINK, CYAN, GOLD, VIOLET, LIME)


def ball(img, cy: float, spin: float, f: int) -> None:
    """Mirror ball: a grid of facets that slide sideways as it spins, shaded toward the edges, with glints."""
    for y in range(int(cy - R - 1), int(cy + R + 2)):
        for x in range(int(CX - R - 1), int(CX + R + 2)):
            dx, dy = x - CX, y - cy
            if dx * dx + dy * dy > R * R:
                continue
            nx = max(-1.0, min(1.0, dx / math.sqrt(max(0.01, R * R - dy * dy))))
            lon = math.asin(nx) + spin
            col = int(math.floor(lon / (math.pi / 5)))
            row = int(math.floor((dy + R) / 1.6))
            v = hash01(col, row, 7)
            limb = 1 - 0.55 * (dx * dx + dy * dy) / (R * R)
            base = dim(SILVER, (0.35 + 0.5 * v) * limb + 0.1)
            put(img, x, y, base)
            g = hash01(col, row, f // 3)
            if g > 0.9:
                put(img, x, y, WHITE)
            elif g > 0.84:
                put(img, x, y, SPOT_COLORS[(col + row) % len(SPOT_COLORS)])


def floor(img, f: int) -> None:
    beat = f // 8
    for x in range(72):
        t = (x // 6 + beat) % len(TILE_COLORS)
        on = (x // 6 + beat) % 3 == 0
        c = TILE_COLORS[t]
        put(img, x, 15, dim(c, 0.75 if on else 0.22))
        put(img, x, 14, dim(c, 0.28 if on else 0.08))


def render():
    bg = vgradient((10, 4, 26), (26, 8, 40))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        floor(img, f)
        # drop in with a little bounce
        d = phase(f, 0, sec(2.2))
        cy = -6 + 11.5 * ease_out(d) + (0.8 * math.sin(d * math.pi * 3) * (1 - d) if d < 1 else 0)
        spinning = phase(f, sec(2.0), sec(3.5))
        spin = 0.0 if t < 2.0 else (t - 2.0) * 2.2 * (0.4 + 0.6 * spinning)
        # spots: rotate around the room once the ball spins
        if spinning > 0:
            for i in range(18):
                a = spin * 0.9 + i * 2 * math.pi / 18
                rx = 30 + 5 * (i % 4)
                x = CX + rx * math.cos(a)
                y = cy + 2 + 6.5 * math.sin(a * 1.0 + i)
                c = SPOT_COLORS[i % len(SPOT_COLORS)]
                k = spinning * (0.8 + 0.2 * math.sin(a * 3))
                add(img, x, y, c, k)
                add(img, x + 1, y, c, 0.5 * k)
            # a few faint beams from the ball
            for i in range(4):
                a = spin * 0.9 + i * math.pi / 2 + 0.4
                for s in range(6, 22, 2):
                    add(img, CX + s * math.cos(a), cy + s * 0.45 * math.sin(a), SILVER, 0.08 * spinning)
        # chain and cap
        for y in range(0, int(cy - R)):
            put(img, CX, y, (150, 150, 170))
        put(img, CX, int(cy - R), (210, 180, 90))
        ball(img, cy, spin, f)
        add(img, CX - 2, cy - 2, WHITE, 0.6)
        # two guests slide in and dance from 8 s
        if t >= 7.6:
            k = phase(f, sec(7.6), sec(9.0))
            beat = (f // 5) % 4
            frame_l = (1, 0, 2, 0)[beat]
            frame_r = (0, 1, 0, 3)[beat]
            hop = -1 if beat in (1, 3) else 0
            blit(img, GUESTS[1].img(frame_l), -8 + 18 * ease_out(k), 3 + hop)
            blit(img, GUESTS[0].img(frame_r, flip=True), 73 - 19 * ease_out(k), 3 + (0 if hop else -1) + 1)
        frames.append(img)
    return frames
