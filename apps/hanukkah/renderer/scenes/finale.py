"""Scene: the blue-and-silver finale. Blue, silver and white fireworks over a starry night; a silver Star of David
traces itself and glitters, bursts, and HAPPY / HANUKKAH appears, with fireworks still popping at the edges.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, ease_out, lerp, phase, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import Stars
from busybar.party import Firework, glitter, line
from hfx import BLUE, BLUE_HI, GOLD_HI, SILVER, WHITE

NAME = "finale"
TITLE = "Happy Hanukkah"
SECONDS = 16
KEYFRAMES = [(1.8, "Blue and silver fireworks"), (4.0, "White and gold too"), (7.4, "A Star of David glitters"),
             (9.4, "It bursts"), (11.0, "HAPPY HANUKKAH"), (14.4, "Fireworks at the edges")]

T_STAR0, T_STAR1, T_BURST = 5.2, 7.0, 9.0
T_HAPPY, T_HANUKKAH = 9.6, 10.4
PALE_BLUE = (150, 196, 255)
WORDS = [("HAPPY", 0, (WHITE, PALE_BLUE)), ("HANUKKAH", 8, (PALE_BLUE, (70, 130, 245)))]
COLORS = [(BLUE_HI,), (SILVER,), (WHITE, BLUE_HI), (BLUE, SILVER), (GOLD_HI,)]


def star_lines(cx=36.0, cy=7.5, r=7.4):
    pts = lambda a0: [(cx + r * math.cos(math.radians(a0 + 120 * k)), cy + r * math.sin(math.radians(a0 + 120 * k)))
                      for k in range(3)]
    out = []
    for tri in (pts(-90), pts(90)):
        for k in range(3):
            out.append((tri[k], tri[(k + 1) % 3]))
    return out


def fireworks():
    rng = random.Random(131)
    out = []
    for i, (t, x, y) in enumerate([(0.3, 18, 5), (1.0, 52, 4), (1.7, 34, 6), (2.4, 10, 4), (2.9, 62, 6),
                                    (3.5, 26, 3), (4.1, 46, 5), (4.6, 36, 4)]):
        out.append(Firework(seed=200 + i, t0=sec(t), x=x, y=y, colors=COLORS[i % len(COLORS)],
                            kind=("peony", "ring", "willow", "peony", "palm")[i % 5], speed=rng.uniform(0.8, 1.1)))
    # the star's burst
    out.append(Firework(seed=250, t0=sec(T_BURST), x=36, y=7.5, colors=(WHITE, BLUE_HI, SILVER), kind="ring",
                        speed=1.3, rocket=False, life=20))
    # after the words: small ones at the edges
    t, k = T_HANUKKAH + 0.6, 0
    while t < SECONDS - 1.4:
        x = (4, 67, 6, 65)[k % 4] + rng.uniform(-1, 1)
        out.append(Firework(seed=300 + k, t0=sec(t), x=x, y=rng.uniform(4, 9), colors=COLORS[k % 4], n=14,
                            speed=0.45, life=20))
        t += rng.uniform(0.7, 1.1)
        k += 1
    return out


def render():
    bg = vgradient((2, 4, 22), (10, 16, 54))
    stars = Stars(seed=141, n=22, period=FPS * 4, color=(200, 214, 255), dim=0.08, bright=0.6)
    fw = fireworks()
    segs = star_lines()
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        if t >= T_HAPPY - 0.4:  # dim the sky under the words
            rect(img, 0, 0, 72, 16, (0, 0, 0), 0.5 * phase(t, T_HAPPY - 0.4, T_HAPPY))
        # the star traces itself, glitters, then bursts
        if T_STAR0 <= t < T_BURST + 0.15:
            u = phase(t, T_STAR0, T_STAR1)
            fade = 1 - phase(t, T_BURST - 0.1, T_BURST + 0.15)
            for i, ((x0, y0), (x1, y1)) in enumerate(segs):
                s = min(1.0, max(0.0, u * 6 - i * 0.85))
                if s > 0:
                    col = SILVER if i < 3 else BLUE_HI
                    line(img, x0, y0, lerp(x0, x1, s), lerp(y0, y1, s), col, fade)
            if u >= 1:
                glitter(img, 151, f, n=10, period=30, area=(28, 0, 45, 16), colors=(WHITE, BLUE_HI),
                        strength=0.9 * fade)
        for fwk in fw:
            fwk.draw(img, f)
        out = 1 - phase(t, SECONDS - 0.6, SECONDS)
        for (word, y, grad), t0 in zip(WORDS, (T_HAPPY, T_HANUKKAH)):
            if t < t0:
                continue
            w = text_width(word)
            reveal = int(lerp(0, w + 1, ease_out(phase(t, t0, t0 + 0.5))))
            draw_text(img, word, (72 - w) // 2, y, None, gradient=grad, shadow=(10, 20, 80), reveal=reveal,
                      alpha=out)
        if t > T_HANUKKAH + 0.5:
            glitter(img, 152, f, n=8, period=36, area=(12, 0, 60, 16), colors=(WHITE, SILVER),
                    strength=0.6 * out)
        frames.append(img)
    return frames
