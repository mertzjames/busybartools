"""Scene: Drums and Dance. At dusk under a baobab, two drummers keep the beat on hand drums while three dancers in
kente-colored clothes dance to it. The drums roll faster, the dancers leap together, and red, black, green and
gold confetti flies."""

from __future__ import annotations

import math

from busybar.canvas import FPS, add, mix, put, sec, vgradient
from busybar.party import Confetti
from kfx import CHARCOAL_HI, GOLD, GOLD_HI, GREEN, GREEN_HI, RED, RED_HI, SKIN, WOOD, WOOD_DK, WOOD_HI, person

NAME = "drums"
TITLE = "Drums and Dance"
SECONDS = 15
KEYFRAMES = [(1.0, "Drummers at dusk"), (3.0, "The dancers join in"), (6.6, "Arms up on the beat"),
             (10.4, "The drums roll faster"), (12.4, "Everyone leaps"), (13.6, "Confetti")]

GROUND = 13
BEAT = 8  # frames per beat (about 112 bpm)
T_DANCE = 1.6  # dancers step in
T_ROLL = 9.6  # drum roll: twice as fast
T_LEAP = 11.8

# dancers: x (left column), skin, cloth, accent, head, headwear
DANCERS = [
    (22, SKIN[2], (230, 170, 40), GREEN, "wrap", (30, 140, 60)),
    (33, SKIN[0], (40, 150, 70), GOLD, "kufi", (200, 40, 40)),
    (44, SKIN[3], (200, 40, 40), GOLD, "wrap", (240, 190, 50)),
]
# arm poses per beat of a 4-beat bar: (left, right) in turns
POSES = [(0.42, 0.12), (0.12, 0.42), (0.3, 0.3), (0.48, 0.48)]


def baobab(img, x: int) -> None:
    """A baobab silhouette on the horizon: a thick trunk and a flat crown of short branches (lit, dim)."""
    trunk = (70, 40, 56)
    for y in range(5, GROUND):
        for dx in range(-2, 2):
            put(img, x + dx, y, trunk)
    for dx in range(-6, 6):
        put(img, x + dx, 4, trunk)
        if dx % 3 == 0:
            put(img, x + dx, 3, trunk)
            put(img, x + dx + (1 if dx > 0 else -1), 2, trunk)


def drum(img, x: int, top: int, hit: float) -> None:
    """A goblet hand drum, 5 px wide at the head, 6 rows tall; the head flashes when struck."""
    head = mix((222, 196, 150), (255, 250, 230), hit)
    for dx in range(5):
        put(img, x + dx, top, head)
    rows = [(0, 5, RED), (0, 5, GOLD), (1, 4, WOOD_HI), (2, 3, WOOD), (1, 4, WOOD), (1, 4, WOOD_DK)]
    for r, (a, b, c) in enumerate(rows):
        for dx in range(a, b):
            put(img, x + dx, top + 1 + r, c if r != 1 else (GOLD if dx % 2 else RED))


def drummer(img, x: int, skin, cloth, wrap, f: int, roll: bool, flip: bool) -> float:
    """A standing drummer behind a hand drum (the drum on the inner side). Returns the strike (0..1)."""
    period = BEAT // 2 if roll else BEAT
    k = f % period
    hand = (f // period) % 2
    strike = 1.0 if k < 2 else 0.0
    person(img, x, GROUND, skin, cloth, GOLD, head="kufi", wrap=wrap, arms=(0.0, 0.0))
    dx = x + 3 if not flip else x - 3
    top = GROUND - 6
    drum(img, dx, top, strike * 0.9)
    # two hands over the drum head: the striking one comes down on the beat
    for side in (0, 1):
        hx = dx + 1 + side * 2
        lift = 0 if (side == hand and k < 2) else (2 if side == hand else 1)
        put(img, hx, top - 1 - lift, skin)
        put(img, hx + (-1 if not flip else 1), top - 2 - lift, skin, 0.7)
    return strike


def render():
    bg = vgradient((14, 8, 40), (56, 20, 50))
    for x in range(72):  # the last of the sunset along the horizon
        for y in range(9, GROUND):
            add(bg, x, y, (150, 60, 30), 0.5 * (y - 8) / 4)
        for y in range(GROUND, 16):
            put(bg, x, y, (96, 44, 28) if (x * 3 + y) % 5 else (78, 36, 24))
    baobab(bg, 55)
    for sx, sy in ((5, 1), (14, 3), (27, 0), (40, 2), (50, 1), (66, 2), (70, 0)):  # a few early stars
        put(bg, sx, sy, (200, 200, 230), 0.6)
    confetti = Confetti(seed=44, t0=sec(T_LEAP + 0.4), x=36, y=6, n=72, vx=(-2.2, 2.2), vy=(-2.4, -0.8),
                        colors=(RED, RED_HI, GREEN, GREEN_HI, GOLD, GOLD_HI, CHARCOAL_HI), spread=12, stagger=6)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        roll = t >= T_ROLL
        hits = [drummer(img, 1, SKIN[1], (180, 40, 40), (40, 140, 60), f, roll, False),
                drummer(img, 66, SKIN[4], (40, 120, 60), (230, 180, 40), f + BEAT // 2, roll, True)]
        # sound rings from struck drums
        for (dxs, off, sgn) in ((10, 0, 1), (62, BEAT // 2, -1)):
            age = (f + off) % (BEAT // 2 if roll else BEAT)
            if age < 5:
                r = 1 + age
                for dy in (-1, 0, 1):
                    add(img, dxs + sgn * r, GROUND - 7 + dy * (1 + r // 2), GOLD_HI, 0.55 * (1 - age / 5))
        # the dancers
        beat = f // BEAT
        sub = (f % BEAT) / BEAT
        for i, (x, skin, cloth, accent, head, hw) in enumerate(DANCERS):
            if t < T_DANCE:
                arms, legs, lift = (0.02, 0.02), 0, 0
            elif t < T_LEAP:
                pose = POSES[(beat + i) % 4]
                arms = pose
                legs = 1 if (beat + i) % 2 else 0
                lift = 1 if sub < 0.35 and (beat + i) % 4 == 3 else 0
            else:
                u = (t - T_LEAP) % 1.0
                arms = (0.48, 0.48)
                legs = 1
                lift = round(3 * math.sin(math.pi * min(1.0, u / 0.6))) if u < 0.6 else 0
            sway = (1 if (beat + i) % 2 else -1) if T_DANCE <= t < T_LEAP and sub > 0.5 else 0
            person(img, x + sway, GROUND + 1 - lift, skin, cloth, accent, head=head, wrap=hw, arms=arms, legs=legs)
        confetti.draw(img, f, floor=GROUND + 1)
        frames.append(img)
    return frames
