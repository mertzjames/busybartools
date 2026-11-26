"""Champagne Pop: the bottle shakes, the cork flies across the room, then two flutes clink. CHEERS!"""

import math

from busybar.canvas import FPS, add, blit, ease_in, ease_in_out, ease_out, lerp, phase, put, sec, vgradient
from busybar.font import draw_text
from busybar.fx import Particles
from party import GOLD, GOLD_LIGHT, SILVER, WHITE, string_lights
from sprites import BOTTLE, CORK

NAME = "champagne"
TITLE = "Champagne Pop"
SECONDS = 14
KEYFRAMES = [(1.0, "A bottle on ice"), (2.6, "Shake it up..."), (3.4, "POP!"), (4.4, "The cork flies"),
             (7.4, "Two flutes rise"), (10.1, "Clink!"), (12.5, "CHEERS!")]

BX, BY = 14, 4          # bottle top-left
NECK = (BX + 2, BY)     # cork sits just above
POP = sec(3.0)
FOAM = (255, 246, 214)
CHAMPAGNE = (255, 206, 70)


def flute(img, cx: int, top: int, level: float, f: int, seed: int) -> None:
    """A 5 px wide champagne flute: silver glass, gold wine `level` (0..1) full, rising bubbles."""
    glass = (190, 206, 236)
    bowl_h = 6
    for y in range(bowl_h):
        put(img, cx - 2, top + y, glass, 0.85)
        put(img, cx + 2, top + y, glass, 0.85)
    put(img, cx - 1, top + bowl_h, glass, 0.85)
    put(img, cx + 1, top + bowl_h, glass, 0.85)
    for y in range(top + bowl_h + 1, top + bowl_h + 3):
        put(img, cx, y, glass, 0.85)
    for dx in (-2, -1, 0, 1, 2):
        put(img, cx + dx, top + bowl_h + 3, glass)
    fill_rows = int(round(level * bowl_h))
    for y in range(top + bowl_h - fill_rows, top + bowl_h):
        for dx in (-1, 0, 1):
            put(img, cx + dx, y, CHAMPAGNE)
    put(img, cx, top + bowl_h, CHAMPAGNE)
    if fill_rows:
        for dx in (-1, 0, 1):
            put(img, cx + dx, top + bowl_h - fill_rows, FOAM)  # head of foam
        for k in range(2):  # bubbles
            y = top + bowl_h - 1 - ((f // 3 + k * 3 + seed) % max(1, fill_rows - 1))
            put(img, cx + (-1 if (k + seed) % 2 else 1), y, WHITE, 0.9)


def bucket(img, bx: int) -> None:
    """An ice bucket around the bottom of the bottle, with a few ice cubes."""
    for x in range(bx - 4, bx + 9):
        for y in range(13, 16):
            put(img, x, y, (150, 160, 190) if y == 13 else (96, 104, 138))
    for x in (bx - 3, bx + 7):
        put(img, x, 12, (220, 240, 255))
    put(img, bx + 6, 12, (180, 220, 255))


def render():
    bg = vgradient((22, 6, 22), (40, 12, 34))
    foam = Particles(seed=31)
    spark = Particles(seed=32)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        string_lights(img, f, y0=0, sag=1.5, offset=3)

        # --- bottle: slides away left after 5.6 s ---
        out = ease_in(phase(f, sec(5.6), sec(6.6)))
        bx = BX - 24 * out
        shake = 0
        if sec(1.6) <= f < POP:
            shake = (1, 0, -1, 0)[f % 4] if f > sec(2.2) else (1, -1)[(f // 2) % 2] * (f % 4 == 0)
        if out < 1:
            blit(img, BOTTLE.img(), bx + shake, BY)
            bucket(img, round(bx))
        # cork: on the bottle until POP, then a spinning arc up and across the room
        if f < POP:
            if out < 1:
                blit(img, CORK.img(0), bx + 2 + shake - 0.5, BY - 2)
            if f > sec(2.2):  # foam peeking out
                add(img, NECK[0] + shake, BY - 1, FOAM, 0.4)
        else:
            u = (f - POP) / FPS
            if u < 2.2:
                cx = NECK[0] + 30 * u
                cy = BY - 3 - 4 * u + 2.4 * u * u  # a flat arc that stays on screen
                blit(img, CORK.img((f // 2) % 2), cx, cy)
                spark.emit(cx, cy + 1, 1, vx=(-0.3, 0.0), vy=(-0.1, 0.2), life=(4, 8), colors=(GOLD_LIGHT, WHITE),
                           glow=True)
        # pop: flash and a foam fountain
        if POP <= f < POP + 3:
            k = 1 - (f - POP) / 3
            for dx in range(-3, 4):
                for dy in range(-3, 2):
                    if abs(dx) + abs(dy) <= 3:
                        add(img, NECK[0] + 0.5 + dx, BY - 1 + dy, WHITE, k * (1 - (abs(dx) + abs(dy)) / 4))
        if POP <= f < POP + sec(2.0):
            foam.emit(bx + NECK[0] - BX + 0.5, BY - 1, 3, vx=(-0.5, 0.9), vy=(-1.3, -0.5), life=(8, 16),
                      colors=(FOAM, CHAMPAGNE, WHITE), gravity=0.11)
        foam.step_draw(img)
        spark.step_draw(img)
        if POP + 2 <= f < sec(5.6):
            r = int(lerp(0, 30, phase(f, POP + 2, POP + 8)))
            draw_text(img, "POP!", 30, 6, None, gradient=(WHITE, GOLD), shadow=(110, 40, 0), reveal=r)

        # --- two flutes rise in, fill, and clink ---
        if t >= 6.4:
            rise = ease_out(phase(f, sec(6.4), sec(7.6)))
            meet = ease_in_out(phase(f, sec(8.6), sec(10.0)))
            part = ease_in_out(phase(f, sec(10.5), sec(11.4)))
            top = round(lerp(17, 5, rise))
            lx = round(lerp(26, 33, meet) - 21 * part)
            rx = round(lerp(46, 39, meet) + 21 * part)
            level = 0.35 + 0.65 * phase(f, sec(7.0), sec(8.4))
            flute(img, lx, top, level, f, 0)
            flute(img, rx, top, level, f, 1)
            clink = sec(10.0)
            if clink <= f < clink + 4:  # flash where the rims touch
                k = 1 - (f - clink) / 4
                for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, -1), (0, 1), (2, -1), (-2, -1), (0, -2)):
                    add(img, 36 + dx, top + dy, WHITE, k)
            if f == clink:
                spark.emit(36, top, 18, vx=(-1.4, 1.4), vy=(-1.4, 0.3), life=(8, 16),
                           colors=(GOLD_LIGHT, WHITE, CHAMPAGNE, SILVER), gravity=0.08, glow=True)
        if t >= 10.9:
            r = int(lerp(0, 40, phase(f, sec(10.9), sec(11.6))))
            fade = 1 - phase(f, sec(13.4), sec(14.0))
            draw_text(img, "CHEERS!", 18, 5, None, gradient=(WHITE, GOLD), shadow=(110, 40, 0), reveal=r, alpha=fade)
        frames.append(img)
    return frames
