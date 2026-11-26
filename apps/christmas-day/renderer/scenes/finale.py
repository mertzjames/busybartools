"""Scene: Merry Christmas finale. Fireworks over the snowy village, then MERRY / CHRISTMAS bursts in, twinkling,
with fireworks still popping at the edges."""

import math
import random

from busybar.canvas import FPS, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import Particles, Stars, sparkle
from xfx import BLUE, GOLD, GREEN, RED, SILVER, Fireworks, Snow, draw_tree, house, snow_ground

NAME = "finale"
TITLE = "Merry Christmas"
SECONDS = 18
KEYFRAMES = [(1.6, "Fireworks over the village"), (4.4, "Red, green, gold and silver"), (7.6, "MERRY..."),
             (9.6, "...CHRISTMAS"), (13.0, "Twinkling, with fireworks at the edges")]

GROUND = 15
T_MERRY, T_XMAS = 6.8, 8.0
DIM = 0.72
WORDS = [("MERRY", 0, ((255, 140, 130), (215, 30, 44)), (90, 10, 24)),
         ("CHRISTMAS", 8, ((150, 250, 150), (30, 165, 64)), (10, 60, 26))]
PINK = (255, 120, 200)


def schedule():
    early = [(3, 14, 4, RED), (12, 50, 3, GREEN), (24, 30, 2, GOLD), (36, 62, 5, SILVER), (46, 8, 3, BLUE),
             (55, 40, 4, PINK), (66, 22, 3, GOLD), (74, 56, 2, RED), (84, 34, 5, GREEN), (92, 12, 2, SILVER)]
    # once the words are up, only at the edges
    edge = []
    rng = random.Random(97)
    f = sec(T_XMAS + 0.6)
    k = 0
    while f < sec(SECONDS - 1.6):
        x = rng.choice((3, 5, 66, 68))
        edge.append((f, x, rng.randint(2, 6), (RED, GREEN, GOLD, SILVER, BLUE, PINK)[k % 6]))
        f += rng.randint(9, 15)
        k += 1
    return early + edge


def render():
    bg = vgradient((3, 4, 20), (12, 14, 40))
    snow_ground(bg, GROUND, seed=9)
    for x, w, wall, roof in ((1, 7, (130, 60, 50), (80, 36, 50)), (16, 9, (90, 70, 110), (60, 40, 80)),
                             (33, 7, (60, 100, 70), (40, 60, 50)), (47, 9, (130, 90, 50), (90, 50, 40)),
                             (62, 8, (110, 50, 70), (70, 30, 50))):
        house(bg, x, w, GROUND, 2, wall, roof)
    for cx in (11, 28, 43, 58):
        draw_tree(bg, cx, GROUND - 5, height=5, trunk=0, snowy=True)
    stars = Stars(seed=91, n=24, ymax=9, period=FPS * 4)
    snow = Snow(seed=92, n=12, period=FPS * 6, laps=(1,), bright=(0.2, 0.5))
    fw = Fireworks(schedule(), seed=93)
    sp = Particles(seed=94)
    rng = random.Random(95)
    layers = []
    for word, y, grad, shadow in WORDS:
        x = (72 - text_width(word)) // 2
        layers.append((word, x, y, grad, shadow))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        snow.draw(img, f)
        # dim the village under the words so they read cleanly (fireworks stay bright on top)
        dim = DIM * phase(f, sec(T_MERRY - 0.5), sec(T_MERRY))
        if dim > 0:
            rect(img, 0, 0, 72, 16, (0, 0, 0), dim)
        fw.draw(img, f)
        fade = 1 - phase(f, sec(SECONDS - 0.8), sec(SECONDS))

        for (word, x, y, grad, shadow), t0 in zip(layers, (T_MERRY, T_XMAS)):
            if t < t0:
                continue
            w = text_width(word)
            pop = ease_out(phase(f, sec(t0), sec(t0 + 0.5)))
            reveal = int(lerp(0, w + 1, pop))
            draw_text(img, word, x, y, None, gradient=grad, shadow=shadow, reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, y + 3, f)
                sp.emit(x + reveal, y + 3, 2, vx=(-0.6, 0.2), vy=(-0.6, 0.6), life=(6, 12),
                        colors=((255, 255, 255), GOLD), glow=True)
        # twinkles dancing over the letters
        if t > T_XMAS + 0.8 and fade > 0.5:
            for _ in range(2):
                word, x, y, _, _ = layers[rng.randrange(2)]
                tx, ty = x + rng.randrange(text_width(word)), y + rng.randrange(7)
                if f % 2 == 0:
                    sp.emit(tx, ty, 1, life=(4, 8), colors=((255, 255, 255), (255, 240, 170)), glow=True)
        sp.step_draw(img)
        if fade < 1:
            rect(img, 0, 0, 72, 16, (0, 0, 0), 1 - fade)
        frames.append(img)
    return frames
