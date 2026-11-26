"""Scene: spin the dreidel. A blue dreidel drops onto the table spinning fast, drifts, slows until its letters
(nun, gimel, hei, shin) pass by one by one, wobbles, and stops on gimel. The pot of gelt hops over to it.

The dreidel is drawn as a turning square prism: each column of the body shows whichever face is in front there,
with that face's letter squeezed by perspective, so the letters slide across as it turns (docs/DECISIONS.md D6).
"""

from __future__ import annotations

import math

from busybar.canvas import FPS, clamp01, ease_in, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.party import glitter
from hfx import (BLUE, BLUE_HI, BLUE_LO, GOLD_HI, LETTERS, SILVER, WHITE, coin, flat_coin, glow)

NAME = "dreidel"
TITLE = "Spin the Dreidel"
SECONDS = 15
KEYFRAMES = [(0.4, "A dreidel drops in, spinning"), (3.0, "Spinning fast"), (8.2, "Slowing: the letters pass by"),
             (10.4, "It stops on gimel"), (13.0, "Gimel: take the pot!")]

FACES = ("nun", "gimel", "hei", "shin")
TABLE_Y = 13
HALF = 3.5  # half-side of the square body, px
T_DROP, T_SLOW, T_STOP = 0.6, 7.0, 10.0
T_CAPTION, T_COINS = 10.6, 11.2
END_X = 14


def angle(t: float) -> float:
    """Total turn angle (radians); it stops with gimel (face 1) facing the viewer at T_STOP."""
    # angular speed: fast, then easing down to zero at T_STOP (integrated in closed form numerically)
    def speed(u):
        if u >= T_STOP:
            return 0.0
        return 2 * math.pi * (2.6 * (1 - u / T_STOP) ** 1.6 + 0.0)
    n = int(t * 30)
    a = 0.0
    for i in range(n):
        a += speed((i + 0.5) / 30) / 30
    a += speed(t) * (t - n / 30)
    return a


A_STOP = angle(T_STOP)


def theta(t: float) -> float:
    # offset so that face 1 (gimel) faces front (normal angle 0) when it stops: phi_i = theta + i*pi/2
    return angle(min(t, T_STOP)) - A_STOP - math.pi / 2


def body_x(t: float) -> float:
    if t < T_STOP:
        drift = 6 * math.sin(t * 0.9) + 3 * math.sin(t * 2.1)
        return lerp(36 + drift, END_X, ease_in(phase(t, T_SLOW - 2, T_STOP)))
    return END_X


def draw_dreidel(img, cx: float, base_y: int, th: float, spin: float, wob: float, wph: float) -> None:
    """cx: center column; base_y: row of the point; th: turn angle; spin: rev/s (blurs the letters)."""
    s2 = HALF * math.sqrt(2)
    letter_a = clamp01(1.4 - spin / 1.6)
    top = base_y - 12

    def shift(row):
        return wob * (base_y - row) / 12 * math.sin(wph)

    # faces in front, with their projected spans
    faces = []
    for i in range(4):
        phi = th + i * math.pi / 2
        if math.cos(phi) <= 0.02:
            continue
        xl, xr = s2 * math.sin(phi - math.pi / 4), s2 * math.sin(phi + math.pi / 4)
        faces.append((xl, xr, math.cos(phi), FACES[i], i))
    left = min(f[0] for f in faces)
    right = max(f[1] for f in faces)

    def face_at(dx):
        for xl, xr, light, name, i in faces:
            if xl <= dx < xr:
                return xl, xr, light, name, i
        return None

    for row in range(top, base_y + 1):
        r = row - top
        ox = shift(row)
        if r <= 1:  # handle
            put(img, cx - 0.5 + ox, row, SILVER if r == 0 else WHITE)
            put(img, cx + 0.5 + ox, row, SILVER)
            continue
        inset = {2: 1.0, 10: 1.0, 11: 2.4, 12: 3.4}.get(r, 0.0)
        for px in range(int(math.floor(cx + left - 1)), int(math.ceil(cx + right + 1)) + 1):
            dx = px + 0.5 - cx - ox
            if dx < left + inset or dx >= right - inset:
                continue
            fa = face_at(dx)
            if not fa:
                continue
            xl, xr, light, name, i = fa
            col = mix(BLUE_LO, BLUE_HI, 0.15 + 0.85 * light) if i % 2 == 0 else mix(BLUE_LO, BLUE, 0.2 + 0.8 * light)
            if r == 2:
                col = mix(col, SILVER, 0.35)
            if 4 <= r <= 8 and letter_a > 0:
                u = (dx - xl) / max(0.01, xr - xl)
                gx = int(u * 7) - 1  # a 1 px margin either side of the 5 px letter
                if 0 <= gx < 5 and LETTERS[name][r - 4][gx] == "#":
                    col = mix(col, GOLD_HI, letter_a * (0.5 + 0.5 * light))
            put(img, px, row, col)
    if spin > 1.2:  # speed lines
        for row in (4, 7):
            put(img, cx + right + 1.5, row, SILVER, 0.35)
            put(img, cx + left - 1.5, row + 1, SILVER, 0.35)


PILE = [(54, 12), (57, 12), (60, 12), (63, 12), (66, 12), (55, 11), (58, 11), (61, 11), (64, 11), (59, 10)]


def render():
    bg = vgradient((12, 14, 44), (24, 26, 70))
    for x in range(72):
        for y in range(TABLE_Y, 16):
            put(bg, x, y, (110, 70, 42) if y == TABLE_Y else (84, 52, 32))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # the pot of gelt; after the stop the coins hop one by one to the dreidel's side
        for k, (x, y) in enumerate(PILE):
            t0 = T_COINS + k * 0.22
            u = phase(f, sec(t0), sec(t0 + 0.6))
            if u <= 0:
                flat_coin(img, x, y, gold=k % 4 != 3)
                continue
            tx, ty = END_X + 9 + (k % 5) * 3 + (k // 5), TABLE_Y - 1 - (k // 5)
            hx, hy = lerp(x, tx, u), lerp(y, ty, u) - 3 * math.sin(math.pi * u)
            if u < 1:
                coin(img, hx, hy, spin=u * 2, r=1.4, gold=k % 4 != 3)
            else:
                flat_coin(img, tx, ty, gold=k % 4 != 3)
        glitter(img, 31, f, n=4, period=45, area=(53, 9, 68, 13), strength=0.6)

        # spin, wobble, drop
        th = theta(t)
        spin = (theta(t + 0.05) - th) / 0.05 / (2 * math.pi)
        wob = 0.0
        if t < T_STOP + 1.2:
            wob = 0.4 + 1.6 * phase(t, T_SLOW, T_STOP) * (1 - phase(t, T_STOP, T_STOP + 1.2))
        y = TABLE_Y - 1
        if t < T_DROP:
            y = int(lerp(-2, TABLE_Y - 1, ease_in(t / T_DROP)))
        cx = body_x(t)
        # a soft shadow under the point
        put(img, cx - 1, TABLE_Y, (60, 36, 22))
        put(img, cx, TABLE_Y, (60, 36, 22))
        draw_dreidel(img, cx, y, th, spin, wob, t * 9)

        if t >= T_CAPTION:
            # "GIMEL!", then "TAKE ALL" while the pot hops over (the rule of the game)
            out = 1 - phase(t, SECONDS - 0.5, SECONDS)
            swap = T_COINS + 0.9
            for word, t0, t1, grad in (("GIMEL!", T_CAPTION, swap, (GOLD_HI, (236, 170, 50))),
                                       ("TAKE ALL", swap, SECONDS, (WHITE, SILVER))):
                a = ease_out(phase(t, t0, t0 + 0.35)) * (1 - phase(t, t1 - 0.25, t1)) * out
                if a <= 0:
                    continue
                x = 47 - text_width(word) // 2
                draw_text(img, word, x, 1, None, gradient=grad, shadow=(20, 30, 90), alpha=a)
        frames.append(img)
    return frames
