"""Scene: Lovebirds. At dusk a rosy bird and a golden bird fly in from either side and land on a wire over the
rooftops. They hop closer, one step at a time, until their beaks meet and a heart pops up above them. Stars come
out while the heart beats and small hearts drift up."""

import math

from busybar.canvas import FPS, H, W, add, blit, ease_in_out, ease_out, lerp, put, sec
from busybar.fx import Stars
from sprites import GOLD_BIRD, ROSE_BIRD
from vfx import BLUSH, GOLD_LIGHT, PINK, RED, ROSE, gradient, heart, heart_c, heart_glow, twinkle

NAME = "lovebirds"
TITLE = "Lovebirds"
SECONDS = 14
KEYFRAMES = [(1.6, "A rosy bird flies in"), (3.6, "A golden bird lands too"), (6.5, "They hop closer"),
             (9.3, "Their beaks meet"), (10.2, "A heart pops up"), (13.0, "Stars come out")]

POLES = (3, 68)
WIRE_Y, SAG = 10.0, 2.0
MEET = 9.2  # seconds: they lean in
POP = 9.7
GROW = (3, 5, 7, 9, 9)
HEART_X, HEART_Y = 36.5, 3.0

# hops: (start second, from x, to x) for each bird's sprite left edge; the gold bird is drawn flipped
ROSE_HOPS = [(4.4, 14, 19), (5.6, 19, 24), (6.8, 24, 28), (8.0, 28, 30)]
GOLD_HOPS = [(5.0, 52, 47), (6.2, 47, 42), (7.4, 42, 38), (8.5, 38, 36)]
HOP = 0.4


def wire_y(x: float, dips) -> float:
    u = (x - (POLES[0] + POLES[1]) / 2) / ((POLES[1] - POLES[0]) / 2)
    y = WIRE_Y + SAG * (1 - u * u)
    for bx in dips:  # a little dip under each bird
        y += 0.8 * max(0.0, 1 - abs(x - bx) / 6)
    return y


def hop_x(t: float, hops, start: float) -> tuple[float, float]:
    """(x, height above the wire) on the hop schedule."""
    x, lift = start, 0.0
    for t0, a, b in hops:
        if t >= t0 + HOP:
            x = b
        elif t >= t0:
            p = (t - t0) / HOP
            x, lift = lerp(a, b, p), 2.2 * math.sin(p * math.pi)
    return x, lift


def bird_state(t: float, which: str):
    """(x, y_offset_above_perch or None while flying, sprite frame, flying y) for one bird."""
    if which == "rose":
        land, start, frm = 2.4, 14, -10
        hops = ROSE_HOPS
    else:
        land, start, frm = 3.8, 52, W + 4
        hops = GOLD_HOPS
    t_in = land - 2.2
    if t < land:
        p = max(0.0, (t - t_in) / 2.2)
        e = ease_out(p)
        x = lerp(frm, start, e)
        return x, None, 1 if (int(t * FPS) // 3) % 2 == 0 else 0, lerp(-1, 0, e) + 4 * (1 - e) * 0 + lerp(1, 6.5, e)
    x, lift = hop_x(t, hops, start)
    frame = 2 if t >= MEET else (1 if lift > 1.2 else 0)
    return x, lift, frame, None


def render():
    bg = gradient([(0, (14, 8, 40)), (8, (40, 16, 70)), (13, (96, 36, 86)), (15, (150, 64, 84))])
    # a low, distant skyline along the bottom (lit plum, so it reads as shapes rather than holes), warm windows
    roofs = [14, 14, 14, 15, 15, 14, 14, 14, 14, 15, 15, 15, 14, 14, 13, 13, 14, 14, 15, 15, 14, 14, 14, 15, 15,
             15, 14, 14, 14, 14, 15, 15, 15, 14, 14, 13, 13, 13, 14, 14, 15, 15, 14, 14, 14, 14, 15, 15, 15, 14,
             14, 14, 15, 15, 14, 14, 13, 13, 14, 14, 14, 15, 15, 14, 14, 14, 15, 15, 14, 14, 14, 15]
    for x in range(W):
        for y in range(roofs[x], H):
            put(bg, x, y, (40, 14, 44))
    for x, y in ((6, 15), (15, 14), (27, 15), (36, 14), (45, 15), (57, 14), (65, 15)):
        put(bg, x, y, (255, 190, 100), 0.75)
    for px in POLES:
        for y in range(int(WIRE_Y) - 2, H):
            put(bg, px, y, (96, 60, 90))
        put(bg, px - 1, int(WIRE_Y) - 1, (96, 60, 90))
        put(bg, px + 1, int(WIRE_Y) - 1, (96, 60, 90))
    stars = Stars(seed=12, n=18, ymax=7, period=FPS * 3, color=(240, 230, 255), dim=0.1, bright=0.7)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        if t > 8.0:  # stars come out as it gets dark
            stars.draw(img, f)
        birds = []
        for which, spr, flip in (("rose", ROSE_BIRD, False), ("gold", GOLD_BIRD, True)):
            x, lift, frame, fly_y = bird_state(t, which)
            birds.append((x, lift, frame, fly_y, spr, flip))
        dips = [x + 3 for x, lift, _, fy, _, _ in birds if fy is None and lift < 0.5]
        for x in range(POLES[0], POLES[1] + 1):
            put(img, x, wire_y(x, dips), (150, 120, 150))
        if t >= POP:  # the heart above them
            k = int((t - POP) / 0.09)
            u = (t - POP - 0.4) % 1.5
            w = GROW[k] if k < len(GROW) else (9 if u < 0.13 or 0.27 <= u < 0.37 else 7)
            heart_glow(img, HEART_X, HEART_Y + 1, 7, (110, 20, 60), 0.7)
            heart_c(img, HEART_X, HEART_Y + (0.5 if w == 9 else 0), w, RED, halo=(40, 10, 44))
            for i in range(6):  # small hearts drifting up and out
                age = t - POP - 0.6 - i * 0.7
                if 0 <= age < 3.2:
                    side = -1 if i % 2 else 1
                    heart(img, HEART_X - 1 + side * (6 + age * 2.2), HEART_Y + 2 - age * 2.2, 3,
                          (ROSE, PINK, BLUSH)[i % 3], min(1.0, (3.2 - age) / 1.0))
            if t > POP + 1.5:
                for i, (x, y) in enumerate(((27, 2), (46, 1), (25, 6), (48, 5))):
                    twinkle(img, x, y, f, GOLD_LIGHT, 0.8, period=24, ph=i / 4)
        for x, lift, frame, fly_y, spr, flip in birds:
            if fly_y is not None:
                y = fly_y - 1 + 0.6 * math.sin(f * 0.8)
            else:
                y = wire_y(x + 3, dips) - 4 - lift
            blit(img, spr.img(frame, flip=flip), x, y)
        frames.append(img)
    return frames
