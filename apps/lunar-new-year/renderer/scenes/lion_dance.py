"""Lion Dance: to a drummer's beat, a two-dancer lion prances in, blinks and shakes its mane, spots the greens and
the red envelope hung high on a pole, rears up to take them, scatters lettuce leaves for good luck, and bows
(docs/DECISIONS.md D2). This is the traditional "plucking the greens" (cai qing).
"""

from __future__ import annotations

import math

from busybar.canvas import W, blit, ease_in_out, mix, phase, put, sec, vgradient
from busybar.party import Confetti, glitter

import lnyfx as fx
import sprites

NAME = "lion_dance"
TITLE = "Lion Dance"
SECONDS = 14
KEYFRAMES = [(1.5, "The drummer starts; the lion prances in"), (3.8, "It blinks and shakes its mane"),
             (6.6, "It rears up for the greens"), (8.2, "Greens and red envelope taken"),
             (9.6, "Lettuce leaves scattered for luck"), (12.5, "The lion bows")]

N = sec(SECONDS)
FLOOR = 15
BEAT = 8  # frames per drum beat
POLE_X = 64
FUR = (255, 248, 240)
CLOTH = fx.RED
PANTS = (255, 200, 60)


def drummer(img, f: int) -> None:
    """A drummer and a big red drum on the left; the sticks come down on the beat."""
    x = 4
    hit = f % BEAT < 2
    # drum
    for dx in range(-2, 4):
        for dy in range(10, 14):
            c = fx.RED if 0 <= dx <= 2 else fx.RED_DARK
            put(img, x + 3 + dx, dy, c)
        put(img, x + 3 + dx, 9, fx.GOLD_LIGHT if hit else (230, 210, 170))
        put(img, x + 3 + dx, 14, fx.GOLD_DARK)
    fx.figure(img, x - 2, FLOOR, (245, 240, 230), pants=(60, 70, 140), height=7)
    # stick
    sy = 8 if hit else 6
    put(img, x, sy, (230, 200, 150))
    put(img, x + 1, sy + (1 if hit else 0), (230, 200, 150))
    if hit and f > sec(0.5):
        fx.flash(img, x + 3, 8, 0.4, color=fx.GOLD_LIGHT)


def lion(img, f: int, hx: float, hy: float, lift: float, frame: int, legs_step: int) -> None:
    """The lion: head top-left at (hx, hy); the humped body trails 14 px behind. `lift` raises the front dancer
    (the body tilts up toward the head and the front legs show longer)."""
    hx, hy = int(round(hx)), int(round(hy))
    body_x0 = hx - 13
    rest = FLOOR - 3
    for i in range(16):
        x = body_x0 + i
        u = i / 15
        top = int(round(hy + 3 + lift - 1.5 * math.sin(math.pi * u) - u * lift))
        bottom = int(round(rest - u * lift))
        for y in range(top, bottom):
            c = CLOTH if (x + y) % 3 else mix(CLOTH, fx.GOLD, 0.6)  # gold scales
            put(img, x, y, c)
        put(img, x, top, fx.GOLD)
        put(img, x, bottom, FUR if i % 2 == 0 else (220, 220, 235))  # fur trim along the hem
    # tail
    put(img, body_x0 - 1, hy + 3 + lift, FUR)
    put(img, body_x0 - 2, hy + 2 + lift, FUR)
    put(img, body_x0 - 1, hy + 4 + lift, fx.GOLD)
    # legs: back dancer, then the front dancer (longer when lifted)
    for lx, ph, hem in ((body_x0 + 2, 0, rest), (body_x0 + 11, 1, int(round(rest - lift * 0.75)))):
        s = (legs_step + ph) % 2
        for k, dx in enumerate((0, 2)):
            off = 1 if (s + k) % 2 else 0
            for y in range(hem + 1, FLOOR - 1):
                put(img, lx + dx, y, PANTS)
            put(img, lx + dx + off, FLOOR - 1, PANTS)
            put(img, lx + dx + off, FLOOR - 1, PANTS)
    blit(img, sprites.LION_HEAD.img(frame), hx, hy)


def render():
    bg = vgradient((24, 6, 14), (62, 14, 22))
    fx.rooftops(bg, base=10, color=(36, 26, 44), edge=(110, 70, 60), wall=(70, 18, 24), seed=21, lit=0.5)
    for x in range(W):
        put(bg, x, FLOOR, (80, 60, 60))
    leaves = Confetti(seed=8, t0=sec(9.0), x=56, y=8, n=26, vx=(0.3, 2.4), vy=(-2.4, -0.6), fall=(0.08, 0.16),
                      colors=((80, 220, 80), (40, 170, 60), (150, 240, 110)), stagger=sec(0.4))
    frames = []
    for f in range(N):
        img = bg.copy()
        fx.lantern_string(img, f, y0=0, spacing=14, offset=4, sag=1.0, size=0)
        # the pole with the greens and a red envelope, hung high
        for y in range(1, FLOOR):
            put(img, POLE_X + 3, y, (150, 110, 70))
        for x in range(POLE_X - 6, POLE_X + 3):
            put(img, x, 1, (150, 110, 70))
        taken = f >= sec(7.8)
        if not taken:
            put(img, POLE_X - 4, 2, (120, 90, 60))
            blit(img, sprites.LETTUCE.img(0), POLE_X - 6, 3)
        drummer(img, f)

        t = f / 15
        beat = (f % BEAT) < 3
        frame = 0
        lift = 0.0
        if t < 3.0:  # prance in on the beat
            hx = -2 + 34 * ease_in_out(t / 3.0)
            hy = 2 - (1 if beat else 0)
            step = f // 4
        elif t < 4.6:  # stop, blink, shake the mane
            hx = 32 + (1 if (f // 3) % 2 and t > 3.8 else 0)
            hy = 2
            frame = 2 if 3.2 < t < 3.5 else 0
            step = 0
        elif t < 6.0:  # creep toward the pole
            hx = 32 + 18 * ease_in_out(phase(f, sec(4.6), sec(6.0)))
            hy = 3
            step = f // 6
        elif t < 9.0:  # rear up, take the greens, come back down
            hx = 50
            up = ease_in_out(phase(f, sec(6.0), sec(7.0))) - ease_in_out(phase(f, sec(8.2), sec(9.0)))
            lift = up * 3
            hy = 2 - lift
            frame = 1 if 7.2 < t < 8.4 and (f // 4) % 2 else 0
            step = 0
        elif t < 10.6:  # shake and scatter the leaves
            hx = 50 + (1 if (f // 2) % 2 else 0)
            hy = 2
            frame = 1 if t < 9.6 else 0
            step = 0
        else:  # bow three times
            hx = 50
            k = (t - 10.6) / 1.1
            hy = 2 + (2 if (k % 1) < 0.5 and k < 3 else 0)
            step = 0
        lion(img, f, hx, hy, lift, frame, step)
        if 7.8 <= t < 9.0:  # the envelope in the lion's mouth
            fx.envelope(img, hx + 9, hy + 8, alpha=1.0)
        leaves.draw(img, f, floor=FLOOR - 1)
        if t > 10.6:
            glitter(img, seed=3, f=f, n=10, period=40, area=(30, 1, 70, 9), strength=0.8)
        frames.append(img)
    return frames
