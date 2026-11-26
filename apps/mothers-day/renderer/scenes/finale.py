"""Finale: a border of flowers blooms along the bottom while hearts float up, HAPPY appears, and then MOTHER'S DAY
with a shower of petals and hearts (docs/DECISIONS.md D3)."""

import math
import random

from busybar.canvas import H, W, ease_in_out, ease_out, phase, put, sec
from busybar.font import draw_text, text_width
from busybar.party import Confetti, glitter

import mfx
from scenes.text import BLUSH

NAME = "finale"
TITLE = "Happy Mother's Day"
SECONDS = 14
N = sec(SECONDS)
KEYFRAMES = [(1.2, "Flowers bloom along the bottom"), (4.2, "HAPPY"), (7.4, "Hearts rise"),
             (9.0, "MOTHER'S DAY"), (12.5, "Petals and hearts")]

HAPPY0, HAPPY1 = sec(2.8), sec(7.0)
MD0 = sec(7.6)
BURST = sec(8.2)
PETALS = (mfx.PINK, mfx.PINK_HI, mfx.LAVENDER_HI, mfx.YELLOW_HI, mfx.WHITE, mfx.CORAL)
KINDS = [("tulip", mfx.PINK), ("daisy", mfx.WHITE), ("rose", mfx.ROSE), ("tulip", mfx.YELLOW),
         ("lavender", None), ("tulip", mfx.LAVENDER), ("daisy", mfx.WHITE), ("rose", mfx.PINK_DK)]
TOP, BOTTOM, SHADOW = (tuple(BLUSH[k]) for k in ("top", "bottom", "shadow"))


def flowers():
    """The border: (column, head row, kind, color, bloom frame)."""
    out = []
    for i, x in enumerate(range(2, W, 5)):
        kind, color = KINDS[i % len(KINDS)]
        head = 11 + (i * 7 % 3 == 0)
        out.append((x, head, kind, color, sec(0.2) + abs(x - 35) * 2))
    return out


def caption(img, text: str, y: int, alpha: float, reveal=None) -> None:
    x = (W - text_width(text)) // 2
    draw_text(img, text, x, y, None, gradient=(TOP, BOTTOM), shadow=SHADOW, alpha=alpha, reveal=reveal)


def render():
    bg = mfx.sky([(0, (30, 8, 34)), (10, (54, 14, 50)), (15, (70, 20, 56))])
    mfx.glow(bg, 36, 6, 30, (60, 20, 50), 0.6, squash=2.5)
    border = flowers()
    rng = random.Random(9)
    floaters = [(rng.uniform(3, 69), rng.randrange(0, sec(3)), rng.choice((3, 3, 5)),
                 rng.choice((mfx.PINK, mfx.ROSE, mfx.PINK_DK, mfx.LAVENDER))) for _ in range(9)]
    bursts = [Confetti(seed=21, t0=BURST, x=2, y=14, n=26, vx=(0.6, 2.2), vy=(-2.2, -0.9), colors=PETALS),
              Confetti(seed=22, t0=BURST, x=69, y=14, n=26, vx=(-2.2, -0.6), vy=(-2.2, -0.9), colors=PETALS),
              Confetti(seed=23, t0=BURST + sec(2.4), x=36, y=-2, n=22, vx=(-1.6, 1.6), vy=(0.0, 0.4),
                       colors=PETALS, spread=30)]
    frames = []
    for f in range(N):
        img = bg.copy()
        # hearts float up from the flowers, behind the words
        for i, (x, t0, size, c) in enumerate(floaters):
            period = sec(4)
            if f < t0 + sec(0.6):
                continue
            age = ((f - t0) % period) / period
            y = 12 - 15 * age
            mfx.heart(img, x + math.sin(age * 7 + i) * 1.2, y, size, c, alpha=0.75 * min(1.0, (1 - age) * 3),
                      halo=(40, 10, 40))
        # the flower border
        for x, head, kind, color, t0 in border:
            g = phase(f, t0, t0 + sec(1.2))
            if g <= 0:
                continue
            top = int(round(16 - (16 - head) * ease_out(min(1.0, g * 1.5))))
            for y in range(top + 2, H):
                put(img, x, y, mfx.GREEN)
            if g > 0.4:
                put(img, x + 1, 14, mfx.GREEN_HI)
            mfx.bloom(img, kind, x, head, color, grow=max(0.0, (g - 0.4) / 0.6))
        for b in bursts:  # petals, behind the words
            b.draw(img, f)
        # the words: HAPPY wipes in and lifts away, then MOTHER'S DAY
        if HAPPY0 <= f < MD0:
            reveal = int(text_width("HAPPY") * ease_out(phase(f, HAPPY0, HAPPY0 + sec(0.8)))) + 1
            fade = 1 - ease_in_out(phase(f, HAPPY1, MD0))
            mfx.dim_rect(img, 20, 2, 51, 9, 0.5 * fade, 2)
            caption(img, "HAPPY", 3 - int(round(3 * (1 - fade))), fade, reveal)
        if f >= MD0:
            k = ease_in_out(phase(f, MD0, MD0 + sec(0.6)))
            mfx.dim_rect(img, 0, 2, 71, 10, 0.6 * k, 1)
            caption(img, "MOTHER'S DAY", 2 + int(round(k)), k)
            glitter(img, seed=31, f=f, n=12, period=sec(2), colors=(mfx.YELLOW_HI, mfx.WHITE),
                    area=(0, 0, W, 3), strength=0.8 * k)
        frames.append(img)
    return frames
