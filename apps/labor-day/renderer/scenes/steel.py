"""Scene: topping out. At sunrise a yellow tower crane lifts the last beam of a new building (painted white, with a
small flag and an evergreen on it, the ironworkers' topping-out tradition) into the steel frame. Two ironworkers in
hard hats guide it home, then one welds it in a shower of sparks (docs/DECISIONS.md D3, D4)."""

from __future__ import annotations

import math
import random

from busybar.canvas import H, W, add, ease_in_out, phase, put, sec
from busybar.fx import FIRE

import lfx

NAME = "steel"
TITLE = "Topping Out"
SECONDS = 14
KEYFRAMES = [(0.5, "Sunrise over the steel frame"), (3.5, "The crane lifts the last beam"),
             (6.6, "Ironworkers guide it home"), (9.0, "Welding it in"), (12.8, "Topped out at sunrise")]

DAWN = [(0, (34, 46, 120)), (6, (196, 110, 128)), (11, (255, 164, 96)), (15, (255, 206, 128))]
MORNING = [(0, (60, 100, 186)), (6, (230, 150, 140)), (11, (255, 196, 120)), (15, (255, 226, 160))]

FRAME = (50, 38, 70)  # the steel frame: a lit slate silhouette against the sunrise
RIM = (255, 196, 120)
COLS = (40, 48, 56, 64)
TOP = 7  # the top floor's beams (row)
MID = 11
BEAM_X = 48  # the last beam spans columns 48..56
BEAM_LEN = 9
BEAM_Y0, BEAM_Y1 = 13, TOP - 1
LIFT0, LIFT1 = sec(0.8), sec(6.4)
TROLLEY_X = 52
JIB = 0
WELDS = [(sec(8.6), sec(9.8)), (sec(10.3), sec(11.5)), (sec(12.0), sec(13.0))]
WELD_AT = (48, TOP - 1)


def skyline(img) -> None:
    """A low distant city along the bottom, dusky violet with a few warm windows."""
    rng = random.Random(7)
    x = 0
    while x < W:
        w, h = rng.randint(3, 7), rng.randint(1, 3)
        for xx in range(x, min(W, x + w)):
            for yy in range(H - h, H):
                put(img, xx, yy, (176, 110, 120))
        for yy in range(H - h + 1, H, 2):
            for xx in range(x + 1, min(W, x + w) - 1, 2):
                if rng.random() < 0.3:
                    put(img, xx, yy, (255, 230, 160), 0.8)
        x += w


def steel_frame(img) -> None:
    for x in COLS:
        for y in range(TOP, H):
            put(img, x, y, FRAME)
    for y in (TOP, MID):
        for x in range(COLS[0], COLS[-1] + 1):
            if y == TOP and BEAM_X < x < BEAM_X + BEAM_LEN - 1:
                continue  # the gap the last beam fills
            put(img, x, y, FRAME)
            add(img, x, y - 1, RIM, 0.25)  # warm rim light along the top edges
    for x in COLS:
        for y in range(TOP, H):
            add(img, x - 1, y, RIM, 0.12)  # the sun is to the left: rim light on the left edges


def render():
    frames = []
    sparks = lfx_particles()
    for f in range(sec(SECONDS)):
        k = lfx.quant(f / (sec(SECONDS) - 1), 40)
        img = lfx.sky(lfx.blend_stops(DAWN, MORNING, k))
        sun_y = 15.5 - 6 * k
        lfx.glow(img, 34, sun_y, 11, (255, 170, 80), 0.4, squash=1.2)
        lfx.disc(img, 34, sun_y, 2.7, (255, 248, 214))
        skyline(img)
        steel_frame(img)

        # the crane: trolley out over the gap during the lift, then back toward the mast
        back = ease_in_out(phase(f, sec(8.0), sec(10.5)))
        tx = round(TROLLEY_X - back * 18)
        lfx.tower_crane(img, 24, JIB, 12, 62)
        put(img, tx - 1, JIB + 1, lfx.STEEL)
        put(img, tx, JIB + 1, lfx.STEEL)
        put(img, tx + 1, JIB + 1, lfx.STEEL)

        lift = ease_in_out(phase(f, LIFT0, LIFT1))
        by = round(BEAM_Y0 + (BEAM_Y1 - BEAM_Y0) * lift)
        sway = 0
        if 0 < lift < 1:
            sway = round(1.2 * (1 - lift) * math.sin(f / 5))
        bx = BEAM_X + sway
        # the hook line: down to the beam during the lift, then the hook rises away
        if f < sec(7.6):
            hook_y = by - 3
            lfx.line(img, tx, JIB + 2, tx, hook_y, (200, 204, 216), 0.9)
            put(img, tx, hook_y, lfx.GOLD)
            lfx.line(img, tx, hook_y, bx + 1, by - 1, (190, 190, 200), 0.75)
            lfx.line(img, tx, hook_y, bx + BEAM_LEN - 2, by - 1, (190, 190, 200), 0.75)
        else:
            rise = ease_in_out(phase(f, sec(7.6), sec(8.6)))
            hook_y = round((BEAM_Y1 - 3) - rise * (BEAM_Y1 - 3 - (JIB + 3)))
            lfx.line(img, tx, JIB + 2, tx, hook_y, (200, 204, 216), 0.9)
            put(img, tx, hook_y, lfx.GOLD)
        lfx.ibeam(img, bx, by, BEAM_LEN, (226, 226, 236), hi=(255, 255, 255))
        lfx.tiny_flag(img, bx + 1, by - 4, f)
        lfx.evergreen(img, bx + 7, by - 1)

        # ironworkers on the top floor
        guiding = sec(4.6) <= f < sec(7.4)
        welding = any(a <= f < b for a, b in WELDS)
        lfx.ironworker(img, 44, TOP - 1, lfx.SAFETY, (70, 120, 240), lfx.SKIN[1],
                       arms="weld" if welding else ("up" if guiding else "down"))
        wave = f >= sec(12.6) and (f // 4) % 2 == 0
        lfx.ironworker(img, 60, TOP - 1, lfx.WHITE, (70, 120, 240), lfx.SKIN[3],
                       arms="up" if (guiding or wave) else "down")

        # welding sparks: a bright point at the joint, sparks that fall and fade
        if welding:
            for _ in range(3):
                sparks.emit(*WELD_AT)
            put(img, WELD_AT[0], WELD_AT[1], (255, 255, 255))
            add(img, WELD_AT[0] + 1, WELD_AT[1], (180, 210, 255), 0.6)
            add(img, WELD_AT[0], WELD_AT[1] - 1, (180, 210, 255), 0.4)
        sparks.draw(img)
        frames.append(img)
    return frames


class lfx_particles:
    """Welding sparks: ballistic, gravity, bright yellow to orange as they cool (seeded, frame-stepped)."""

    def __init__(self):
        self.rng = random.Random(41)
        self.items: list[list[float]] = []

    def emit(self, x: float, y: float) -> None:
        r = self.rng
        self.items.append([x, y, r.uniform(-0.9, 0.9), r.uniform(-0.9, 0.1), 0, r.randint(6, 12)])

    def draw(self, img) -> None:
        alive = []
        for p in self.items:
            x, y, vx, vy, age, life = p
            c = FIRE[min(3, int(4 * age / life))]
            put(img, x, y, c, 1.0 - (age / life) ** 2)
            p[0], p[1], p[3], p[4] = x + vx, y + vy, vy + 0.18, age + 1
            if p[4] < life and p[1] < H:
                alive.append(p)
        self.items = alive
