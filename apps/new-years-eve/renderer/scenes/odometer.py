"""Year Odometer: a gold counter rolls from the old year to the new one.

The digits are live: the app draws the current years into the four windows (OVERLAY), so the scene never shows a
baked-in year (docs/DECISIONS.md D10). The frame, the windows' shading, the glint and the confetti are baked here.
"""

import math

from busybar.canvas import FPS, add, phase, put, sec, vgradient
from live import ODO_WIN_H, ODO_WIN_W, ODO_WIN_Y, ODO_WINDOWS
from party import CONFETTI, GOLD_LIGHT, WHITE, Confetti, glitter

NAME = "odometer"
TITLE = "Year Odometer"
SECONDS = 12
KEYFRAMES = [(0.5, "The counter lights up"), (3.0, "The old year"), (6.1, "Rolling over..."),
             (6.6, "The new year!"), (9.0, "Confetti")]

ROLL = sec(6.0)
# [ms into the scene, roll progress]: the app redraws the digits at each event (screens.ts overlayAt)
OVERLAY = {"kind": "odometer", "events": [[900, 0], [6000, 0.5], [6400, 1]]}

FRAME = (214, 160, 44)
FRAME_HI = (255, 226, 120)
FRAME_LO = (150, 100, 20)
WINDOW = (30, 30, 52)


def counter(img, alpha: float) -> None:
    x0, x1 = ODO_WINDOWS[0] - 2, ODO_WINDOWS[-1] + ODO_WIN_W + 1
    y0, y1 = ODO_WIN_Y - 1, ODO_WIN_Y + ODO_WIN_H
    for x in range(x0, x1 + 1):
        put(img, x, y0, FRAME_HI, alpha)
        put(img, x, y1, FRAME_LO, alpha)
    for y in range(y0, y1 + 1):
        put(img, x0, y, FRAME, alpha)
        put(img, x0 + 1, y, FRAME_LO, alpha)
        put(img, x1, y, FRAME, alpha)
    for i, wx in enumerate(ODO_WINDOWS):
        for y in range(ODO_WIN_Y, ODO_WIN_Y + ODO_WIN_H):
            edge = min(y - ODO_WIN_Y, ODO_WIN_Y + ODO_WIN_H - 1 - y)
            shade = 0.55 + 0.15 * min(edge, 3)  # a drum: darker at the top and bottom
            for x in range(wx, wx + ODO_WIN_W):
                put(img, x, y, tuple(int(c * shade) for c in WINDOW), alpha)
        if i < len(ODO_WINDOWS) - 1:  # gold divider between windows
            for y in range(ODO_WIN_Y, ODO_WIN_Y + ODO_WIN_H):
                put(img, wx + ODO_WIN_W, y, FRAME_LO, alpha)
                put(img, wx + ODO_WIN_W + 1, y, FRAME, alpha)


def render():
    bg = vgradient((6, 6, 24), (18, 8, 36))
    left = Confetti(seed=61, t0=ROLL + 6, x=7, y=15, n=34, vx=(-0.3, 0.9), vy=(-2.4, -1.2), fall=(0.05, 0.1),
                    colors=CONFETTI, stagger=3)
    right = Confetti(seed=62, t0=ROLL + 6, x=65, y=15, n=34, vx=(-0.9, 0.3), vy=(-2.4, -1.2), fall=(0.05, 0.1),
                     colors=CONFETTI, stagger=3)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        glitter(img, 63, f, n=8, period=FPS * 4, strength=0.6, area=(0, 0, 12, 16))
        glitter(img, 64, f, n=8, period=FPS * 4, strength=0.6, area=(60, 0, 72, 16))
        counter(img, phase(f, 0, sec(0.8)))
        # a glint sweeps the frame as it rolls over
        if ROLL <= f < ROLL + sec(1.0):
            gx = 10 + (f - ROLL) / sec(1.0) * 60
            for y in range(16):
                for dx in range(2):
                    x = int(gx - y * 0.5 + dx)
                    if y in (0, 15) or not any(wx <= x < wx + ODO_WIN_W for wx in ODO_WINDOWS):
                        add(img, x, y, WHITE, 0.7)
        # little arrows either side, pulsing before the roll
        if sec(2.5) <= f < ROLL:
            k = 0.5 + 0.5 * math.sin(t * 8)
            for dy in range(3):
                put(img, 8 + dy, 6 + dy, GOLD_LIGHT, k)
                put(img, 8 + dy, 10 - dy, GOLD_LIGHT, k)
                put(img, 63 - dy, 6 + dy, GOLD_LIGHT, k)
                put(img, 63 - dy, 10 - dy, GOLD_LIGHT, k)
        left.draw(img, f)
        right.draw(img, f)
        frames.append(img)
    return frames
