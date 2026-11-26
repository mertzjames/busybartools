"""Scene: Present Surprise. Christmas morning: a boy pulls a ribbon and a jack-in-the-box springs out (BOING),
then the big green box starts to wiggle... and a puppy pops out and smothers him in licks. BEST GIFT!"""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, sparkle
from sprites import BOY, HEART, JACK, PUPPY
from xfx import BULBS, GOLD, draw_tree, garland_path, present, tree_star

NAME = "presents"
TITLE = "Present Surprise"
SECONDS = 17
KEYFRAMES = [(1.6, "Christmas morning, presents waiting"), (3.4, "BOING! A jack-in-the-box"),
             (8.4, "The big box starts to wiggle..."), (9.6, "...a puppy peeks out"),
             (11.6, "Puppy kisses"), (14.5, "BEST GIFT!")]

FLOOR = 15
KID_Y = FLOOR - BOY.h
TREE_CX, TREE_TOP, TREE_H = 7, 2, 12
BOX1 = (24, 10, 7, 5, (214, 36, 46), GOLD)  # x, y, w, h, box, ribbon
BOX2 = (50, 9, 8, 6, (40, 150, 70), (240, 60, 70))
T_PULL, T_BOING = 2.2, 2.9
T_TO2, T_AT2 = 6.0, 7.8
T_WIGGLE, T_POP, T_JUMP, T_LAND = 7.9, 9.0, 10.2, 10.8
KID1_X, KID2_X = 16, 39
PUP_LAND_X = 46
CAPTION = "BEST GIFT!"


def spring(img, x, y_top, y_bot, f):
    """Zig-zag spring from the box up to the jack's chin."""
    n = max(0, int(round(y_bot - y_top)))
    for k in range(n + 1):
        yy = y_bot - k
        put(img, x + (1 if k % 2 else -1), yy, (200, 210, 230))
        put(img, x, yy, (150, 160, 190))


def render():
    bg = vgradient((10, 12, 36), (20, 22, 50))
    rect(bg, 0, FLOOR, 72, 1, (110, 66, 36))
    draw_tree(bg, TREE_CX, TREE_TOP, TREE_H, trunk=1)
    lights = garland_path(TREE_CX, TREE_TOP, TREE_H)
    sp = Particles(seed=61)
    hearts = []
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        tree_star(img, TREE_CX, TREE_TOP - 1, glow=0.6 + 0.4 * math.sin(t * 3))
        for i, (lx, ly) in enumerate(lights):
            put(img, lx, ly, BULBS[i % len(BULBS)], 0.55 + 0.45 * math.sin(t * 4 + i * 1.3))
        # morning light from an unseen window
        for x in range(60, 72):
            for y in range(0, FLOOR):
                add(img, x, y, (60, 50, 30), 0.12 * (x - 60) / 12)

        # --- box 1: the jack-in-the-box ---
        bx, by, bw, bh, bc, rc = BOX1
        if t >= T_BOING:
            u = t - T_BOING
            ext = 1 - math.exp(-u * 2.2) * math.cos(u * 11)
            ext = max(0.0, ext) if u > 0.05 else 0.0
            sway = 1.6 * math.exp(-u * 0.6) * math.sin(u * 6)
            hx = bx + bw // 2 + sway
            head_y = lerp(by - 2, 0, min(1.15, ext))
            spring(img, round(bx + bw // 2), head_y + 7, by, f)
            blit(img, JACK.img(), hx - 3, head_y)
            if u < 0.15:
                sp.emit(bx + bw // 2, by, 10, vx=(-1.0, 1.0), vy=(-1.2, -0.3), life=(6, 12), colors=SPARKLE,
                        glow=True)
        lid_t = phase(f, sec(T_PULL + 0.5), sec(T_PULL + 1.3))
        if t < T_PULL + 0.5:
            present(img, bx, by, bw, bh, bc, rc)
        else:
            present(img, bx, by, bw, bh, bc, rc, open_=True, lid=False)
            if lid_t < 1:  # lid flies off up and to the right
                present(img, bx, by, bw, 0, bc, rc, lid_dy=-14 * ease_out(lid_t) + 10 * lid_t ** 2,
                        lid_dx=10 * lid_t)

        # --- box 2: the puppy ---
        bx2, by2, bw2, bh2, bc2, rc2 = BOX2
        jig = 0
        if T_WIGGLE <= t < T_POP:
            jig = round(math.sin(t * 30)) if int(t * 4) % 2 == 0 else 0
        hop = 1 if (T_WIGGLE + 0.5 <= t < T_POP and f % 6 < 2) else 0
        if T_POP <= t < T_JUMP:
            rise = ease_out(phase(f, sec(T_POP), sec(T_POP + 0.4)))
            blit(img, PUPPY.img(0, flip=True), bx2, by2 - 1 - round(3 * rise))
        if t < T_POP:
            present(img, bx2 + jig, by2 - hop, bw2, bh2, bc2, rc2)
        else:
            present(img, bx2, by2, bw2, bh2, bc2, rc2, open_=True, lid=False)
            lt = phase(f, sec(T_POP), sec(T_POP + 0.9))
            if lt < 1:
                present(img, bx2, by2, bw2, 0, bc2, rc2, lid_dy=-12 * ease_out(lt) + 9 * lt ** 2, lid_dx=7 * lt)
            if abs(t - T_POP) < 0.5 / FPS:
                sp.emit(bx2 + bw2 // 2, by2, 12, vx=(-1.0, 1.0), vy=(-1.2, -0.3), life=(6, 12), colors=SPARKLE,
                        glow=True)

        # --- the boy ---
        fr, kx, ky, flip = 0, KID1_X, KID_Y, False
        if t < T_PULL:
            kx = lerp(-8, KID1_X, ease_out(phase(f, 0, sec(T_PULL))))
            fr = (f // 3) % 4 if t < T_PULL - 0.3 else 0
        elif t < T_BOING:
            fr = 5
            kx = KID1_X + (1 if t > T_PULL + 0.4 else 0)
        elif t < T_TO2:
            p = phase(f, sec(T_BOING), sec(T_BOING + 0.5))
            kx = lerp(KID1_X + 1, KID1_X - 4, p)
            ky = KID_Y - 3 * math.sin(math.pi * p)
            fr = 4 if t < T_BOING + 1.2 else 0
            if t > T_BOING + 1.5:  # laughing bob
                ky = KID_Y - (1 if (f // 4) % 2 else 0)
                fr = 4 if (f // 8) % 2 else 0
        elif t < T_AT2:
            kx = lerp(KID1_X - 4, KID2_X, ease_in_out(phase(f, sec(T_TO2), sec(T_AT2))))
            fr = (f // 3) % 4
        elif t < T_LAND:
            kx = KID2_X
            fr = 0
        else:
            kx = KID2_X
            fr = 4
            ky = KID_Y - (1 if (f // 5) % 2 else 0)
        blit(img, BOY.img(fr, flip=flip), kx, ky)
        if T_WIGGLE + 0.3 <= t < T_POP:
            draw_text(img, "?", KID2_X + 2, -1, (255, 230, 120), font="tiny")

        # --- puppy jumps out to the boy and licks him ---
        if T_JUMP <= t < T_LAND:
            p = phase(f, sec(T_JUMP), sec(T_LAND))
            px = lerp(bx2, PUP_LAND_X, p)
            py = lerp(by2 - 4, FLOOR - PUPPY.h, p) - 5 * math.sin(math.pi * p)
            blit(img, PUPPY.img(1, flip=True), px, py)
        elif t >= T_LAND:
            licking = int(t * 3) % 2 == 0
            blit(img, PUPPY.img(4 if licking else 3, flip=True), PUP_LAND_X, FLOOR - PUPPY.h - (1 if licking else 0))
            if f % 14 == 0 and t < SECONDS - 1.0:
                hearts.append([PUP_LAND_X - 3, FLOOR - PUPPY.h - 5, f])
        for hx, hy, h0 in hearts:
            age = (f - h0) / FPS
            if age < 1.6:
                blit(img, HEART.img(), hx + math.sin(age * 5 + h0) * 1.5, hy - age * 5, alpha=1 - (age / 1.6) ** 2)

        sp.step_draw(img)

        if t >= 13.4:
            w = text_width(CAPTION, "tiny")
            x = 70 - w
            reveal = int(lerp(0, w + 1, phase(f, sec(13.4), sec(14.0))))
            fade = 1 - phase(f, sec(16.5), sec(17.0))
            draw_text(img, CAPTION, x, 0, None, font="tiny", gradient=((255, 244, 170), (255, 170, 50)),
                      shadow=(120, 20, 30), reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, 2, f, 0.8)
        frames.append(img)
    return frames
