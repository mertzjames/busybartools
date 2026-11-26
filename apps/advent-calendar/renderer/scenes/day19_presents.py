"""Dec 19: Presents. Wrapped gifts tumble down one by one into a wobbly pile, then a bow bursts into confetti."""

import math

from busybar.canvas import FPS, ease_in, lerp, phase, put, sec, vgradient
from busybar.fx import SPARKLE, Particles

from common import LIGHTS, string_points, twinkle_lights

NAME = "day19"
TITLE = "Presents"
SECONDS = 8
KEYFRAMES = [(1.0, "The first present lands"), (3.0, "More and more"), (5.2, "A wobbly pile"),
             (6.6, "Confetti!")]

# x, final top y, w, h, body, ribbon, landing time
GIFTS = [
    (22, 8, 12, 7, (214, 30, 46), (255, 214, 92), 0.8),
    (36, 9, 10, 6, (40, 150, 80), (250, 250, 255), 1.6),
    (11, 10, 9, 5, (60, 110, 230), (255, 120, 200), 2.4),
    (25, 3, 7, 5, (250, 200, 50), (214, 30, 46), 3.2),
    (47, 11, 8, 4, (170, 70, 210), (255, 214, 92), 3.9),
    (38, 5, 6, 4, (250, 250, 255), (214, 30, 46), 4.6),
    (57, 9, 9, 6, (230, 110, 40), (40, 150, 80), 5.2),
]


def gift(img, x, y, w, h, body, ribbon, stripes=False):
    for yy in range(h):
        for xx in range(w):
            c = body
            if xx == 0 or yy == h - 1:
                c = tuple(int(v * 0.72) for v in body)
            if xx == w // 2 or yy == h // 2 - 1:
                c = ribbon
            put(img, x + xx, y + yy, c)
    # bow on top
    cx = x + w // 2
    for dx, dy in ((-2, -1), (-1, -1), (1, -1), (2, -1), (-1, -2), (1, -2), (0, -1)):
        put(img, cx + dx, y + dy, ribbon)


def render():
    bg = vgradient((14, 10, 40), (40, 20, 50))
    for x in range(72):
        put(bg, x, 15, (90, 50, 30))
    lights = string_points(0, 71, 0, 2.0, step=4)
    sp = Particles(seed=19)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        for x0, x1 in ((0, 71),):
            for x in range(x0, x1 + 1):
                tt = x / 71
                put(img, x, 0 + 2.0 * 4 * tt * (1 - tt), (40, 110, 60), 0.8)
        twinkle_lights(img, lights, f, rate=7)
        for i, (x, y, w, h, body, ribbon, t_land) in enumerate(GIFTS):
            if t < t_land - 0.5:
                continue
            k = ease_in(phase(f, sec(t_land - 0.5), sec(t_land)))
            yy = lerp(-h - 3, y, k)
            if t_land <= t < t_land + 0.3:  # squash-bounce
                yy = y - 1.5 * math.sin(math.pi * (t - t_land) / 0.3)
            wob = 0
            if 5.4 <= t < 6.4:
                wob = round(0.6 * math.sin((t - 5.4) * 14 + i))
            gift(img, round(x + wob), round(yy), w, h, body, ribbon)
            if abs(t - t_land) < 0.04:
                sp.emit(x + w / 2, y + h, 6, vx=(-1.0, 1.0), vy=(-0.5, -0.1), life=(5, 9), colors=((200, 200, 220),))
        if 6.4 <= t < 6.5:
            sp.emit(41, 4, 40, vx=(-2.2, 2.2), vy=(-1.8, 0.2), life=(14, 30), colors=LIGHTS + SPARKLE,
                    gravity=0.08)
        sp.step_draw(img)
        frames.append(img)
    return frames
