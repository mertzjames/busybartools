"""Scene 6 (playlist #2): The Gravy Express. A steam train hauls the feast across the night hills."""

import math

from canvas import FPS, add, blit, ease_in, ease_out, lerp, new, phase, put, sec, vgradient
from font import draw_text
from fx import Stars, hills, moon, puff
from sprites import CAR, GRAVY_BOAT, LOCO, PUMPKIN, ROAST

NAME = "gravy_express"
TITLE = "The Gravy Express"
SECONDS = 14
KEYFRAMES = [(2.0, "Train rolls in"), (5.6, "Stops: TOOT TOOT!"), (7.0, "Steam everywhere"),
             (10.0, "Pulls away with the feast"), (13.0, "Steam drifts off")]

TRAIN_Y = 6     # loco top row (wheels on the rail at row 15)
CAR_Y = 11
STOP_X = 54     # loco left edge when stopped
LENGTH = 16 + 3 * 11


def front_x(t: float) -> float:
    """Loco left edge over time: decelerate in, stop, accelerate out."""
    if t < 5:
        return lerp(-16, STOP_X, ease_out(t / 5))
    if t < 8:
        return STOP_X
    return lerp(STOP_X, 72 + LENGTH, ease_in((t - 8) / 5))


def render():
    sky = vgradient((5, 6, 24), (16, 14, 40))
    stars = Stars(seed=6, n=16, ymax=9, period=FPS * 4)
    smoke = []  # [x, y, r, age, life]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        stars.draw(img, f)
        moon(img, 6, 1)
        hills(img, seed=3, base=12, amp=2.2, color=(10, 26, 20))
        hills(img, seed=8, base=14, amp=1.2, color=(16, 38, 26), freq=0.2)
        # rail + ties
        for x in range(72):
            put(img, x, 15, (70, 62, 58) if x % 3 else (110, 90, 60))

        fx_ = front_x(t)
        moving = 0.2 < t < 5 or 8.05 < t < 13.5
        wheel = int(fx_ / 2) % 2 if moving else 0
        x0 = int(round(fx_))
        # cars behind (to the left of) the loco, cargo on top
        cargo = [(ROAST, 0, -8), (PUMPKIN, 2, -5), (GRAVY_BOAT, 1, -4)]
        for i, (spr, dx, dy) in enumerate(cargo):
            cx = x0 - 11 * (i + 1)
            blit(img, spr.img(), cx + dx, CAR_Y + dy)
            blit(img, CAR.img(wheel), cx, CAR_Y)
            put(img, cx + 10, CAR_Y + 1, (60, 60, 70))  # coupling
        blit(img, LOCO.img(wheel, flip=True), x0, TRAIN_Y)
        # headlamp glow
        if -2 < x0 < 72:
            for k, a in ((16, 0.9), (17, 0.45), (18, 0.2)):
                add(img, x0 + k, TRAIN_Y + 5, (255, 230, 140), a)

        # smoke from the chimney (flipped sprite: chimney at columns 12-13)
        chim_x, chim_y = x0 + 12.5, TRAIN_Y - 1
        rate = 4 if moving else (2 if 5 < t < 7.5 else 6)
        if t < 13.4 and f % rate == 0 and -4 < chim_x < 76:
            big = 5.2 < t < 7.5
            smoke.append([chim_x, chim_y, 0.8, 0, 26 if big else 20, 1.6 if big else 1.0])
        alive = []
        for s in smoke:
            x, y, r, age, life, grow = s
            k = age / life
            puff(img, x, y, r, (175, 175, 190), 0.75 * (1 - k))
            drift = -0.55 if moving else -0.15
            s[0] += drift + 0.1 * math.sin(age * 0.5)
            s[1] -= 0.28
            s[2] = min(2.6 * grow, r + 0.09 * grow)
            s[3] += 1
            if s[3] < life:
                alive.append(s)
        smoke = alive

        if 5.3 <= t < 7.6:
            on = int((t - 5.3) * 3) % 2 == 0
            if on:
                draw_text(img, "TOOT!", 24, 1, (255, 255, 255), font="tiny", shadow=(40, 40, 60))
        frames.append(img)
    return frames
