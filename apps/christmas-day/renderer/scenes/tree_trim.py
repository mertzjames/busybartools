"""Scene: Trimming the Tree. An elf hops around a bare fir hanging ornaments, the lights spiral on, and the star
is tossed up to the top. TA-DA!"""

import math

from busybar.canvas import FPS, add, blit, ease_in_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, sparkle
from sprites import ELF, STAR
from xfx import BLUE, BULBS, GOLD, RED, SILVER, draw_tree, garland_path, present, tree_spots, tree_star

NAME = "tree_trim"
TITLE = "Trimming the Tree"
SECONDS = 17
KEYFRAMES = [(1.2, "An elf arrives at a bare tree"), (4.6, "Hop, hang an ornament, repeat"),
             (8.9, "The lights spiral on"), (11.1, "The star goes up..."), (12.4, "...and lands on top"),
             (15.0, "TA-DA!")]

CX, TOP, HT = 33, 2, 12
FLOOR = 14
ELF_Y = FLOOR - ELF.h  # feet on the floor
ORN_COLORS = (RED, GOLD, BLUE, SILVER, (255, 110, 200), RED, GOLD)
T_ORN, ORN_DT = 2.0, 0.95
N_ORN = 6
T_LIGHTS, T_LIGHTS_END = 8.0, 9.8
T_PICK, T_THROW, T_LAND = 10.0, 11.0, 11.9
THROW_FROM = (16, ELF_Y)
CAPTION = "TA-DA!"


def wreath(img, cx, cy):
    for a in range(16):
        ang = 2 * math.pi * a / 16
        x, y = cx + 3 * math.cos(ang), cy + 3 * math.sin(ang)
        put(img, x, y, (30, 130, 56) if a % 2 else (20, 100, 44))
    for x, y in ((cx - 2, cy - 2), (cx + 2, cy + 1), (cx - 1, cy + 3)):
        put(img, x, y, RED)
    put(img, cx, cy + 3, RED)
    put(img, cx - 1, cy + 4, RED)
    put(img, cx + 1, cy + 4, RED)


def render():
    bg = vgradient((30, 8, 16), (48, 14, 22))
    rect(bg, 0, FLOOR, 72, 2, (96, 56, 30))
    for x in range(0, 72, 6):
        put(bg, x, FLOOR + 1, (70, 40, 22))
    wreath(bg, 6, 6)
    draw_tree(bg, CX, TOP, HT, trunk=1)
    # presents waiting on the right, below the caption
    present(bg, 50, 10, 6, 4, (210, 36, 46), GOLD)
    present(bg, 58, 9, 7, 5, (40, 150, 70), (240, 60, 70))
    present(bg, 66, 11, 4, 3, (70, 110, 230), SILVER)
    spots = tree_spots(CX, TOP, HT, N_ORN, seed=4)
    spots.sort(key=lambda p: (p[0], p[1]))
    lights = garland_path(CX, TOP, HT)
    sp = Particles(seed=21)
    frames = []
    hung = 0
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()

        # ornaments placed so far
        for i, (ox, oy) in enumerate(spots[:hung]):
            put(img, ox, oy, ORN_COLORS[i])
            add(img, ox - 1, oy, ORN_COLORS[i], 0.15)

        # light garland spirals on, then twinkles
        if t >= T_LIGHTS:
            n = int(len(lights) * phase(f, sec(T_LIGHTS), sec(T_LIGHTS_END)))
            for i, (lx, ly) in enumerate(lights[:n]):
                k = 0.5 + 0.5 * math.sin(t * 5 + i * 1.7)
                put(img, lx, ly, BULBS[i % len(BULBS)], 0.5 + 0.5 * k if t > T_LIGHTS_END else 1.0)

        # --- the elf ---
        frame, ex, ey, flip = 0, -8.0, float(ELF_Y), False
        if t < T_ORN:  # walk in from the left
            ex = lerp(-8, spots[0][0] - 9, ease_in_out(phase(f, 0, sec(T_ORN))))
            frame = (f // 3) % 4
        elif t < T_ORN + N_ORN * ORN_DT:
            i = int((t - T_ORN) / ORN_DT)
            s = T_ORN + i * ORN_DT
            ox, oy = spots[i]
            target = ox - 6
            prev = spots[i - 1][0] - 6 if i else spots[0][0] - 9
            if t < s + 0.45:  # hop over to the next spot
                p = phase(f, sec(s), sec(s + 0.45))
                ex = lerp(prev, target, p)
                ey = ELF_Y - 2.5 * math.sin(math.pi * p)
                frame = 1
            else:  # jump and hang it
                q = phase(f, sec(s + 0.45), sec(s + ORN_DT))
                ex = target
                ey = lerp(ELF_Y, min(ELF_Y, oy), math.sin(math.pi * q))
                frame = 5
                if q >= 0.5 and hung == i:
                    hung = i + 1
                    sp.emit(ox, oy, 6, vx=(-0.7, 0.7), vy=(-0.7, 0.4), life=(5, 10), colors=SPARKLE, glow=True)
        elif t < T_PICK:  # walk back out to the left of the tree
            p = phase(f, sec(T_ORN + N_ORN * ORN_DT), sec(T_PICK))
            ex = lerp(spots[-1][0] - 6, THROW_FROM[0], ease_in_out(p))
            frame = (f // 3) % 4
            flip = p < 0.98
        elif t < T_THROW:  # holds the star up
            ex = THROW_FROM[0]
            frame = 4
        elif t < T_THROW + 0.6:
            ex = THROW_FROM[0]
            frame = 5
        else:
            ex = THROW_FROM[0]
            frame = 4 if t > T_LAND + 0.2 else 0
            ey = ELF_Y - (2 * abs(math.sin((t - T_LAND) * 6)) if T_LAND + 0.2 < t < T_LAND + 3.0 else 0)
        blit(img, ELF.img(frame, flip=flip), ex, ey)

        # --- the star ---
        if T_PICK <= t < T_THROW:
            blit(img, STAR.img(), ex + 1, ey - 4)
            if f % 3 == 0:
                sparkle(img, ex + 3, ey - 4, f, 0.5)
        elif T_THROW <= t < T_LAND:
            p = phase(f, sec(T_THROW), sec(T_LAND))
            sx = lerp(ex + 3, CX, p)
            sy = lerp(ey - 3, TOP - 2, p) - 6 * math.sin(math.pi * p)
            blit(img, STAR.img(), sx - 2, sy - 1)
            sp.emit(sx, sy, 1, vx=(-0.2, 0.2), vy=(0.0, 0.3), life=(4, 8), colors=SPARKLE, glow=True)
        elif t >= T_LAND:
            glow = max(0.0, 1.0 - (t - T_LAND) / 1.2)
            tree_star(img, CX, TOP - 1, glow=1.0)
            if glow > 0:
                r = 2 + (1 - glow) * 10
                for a in range(12):
                    ang = 2 * math.pi * a / 12
                    add(img, CX + r * math.cos(ang), TOP - 1 + r * math.sin(ang) * 0.6, GOLD, glow)
            if t < T_LAND + 0.1:
                sp.emit(CX, TOP - 1, 14, vx=(-1.4, 1.4), vy=(-0.8, 1.0), life=(8, 16), colors=SPARKLE, glow=True)

        sp.step_draw(img)

        if t >= 13.0:
            w = text_width(CAPTION)
            x = 41
            reveal = int(lerp(0, w + 1, ease_in_out(phase(f, sec(13.0), sec(13.7)))))
            fade = 1 - phase(f, sec(16.5), sec(17.0))
            draw_text(img, CAPTION, x, 1, None, gradient=((255, 240, 160), (240, 150, 30)), shadow=(110, 20, 20),
                      reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, 2 + f % 5, f)
        frames.append(img)
    return frames
