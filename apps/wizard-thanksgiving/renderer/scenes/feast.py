"""Scene 9 (playlist #9, the finale): The Feast Appears. The four students arrive at the long table, and a very old
wizard rises in the middle. He speaks four words (NITWIT! BLUBBER! ODDMENT! TWEAK!), raises his staff, and the dishes
appear one by one. The students gasp at each dish, then cheer under confetti.

See docs/DECISIONS.md D28 (the students), D29 (this scene) and D31 (the old wizard and the spoken words).
"""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, lerp, mix, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, Stars, puff, sparkle
from cast import (BLUE, CHEER, E_ARMS, E_CAST, E_POINT, E_STAND, ELDER, ELDER_HAND, ELDER_ORB, GREEN, SCARLET, STAND,
                  SURPRISE, WALK, YELLOW)
from sprites import CANDLE, GOBLET, GRAVY_BOAT, PIE_STAND, POTATOES, ROAST

NAME = "feast"
TITLE = "The Feast Appears"
SECONDS = 18
KEYFRAMES = [(2.4, "Four students arrive"), (5.0, "A very old wizard rises"), (6.2, "NITWIT!"), (7.3, "BLUBBER!"),
             (8.4, "ODDMENT!"), (9.6, "TWEAK!"), (11.5, "His staff conjures the feast"), (16.6, "Three cheers!")]

TABLE_Y = 12            # tabletop rows 12-13, front 14-15; everyone stands behind it (legs hidden)
DISH_BASE = 13          # bottom row of every dish (they sit on the tabletop)

# Students: (student, x, enter_from_x, walk_start, walk_end). Two on each side of the old wizard.
SEATS = [
    (SCARLET, 0, -10, 1.8, 3.4),
    (BLUE, 9, -11, 0.8, 3.0),
    (YELLOW, 50, 73, 0.8, 3.4),
    (GREEN, 62, 73, 2.0, 3.6),
]

# The old wizard: stands up behind the middle of the table
ELDER_X = 30
RISE = (4.0, 5.0)

# His speech: one word per beat, each with its own gesture and house colors (top, bottom, shadow)
WORDS = [
    (5.8, "NITWIT!", E_ARMS, ((255, 214, 120), (230, 40, 60), (70, 0, 10))),
    (6.9, "BLUBBER!", E_POINT, ((176, 204, 255), (60, 100, 240), (10, 20, 70))),
    (8.0, "ODDMENT!", E_ARMS, ((255, 244, 150), (245, 190, 30), (64, 64, 64))),
    (9.1, "TWEAK!", E_POINT, ((226, 236, 246), (40, 190, 100), (5, 50, 25))),
]
SPEECH_END = 10.6       # the last word holds until here
DIM = (5.4, 0.55)       # the hall dims from this time for the speech (to 45 % brightness)
TEXT_Y = 9              # words sit low, over the empty table, so his face stays visible above them
CAST_T = 10.6           # he raises the staff; the orb charges, then the dishes pop in

DISHES = [
    (11.2, [(ROAST, 19)]),
    (12.1, [(PIE_STAND, 43)]),
    (13.0, [(POTATOES, 56)]),
    (13.9, [(GRAVY_BOAT, 5)]),
    (14.8, [(GOBLET, 1), (GOBLET, 14), (GOBLET, 32), (GOBLET, 52), (GOBLET, 66)]),
]
STREAM = 0.6            # seconds the sparkles take from the orb to a dish
GASP = 0.35             # students gasp and hop as each dish lands
CHEER_T = 15.4          # the students cheer, the old wizard raises both arms; confetti until the end
CANDLES = [(5, 1.2), (24, 0.4), (47, 2.6), (58, 1.1)]


def table(img):
    rows = ((138, 84, 40), (112, 66, 30), (74, 42, 18), (54, 30, 12))  # tabletop (2 rows), then the front
    for x in range(72):
        for i, c in enumerate(rows):
            put(img, x, TABLE_Y + i, c)
    # empty plates in front of everyone
    for sx in [s[1] for s in SEATS] + [ELDER_X + 4]:
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
    return lerp(x0, x, k), k < 1, x0 > x


def current_word(t: float):
    for i, (t0, *_rest) in enumerate(WORDS):
        t1 = WORDS[i + 1][0] if i + 1 < len(WORDS) else SPEECH_END
        if t0 <= t < t1:
            return i, t - t0
    return None, 0.0


def elder_pose(t: float):
    """(frame, y) of the old wizard at time t, or None before he rises."""
    if t < RISE[0]:
        return None
    y = round(lerp(12, 0, ease_in_out(phase(int(t * FPS), sec(RISE[0]), sec(RISE[1])))))
    w, since = current_word(t)
    if w is not None:
        return WORDS[w][2], y - (1 if since < 0.2 else 0)
    if CAST_T <= t < CHEER_T:
        return E_CAST, y
    if t >= CHEER_T:
        return E_ARMS, y
    return E_STAND, y


def render():
    ceiling = vgradient((6, 8, 30), (24, 14, 42))
    stars = Stars(seed=28, n=18, ymax=9, period=FPS * 4, dim=0.1, bright=0.6)
    sp = Particles(seed=281)
    confetti = Particles(seed=282)
    house = [c for st, *_ in SEATS for c in st.house]
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
        gasp = any(t0 <= t < t0 + GASP for t0, _ in DISHES)
        for n, seat in enumerate(SEATS):
            pos = student_pos(t, seat)
            if pos is None:
                continue
            x, walking, from_right = pos
            spr = seat[0].sprite
            y = 15 - spr.h
            flip = False
            if walking:
                frame, flip = WALK[(f // 3) % 4], from_right
                y -= (f // 3) % 2  # a little bob, since the table hides the legs
            elif t >= CHEER_T:
                frame = CHEER
                y -= 1 if ((f // 4) + n) % 2 == 0 else 0
            elif gasp:
                frame, y = SURPRISE, y - 1
            elif t >= DISHES[0][0]:
                frame = SURPRISE  # mouths stay open in wonder once the feast starts appearing
            else:
                frame = STAND
            blit(img, spr.img(frame, flip=flip), x, y)

        # the old wizard rises behind the middle of the table
        pose = elder_pose(t)
        orb = None
        if pose:
            ef, ey = pose
            blit(img, ELDER.img(ef), ELDER_X, ey)
            orb = (ELDER_X + ELDER_ORB[ef][0], ey + ELDER_ORB[ef][1])
            add(img, *orb, (200, 240, 255), 0.5)
            if RISE[1] <= t < RISE[1] + 0.1:
                sp.emit(*orb, 8, vx=(-0.8, 0.8), vy=(-0.6, 0.8), life=(6, 12), colors=SPARKLE, glow=True)

        table(img)

        # dishes: sparkle streams from the staff's orb, a flash, then the dish pops in
        for d, (t0, items) in enumerate(DISHES):
            cx, cy = dish_center(items)
            if t0 - STREAM <= t < t0 and orb:
                k = phase(f, sec(t0 - STREAM), sec(t0))
                for j in range(4):
                    kk = max(0.0, k - j * 0.07)
                    x = lerp(orb[0], cx, kk)
                    y = lerp(orb[1], cy, kk) - 3 * math.sin(math.pi * kk)
                    add(img, x, y, (255, 245, 190), 1.0 - j * 0.22)
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

        # the orb charges before the first dish
        if orb and CAST_T <= t < DISHES[-1][0] + 0.3:
            k = phase(f, sec(CAST_T), sec(CAST_T + 0.6))
            puff(img, *orb, 0.6 + 1.6 * k + 0.4 * math.sin(t * 9), (210, 240, 255), 0.55)
            add(img, *orb, (255, 255, 255), 1.0)
            if f % 3 == 0:
                sp.emit(*orb, 1, vx=(-0.4, 0.4), vy=(-0.4, 0.3), life=(5, 9), colors=SPARKLE, glow=True)

        # the speech: the hall dims, his face stays lit above the words
        w, since = current_word(t)
        dim = DIM[1] * phase(f, sec(DIM[0]), sec(DIM[0] + 0.4)) * (1 - phase(f, sec(SPEECH_END), sec(SPEECH_END + 0.3)))
        if dim > 0:
            rect(img, 0, 0, 72, 16, (0, 0, 0), dim)
            if pose:
                ef, ey = pose
                keep = max(0, TEXT_Y - 1 - ey)  # rows of the sprite above the words
                if keep:
                    blit(img, ELDER.img(ef).crop((0, 0, ELDER.w, keep)), ELDER_X, ey)
        if w is not None:
            _, word, gesture, (top, bottom, shadow) = WORDS[w]
            flash = 1 - phase(f, sec(WORDS[w][0]), sec(WORDS[w][0] + 0.3))
            tw = text_width(word)
            x0 = (72 - tw) // 2
            y0 = TEXT_Y - (1 if since < 2 / FPS else 0)
            draw_text(img, word, x0, y0, None, gradient=(mix(top, (255, 255, 255), flash),
                                                         mix(bottom, (255, 255, 255), flash * 0.7)), shadow=shadow)
            if since < 1 / FPS:
                for ex in (x0 - 1, x0 + tw):
                    sp.emit(ex, y0 + 3, 6, vx=(-0.9, 0.9), vy=(-0.9, 0.6), life=(6, 12), colors=(top, bottom),
                            glow=True)
                hand = (ELDER_X + ELDER_HAND[0], pose[1] + ELDER_HAND[1]) if gesture == E_POINT else orb
                if hand:
                    sp.emit(*hand, 6, vx=(-0.8, 0.8), vy=(-0.8, 0.5), life=(6, 12), colors=SPARKLE, glow=True)
            if gesture == E_POINT and f % 3 == 0:
                sparkle(img, ELDER_X + ELDER_HAND[0], pose[1] + ELDER_HAND[1], f, 0.6)
        sp.step_draw(img)

        # closing beat: everyone cheers under house-colored confetti
        if t >= CHEER_T and f % 2 == 0:
            confetti.emit(1 + (f * 13) % 70, -1, 2, vx=(-0.25, 0.25), vy=(0.15, 0.4), life=(18, 30), colors=house)
        confetti.step_draw(img)
        frames.append(img)
    return frames
