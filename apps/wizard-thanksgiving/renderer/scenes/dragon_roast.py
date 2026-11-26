"""Scene 8 (playlist #7): Dragon Roast. A winged serpent dragon swoops in and torches the turkey (D22).

The dragon's long body is procedural: the neck follows a flight path, and each body segment sits a fixed
arc length behind it on that same path, so the body trails the head like a snake. A small traveling wave keeps
it writhing while it hovers.
"""

import bisect
import math
import random

from busybar.canvas import FPS, add, blit, ease_in, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.font import draw_text
from busybar.fx import FIRE, SPARKLE, Particles, Stars, sparkle
from sprites import DRAGON_HEAD, DRAGON_WING, RAW_TURKEY, ROAST, SPIT

NAME = "dragon_roast"
TITLE = "Dragon Roast"
SECONDS = 16
KEYFRAMES = [(2.5, "A winged serpent swoops in"), (5.4, "Rears up, smoke curling"), (7.6, "Torches the turkey"),
             (11.6, "Flies off over the roast"), (14.0, "WELL DONE!")]

SPIT_X, SPIT_Y = 52, 9
TURKEY_X, TURKEY_Y = SPIT_X + 1, SPIT_Y - 3
BODY_LEN = 30
HOVER_X = 31

SCALE = (31, 122, 62)       # body
SCALE_HI = (47, 160, 90)    # back highlight
SCALE_LO = (20, 82, 41)     # tail
BELLY = (201, 180, 88)
SPINE = (176, 18, 30)


def neck(t: float):
    """Neck point (where the head joins the body) over time, including an off-screen pre-roll."""
    if t < 0:
        x = -12 + 19 * t
        return x, 7 + 3 * math.sin(x * 0.2 + 1)
    if t < 4.5:
        k = ease_out(t / 4.5)
        x = lerp(-12, HOVER_X, k)
        return x, 7 + 3 * math.sin(x * 0.2 + 1) * (1 - k * k) + lerp(0, -1, k)
    if t < 10.4:
        rear = ease_out(phase(int(t * FPS), sec(4.8), sec(5.6)))
        return HOVER_X - rear, 6 - 1.5 * rear + 0.4 * math.sin(t * 2.2)
    k = ease_in((t - 10.4) / 2.6)
    return lerp(HOVER_X - 1, 72, k), lerp(4.5, -18, k)


def build_path():
    """Dense samples of the neck path with cumulative arc length, for placing body segments."""
    dt = 1 / (FPS * 6)
    ts = [-4 + i * dt for i in range(int((SECONDS + 4) / dt) + 1)]
    pts = [neck(t) for t in ts]
    arc = [0.0]
    for a, b in zip(pts, pts[1:]):
        arc.append(arc[-1] + math.hypot(b[0] - a[0], b[1] - a[1]))
    return ts, pts, arc


def body_points(t, ts, pts, arc):
    """BODY_LEN+1 points, one per pixel of arc length behind the neck."""
    k = min(len(ts) - 1, bisect.bisect_left(ts, t))
    s_head = arc[k]
    out = []
    j = k
    for i in range(BODY_LEN + 1):
        target = s_head - i
        while j > 0 and arc[j] > target:
            j -= 1
        a, b = pts[j], pts[min(j + 1, len(pts) - 1)]
        span = arc[min(j + 1, len(arc) - 1)] - arc[j]
        u = 0.0 if span <= 1e-9 else (target - arc[j]) / span
        x, y = lerp(a[0], b[0], u), lerp(a[1], b[1], u)
        y += 0.9 * math.sin(i * 0.45 - t * 4) * min(1.0, i / 6)  # writhe
        out.append((x, y))
    return out


def draw_body(img, pts):
    for i in range(BODY_LEN, -1, -1):
        x, y = pts[i]
        x, y = int(round(x)), int(round(y))
        thick = 3 if i < 10 else (2 if i < 20 else 1)
        if thick == 3:
            put(img, x, y - 1, SCALE_HI)
            put(img, x, y, SCALE)
            put(img, x, y + 1, BELLY)
        elif thick == 2:
            put(img, x, y, SCALE)
            put(img, x, y + 1, BELLY)
        else:
            put(img, x, y, SCALE_LO)
        if 2 <= i < 24 and i % 3 == 0:
            put(img, x, y - (thick + 1) // 2 - (1 if thick == 3 else 0), SPINE)
    # spade tail tip
    x, y = (int(round(v)) for v in pts[-1])
    for dx, dy in ((-1, 0), (-2, -1), (-2, 1), (-2, 0)):
        put(img, x + dx, y + dy, SPINE)


def courtyard(img):
    wall = (28, 18, 34)
    for x in range(72):
        top = 8 if (x // 3) % 2 == 0 else 9
        for y in range(top, 14):
            put(img, x, y, wall)
    for x, y in ((9, 11), (21, 10), (37, 11), (46, 10)):
        put(img, x, y, (255, 196, 80), 0.7)
    for x in range(72):
        put(img, x, 14, (34, 40, 20))
        put(img, x, 15, (24, 28, 14))


def render():
    rng = random.Random(8)
    sky = vgradient((26, 10, 40), (66, 26, 36))
    courtyard(sky)
    stars = Stars(seed=8, n=10, ymax=7, period=FPS * 4)
    fire = Particles(seed=81)
    flames = Particles(seed=82)
    smoke = Particles(seed=83)
    sp = Particles(seed=84)
    cooked_img = ROAST.img().crop((0, 0, ROAST.w, 6))
    ts, pts, arc = build_path()
    target = (TURKEY_X + 5, TURKEY_Y + 3)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        stars.draw(img, f)

        # campfire: embers until the dragon lights it, roaring after
        roaring = t >= 6.6
        if f % (1 if roaring else 3) == 0:
            flames.emit(SPIT_X + rng.uniform(4, 9), SPIT_Y + 4, 2 if roaring else 1, vx=(-0.1, 0.1),
                        vy=(-0.6, -0.3) if roaring else (-0.25, -0.1), life=(3, 6), colors=FIRE, glow=True)
        blit(img, SPIT.img(), SPIT_X, SPIT_Y)
        flames.step_draw(img)

        # turkey cooks under the flame 6.6-9.6s
        k = phase(f, sec(6.6), sec(9.6))
        rot = 0 if (f // 8) % 2 == 0 or t > 10.0 else 1
        blit(img, RAW_TURKEY.img(), TURKEY_X, TURKEY_Y + rot)
        if k > 0:
            blit(img, cooked_img, TURKEY_X, TURKEY_Y + rot, alpha=k)
        for x in range(SPIT_X, SPIT_X + 13):
            put(img, x, SPIT_Y + 1, (110, 110, 125))
        if t >= 9.6 and f % 5 == 0:
            smoke.emit(TURKEY_X + rng.uniform(2, 8), TURKEY_Y - 1, 1, vx=(-0.05, 0.05), vy=(-0.3, -0.15),
                       life=(10, 16), colors=((200, 200, 215),))

        # --- dragon ---
        body = body_points(t, ts, pts, arc)
        nx, ny = body[0]
        hx, hy = int(round(nx)) + 1, int(round(ny)) - 3
        flying = t < 4.5 or t >= 10.4
        wing = (f // 2) % 4 if flying else (f // 4) % 4
        wx, wy = body[12]   # wings sit back along the body so the head stays clear
        draw_body(img, body)
        blit(img, DRAGON_WING.img(wing), wx - 4, wy - 6)
        breathing = 6.0 <= t < 9.7
        blit(img, DRAGON_HEAD.img(1 if breathing else 0), hx, hy)
        # glowing eye, flaring as it rears
        flare = 0.35 + (0.4 * (0.5 + 0.5 * math.sin(t * 9)) if 4.8 <= t < 10.4 else 0)
        for dx, dy, a in ((0, 0, 0.6), (-1, 0, 0.5), (1, 0, 0.5), (0, -1, 0.35)):
            add(img, hx + 4 + dx, hy + 2 + dy, (255, 60, 30), flare * a)
        # nostril smoke while it rears and after it torches
        if (4.8 <= t < 6.0 or 9.7 <= t < 10.6) and f % 3 == 0 and 0 <= hy:
            smoke.emit(hx + 8, hy + 2, 1, vx=(0.0, 0.15), vy=(-0.35, -0.2), life=(8, 14),
                       colors=((150, 150, 160), (110, 110, 120)))

        # sustained flame jet from the jaws to the turkey
        if breathing and t >= 6.2:
            mx, my = hx + 9, hy + 4
            reach = min(1.0, (t - 6.2) / 0.35)
            dist = math.hypot(target[0] - mx, target[1] - my)
            n = int(dist * reach)
            for d in range(n + 1):
                u = d / max(1.0, dist)
                x = lerp(mx, target[0], u)
                y = lerp(my, target[1], u) + 0.6 * math.sin(d * 0.9 + t * 25)
                core = mix((255, 250, 210), (255, 140, 30), u)
                put(img, x, y, core)
                if rng.random() < 0.7:
                    add(img, x, y - 1, rng.choice(FIRE), 0.7)
                if rng.random() < 0.5:
                    add(img, x, y + 1, rng.choice(FIRE), 0.6)
            fire.emit(mx, my, 3, vx=(1.6, 2.6), vy=(-0.5, 0.3), life=(4, 9), colors=FIRE, glow=True, drag=0.95)
            if reach >= 1:
                fire.emit(target[0], target[1], 3, vx=(-0.6, 0.8), vy=(-0.9, -0.2), life=(4, 8), colors=FIRE,
                          glow=True)
        fire.step_draw(img)
        smoke.step_draw(img)

        if 9.6 <= t < 10.1:
            sp.emit(TURKEY_X + 5, TURKEY_Y + 2, 2, vx=(-1, 1), vy=(-1, 0.3), life=(8, 14), colors=SPARKLE, glow=True)
        if t >= 12.6:
            r = int(lerp(0, 40, phase(f, sec(12.6), sec(13.3))))
            draw_text(img, "WELL DONE!", 6, 5, None, font="tiny", gradient=((255, 236, 150), (235, 140, 25)),
                      shadow=(90, 38, 0), reveal=r)
            if f % 6 == 0:
                sparkle(img, TURKEY_X + rng.choice((0, 9)), TURKEY_Y + rng.choice((0, 3)), f, 0.8)
        sp.step_draw(img)
        frames.append(img)
    return frames
