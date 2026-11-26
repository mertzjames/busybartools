"""Dragon Dance: a long red-and-gold dragon on poles winds down a lantern-lit street, chasing a pearl carried
ahead of it. Every hoop of the body has its own dancer, and the wave runs from the head to the tail
(docs/DECISIONS.md D2).
"""

from __future__ import annotations

import math

from busybar.canvas import W, blit, mix, phase, put, sec, vgradient
from busybar.party import Confetti

import lnyfx as fx
import sprites

NAME = "dragon_dance"
TITLE = "Dragon Dance"
SECONDS = 16
KEYFRAMES = [(1.0, "The pearl leads the way"), (3.5, "The dragon's head appears"),
             (7.5, "The whole dragon winds down the street"), (10.0, "A big wave runs down its back"),
             (13.5, "The tail passes"), (15.5, "Gold confetti")]

N = sec(SECONDS)
GROUND = 15  # street row; dancers' feet stand on row 14
HOOPS = 9
SPACING = 6
SHIRT = (255, 200, 60)
PANTS = (190, 30, 40)
POLE = (170, 120, 70)
PEARL_GAP = 9


def head_x(f: int) -> float:
    return -16 + f * 0.62


def wave_y(x: float, f: int, amp: float) -> float:
    return 6.0 + amp * math.sin(0.33 * x - 0.32 * f)


def amp_at(f: int) -> float:
    return 2.0 + 1.6 * math.sin(math.pi * phase(f, sec(8.5), sec(11.5)))


def dancer(img, x: float, f: int, seed: int, hand_y: float) -> None:
    """A dancer under a pole: the pole runs from the hands up to `hand_y`."""
    x = int(round(x))
    step = (f // 4 + seed) % 2
    fx.figure(img, x, GROUND, SHIRT, pants=PANTS, step=step, height=5)
    for y in range(int(round(hand_y)), GROUND - 4):
        put(img, x + 1, y, POLE)


def render():
    bg = vgradient((14, 8, 34), (70, 22, 46))
    fx.rooftops(bg, base=11, color=(34, 28, 48), edge=(100, 70, 60), wall=(60, 16, 22), seed=11, lit=0.5)
    for x in range(W):
        put(bg, x, GROUND, (70, 56, 62))
    confetti = Confetti(seed=5, t0=sec(13.2), x=36, y=-2, n=46, vx=(-2.2, 2.2), vy=(0.0, 0.6), fall=(0.05, 0.1),
                        colors=(fx.GOLD, fx.GOLD_LIGHT, fx.RED, (255, 120, 40)), spread=30, stagger=sec(1.5))
    frames = []
    for f in range(N):
        img = bg.copy()
        fx.lantern_string(img, f, y0=0, spacing=12, offset=6, sag=1.0, size=0)
        hx = head_x(f)
        amp = amp_at(f)
        # the body: a thick cloth band along the wave, drawn tail first
        tail = hx - HOOPS * SPACING
        for x in range(int(math.floor(tail)), int(math.ceil(hx)) + 1):
            if not (0 <= x < W):
                continue
            u = (hx - x) / (HOOPS * SPACING)
            thick = 4 if u < 0.85 else 3 if u < 0.95 else 2
            y = wave_y(x, f, amp)
            top = int(round(y - thick / 2))
            for k in range(thick):
                c = fx.RED if k < thick - 1 else fx.GOLD
                if k == 1 and (x + int(f * 0.0)) % 3 == 0:
                    c = mix(fx.RED, fx.GOLD_LIGHT, 0.35)  # scales
                put(img, x, top + k, c)
            if x % 2 == 0:
                put(img, x, top - 1, (60, 200, 120))  # green fin along the spine
        # hoops, poles and dancers
        for i in range(1, HOOPS + 1):
            x = hx - i * SPACING + 2
            y = wave_y(x, f, amp)
            for k in range(-2, 2):
                put(img, x, y + k, fx.GOLD_DARK if k > -2 else fx.GOLD)
            dancer(img, x - 1, f, i, y + 2)
        # tail tuft
        tx = int(round(tail))
        ty = wave_y(tx, f, amp)
        for dy in (-2, -1, 1):
            put(img, tx - 1, ty + dy, (60, 200, 120))
        put(img, tx - 2, ty - 2, fx.GOLD)
        # the head, held high by the lead dancer, bobbing with the wave
        hy = wave_y(hx, f, amp) - 6 + (1 if (f // 6) % 2 else 0)
        dancer(img, hx + 3, f, 0, hy + 9)
        blit(img, sprites.DRAGON_HEAD.img((f // 7) % 2), hx - 1, hy)
        # the pearl, on its own pole, darting ahead
        px = hx + 15 + PEARL_GAP + 2 * math.sin(f * 0.11)
        py = 4 + 2 * math.sin(f * 0.19)
        dancer(img, px, f, 3, py + 2)
        put(img, px + 1, py, fx.GOLD_LIGHT)
        put(img, px + 2, py, fx.GOLD)
        put(img, px + 1, py + 1, fx.GOLD)
        put(img, px + 2, py + 1, fx.RED)
        if (f // 3) % 3 == 0:
            put(img, px, py - 1, fx.GOLD_LIGHT, 0.7)
        confetti.draw(img, f, floor=GROUND - 1)
        frames.append(img)
    return frames
