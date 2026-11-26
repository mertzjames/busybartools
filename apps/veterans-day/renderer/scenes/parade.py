"""Scene: the parade. Veterans come down Main Street: a flag bearer in a plain dress uniform, three veterans of
different ages marching in step, an open car carrying two older veterans who wave, and an older veteran walking
behind it. Neighbours seen from behind wave small flags at the curb (docs/DECISIONS.md D3, D10)."""

import math

from busybar.canvas import W, mix, put, sec

import vfx
from scenes import main_street
from vfx import (GOLD, HAIR_BROWN, HAIR_DARK, HAIR_GREY, HAIR_SILVER, SKIN, U_DARK, U_NAVY, U_TAN, U_WHITE, draw_flag,
                 person)

U_OLIVE = (132, 148, 82)  # a lit olive: the darker kit olive vanished against the shopfronts

NAME = "parade"
TITLE = "The Parade"
SECONDS = 16
KEYFRAMES = [(1.5, "The flag leads the parade"), (5.0, "Veterans march in step"), (9.0, "An open car"),
             (12.0, "Older veterans wave"), (15.0, "Neighbours wave small flags")]

SPEED = 0.42  # px per frame
CAR = (190, 44, 54)
CAR_HI = (236, 92, 92)
CHROME = (214, 218, 226)
TIRE = (70, 72, 84)


def backdrop():
    """Main Street kept quiet behind the parade: a morning sky over plain, muted shopfronts with a few warm windows
    and an awning line, so the marchers in front read clearly."""
    img = vfx.sky(main_street.SKY_DAY)
    walls = [(0, 14, 6, (88, 62, 64)), (14, 13, 5, (92, 86, 80)), (27, 15, 6, (66, 80, 76)), (42, 13, 5, (90, 64, 62)),
             (55, 17, 6, (70, 74, 96))]
    for x0, w, top, wall in walls:
        vfx.fill(img, x0, top, x0 + w - 1, 13, wall)
        for x in range(x0, x0 + w):
            put(img, x, top, mix(wall, vfx.TRIM, 0.35))
            put(img, x, 9, mix(wall, (200, 80, 80) if (x // 2) % 2 else vfx.TRIM, 0.45))
        for x in range(x0 + 2, x0 + w - 2, 4):
            put(img, x, top + 2, mix(wall, vfx.WINDOW, 0.6))
            put(img, x + 1, top + 2, mix(wall, vfx.WINDOW, 0.6))
    for x in range(W):
        put(img, x, 14, mix(vfx.SIDEWALK, (0, 0, 0), 0.3))
        put(img, x, 15, vfx.STREET)
    return img


def car(img, x: int, f: int) -> None:
    """A vintage open car, 22 px long, driving right; its front at x + 21."""
    rows = [
        "........WW............",  # windshield frame (row 10)
        ".RRRRRRRRWRRRRRRRRRR..",  # 11
        "RRRRRRRRRRRRRRRRRRRRRR",  # 12
        "CCCCCCCCCCCCCCCCCCCCCC",  # 13 chrome trim
        "RRTTTRRRRRRRRRRRTTTRRR",  # 14
        "..TTT...........TTT...",  # 15
    ]
    pal = {"R": CAR, "W": CHROME, "C": CHROME, "T": TIRE}
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row):
            if ch in pal:
                put(img, x + dx, 10 + dy, pal[ch])
    for wx in (x + 2, x + 16):  # turning wheels: a lit spoke dot that circles the tire
        dx, dy = ((0, 0), (2, 0), (2, 1), (0, 1))[(f // 3) % 4]
        put(img, wx + dx, 14 + dy, CHROME)
    put(img, x + 21, 12, (255, 236, 170))  # headlamp
    for dx in range(1, 9):
        put(img, x + dx, 11, CAR_HI)  # the light catches the rear deck
    # small flags on the front fenders
    for fx in (x + 19,):
        for y in range(7, 12):
            put(img, fx, y, CHROME)
        draw_flag(img, fx - 1, 7, 4, 3, f / 10, amp=0.6, wavelength=5, color=vfx.tiny_flag_color, direction=-1)


def render():
    n = sec(SECONDS)
    base = backdrop()
    frames = []
    for f in range(n):
        img = base.copy()
        lead = int(-4 + SPEED * f)
        step = (f // 5) % 2
        sw = 0.05 * (1 - 2 * step)
        # the flag bearer: plain navy dress uniform, white peaked cap, white gloves; the flag flies back over him
        h = person(img, lead, 15, SKIN[2], U_NAVY, U_DARK, HAIR_DARK, hat="peaked", hat_c=U_WHITE,
                   hat_c2=U_DARK, gloves=U_WHITE, buttons=GOLD, arms=(0.0, 0.18), legs=step)
        hx, hy = h["r"]
        px = hx + 1
        for y in range(1, hy + 2):
            put(img, px, y, vfx.BRASS)
        put(img, px, 0, vfx.GOLD_LIGHT)
        # the flag flies ahead of him on the breeze (behind him it would hide his head: 16 rows leave no room above)
        draw_flag(img, px + 1, 1, 10, 7, f / 14, amp=1.0, wavelength=10, color=vfx.small_flag_color,
                  shade_levels=2)
        # three veterans marching in step: plain olive and tan uniforms, garrison caps
        marchers = [
            (-11, SKIN[0], U_OLIVE, HAIR_DARK, "short", (126, 140, 80)),
            (-17, SKIN[4], U_TAN, HAIR_BROWN, "bun", (206, 182, 128)),
            (-23, SKIN[1], U_OLIVE, HAIR_GREY, "short", (126, 140, 80)),
        ]
        for dx, skin, coat, hair, style, cap in marchers:
            person(img, lead + dx, 15, skin, coat, mix(coat, (40, 40, 60), 0.4), hair, style=style, hat="garrison",
                   hat_c=cap, arms=(sw, -sw), legs=step)
        # the open car with two older veterans waving
        cx = lead - 52
        wave = 0.40 + 0.06 * math.sin(2 * math.pi * f / 18)
        person(img, cx + 7, 16, SKIN[3], (120, 70, 140), U_DARK, HAIR_SILVER, style="short", seated=True,
               arms=(0.0, wave))
        person(img, cx + 13, 16, SKIN[1], (70, 110, 170), U_DARK, HAIR_SILVER, hat="ball", hat_c=(196, 52, 60),
               hat_c2=(220, 80, 84), seated=True, arms=(0.45 - 0.06 * math.sin(2 * math.pi * f / 18), 0.0))
        car(img, cx, f)
        # an older veteran walking behind, in a ball cap and a light jacket, waving
        person(img, lead - 60, 15, SKIN[2], (200, 184, 150), (80, 90, 130), HAIR_SILVER, hat="ball",
               hat_c=U_NAVY, hat_c2=(84, 104, 190), arms=(0.0, wave), legs=step)
        # neighbours at the curb, seen from behind, waving small flags
        for sx, hair, shirt, child, ph in ((4, HAIR_BROWN, (90, 160, 110), False, 0.0),
                                           (10, vfx.HAIR_BLOND, (230, 120, 90), True, 0.3),
                                           (66, HAIR_DARK, (110, 140, 220), False, 0.6)):
            curb(img, sx, hair, shirt, child, f, ph)
        frames.append(img)
    return frames


def curb(img, x: int, hair, shirt, child: bool, f: int, ph: float) -> None:
    """A neighbour at the curb seen from behind: the back of the head and the shoulders, one arm up with a flag."""
    top = 12 if child else 10
    for dy in range(3):
        for dx in (-1, 0, 1):
            if dy == 2 and dx != 0:
                continue
            put(img, x + dx, top + dy, hair)
    for y in range(top + 3, 16):
        for dx in (-2, -1, 0, 1, 2):
            put(img, x + dx, y, shirt)
    lift = int(math.floor(0.5 + 0.5 * math.sin(2 * math.pi * (f / 20 + ph))))
    ax = x + 2
    for y in range(top - 1 - lift, top + 3):
        put(img, ax, y, mix(shirt, (255, 255, 255), 0.1) if y > top else SKIN[3])
    sy = top - 4 - lift
    for y in range(sy, top - 1 - lift):
        put(img, ax, y, (200, 180, 140))
    draw_flag(img, ax + 1, sy, 4, 3, f / 8 + ph, amp=0.6, wavelength=5, color=vfx.tiny_flag_color)
