"""Scene: Stockings by the Fire. A cat pads up to the mantel and bats at a stocking, once, twice... it drops,
the cat dives in, and pops its head out of the cuff. STUFFED!"""

import math

from busybar.canvas import FPS, add, blit, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, bricks, sparkle
from sprites import CANDY_CANE, CAT, CAT_HEAD, STOCKING, STOCKING_FLAT
from xfx import BULBS, Snow, fire

NAME = "stockings"
TITLE = "Stockings by the Fire"
SECONDS = 16
KEYFRAMES = [(1.8, "The fire crackles; a cat wanders in"), (5.2, "Bat..."), (6.6, "...bat..."),
             (8.3, "...and down it comes"), (10.4, "The cat dives in"), (13.5, "STUFFED!")]

FLOOR = 14
MANTEL_Y = 4
FP_X0, FP_X1 = 2, 33  # chimney breast
BOX_X0, BOX_X1 = 12, 23  # firebox
HANG = [(2, "#2E9A48", "#F4F4FF"), (6, "#D8202A", "#FFD84A"), (23, "#E04A8A", "#F4F4FF"), (30, "#3A6AD0", "#F4F4FF")]
TARGET = 3
CAT_Y = FLOOR - CAT.h
CAT_SIT_X = 31
T_WALK = 3.4
BATS = (5.0, 6.4, 7.8)
T_FALL, T_LAND = 7.95, 8.45
FLAT_X, FLAT_Y = 27, FLOOR - STOCKING_FLAT.h
T_LEAP, T_IN = 9.4, 9.9
T_PEEK = 11.6
WINDOW = (51, 7, 14, 6)  # x, y, w, h
CAPTION = "STUFFED!"


def stockings():
    return [STOCKING.recolor(f"stocking{i}", C=c, S=s) for i, (_, c, s) in enumerate(HANG)]


def draw_room(img):
    rect(img, 0, FLOOR, 72, 2, (96, 56, 30))
    for x in range(2, 72, 7):
        put(img, x, FLOOR + 1, (70, 40, 22))
    # window with a snowy night outside
    wx, wy, ww, wh = WINDOW
    rect(img, wx - 1, wy - 1, ww + 2, wh + 2, (130, 90, 50))
    rect(img, wx, wy, ww, wh, (8, 14, 40))
    for xx in range(wx, wx + ww):
        put(img, xx, wy + wh - 1, (200, 210, 240))
    rect(img, wx + ww // 2, wy, 1, wh, (130, 90, 50))
    rect(img, wx, wy + wh // 2 - 1, ww, 1, (130, 90, 50))
    # chimney breast, firebox, mantel
    tmp = img.copy()
    bricks(tmp, (150, 52, 42), (96, 40, 36), y0=MANTEL_Y + 1, y1=FLOOR, bw=5, bh=2)
    img.paste(tmp.crop((FP_X0, MANTEL_Y + 1, FP_X1 + 1, FLOOR)), (FP_X0, MANTEL_Y + 1))
    rect(img, BOX_X0, 8, BOX_X1 - BOX_X0 + 1, FLOOR - 8, (22, 8, 6))
    put(img, BOX_X0, 8, (150, 52, 42))
    put(img, BOX_X1, 8, (150, 52, 42))
    rect(img, BOX_X0 + 2, FLOOR - 1, BOX_X1 - BOX_X0 - 3, 1, (110, 64, 30))
    rect(img, FP_X0 - 2, MANTEL_Y, FP_X1 - FP_X0 + 5, 1, (170, 110, 60))
    # garland on the mantel, candles at the ends
    for x in range(FP_X0 - 1, FP_X1 + 2):
        put(img, x, MANTEL_Y - 1, (30, 120, 50) if x % 2 else (20, 96, 40))
    for cx in (FP_X0, FP_X1):
        put(img, cx, MANTEL_Y - 2, (240, 236, 220))
        put(img, cx, MANTEL_Y - 3, (240, 236, 220))


def render():
    bg = vgradient((5, 20, 12), (10, 30, 18))
    draw_room(bg)
    socks = stockings()
    flat = STOCKING_FLAT.recolor("flat", C=HANG[TARGET][1], S=HANG[TARGET][2])
    wx, wy, ww, wh = WINDOW
    snow = Snow(seed=51, n=10, period=FPS * 5, laps=(1,), bright=(0.5, 0.9), xmin=wx, xmax=wx + ww)
    sp = Particles(seed=52)
    frames = []
    swing_amp, swing_t0 = 0.0, 0.0
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # snow only inside the window panes
        snow.draw(img, f, skip=lambda x, y: not (wy <= y < wy + wh - 1) or x == wx + ww // 2 or y == wy + wh // 2 - 1)
        fire(img, f, BOX_X0 + 2, BOX_X1 - 2, FLOOR - 2, 4)
        for k, cx in enumerate((FP_X0, FP_X1)):  # candle flames
            put(img, cx, MANTEL_Y - 4, (255, 210, 90) if (f // 3 + k) % 4 else (255, 160, 60))
            add(img, cx, MANTEL_Y - 5, (255, 180, 60), 0.3)
        for i, x in enumerate(range(FP_X0, FP_X1 + 1, 3)):  # garland bulbs
            on = (f // 8 + i) % 3 != 0
            put(img, x, MANTEL_Y - 1, BULBS[i % len(BULBS)], 1.0 if on else 0.35)
        # warm glow from the fire onto the floor
        for x in range(BOX_X0 - 6, BOX_X1 + 7):
            add(img, x, FLOOR, (255, 140, 40), 0.18 * (0.8 + 0.2 * math.sin(f * 0.7 + x)))

        # --- the stockings; the target one swings when batted ---
        for b in BATS[:2]:
            if abs(t - (b + 0.25)) < 0.5 / FPS:
                swing_amp, swing_t0 = (1.4 if b == BATS[0] else 2.4), t
        for i, (x, _, _) in enumerate(HANG):
            if i != TARGET:
                blit(img, socks[i].img(), x, MANTEL_Y + 1)
                continue
            if t < T_FALL:
                ang = swing_amp * math.exp(-(t - swing_t0) * 1.2) * math.sin((t - swing_t0) * 7) if swing_amp else 0
                src = socks[i].img()
                for row in range(src.height):
                    strip = src.crop((0, row, src.width, row + 1))
                    blit(img, strip, x + round(ang * row / 6), MANTEL_Y + 1 + row)
            elif t < T_LAND:
                p = phase(f, sec(T_FALL), sec(T_LAND)) ** 2
                blit(img, socks[i].img(), lerp(x, FLAT_X + 1, p), lerp(MANTEL_Y + 1, FLOOR - 7, p))
            else:
                wig = 0
                if T_IN <= t < T_PEEK:
                    wig = round(math.sin(t * 14)) if int(t * 3) % 2 == 0 else 0
                blit(img, flat.img(), FLAT_X + wig, FLAT_Y - (1 if wig and f % 4 < 2 else 0))
                if t >= T_PEEK:
                    pop = ease_out(phase(f, sec(T_PEEK), sec(T_PEEK + 0.3)))
                    blink = 1 if 13.8 < t < 14.0 else 0
                    head = CAT_HEAD.img()
                    blit(img, head, FLAT_X + 8, FLAT_Y + 1 - round(2 * pop) + blink)
                    # tail flicks out of the toe end
                    tx = FLAT_X - 1
                    put(img, tx, FLAT_Y + 2 - (f // 5) % 2, (240, 154, 58))
                    put(img, tx - 1, FLAT_Y + 1 - (f // 5) % 2, (240, 154, 58))
        if T_LAND <= t < T_LAND + 0.1:
            sp.emit(FLAT_X + 4, FLOOR - 1, 8, vx=(-0.9, 0.9), vy=(-0.8, -0.2), life=(6, 12), colors=SPARKLE,
                    glow=True)

        # candy cane bounces out when it lands
        if t >= T_LAND:
            p = phase(f, sec(T_LAND), sec(T_LAND + 0.8))
            cx = lerp(FLAT_X, FLAT_X - 6, ease_out(p))
            cy = FLOOR - 4 - 3 * math.sin(math.pi * p)
            blit(img, CANDY_CANE.img(), cx, cy)

        # --- the cat ---
        if t < T_WALK:
            cx = lerp(74, CAT_SIT_X, ease_out(phase(f, 0, sec(T_WALK))))
            blit(img, CAT.img((f // 3) % 2, flip=True), cx, CAT_Y)
        elif t < T_FALL + 0.1:
            fr = 2
            for b in BATS:
                if b <= t < b + 0.45:
                    fr = 5
            blit(img, CAT.img(fr, flip=True), CAT_SIT_X, CAT_Y)
        elif t < T_LAND + 0.2:  # startled hop backwards
            p = phase(f, sec(T_FALL + 0.1), sec(T_LAND + 0.2))
            blit(img, CAT.img(4, flip=True), lerp(CAT_SIT_X, 42, p), CAT_Y - 3 * math.sin(math.pi * p))
        elif t < T_LEAP:  # crouch and wiggle
            blit(img, CAT.img(3, flip=True), 42 + (1 if (f // 2) % 2 and t > T_LEAP - 0.6 else 0), CAT_Y)
        elif t < T_IN:  # pounce into the cuff
            p = phase(f, sec(T_LEAP), sec(T_IN))
            blit(img, CAT.img(4, flip=True), lerp(42, FLAT_X + 4, p), CAT_Y - 4 * math.sin(math.pi * p) + 2 * p)
        if abs(t - T_IN) < 0.5 / FPS:
            sp.emit(FLAT_X + 7, FLAT_Y + 1, 10, vx=(-0.8, 1.0), vy=(-1.0, -0.2), life=(6, 12), colors=SPARKLE,
                    glow=True)
        sp.step_draw(img)

        if t >= 12.2:
            w = text_width(CAPTION, "tiny")
            x = 70 - w
            reveal = int(lerp(0, w + 1, phase(f, sec(12.2), sec(12.8))))
            fade = 1 - phase(f, sec(15.5), sec(16.0))
            draw_text(img, CAPTION, x, 0, None, font="tiny", gradient=((255, 244, 170), (255, 170, 50)),
                      shadow=(120, 20, 30), reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, 2, f, 0.8)
        frames.append(img)
    return frames
