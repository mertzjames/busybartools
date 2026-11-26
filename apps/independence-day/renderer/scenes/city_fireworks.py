"""Scene: fireworks over a city skyline on the river (docs/DECISIONS.md D3). Rockets climb from the far bank and burst
in red, white, blue and gold, one at a time and then in pairs; the bursts glint in the water. Then the big finale
volley: a dozen shells in under three seconds, crackling gold to finish, and the smoke drifts off."""

import math

from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.party import Firework, glitter

import jfx
from jfx import FW_BLUE, FW_GOLD, FW_RED, FW_WHITE

NAME = "city_fireworks"
TITLE = "Fireworks over the City"
SECONDS = 16
KEYFRAMES = [(0.8, "Dusk over the city"), (1.9, "The first shell bursts"), (4.4, "Red, white and blue"),
             (7.6, "A gold willow"), (11.0, "The finale volley"), (12.6, "Every color at once"),
             (14.8, "Smoke drifts off")]

WATER = 14  # rows 14-15 are the river
FINALE = sec(10.4)


def shells():
    s = [
        Firework(1, sec(1.6), 30, 5, (FW_RED,), "peony", n=26),
        Firework(2, sec(2.8), 52, 4, (FW_WHITE,), "ring"),
        Firework(3, sec(3.8), 16, 6, (FW_BLUE, FW_WHITE), "peony", n=28),
        Firework(4, sec(4.6), 44, 3, (FW_RED, FW_WHITE), "palm"),
        Firework(5, sec(5.6), 62, 5, (FW_BLUE,), "peony", n=24),
        Firework(6, sec(6.2), 24, 4, (FW_WHITE, FW_RED), "ring"),
        Firework(7, sec(7.2), 38, 4, None, "willow"),
        Firework(8, sec(8.4), 10, 5, (FW_RED,), "ring"),
        Firework(9, sec(8.7), 60, 4, (FW_BLUE, FW_WHITE), "peony", n=26),
        Firework(10, sec(9.6), 34, 6, (FW_GOLD, FW_RED), "palm"),
    ]
    # the finale: a dozen shells across the whole sky in under three seconds
    volley = [(8, 4, (FW_RED,), "peony"), (60, 5, (FW_BLUE,), "peony"), (34, 3, (FW_WHITE,), "ring"),
              (20, 6, (FW_BLUE, FW_WHITE), "peony"), (48, 4, (FW_RED, FW_WHITE), "peony"), (66, 3, None, "willow"),
              (4, 6, None, "willow"), (28, 5, (FW_RED,), "ring"), (42, 6, (FW_BLUE,), "ring"),
              (14, 3, (FW_WHITE, FW_RED), "palm"), (56, 3, (FW_WHITE, FW_BLUE), "palm"), (36, 5, (FW_GOLD,), "peony")]
    for i, (x, y, cols, kind) in enumerate(volley):
        s.append(Firework(40 + i, FINALE + (i * 31) % 40 + i // 3, x, y, cols, kind, n=24, rise=8))
    return s


def render():
    base = jfx.sky([(0, (6, 6, 30)), (7, (18, 12, 54)), (12, (70, 32, 84))])
    for x in range(W):  # the river: dark blue with a faint shimmer line
        put(base, x, WATER, (16, 22, 60))
        put(base, x, WATER + 1, (10, 14, 44))
    roofs = jfx.city(base, seed=7, base=WATER, color=(24, 26, 58), towers=4)
    for x in range(W):  # a lit promenade along the far bank
        if x % 6 == 2:
            put(base, x, WATER - 1, (255, 220, 150), 0.8)
    fws = shells()
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        sky = img.copy()
        for fw in fws:
            fw.draw(sky, f)
        # bursts only light the sky above the roofs; keep the buildings in front
        px, spx = img.load(), sky.load()
        for y in range(WATER):
            for x in range(W):
                if y < roofs[x] and y < WATER - 1:
                    px[x, y] = spx[x, y]
        if f >= FINALE + sec(2.2):  # the crackle: gold glints across the top, then the smoke haze
            k = phase(f, FINALE + sec(2.2), FINALE + sec(3.0)) * (1 - phase(f, sec(13.6), sec(15.4)))
            glitter(img, 5, f, n=22, period=20, colors=(FW_GOLD, (255, 240, 200)), ymax=8, strength=0.9 * k)
        haze = phase(f, FINALE + sec(1.5), FINALE + sec(3.5)) * (1 - phase(f, sec(13.8), sec(SECONDS)))
        if haze > 0:
            hq = math.floor(haze * 20 + 0.5) / 20  # quantized, so the slow fade costs few changed pixels
            for x in range(W):
                for y in range(5, 11):
                    if y < roofs[x]:
                        k = math.sin(math.pi * (y - 4) / 7) * (0.6 + 0.4 * math.sin(x * 0.31))
                        add(img, x, y, (54, 40, 70), 0.6 * hq * k)
        # the water: each column glows with the brightest light in the sky above it
        for x in range(W):
            light = max(sum(px[x, y][:3]) for y in range(0, WATER - 4)) / (3 * 255)
            if light > 0.25:
                lit = mix((16, 22, 60), (230, 200, 220), light * 0.5)
                put(img, x, WATER, lit)
                put(img, x, WATER + 1, mix((10, 14, 44), lit, 0.5) if (x + f // 3) % 2 else (10, 14, 44))
        frames.append(img)
    return frames
