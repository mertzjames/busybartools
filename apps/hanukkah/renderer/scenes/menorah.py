"""Scene: tonight's menorah, in nine variants (0-8 candles; docs/DECISIONS.md D2, D3).

The menorah stands in a window at night. Tonight's candles stand in the rightmost cups (they are placed from right
to left). The shamash is lit first, lifted out of its raised holder, and lights the candles from left to right,
newest first. Then it goes back to its place and the room glows warmer with every flame.

Variant 0 is the resting menorah: no candles, the shamash unlit, stars twinkling and a glint along the brass. It is
what the show plays outside Hanukkah and on the first evening before sundown.
"""

from __future__ import annotations

import math
from types import SimpleNamespace

from busybar.canvas import FPS, add, clamp01, ease_in_out, lerp, mix, put, sec
from busybar.fx import Stars
from hfx import Menorah, warm_room

SECONDS = 16
FRAMES = sec(SECONDS)

WALL = (26, 16, 40)
SKY_TOP, SKY_BOTTOM = (6, 10, 38), (16, 30, 80)
FRAME = (78, 60, 104)
TABLE, TABLE_HI = (96, 58, 36), (128, 84, 52)
WIN_X0, WIN_X1, WIN_Y1 = 5, 66, 12

T_SHAMASH = 1.0  # the shamash is lit
T_LIFT = 2.2  # it leaves its holder
HOLD = 0.4  # seconds at each wick
IGNITE = 0.45  # a new flame grows over this long


def background():
    from busybar.canvas import new
    img = new(WALL)
    for y in range(16):
        for x in range(72):
            if WIN_X0 < x < WIN_X1 and y < WIN_Y1:
                put(img, x, y, mix(SKY_TOP, SKY_BOTTOM, y / WIN_Y1))
            elif (x in (WIN_X0, WIN_X1) and y <= WIN_Y1) or (WIN_X0 <= x <= WIN_X1 and y == WIN_Y1):
                put(img, x, y, FRAME)
            elif y == 13:
                put(img, x, y, TABLE_HI)
            elif y >= 14:
                put(img, x, y, TABLE)
    return img


def timeline(m: Menorah, n: int):
    """Shamash path keyframes and when each candle ignites.

    Returns (path, ignite) where path = [(t0, t1, (x0, y0), (x1, y1))] for the held shamash's wick end, and
    ignite = {position: start time}. The shamash is back in its holder after the last segment.
    """
    home = (m.cx, 3)
    path, ignite = [], {}
    t, at = T_LIFT, home
    for p in Menorah.lighting_order(n):
        x = m.pos_x(p)
        to = (x + 2, 5)
        dur = 0.3 + abs(to[0] - at[0]) * 0.028
        path.append((t, t + dur, at, to))
        t += dur
        ignite[p] = t + 0.08
        path.append((t, t + HOLD, to, to))
        t += HOLD
        at = to
    if n:
        dur = 0.3 + abs(home[0] - at[0]) * 0.028
        path.append((t, t + dur, at, home))
    return path, ignite


def shamash_at(path, t):
    for t0, t1, a, b in path:
        if t0 <= t < t1:
            u = ease_in_out((t - t0) / (t1 - t0))
            hop = 1.5 * math.sin(math.pi * u) if a != b else 0.0
            return lerp(a[0], b[0], u), lerp(a[1], b[1], u) - hop
    return None


def make(n: int):
    m = Menorah()
    path, ignite = timeline(m, n)
    done = path[-1][1] if path else 0.0
    if n:
        keys = [(0.6, "The menorah in the window"), (T_SHAMASH + 0.8, "The shamash is lit first"),
                (path[0][1] + 0.2, "Then it lights the newest candle"), (done + 0.6, "Back in its place"),
                (SECONDS - 2, f"Night {n}: {n} candle{'s' if n > 1 else ''} and the shamash")]
    else:
        keys = [(0.6, "The menorah rests in the window"), (5.0, "A glint along the brass"),
                (12.0, "Waiting for Hanukkah")]

    def render():
        bg = background()
        stars = Stars(seed=41, n=16, ymax=WIN_Y1, period=FPS * 4, color=(220, 226, 255), dim=0.1, bright=0.75)
        frames = []
        for f in range(FRAMES):
            t = f / FPS
            img = bg.copy()
            stars.draw(img, f)
            # keep stars inside the window
            for y in range(16):
                for x in range(72):
                    if not (WIN_X0 < x < WIN_X1 and y < WIN_Y1) and img.getpixel((x, y))[:3] != bg.getpixel((x, y))[:3]:
                        img.putpixel((x, y), bg.getpixel((x, y)))
            lit = {p: clamp01((t - t0) / IGNITE) for p, t0 in ignite.items() if t >= t0}
            sh_lit = clamp01((t - T_SHAMASH) / 0.6) if n else 0.0
            flames = sum(1 for v in lit.values() if v > 0) + (1 if sh_lit > 0 else 0)
            warm_room(img, flames / 9)
            glint = None
            if n == 0:
                for g0 in (3.5, 10.0):
                    if g0 <= t < g0 + 1.4:
                        glint = lerp(10, 64, (t - g0) / 1.4)
            m.draw_body(img, glint=glint)
            held = shamash_at(path, t) if n and T_LIFT <= t < done else None
            m.draw_candles(img, f, n, lit, not held, sh_lit)
            if held:
                m.held_shamash(img, held[0], held[1], f)
            if n == 0:
                # a faint gleam on the waiting shamash wick
                add(img, m.cx, 2, (120, 100, 70), 0.25 + 0.15 * math.sin(f * 0.2))
            frames.append(img)
        return frames

    title = "Tonight's Menorah" if n else "The Resting Menorah"
    return SimpleNamespace(NAME=f"menorah_{n}", TITLE=f"{title} ({n})" if n else title, SECONDS=SECONDS,
                           KEYFRAMES=keys, render=render, NIGHT=n)


VARIANTS = [make(n) for n in range(9)]
