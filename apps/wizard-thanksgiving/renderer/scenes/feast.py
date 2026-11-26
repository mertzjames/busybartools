"""Scene 9 (playlist #9, the finale): The Feast Appears. All four students meet at the long table, raise their
wands together, and the dishes appear one by one: turkey, pie, potatoes, gravy, goblets. Then a cheer: DIG IN!

See docs/DECISIONS.md D28 (the cast) and D29 (this scene).
"""

import math

from busybar.canvas import FPS, add, blit, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, Stars, puff, sparkle
from cast import BLUE, CHEER, GREEN, SCARLET, STAND, WALK, WAND, YELLOW
from sprites import CANDLE, GOBLET, GRAVY_BOAT, PIE_STAND, POTATOES, ROAST

NAME = "feast"
TITLE = "The Feast Appears"
SECONDS = 18
KEYFRAMES = [(1.0, "An empty table in the Great Hall"), (3.0, "Four students arrive"),
             (6.4, "Wands up together"), (7.4, "The turkey appears"), (12.2, "...then pie, potatoes, gravy, goblets"),
             (13.5, "Three cheers!"), (16.5, "DIG IN!")]

TABLE_Y = 12            # tabletop rows 12-13, front 14-15; students stand behind it (legs hidden)
DISH_BASE = 13          # bottom row of every dish (they sit on the tabletop)

# Where each student stands (x) and how they walk in: (student, x, enter_from_x, walk_start, walk_end)
SEATS = [
    (SCARLET, 0, -10, 2.0, 3.6),
    (BLUE, 16, -11, 0.8, 3.2),
    (YELLOW, 46, 73, 0.8, 3.4),
    (GREEN, 63, 73, 2.0, 3.6),
]

# Dishes appear one at a time: (time, name, sprites at x positions)
DISHES = [
    (7.0, "turkey", [(ROAST, 34)]),
    (8.2, "pie", [(PIE_STAND, 9)]),
    (9.4, "potatoes", [(POTATOES, 27)]),
    (10.6, "gravy", [(GRAVY_BOAT, 55)]),
    (11.8, "goblets", [(GOBLET, 6), (GOBLET, 23), (GOBLET, 49), (GOBLET, 65)]),
]
STREAM = 0.7            # seconds the wand sparkles take to reach a dish
WANDS_UP = (5.6, 12.6)
CHEER_T = 12.8          # wands down, arms up, hop and cheer until the end
CAPTION_T = 15.0        # the hall dims and the caption wipes in
DIM = 0.55
HOP = 0.25              # everyone hops as each dish appears
CAPTION = "DIG IN!"
CANDLES = [(12, 0.4), (29, 1.7), (41, 2.6), (59, 1.1)]


def table(img):
    rows = ((138, 84, 40), (112, 66, 30), (74, 42, 18), (54, 30, 12))  # tabletop (2 rows), then the front
    for x in range(72):
        for i, c in enumerate(rows):
            put(img, x, TABLE_Y + i, c)
    # empty plates in front of each student
    for _, sx, *_ in SEATS:
        for dx in (2, 3, 4):
            put(img, sx + dx, TABLE_Y + 1, (226, 226, 234))


def dish_center(items):
    xs = [x + s.w / 2 for s, x in items]
    hs = [s.h for s, _ in items]
    return sum(xs) / len(xs), DISH_BASE + 1 - max(hs) / 2


def student_pos(t: float, seat):
    st, x, x0, t0, t1 = seat
    if t < t0:
        return None
    k = phase(int(t * FPS), sec(t0), sec(t1))
    walking = k < 1
    return lerp(x0, x, k), walking, x0 > x


def render():
    ceiling = vgradient((6, 8, 30), (24, 14, 42))
    stars = Stars(seed=28, n=18, ymax=9, period=FPS * 4, dim=0.1, bright=0.6)
    sp = Particles(seed=281)
    confetti = Particles(seed=282)
    house = [c for st, *_ in SEATS for c in st.house]
    cap_w = text_width(CAPTION)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = ceiling.copy()
        stars.draw(img, f)
        for i, (cx, ph) in enumerate(CANDLES):
            cy = round(math.sin(t * 1.6 + ph * 2) * 1.0) - 1
            blit(img, CANDLE.img((f // 3 + i) % 4), cx - 1, cy)
            add(img, cx, cy, (255, 180, 60), 0.25)
            add(img, cx, cy + 1, (255, 160, 40), 0.15)

        # students (drawn before the table, which hides their legs)
        tips = []
        for n, seat in enumerate(SEATS):
            pos = student_pos(t, seat)
            if pos is None:
                continue
            x, walking, from_right = pos
            st = seat[0]
            spr = st.sprite
            y = 15 - spr.h
            if walking:
                frame = WALK[(f // 3) % 4]
                y -= (f // 3) % 2  # a little bob, since the table hides the legs
                flip = from_right
            elif WANDS_UP[0] <= t < WANDS_UP[1]:
                frame, flip = WAND, False
                y -= 1 if any(t0 <= t < t0 + HOP for t0, _, _ in DISHES) else 0
            elif t >= CHEER_T:
                frame, flip = CHEER, False
                y -= 1 if ((f // 4) + n) % 2 == 0 else 0
            else:
                frame, flip = STAND, False
            blit(img, spr.img(frame, flip=flip), x, y)
            if frame in (WAND, CHEER):
                tips.append((x + st.tip[0], y + st.tip[1]))

        # light gathers at the wand tips
        if WANDS_UP[0] <= t < WANDS_UP[1]:
            k = phase(f, sec(WANDS_UP[0]), sec(WANDS_UP[0] + 0.8))
            for tx, ty in tips:
                add(img, tx, ty, (255, 250, 220), 0.6 + 0.4 * k)
                if k < 1 or f % 4 == 0:
                    sparkle(img, tx, ty, f, 0.35 + 0.35 * k)

        table(img)

        # dishes: sparkle streams from every wand, a flash, then the dish pops in
        for d, (t0, _, items) in enumerate(DISHES):
            cx, cy = dish_center(items)
            if t0 - STREAM <= t < t0 and tips:
                k = phase(f, sec(t0 - STREAM), sec(t0))
                for tx, ty in tips:
                    for j in range(3):
                        kk = max(0.0, k - j * 0.08)
                        x = lerp(tx, cx, kk)
                        y = lerp(ty, cy, kk) - 3 * math.sin(math.pi * kk)
                        add(img, x, y, (255, 245, 190), 0.9 - j * 0.25)
            if t >= t0:
                k = phase(f, sec(t0), sec(t0 + 0.3))
                pop = -1 if k < 1 else 0
                for spr, x in items:
                    blit(img, spr.img(), x, DISH_BASE + 1 - spr.h + pop, alpha=0.35 + 0.65 * k)
            if t0 <= t < t0 + 0.5:
                k = phase(f, sec(t0), sec(t0 + 0.5))
                for spr, x in items:
                    puff(img, x + spr.w / 2, DISH_BASE + 1 - spr.h / 2, 1.5 + 3 * k, (255, 248, 220),
                         0.7 * (1 - k))
            if t0 <= t < t0 + 1 / FPS:
                for spr, x in items:
                    sp.emit(x + spr.w / 2, DISH_BASE - spr.h / 2, 10 if len(items) == 1 else 5,
                            vx=(-1.2, 1.2), vy=(-1.3, 0.5), life=(8, 16), colors=SPARKLE, glow=True)
            if t >= t0 + 0.5 and f % 9 == d * 2:
                sparkle(img, cx + ((f * 5) % 7) - 3, cy - 1, f, 0.5)

        sp.step_draw(img)

        # caption: the hall dims so the text reads cleanly over the busy table
        if t >= CAPTION_T:
            rect(img, 0, 0, 72, 16, (0, 0, 0), DIM * phase(f, sec(CAPTION_T), sec(CAPTION_T + 0.4)))

        # cheer: house-colored confetti from above (kept bright over the dimmed hall)
        if t >= CHEER_T and f % 2 == 0:
            confetti.emit(1 + (f * 13) % 70, -1, 2, vx=(-0.25, 0.25), vy=(0.15, 0.4), life=(18, 30), colors=house)
        confetti.step_draw(img)

        if t >= CAPTION_T + 0.2:
            reveal = int(lerp(0, cap_w + 1, phase(f, sec(CAPTION_T + 0.2), sec(CAPTION_T + 0.8))))
            draw_text(img, CAPTION, (72 - cap_w) // 2, 0, None, gradient=((255, 244, 190), (250, 170, 40)),
                      shadow=(90, 38, 0), reveal=reveal)
            if f % 4 == 0:
                sparkle(img, (72 - cap_w) // 2 + (f * 7) % cap_w, (f % 3) * 3, f, 0.7)
        frames.append(img)
    return frames
