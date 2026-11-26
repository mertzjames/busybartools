"""Scene: Sleigh Across the Moon. Two reindeer pull Santa's sleigh over a sleeping village and across the full
moon. A present drops neatly down a chimney (puff!), and the night answers: HO HO HO!"""

import math

from busybar.canvas import FPS, add, blit, ease_out, lerp, phase, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, Stars, puff, sparkle
from sprites import GIFT_SMALL, LEAD_DEER, REINDEER, SLEIGH
from xfx import Snow, draw_tree, full_moon, house, snow_ground

NAME = "sleigh_ride"
TITLE = "Sleigh Across the Moon"
SECONDS = 16
KEYFRAMES = [(1.0, "A quiet village on Christmas Eve"), (3.6, "Reindeer pull the sleigh into the sky"),
             (6.8, "Santa tosses a present back..."), (7.8, "...down the chimney, past the moon"),
             (11.0, "HO HO..."), (13.5, "HO HO HO!")]

MOON = (64, 5)
GROUND = 14
CHIMNEY_HOUSE = (40, 9)  # x, width
T_IN, T_OUT = 1.2, 9.0
TOSS_S = 1.0  # seconds the tossed present is in the air
WORDS = ["HO", "HO", "HO!"]


def lead_x(t: float) -> float:
    """x of the lead reindeer's nose."""
    return lerp(-2, 72 + 46, phase(round(t * FPS), sec(T_IN), sec(T_OUT)))


def path_y(x: float) -> float:
    """The team rides a gentle swell: low on the left, up over the moon on the right."""
    return 1.0 - 1.5 * math.sin(math.pi * min(1.0, max(0.0, (x + 20) / 110)))


def render():
    sky = vgradient((3, 5, 22), (14, 16, 44))
    stars = Stars(seed=41, n=26, ymax=10, period=FPS * 4)
    full_moon(sky, *MOON, r=5.5)
    snow_ground(sky, GROUND, seed=4)
    for cx in (5, 33, 68):
        draw_tree(sky, cx, GROUND - 6, height=5, trunk=1, snowy=True)
    house(sky, 10, 9, GROUND, 3, (130, 60, 50), (80, 36, 50))
    chim = house(sky, CHIMNEY_HOUSE[0], CHIMNEY_HOUSE[1], GROUND, 3, (90, 70, 110), (60, 40, 80),
                 chimney=CHIMNEY_HOUSE[0] + 6)
    house(sky, 53, 7, GROUND, 3, (60, 100, 70), (40, 60, 50), window_on=0.6)
    snow = Snow(seed=42, n=14, period=FPS * 6, laps=(1,), bright=(0.2, 0.5))
    sp = Particles(seed=43)
    smoke = Particles(seed=44)
    frames = []
    gift = None  # [x, y, vy]
    landed_at = None
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        stars.draw(img, f)
        snow.draw(img, f)

        # chimney smoke, plus a puff when the present lands
        if f % 6 == 0:
            smoke.emit(chim[0] + 0.5, chim[1] - 1, 1, vx=(-0.05, 0.12), vy=(-0.2, -0.12), life=(18, 28),
                       colors=((90, 90, 110),))
        smoke.step_draw(img)
        if landed_at is not None:
            k = phase(f, landed_at, landed_at + sec(1.2))
            if k < 1:
                puff(img, chim[0] + 0.5, chim[1] - 1 - 3 * k, 1 + 2.5 * k, (200, 200, 220), 0.8 * (1 - k))
            glow = max(0.0, 1 - (f - landed_at) / sec(2.0))
            wx = CHIMNEY_HOUSE[0] + CHIMNEY_HOUSE[1] // 2 - 1
            for dx in (0, 1):
                for dy in (1, 2):
                    add(img, wx + dx, GROUND - 3 + dy, (255, 230, 150), glow)

        # --- the team ---
        if T_IN <= t < T_OUT:
            X = lead_x(t)
            gal = f // 3
            ld = (X - 11, path_y(X - 11))
            d2 = (X - 23, path_y(X - 23) + 0.5)
            sl = (X - 41, path_y(X - 41) - 1)
            bob = [math.sin(t * 8 + k) * 0.7 for k in range(3)]
            # reins: sleigh front -> each deer's collar
            fx0, fy0 = sl[0] + 15, sl[1] + bob[2] + 5
            for tx, ty in ((d2[0] + 1, d2[1] + bob[1] + 4), (ld[0] + 1, ld[1] + bob[0] + 4)):
                n = int(abs(tx - fx0)) + 1
                for i in range(n):
                    u = i / max(1, n - 1)
                    put(img, lerp(fx0, tx, u), lerp(fy0, ty, u) + 0.6 * math.sin(math.pi * u), (170, 120, 50))
                fx0, fy0 = tx + 9, ty - 1
            blit(img, REINDEER.img(gal + 2), d2[0], d2[1] + bob[1])
            blit(img, LEAD_DEER.img(gal), ld[0], ld[1] + bob[0])
            blit(img, SLEIGH.img(1 if 6.0 < t < 7.6 and (f // 4) % 2 else 0), sl[0], sl[1] + bob[2])
            # stardust from the runners
            if f % 2 == 0:
                sp.emit(sl[0] + 1, sl[1] + bob[2] + 9, 1, vx=(-0.5, -0.1), vy=(0.0, 0.25), life=(8, 16),
                        colors=SPARKLE, glow=True)
            if gift is None and sl[0] + 3 >= chim[0] + 3:  # Santa tosses it back over his shoulder
                gift = [sl[0] + 3, sl[1] + bob[2] + 2, f]

        # --- the present falls straight down the chimney ---
        if gift is not None and landed_at is None:
            u = phase(f, gift[2], gift[2] + sec(TOSS_S))
            gx = lerp(gift[0], chim[0] + 0.5, u)
            gy = lerp(gift[1], chim[1] - 2, u) - 3 * math.sin(math.pi * u)
            blit(img, GIFT_SMALL.img(), gx - 1, gy)
            if u >= 1:
                landed_at = f
                sp.emit(chim[0] + 0.5, chim[1] - 1, 10, vx=(-0.8, 0.8), vy=(-1.0, -0.2), life=(8, 14),
                        colors=SPARKLE, glow=True)
        sp.step_draw(img)

        # --- HO HO HO! one word at a time, each with a little bounce ---
        if t >= 9.6:
            fade = 1 - phase(f, sec(15.4), sec(16.0))
            total = text_width(" ".join(WORDS))
            x = (72 - total) // 2 - 3
            for k, word in enumerate(WORDS):
                t0 = 9.8 + k * 0.9
                if t >= t0:
                    pop = ease_out(phase(f, sec(t0), sec(t0 + 0.35)))
                    y = 2 + round(3 * (1 - pop))
                    draw_text(img, word, x, y, None, gradient=((255, 255, 255), (255, 70, 70)),
                              shadow=(130, 10, 24), alpha=fade * min(1.0, pop * 2))
                    if t < t0 + 0.3:
                        sparkle(img, x + text_width(word) // 2, y - 1, f)
                x += text_width(word + " ") + 1
        frames.append(img)
    return frames
