"""Scene 2 (playlist #3): Broom Chase. A young wizard chases a winged golden pie over the castle."""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, lerp, phase, put, sec, vgradient
from busybar.font import draw_text
from busybar.fx import SPARKLE, Particles, Stars, puff, sparkle
from sprites import BROOM_RIDER_SG as BROOM_RIDER, GOLDEN_PIE

NAME = "broom_chase"
TITLE = "Broom Chase"
SECONDS = 16
KEYFRAMES = [(1.5, "Golden pie zips by"), (4.0, "Wizard on a broom gives chase"), (8.0, "Loop-the-loop"),
             (12.8, "Caught it!"), (14.5, "GOT IT!")]

LAG = 14            # frames the rider trails the pie
CATCH_T = 11.8      # pie stops here
PIE_REST = (52.0, 5.0)
HAND = (10, 3)      # pie offset relative to rider when caught (facing right)


def pie_path(t: float):
    x = 33 + 27 * math.sin(0.85 * t + 2.2) + 6 * math.sin(2.6 * t)
    y = 5.5 + 4.0 * math.sin(1.7 * t + 1.0) + 1.5 * math.sin(4.3 * t)
    return x, y


def pie_pos(t: float):
    if t < 0:
        return -12.0, 6.0
    if t < 0.9:  # enters from the left
        tx, ty = pie_path(0.9)
        k = t / 0.9
        return lerp(-10, tx, k), lerp(6, ty, k)
    if t < 10.6:
        return pie_path(t)
    sx, sy = pie_path(10.6)
    k = ease_in_out((t - 10.6) / (CATCH_T - 10.6))
    return lerp(sx, PIE_REST[0], k), lerp(sy, PIE_REST[1], k)


def castle(img):
    dark, lit = (14, 9, 26), (255, 196, 80)
    towers = [(44, 9, 4), (49, 6, 3), (53, 10, 6), (60, 7, 3), (64, 11, 5)]
    for x, top, w in towers:
        for xx in range(x, x + w):
            for yy in range(top, 16):
                put(img, xx, yy, dark)
        put(img, x + w // 2, top - 1, dark)
        put(img, x + w // 2, top - 2, dark)
    for x, y in ((50, 9), (55, 12), (61, 10), (45, 12), (66, 13)):
        put(img, x, y, lit, 0.8)


def render():
    sky = vgradient((14, 8, 44), (58, 24, 56))
    stars = Stars(seed=2, n=12, ymax=8, period=FPS * 4)
    clouds = [(10, 4, 2.2), (30, 2, 1.8), (55, 5, 2.5), (75, 3, 2.0)]
    sp = Particles(seed=22)
    trail = Particles(seed=23)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        stars.draw(img, f)
        for cx, cy, r in clouds:
            x = (cx - t * 2.5) % 92 - 10
            for dx, rr in ((0, r), (2.5, r * 0.8), (-2.5, r * 0.7)):
                puff(img, x + dx, cy, rr, (70, 46, 92), 0.55)
        castle(img)

        px, py = pie_pos(t)
        caught = t >= CATCH_T + LAG / FPS
        rt = t - LAG / FPS
        rx, ry = pie_pos(rt)
        vx = rx - pie_pos(rt - 0.1)[0]
        flip = vx < -0.05 and not caught
        # rider position: hand reaches toward the trailing point
        if flip:
            rider_x, rider_y = rx - (BROOM_RIDER.w - HAND[0]) + 4, ry - HAND[1] - 1
        else:
            rider_x, rider_y = rx - HAND[0], ry - HAND[1] - 1
        if caught:
            rider_x, rider_y = PIE_REST[0] - HAND[0], PIE_REST[1] - HAND[1] - 1
            rider_y += math.sin(t * 3) * 0.8
            px, py = rider_x + HAND[0], rider_y + HAND[1]

        if rt > 0.3:
            if f % 2 == 0 and not caught:
                tx = rider_x + (BROOM_RIDER.w if flip else 0)
                trail.emit(tx, rider_y + 9, 1, vx=(-0.1, 0.1), vy=(0.0, 0.1), life=(6, 12),
                           colors=((217, 178, 92), (160, 120, 60)))
            trail.step_draw(img)
            blit(img, BROOM_RIDER.img((f // 4) % 2, flip=flip), rider_x, rider_y)

        wing = (f // 2) % 2 if not caught else (f // 6) % 2
        blit(img, GOLDEN_PIE.img(wing), px - 3, py - 2)
        add(img, px, py, (255, 220, 120), 0.35)
        if not caught and f % 3 == 0:
            sp.emit(px, py, 1, vx=(-0.2, 0.2), vy=(-0.2, 0.2), life=(5, 9), colors=SPARKLE, glow=True)

        if caught and t < CATCH_T + LAG / FPS + 0.2:
            sp.emit(px, py, 14, vx=(-1.6, 1.6), vy=(-1.4, 1.0), life=(10, 20), colors=SPARKLE, glow=True)
        sp.step_draw(img)

        if t >= 13.4:
            k = phase(f, sec(13.4), sec(13.9))
            draw_text(img, "GOT IT!", 4, 4, None, gradient=((255, 236, 150), (235, 140, 25)),
                      shadow=(90, 38, 0), reveal=int(lerp(0, 40, k)))
            if f % 4 == 0:
                sparkle(img, 4 + (f * 7) % 33, 3 + (f % 3) * 4, f)
        frames.append(img)
    return frames
