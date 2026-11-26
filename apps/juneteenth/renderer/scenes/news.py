"""Scene: the news arrives (docs/DECISIONS.md D3, D4).

A rider in a blue coat gallops into a quiet Galveston street on a still morning and posts a notice on the board.
Townspeople come out and gather to read it; one by one they raise their arms. Then the street dims and the date
appears: JUNE 19, 1865, over GALVESTON TEXAS. The moment is about the news and hope, so there are no chains, no
violence and no likenesses: faceless figures in simple 1865 clothes.
"""

import math

from busybar.canvas import H, W, add, blit, ease_in_out, ease_out, phase, put, sec
from busybar.fx import puff

import jfx
from scenes.text import CORAL, NEWS_DATE, NEWS_PLACE, STARLIGHT, look
from sprites import HORSE

NAME = "news"
TITLE = "The News Arrives"
SECONDS = 16
KEYFRAMES = [(1.5, "A rider gallops into town"), (5.0, "The notice is posted"), (8.0, "People gather to read it"),
             (10.0, "Arms raised: the news is freedom"), (13.0, "JUNE 19, 1865 · GALVESTON TEXAS")]

GROUND = 13  # first street row
BOARD = (31, 5, 37, 10)  # x0, y0, x1, y1 of the notice board (on a post)
STOP_X = 17  # the horse's x when it stops


def backdrop():
    img = jfx.sky([(0, (96, 140, 206)), (8, (150, 184, 226)), (12, (196, 210, 228))])
    # a painted blue-grey storefront on the right, with a brown roof edge, trim and two warm windows
    for x in range(44, W):
        for y in range(1, GROUND):
            put(img, x, y, (92, 104, 130) if y % 3 else (78, 88, 112))
        put(img, x, 0, (138, 92, 56))
    for x0 in (49, 63):
        for y in range(5, 9):
            for x in range(x0, x0 + 4):
                put(img, x, y, (232, 196, 120) if y > 5 else (204, 160, 96))
        for y in range(5, 9):
            put(img, x0 + 2, y, (110, 70, 44))
    for x in range(55, 59):  # the door
        for y in range(5, GROUND):
            put(img, x, y, (110, 70, 44) if x in (55, 58) else (138, 92, 56))
    # a few low buildings far away on the left
    for x0, w, h in ((0, 6, 4), (7, 5, 3), (14, 7, 5)):
        for x in range(x0, x0 + w):
            for y in range(GROUND - h, GROUND):
                put(img, x, y, (120, 132, 158))
    # the street
    for x in range(W):
        for y in range(GROUND, H):
            put(img, x, y, (140, 122, 100) if (x * 3 + y) % 5 else (122, 106, 88))
    # the notice board on a post
    x0, y0, x1, y1 = BOARD
    for y in range(y1 + 1, GROUND + 1):
        put(img, 34, y, (110, 70, 44))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            edge = x in (x0, x1) or y in (y0, y1)
            put(img, x, y, (96, 60, 38) if edge else (132, 88, 54))
    return img


def notice(img, k: float) -> None:
    """The posted notice: white paper with grey lines of print, inside the board."""
    x0, y0, x1, y1 = BOARD
    for y in range(y0 + 1, y1):
        for x in range(x0 + 1, x1):
            c = (250, 248, 238)
            if y in (y0 + 3, y0 + 5, y0 + 7) and x0 + 1 < x < x1 - 1:
                c = (150, 146, 140)
            if y == y0 + 2 and x0 + 2 < x < x1 - 2:
                c = (90, 86, 84)
            put(img, x, y, c, k)


PEOPLE = [  # (start x, end x, arrive start s, raise s, skin, shirt, pants, style, hat, height, dress)
    (74, 40, 6.6, 9.4, jfx.SKIN[2], (70, 92, 170), None, "wrap", (232, 150, 50), 11, True),
    (78, 46, 7.0, 9.9, jfx.SKIN[0], (228, 220, 196), (96, 80, 66), "brim", (150, 110, 70), 11, False),
    (82, 52, 7.4, 10.3, jfx.SKIN[3], (190, 60, 64), None, "buns", None, 8, False),
    (86, 58, 7.8, 10.7, jfx.SKIN[1], (224, 204, 140), None, "wrap", (200, 70, 80), 11, True),
    (-6, 6, 7.2, 10.1, jfx.SKIN[4], (200, 190, 170), (80, 90, 120), "short", None, 11, False),
]


def render():
    bg = backdrop()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        s = f / 15
        # the rider: gallops in, slows and stops by the board
        run = ease_out(phase(f, 0, sec(4.5)))
        hx = -16 + (STOP_X + 16) * run
        moving = run < 0.98
        gait = 1 + (f // 3) % 2 if moving else 0
        bob = -1 if moving and gait == 1 else 0
        hy = GROUND - 7 + bob
        if moving:  # dust from the hooves
            for k in range(3):
                age = (f + k * 4) % 12
                puff(img, hx + 1 - age * 0.4, GROUND + 1 - age * 0.15, 0.6 + age * 0.12, (214, 186, 140),
                     0.5 * (1 - age / 12) * (1 - run))
        blit(img, HORSE.img(gait), hx, hy)
        reach = math.sin(math.pi * phase(f, sec(4.6), sec(6.6)))
        jfx.person(img, int(hx) + 3, hy + 6, jfx.SKIN[5], (54, 74, 150), None, style="brim", hat=(70, 64, 60),
                   arms=(0.06, 0.1 + 0.18 * reach), seated=True)
        # the notice goes up with a soft flash
        post = phase(f, sec(5.4), sec(5.9))
        if post > 0:
            notice(img, post)
            flash = 1 - phase(f, sec(5.9), sec(7.0))
            if flash > 0:
                jfx.glow(img, 34, 7.5, 7, (255, 240, 190), 0.35 * flash)
        # townspeople come out, gather at the board and raise their arms
        for i, (xa, xb, t0, up, skin, shirt, pants, style, hat, hgt, dress) in enumerate(PEOPLE):
            walk = phase(f, sec(t0), sec(t0 + 2.2))
            if walk <= 0:
                continue
            x = round(xa + (xb - xa) * ease_in_out(walk))
            legs = (1 + (f // 3 + i) % 2) if 0 < walk < 1 else 0
            lift = ease_in_out(phase(f, sec(up), sec(up + 0.6)))
            sway = 0.04 * math.sin(2 * math.pi * (f / 15 + i * 0.3)) if lift > 0.9 else 0.0
            arms = (0.42 * lift + sway, 0.42 * lift - sway)
            hop = -1 if (hgt < 11 and lift > 0.9 and (f // 4) % 3 == 0) else 0
            jfx.person(img, x, GROUND + 1 + hop, skin, shirt, pants, style=style, hat=hat, arms=arms, legs=legs,
                       height=hgt, dress=dress)
        # the date
        title = phase(f, sec(11.0), sec(12.2))
        if title > 0:
            jfx.dim_rect(img, 0, 0, W - 1, H - 1, 0.62 * title, feather=0)
            jfx.caption(img, NEWS_DATE, 1, look(STARLIGHT), alpha=title)
            jfx.caption(img, NEWS_PLACE, 10, look(CORAL), font="tiny", alpha=phase(f, sec(11.6), sec(12.8)))
            if s > 12.2:  # a slow glint across the date
                gx = 2 + (s - 12.2) * 26
                for y in range(1, 8):
                    add(img, gx + (7 - y) * 0.4, y, (255, 255, 230), 0.25)
        frames.append(img)
    return frames
