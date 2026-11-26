"""Scene: the salute. At sunrise a service member in a plain dress uniform (white cap, white gloves, no insignia)
and an older veteran in a red cap and a green jacket stand by a flagpole. Both raise a hand in salute as the flag
goes up the pole, hold it while the flag reaches the top and catches the breeze, then lower it (docs/DECISIONS.md
D3, D10)."""

from busybar.canvas import ease_in_out, mix, phase, put, sec

import vfx
from vfx import (GOLD, HAIR_DARK, HAIR_SILVER, SKIN, U_DARK, U_NAVY, U_WHITE, blend_stops, draw_flag, glow, person,
                 pole, quant, sky)

NAME = "salute"
TITLE = "The Salute"
SECONDS = 14
KEYFRAMES = [(0.8, "Sunrise by the flagpole"), (2.6, "A salute"), (5.5, "The flag goes up"),
             (9.5, "The flag at the top"), (13.0, "At ease")]

SKY_A = [(0, (34, 50, 120)), (6, (110, 110, 170)), (12, (236, 160, 120)), (13, (250, 190, 130))]
SKY_B = [(0, (54, 90, 170)), (6, (140, 160, 210)), (12, (250, 200, 150)), (13, (255, 220, 160))]
GRASS = (54, 104, 58)
PATH = (176, 164, 140)

POLE_X = 50
FLAG_W = 13
RAISE = (sec(2.8), sec(8.6))
SALUTE_UP = (sec(1.6), sec(2.4))
SALUTE_DOWN = (sec(11.4), sec(12.2))


def ground(img) -> None:
    for x in range(72):
        put(img, x, 14, GRASS)
        put(img, x, 15, mix(GRASS, (0, 0, 0), 0.25))
    for x in range(POLE_X - 3, POLE_X + 4):  # a small stone base
        put(img, x, 14, PATH)
        put(img, x, 15, mix(PATH, (0, 0, 0), 0.2))


def salute_amount(f: int, delay: int = 0) -> float:
    up = phase(f, SALUTE_UP[0] + delay, SALUTE_UP[1] + delay)
    down = phase(f, SALUTE_DOWN[0] + delay, SALUTE_DOWN[1] + delay)
    return max(0.0, up - down)


def render():
    n = sec(SECONDS)
    cache = {}
    frames = []
    for f in range(n):
        light = quant(f / (n - 1), 24)
        if light not in cache:
            img = sky(blend_stops(SKY_A, SKY_B, light))
            glow(img, 62, 14, 12, (255, 200, 120), 0.35 + 0.35 * light, squash=1.6)
            ground(img)
            pole(img, POLE_X, 0, 14, color=(214, 206, 190))
            cache[light] = img
        img = cache[light].copy()
        # the flag: gathered at the foot of the pole, raised briskly, and flying in the breeze as it climbs
        p = ease_in_out(phase(f, *RAISE))
        y0 = int(8 - 7 * p + 0.5)
        width = int(3 + (FLAG_W - 3) * min(1.0, 2.5 * p) + 0.5)  # it unfurls as it leaves the ground
        draw_flag(img, POLE_X + 1, y0, width, 7, f / 16, amp=min(1.0, 2 * p), wavelength=15,
                  color=vfx.small_flag_color, shade_levels=2)
        # the service member: plain navy dress uniform, white peaked cap and gloves, gold buttons
        person(img, 24, 15, SKIN[2], U_NAVY, U_DARK, HAIR_DARK, hat="peaked", hat_c=U_WHITE, hat_c2=U_DARK,
               gloves=U_WHITE, buttons=GOLD, salute=salute_amount(f))
        # an older veteran in a red ball cap and a green jacket, saluting a moment later
        person(img, 34, 15, SKIN[0], (98, 128, 92), (84, 92, 130), HAIR_SILVER, hat="ball",
               hat_c=(196, 52, 60), hat_c2=(222, 84, 86), salute=salute_amount(f, sec(0.4)))
        frames.append(img)
    return frames
