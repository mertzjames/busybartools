"""Scene: The Toy Train. A toy train loops round the Christmas tree, in front and then behind it. The cat sitting
on the back track hops over it, then on the next lap pounces onto the last car and rides away. ALL ABOARD!"""

import math

from PIL import Image

from busybar.canvas import FPS, H, W, blit, ease_in_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import Particles, sparkle
from sprites import CAT, TRAIN_CAR, TRAIN_ENGINE
from xfx import BULBS, GOLD, SILVER, draw_tree, garland_path, present, tree_spots, tree_star

NAME = "toy_train"
TITLE = "The Toy Train"
SECONDS = 15
KEYFRAMES = [(2.4, "A toy train circles the tree"), (6.2, "Round the back: the cat hops over it"),
             (11.8, "The cat lies in wait"), (12.6, "Pounce!"), (14.0, "ALL ABOARD!")]

TREE_CX, TREE_TOP, TREE_H = 24, 1, 11
FRONT_RAIL, BACK_RAIL = 15, 12
CAR_GAP = 1
CAR_STEP = TRAIN_CAR.w + CAR_GAP
TRAIN_LEN = TRAIN_ENGINE.w + 2 * CAR_STEP
CAT_X = 48
CAT_Y = BACK_RAIL - CAT.h + 1
BACK_LAP = (5.0, 9.4)
FRONT_LAPS = [(0.3, 5.0), (9.6, 14.6)]
T_CROUCH, T_POUNCE, T_ABOARD = 11.0, 12.4, 12.9
CAPTION = "ALL ABOARD!"


def rail(img, y):
    for x in range(W):
        put(img, x, y, (120, 120, 140) if x % 3 else (110, 70, 40))


def front_x(t: float, lap) -> float:
    """Left edge of the engine on a front lap (running left to right)."""
    p = phase(round(t * FPS), sec(lap[0]), sec(lap[1]))
    return lerp(-TRAIN_ENGINE.w - 2, W + TRAIN_LEN - TRAIN_ENGINE.w + 2, p)


def back_x(t: float) -> float:
    """Left edge of the engine on the back lap (running right to left)."""
    p = phase(round(t * FPS), sec(BACK_LAP[0]), sec(BACK_LAP[1]))
    return lerp(W + 2, -TRAIN_LEN - 2, p)


def draw_train(img, x: float, rail_y: int, flip: bool, f: int, smoke: Particles) -> list[float]:
    """Engine plus two gift cars; returns the cars' left edges (nearest the engine first)."""
    wheel = (f // 2) % 2
    ey = rail_y - TRAIN_ENGINE.h + 1
    cy = rail_y - TRAIN_CAR.h + 1
    blit(img, TRAIN_ENGINE.img(wheel, flip=flip), x, ey)
    cars = []
    for k in range(2):
        cx = x - (k + 1) * CAR_STEP if not flip else x + TRAIN_ENGINE.w + CAR_GAP + k * CAR_STEP
        blit(img, TRAIN_CAR.img(wheel, flip=flip), cx, cy)
        put(img, (cx + TRAIN_CAR.w) if not flip else (cx - 1), rail_y - 1, (150, 150, 170))  # coupling
        cars.append(cx)
    stack = x + (7.5 if not flip else TRAIN_ENGINE.w - 8.5)
    if f % 4 == 0:
        smoke.emit(stack, ey - 1, 1, vx=(-0.5, -0.2) if not flip else (0.2, 0.5), vy=(-0.25, -0.1), life=(10, 16),
                   colors=((210, 210, 225), (170, 170, 190)))
    return cars


def render():
    bg = vgradient((18, 8, 26), (30, 12, 36))
    rect(bg, 0, BACK_RAIL + 1, W, 3, (96, 22, 34))  # rug between the rails
    rail(bg, BACK_RAIL)
    rail(bg, FRONT_RAIL)
    # the tree lives on its own layer so it can hide the train on the back lap
    tree = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_tree(tree, TREE_CX, TREE_TOP, TREE_H, trunk=1)
    present(tree, TREE_CX - 8, BACK_RAIL - 3, 5, 4, (214, 36, 46), GOLD)
    present(tree, TREE_CX + 4, BACK_RAIL - 2, 4, 3, (70, 110, 230), SILVER)
    lights = garland_path(TREE_CX, TREE_TOP, TREE_H)
    orns = tree_spots(TREE_CX, TREE_TOP, TREE_H, 6, seed=8)
    sp = Particles(seed=71)
    smoke = Particles(seed=72)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()

        # --- back lap, behind the tree ---
        bx = None
        if BACK_LAP[0] <= t < BACK_LAP[1]:
            bx = back_x(t)
            draw_train(img, bx, BACK_RAIL, True, f, smoke)
        img.alpha_composite(tree)
        for i, (lx, ly) in enumerate(lights):
            put(img, lx, ly, BULBS[i % len(BULBS)], 0.55 + 0.45 * math.sin(t * 4 + i * 1.3))
        for i, (ox, oy) in enumerate(orns):
            put(img, ox, oy, (GOLD, SILVER)[i % 2])
        tree_star(img, TREE_CX, TREE_TOP - 1, glow=0.6 + 0.4 * math.sin(t * 3))

        # --- the cat on the back track ---
        if t < T_POUNCE:
            if bx is not None and 0 < (CAT_X + 12 - bx) < TRAIN_LEN + 14:
                p = (CAT_X + 12 - bx) / (TRAIN_LEN + 14)  # hops straight up while the train passes beneath
                blit(img, CAT.img(4, flip=True), CAT_X, CAT_Y - 7 * math.sin(math.pi * p))
            elif t < T_CROUCH:
                blit(img, CAT.img(2, flip=True), CAT_X, CAT_Y)
            else:  # crouch and wiggle, waiting for the next lap
                blit(img, CAT.img(3), CAT_X + (1 if (f // 2) % 2 and t > T_POUNCE - 0.5 else 0), CAT_Y)

        # --- front laps ---
        cars = None
        for lap in FRONT_LAPS:
            if lap[0] <= t < lap[1]:
                cars = draw_train(img, front_x(t, lap), FRONT_RAIL, False, f, smoke)
        smoke.step_draw(img)

        # --- pounce onto the last car, then ride away ---
        if t >= T_POUNCE and cars is not None:
            last = cars[-1]
            ride_y = FRONT_RAIL - TRAIN_CAR.h + 1 - CAT.h + 1
            if t < T_ABOARD:
                p = phase(f, sec(T_POUNCE), sec(T_ABOARD))
                blit(img, CAT.img(4), lerp(CAT_X, last, p), lerp(CAT_Y, ride_y, p) - 4 * math.sin(math.pi * p))
            else:
                blit(img, CAT.img(2), last - 1, ride_y)
                if abs(t - T_ABOARD) < 0.5 / FPS:
                    sp.emit(last + 3, ride_y + 5, 8, vx=(-0.8, 0.8), vy=(-0.8, -0.2), life=(6, 10),
                            colors=((255, 240, 160), (255, 255, 255)), glow=True)
        sp.step_draw(img)

        if t >= 13.1:
            w = text_width(CAPTION, "tiny")
            x = 70 - w
            reveal = int(lerp(0, w + 1, ease_in_out(phase(f, sec(13.1), sec(13.6)))))
            fade = 1 - phase(f, sec(14.5), sec(15.0))
            draw_text(img, CAPTION, x, 0, None, font="tiny", gradient=((255, 244, 170), (255, 170, 50)),
                      shadow=(120, 20, 30), reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, 2, f, 0.8)
        frames.append(img)
    return frames
