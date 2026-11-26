"""Scene 7 (playlist #4): Cauldron Bake-Off. A young witch in school robes brews a pumpkin pie."""

import math
import random

from canvas import FPS, add, blit, ease_in_out, lerp, mix, new, phase, put, sec
from font import draw_text
from fx import FIRE, SPARKLE, Particles, bricks, puff, sparkle
from sprites import APPLE, CAULDRON, PIE, PUMPKIN, SPARK, WITCH_BB as WITCH

NAME = "cauldron"
TITLE = "Cauldron Bake-Off"
SECONDS = 16
KEYFRAMES = [(1.0, "A young witch at the cauldron"), (2.6, "Wand flick: in goes an apple"), (5.0, "...and a pumpkin"),
             (9.4, "POOF!"), (12.5, "A fresh pumpkin pie!")]

CX, CY = 34, 8          # cauldron top-left
WITCH_X, WITCH_Y = 14, 4
HAND = (WITCH_X + 9, WITCH_Y + 6)   # wand tip in the flick frame
MOUTH = (CX + 6, CY - 1)

GREEN = (60, 220, 80)
PINK = (230, 60, 110)
ORANGE = (255, 140, 30)
GOLD = (255, 214, 90)

TOSSES = [(2.0, APPLE, PINK), (4.5, PUMPKIN, ORANGE), (7.0, SPARK, GOLD)]


def liquid_color(t: float):
    c = GREEN
    for t0, _, col in TOSSES:
        if t >= t0 + 1.0:
            c = mix(c, col, phase(int(t * FPS), int((t0 + 1.0) * FPS), int((t0 + 1.6) * FPS)))
    return c


def render():
    rng = random.Random(4)
    bubbles = Particles(seed=41)
    sp = Particles(seed=42)
    fire = Particles(seed=43)
    wall = new()
    bricks(wall, (30, 22, 34), (14, 10, 18), y0=0, y1=15)
    for x in range(72):
        put(wall, x, 15, (22, 18, 22))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = wall.copy()
        # firelight glow on the wall
        glow = 0.10 + 0.04 * math.sin(t * 9) + 0.03 * math.sin(t * 23)
        for y in range(4, 16):
            for x in range(CX - 6, CX + 18):
                d = math.hypot((x - (CX + 6)) / 1.6, y - 15)
                add(img, x, y, (255, 120, 30), max(0.0, glow * (1 - d / 10)))

        # shake before the poof
        shake = 1 if 8.0 <= t < 9.0 and (f % 2 == 0) else 0
        # fire under the pot
        if f % 1 == 0:
            fire.emit(CX + rng.uniform(2, 10), 15, 2, vx=(-0.1, 0.1), vy=(-0.5, -0.25), life=(3, 6), colors=FIRE,
                      glow=True)
        fire.step_draw(img)
        blit(img, CAULDRON.img(), CX + shake, CY)
        # liquid surface
        lc = liquid_color(t)
        for x in range(CX + 1, CX + 11):
            put(img, x + shake, CY - 1, lc if (x + f // 3) % 4 else mix(lc, (255, 255, 255), 0.4))
        add(img, CX + 6, CY - 2, lc, 0.25)
        # bubbles (faster during the rumble)
        rate = 2 if 8.0 <= t < 9.2 else 5
        if t < 9.2 and f % rate == 0:
            bubbles.emit(CX + rng.uniform(2, 10), CY - 2, 1, vx=(-0.05, 0.05), vy=(-0.35, -0.2), life=(5, 11),
                         colors=(mix(lc, (255, 255, 255), 0.35), lc))
        bubbles.step_draw(img)

        # witch: wand-flick pose 0.3 s before each throw
        toss = any(t0 - 0.3 <= t < t0 + 0.2 for t0, _, _ in TOSSES)
        hop = -1 if (11.0 <= t < 15.5 and (f // 4) % 2 == 0) else 0
        blit(img, WITCH.img(1 if toss else 0), WITCH_X, WITCH_Y + hop)

        # ingredients arc from hand to the cauldron mouth
        for t0, spr, col in TOSSES:
            if t0 <= t < t0 + 1.0:
                k = (t - t0) / 1.0
                x = lerp(HAND[0], MOUTH[0], k)
                y = lerp(HAND[1], MOUTH[1], k) - 7 * math.sin(math.pi * k)
                blit(img, spr.img(), x - spr.w // 2, y - spr.h // 2)
            if t0 + 1.0 <= t < t0 + 1.15:
                sp.emit(MOUTH[0], MOUTH[1], 8, vx=(-1.0, 1.0), vy=(-1.4, -0.4), life=(6, 12),
                        colors=(col, mix(col, (255, 255, 255), 0.5)), gravity=0.15)

        # POOF at 9.2s: expanding cloud, then the pie floats up
        if 9.2 <= t < 11.6:
            k = phase(f, sec(9.2), sec(11.6))
            r = lerp(1, 7.5, ease_in_out(min(1, k * 2)))
            a = 1.0 if k < 0.5 else 1 - (k - 0.5) * 2
            for dx, dy, rr in ((0, 0, 1.0), (-4, 1, 0.75), (4, 1, 0.75), (-2, -2, 0.7), (3, -2, 0.7)):
                puff(img, MOUTH[0] + dx * r / 7, MOUTH[1] - 2 + dy * r / 7, r * rr, (225, 210, 245), a * 0.95)
            if k < 0.5:
                draw_text(img, "POOF!", 54, 2, (255, 255, 255), font="tiny", shadow=(80, 40, 120))
        if 9.2 <= t < 9.35:
            sp.emit(MOUTH[0], MOUTH[1] - 2, 18, vx=(-2, 2), vy=(-1.5, 0.8), life=(10, 20), colors=SPARKLE, glow=True)
        if t >= 10.4:
            k = ease_in_out(phase(f, sec(10.4), sec(12.0)))
            pie_y = lerp(CY - 2, 1, k) + (math.sin(t * 3) * 0.7 if k >= 1 else 0)
            blit(img, PIE.img(), MOUTH[0] - 3, pie_y)
            if f % 6 == 0:
                sp.emit(MOUTH[0] + rng.choice((-1, 0, 1)), pie_y - 1, 1, vx=(-0.05, 0.05), vy=(-0.25, -0.15),
                        life=(8, 12), colors=((200, 200, 210),))
            if t >= 12.0 and f % 5 == 0:
                sparkle(img, MOUTH[0] + rng.choice((-6, 6, -5, 5)), pie_y + rng.choice((0, 2)), f, 0.8)
        sp.step_draw(img)

        if t >= 12.4:
            draw_text(img, "PIE!", 54, 5, None, gradient=((255, 236, 150), (235, 140, 25)), shadow=(90, 38, 0),
                      reveal=int(lerp(0, 20, phase(f, sec(12.4), sec(12.8)))))
        frames.append(img)
    return frames
