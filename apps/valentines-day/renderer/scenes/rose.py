"""Scene: A Rose Blooms. In a soft plum glow a green stem grows from the bottom, puts out two leaves and a bud, and
the bud opens, petal by petal, into a red rose. Two smaller roses grow and open beside it, a few petals drift
down, and gold glints twinkle around the bouquet."""

import math
import random

from busybar.canvas import FPS, H, W, add, blit, ease_out, put, sec
from sprites import ROSE_STAGES
from vfx import GOLD_LIGHT, gradient, heart_glow, twinkle

NAME = "rose"
TITLE = "A Rose Blooms"
SECONDS = 14
KEYFRAMES = [(1.2, "A stem grows"), (2.8, "Leaves and a bud"), (4.6, "The bud opens"), (6.4, "A red rose"),
             (9.4, "Two more roses open"), (12.6, "Petals drift; gold glints")]

STEM = (46, 160, 70)
STEM_DARK = (34, 120, 54)
LEAF = (70, 190, 84)
LEAF_DARK = (40, 140, 60)
PETAL = (224, 32, 60)

# (center x, head top y, start second, stage seconds, mirror leaves)
ROSES = [(36, 1, 0.3, 1.0, False), (25, 5, 5.6, 0.7, True), (47, 4, 6.4, 0.7, False)]


def grow_stem(img, cx: int, top: int, p: float, leaves: float, mirror: bool) -> int:
    """Draw the stem rising from the bottom to `top` + 8 (where the head sits) by fraction p. Returns its tip y."""
    base, tip_final = H - 1, top + 7
    tip = int(round(base - (base - tip_final) * p))
    for y in range(tip, H):
        put(img, cx, y, STEM if y % 3 else STEM_DARK)
    if leaves > 0:  # two leaves unfurl from the stem, one each side at different heights
        s = -1 if mirror else 1
        n = 1 + int(round(2 * leaves))
        for side, ly in ((s, tip_final + 4), (-s, tip_final + 6)):
            if ly >= H - 1:
                continue
            pts = [(1, 0), (2, -1), (3, -1), (2, 0)][:n + 1]
            for dx, dy in pts:
                put(img, cx + side * dx, ly + dy, LEAF if dy < 0 else LEAF_DARK)
    return tip


def render():
    bg = gradient([(0, (20, 4, 26)), (10, (40, 8, 40)), (15, (56, 12, 46))])
    heart_glow(bg, 36, 5, 22, (70, 14, 50), 0.6)  # steady glow behind the bouquet
    rng = random.Random(8)
    petals = [(rng.uniform(22, 52), rng.uniform(8.0, 13.5), rng.uniform(1.4, 2.4), rng.uniform(0, 6)) for _ in range(9)]
    glints = [(18, 3), (56, 2), (30, 0), (42, 0), (16, 10), (58, 9), (21, 13), (52, 14)]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        for cx, top, t0, step, mirror in ROSES:
            age = t - t0
            if age < 0:
                continue
            grow = 1.6 if cx == 36 else 1.0
            p = ease_out(min(1.0, age / grow))
            leaves = max(0.0, min(1.0, (age - grow * 0.6) / 0.8))
            grow_stem(img, cx, top, p, leaves, mirror)
            if age > grow:
                stage = min(len(ROSE_STAGES) - 1, int((age - grow) / step))
                if cx != 36:
                    stage = min(stage, 3)  # the side roses stop half open
                blit(img, ROSE_STAGES.img(stage), cx - 5, top)
        if t > 8.0:  # a few petals drift down
            for x0, t0, v, ph in petals:
                age = t - t0
                if 0 <= age:
                    y = -1 + age * v
                    if y < H:
                        x = x0 + 2 * math.sin(age * 1.6 + ph)
                        put(img, x, y, PETAL)
                        put(img, x + (1 if int(age * 3) % 2 else 0), y + 1, (170, 20, 46), 0.8)
        if t > 6.0:
            for i, (x, y) in enumerate(glints):
                twinkle(img, x, y, f, GOLD_LIGHT, 0.85, period=27, ph=i / len(glints))
        frames.append(img)
    return frames
