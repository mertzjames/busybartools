"""Intro: the day's door on the calendar swings open onto a starry night. The app writes the date ("DEC 7") into the
opening at TEXT_MS (docs/DECISIONS.md D3), so one animation serves all 25 days."""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, new, phase, put, rect, sec, vgradient
from busybar.font import draw_text
from busybar.fx import SPARKLE, Particles, Stars
from PIL import Image

from common import glow

NAME = "door"
TITLE = "The door opens"
SECONDS = 3
TEXT_MS = 1400  # the date fades in once the doors are open
KEYFRAMES = [(0.2, "A wrapped door on the calendar"), (0.9, "The doors swing open"),
             (1.6, "The date appears in the opening")]

X0, X1, Y0, Y1 = 18, 53, 1, 14          # opening (inclusive)
PANEL_W = (X1 - X0 + 1) // 2             # 18
PANEL_H = Y1 - Y0 + 1                    # 14
WALL = ((150, 22, 34), (104, 12, 26))
TRIM = (226, 172, 64)
TRIM_DIM = (150, 100, 34)


def wall():
    img = vgradient(*WALL)
    # gold frame around the opening
    for x in range(X0 - 1, X1 + 2):
        put(img, x, Y0 - 1, TRIM)
        put(img, x, Y1 + 1, TRIM)
    for y in range(Y0 - 1, Y1 + 2):
        put(img, X0 - 1, y, TRIM)
        put(img, X1 + 1, y, TRIM)
    # little numbered doors on both sides of the calendar
    for (x, y, n) in ((1, 1, "3"), (9, 1, "8"), (1, 9, "5"), (9, 9, "1"),
                      (56, 1, "9"), (64, 1, "2"), (56, 9, "6"), (64, 9, "4")):
        rect(img, x, y, 7, 6, (34, 112, 60))
        for xx in range(x, x + 7):
            put(img, xx, y, (70, 160, 92))
        for yy in range(y, y + 6):
            put(img, x + 6, yy, (20, 76, 40))
        draw_text(img, n, x + 2, y + 1, (255, 226, 140), font="tiny")
    return img


def panel(left: bool) -> Image.Image:
    """One closed door panel, 18x14: green with a bevel, a ribbon and half a bow (the bow spans both panels)."""
    p = new((36, 128, 66))
    p = p.crop((0, 0, PANEL_W, PANEL_H))
    for x in range(PANEL_W):
        put(p, x, 0, (84, 184, 110))
        put(p, x, PANEL_H - 1, (18, 80, 42))
    for y in range(PANEL_H):
        put(p, 0 if left else PANEL_W - 1, y, (84, 184, 110) if left else (18, 80, 42))
    # inset panel line
    for x in range(3, PANEL_W - 3):
        put(p, x, 3, (24, 96, 50))
        put(p, x, PANEL_H - 4, (24, 96, 50))
    for y in range(3, PANEL_H - 3):
        put(p, 3, y, (24, 96, 50))
        put(p, PANEL_W - 4, y, (24, 96, 50))
    # horizontal ribbon
    for x in range(PANEL_W):
        put(p, x, 6, (226, 34, 48))
        put(p, x, 7, (170, 18, 34))
    # bow (mirrored on the right panel): loop next to the seam
    bow = ["..RRR", ".RrrR", "RRrRR", ".RrrR", "..RRR"] if left else ["RRR..", "RrrR.", "RRrRR", "RrrR.", "RRR.."]
    bx = PANEL_W - 5 if left else 0
    for dy, row in enumerate(bow):
        for dx, ch in enumerate(row):
            if ch != ".":
                put(p, bx + dx, 4 + dy, (240, 50, 64) if ch == "R" else (150, 14, 30))
    # gold knob
    put(p, PANEL_W - 3 if left else 2, 10, (255, 214, 92))
    return p


def render():
    base = wall()
    inside = vgradient((6, 10, 40), (22, 30, 80)).crop((0, 0, X1 - X0 + 1, PANEL_H))
    stars = Stars(seed=7, n=12, period=FPS * 3, dim=0.25, bright=0.95)
    lp, rp = panel(True), panel(False)
    sp = Particles(seed=3)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = base.copy()
        # the night inside the door
        win = inside.copy()
        stars.draw(win, f)
        blit(img, win, X0, Y0)
        k = ease_in_out(phase(f, sec(0.45), sec(1.2)))  # 0 closed -> 1 open
        if k > 0.0:
            glow(img, 36, 8, 10, (255, 200, 120), 0.25 * k * (1 - phase(f, sec(1.2), sec(2.4))))
        # panels swing toward the viewer: they narrow onto their hinges and darken
        w = max(2, int(round(PANEL_W * math.cos(k * math.pi * 0.47))))
        shade = 1.0 - 0.55 * k
        for p, hinge_left in ((lp, True), (rp, False)):
            q = p.resize((w, PANEL_H), Image.NEAREST)
            px = q.load()
            for yy in range(PANEL_H):
                for xx in range(w):
                    r, g, b, a = px[xx, yy]
                    px[xx, yy] = (int(r * shade), int(g * shade), int(b * shade), a)
            blit(img, q, X0 if hinge_left else X1 + 1 - w, Y0)
        if sec(1.0) <= f < sec(1.4):
            sp.emit(36, 8, 3, vx=(-1.6, 1.6), vy=(-1.0, 1.0), life=(8, 18), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        # a little twinkle on the trim while waiting
        if t < 0.45:
            add(img, X0 - 1 + (f * 5) % (X1 - X0 + 3), Y0 - 1, (255, 255, 220), 0.6)
        frames.append(img)
    return frames
