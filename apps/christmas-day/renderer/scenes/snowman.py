"""Scene: Building a Snowman. A girl rolls three snowballs, stacks them, adds a face and tops it with a hat.
A gust of wind steals the hat; she chases it, comes back wearing it, then hands it over. MUCH BETTER!"""

import math

from busybar.canvas import FPS, blit, ease_in_out, ease_out, lerp, mix, phase, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, sparkle
from sprites import GIRL, TOP_HAT
from xfx import SNOW, Snow, draw_tree, snow_ground

NAME = "snowman"
TITLE = "Building a Snowman"
SECONDS = 17
KEYFRAMES = [(2.0, "Rolling the first snowball"), (4.6, "...and the middle one"), (8.8, "A face, arms and a hat"),
             (10.5, "WHOOSH! The wind steals the hat"), (13.2, "She brings it back... on her own head"),
             (15.6, "MUCH BETTER!")]

GROUND = 13
SX = 16  # snowman centre x
R_BASE, R_MID, R_HEAD = 3.3, 2.2, 1.6
BASE_Y = GROUND + 1 - R_BASE  # ball centres
MID_Y = BASE_Y - R_BASE - R_MID + 1.2
HEAD_Y = MID_Y - R_MID - R_HEAD + 1.0
KID_Y = GROUND + 1 - GIRL.h
SLATE = (90, 100, 140)  # coal: a lit grey-blue, not black
STICK = (150, 96, 50)
T_BASE, T_MID0, T_MID1, T_LIFT, T_HEAD, T_FACE, T_HAT = 0.0, 3.4, 5.0, 5.6, 6.2, 7.6, 8.6
T_GUST, T_CHASE, T_GONE, T_BACK, T_RETURN, T_PLACE = 9.8, 10.8, 11.8, 12.4, 14.0, 14.6
STAND_X = SX + 7  # where she stands to decorate (facing left)
CAPTION = "MUCH BETTER!"


def snowball(img, cx, cy, r):
    for yy in range(int(cy - r - 1), int(cy + r + 2)):
        for xx in range(int(cx - r - 1), int(cx + r + 2)):
            d = math.hypot(xx - cx, yy - cy)
            if d <= r + 0.25:
                edge = d > r - 0.8
                shade = (xx - cx + yy - cy) / (2 * r + 0.01)
                c = mix(SNOW, (170, 185, 225), max(0.0, shade) * 0.8)
                if edge:
                    c = mix(c, (110, 130, 200), 0.75)
                put(img, xx, yy, c)


def face(img, mood: str, has_nose: bool):
    hx, hy = SX, HEAD_Y
    put(img, hx, hy - 1, SLATE)
    put(img, hx + 1, hy - 1, SLATE)
    if has_nose:
        put(img, hx + 2, hy, (255, 138, 42))
        put(img, hx + 3, hy, (255, 138, 42))
    if mood == "smile":
        put(img, hx - 1, hy + 1, SLATE)
        put(img, hx, hy + 1, SLATE, 0.6)
        put(img, hx + 1, hy + 1, SLATE)
    elif mood == "oh":
        put(img, hx + 1, hy + 1, SLATE)


def render():
    sky = vgradient((12, 18, 52), (38, 44, 92))
    snow_ground(sky, GROUND, seed=6)
    for cx, top in ((58, 6), (66, 4), (71, 7)):
        draw_tree(sky, cx, top, height=GROUND - top, trunk=0, snowy=True)
    snow = Snow(seed=81, n=30, period=FPS * 5, laps=(1, 2), bright=(0.3, 0.8))
    sp = Particles(seed=82)
    frames = []
    drift = 0.0
    hat_pos = None
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        gust = math.sin(math.pi * phase(f, sec(T_GUST), sec(T_GUST + 1.6))) if T_GUST <= t < T_GUST + 1.6 else 0
        drift += 0.05 + 2.2 * gust
        snow.draw(img, f, drift=drift)
        if gust > 0.2:  # wind streaks
            for k in range(5):
                y = (k * 3 + f) % 12
                x0 = (f * 6 + k * 23) % 90 - 15
                for dx in range(6):
                    put(img, x0 + dx, y, (200, 215, 255), 0.35 * gust * (dx / 6))

        # --- the snowman, as far as it is built ---
        if t < T_MID0:
            p = ease_in_out(phase(f, sec(T_BASE), sec(T_MID0 - 0.4)))
            r = lerp(0.8, R_BASE, p)
            bx = lerp(-1, SX, p)
            snowball(img, bx, GROUND + 1 - r, r)
        else:
            snowball(img, SX, BASE_Y, R_BASE)
        if T_MID0 <= t < T_LIFT:  # roll the middle ball in from the right
            p = ease_in_out(phase(f, sec(T_MID0), sec(T_MID1)))
            r = lerp(0.8, R_MID, p)
            mx = lerp(44, SX + 7, p)
            snowball(img, mx, GROUND + 1 - r, r)
        elif T_LIFT <= t:
            p = ease_out(phase(f, sec(T_LIFT), sec(T_LIFT + 0.5)))
            snowball(img, lerp(SX + 7, SX, p), lerp(GROUND + 1 - R_MID, MID_Y, p) - 2 * math.sin(math.pi * p), R_MID)
        if t >= T_HEAD + 0.8:
            p = ease_out(phase(f, sec(T_HEAD + 0.8), sec(T_HEAD + 1.2)))
            snowball(img, lerp(SX + 3, SX, p), lerp(HEAD_Y - 2, HEAD_Y, p), R_HEAD)
        if t >= T_FACE:
            n = int((t - T_FACE) / 0.25) + 1  # eyes, nose, buttons, arms pop on one by one
            hat_off = T_GUST + 0.3 <= t < T_PLACE + 0.4
            mood = "smile" if (t >= T_FACE + 1.4 and not hat_off) else ("oh" if hat_off else "none")
            face(img, mood, n >= 2)
            if n >= 3:
                put(img, SX, MID_Y - 0.5, SLATE)
                put(img, SX, MID_Y + 1.2, SLATE)
            if n >= 4:
                for k in range(3):
                    put(img, SX - R_MID - 1 - k, MID_Y - 0.5 - k * 0.7, STICK)
                    put(img, SX + R_MID + 1 + k, MID_Y - 0.5 - k * 0.7, STICK)
                put(img, SX - R_MID - 3, MID_Y - 3, STICK)
                put(img, SX + R_MID + 3, MID_Y - 3, STICK)
            for k in range(1, 5):
                if abs(t - (T_FACE + 0.25 * (k - 1))) < 0.5 / FPS:
                    sp.emit(SX, HEAD_Y if k < 3 else MID_Y, 4, vx=(-0.6, 0.6), vy=(-0.6, 0.2), life=(4, 8),
                            colors=SPARKLE, glow=True)

        # --- the hat ---
        hat_on_head = (SX - 2, HEAD_Y - R_HEAD - 2.6)
        if T_HAT <= t < T_HAT + 0.6:  # tossed from her hand onto the snowman
            p = phase(f, sec(T_HAT), sec(T_HAT + 0.6))
            hat_pos = (lerp(STAND_X + 1, hat_on_head[0], p), lerp(KID_Y - 2, hat_on_head[1], p) - 4 * math.sin(math.pi * p))
        elif T_HAT + 0.6 <= t < T_GUST + 0.3 or t >= T_PLACE + 0.4:
            hat_pos = hat_on_head
        elif T_GUST + 0.3 <= t < T_GONE:  # blown away, tumbling off to the right
            p = phase(f, sec(T_GUST + 0.3), sec(T_GONE))
            hat_pos = (lerp(hat_on_head[0], 80, p ** 1.3), hat_on_head[1] - 3 * math.sin(math.pi * p * 2) + 4 * p)
        elif T_PLACE <= t < T_PLACE + 0.4:
            p = phase(f, sec(T_PLACE), sec(T_PLACE + 0.4))
            hat_pos = (lerp(STAND_X + 1, hat_on_head[0], p), lerp(KID_Y - 3, hat_on_head[1], p) - 3 * math.sin(math.pi * p))
        else:
            hat_pos = None
        if hat_pos is not None:
            blit(img, TOP_HAT.img(flip=(T_GUST + 0.3 <= t < T_GONE and (f // 3) % 2 == 1)), *hat_pos)

        # --- the girl ---
        fr, kx, flip, wears_hat = 0, STAND_X, True, False
        if t < T_MID0:  # pushing the base ball to the right
            p = ease_in_out(phase(f, sec(T_BASE), sec(T_MID0 - 0.4)))
            r = lerp(0.8, R_BASE, p)
            kx = lerp(-1, SX, p) - r - 6
            fr, flip = (5 if t < T_MID0 - 0.4 else 0), False
            if t >= T_MID0 - 0.4:
                kx = SX - R_BASE - 6
        elif t < T_MID0 + 0.01:
            kx = SX - R_BASE - 6
        elif t < T_LIFT:  # walk round and push the middle ball in from the right
            p = ease_in_out(phase(f, sec(T_MID0), sec(T_MID1)))
            r = lerp(0.8, R_MID, p)
            kx = lerp(44, SX + 7, p) + r
            fr = 5 if t < T_MID1 else 0
        elif t < T_HEAD:
            kx = SX + 7 + R_MID
            fr = 4 if t < T_LIFT + 0.4 else 0
        elif t < T_HEAD + 0.8:  # scoops a head, holds it up
            kx = lerp(SX + 7 + R_MID, STAND_X, phase(f, sec(T_HEAD), sec(T_HEAD + 0.4)))
            fr = 4
            snowball(img, kx + 3, KID_Y - 2, R_HEAD)
        elif t < T_GUST + 0.3:
            fr = 4 if (T_HAT + 0.6 < t < T_HAT + 1.2) or (T_HAT - 0.5 < t < T_HAT) else 0
        elif t < T_CHASE:
            fr = 4  # startled
        elif t < T_GONE:  # runs after the hat
            kx = lerp(STAND_X, 76, ease_in_out(phase(f, sec(T_CHASE), sec(T_GONE))))
            fr, flip = (f // 2) % 4, False
        elif t < T_BACK:
            kx = 80
        elif t < T_RETURN:  # strolls back wearing it
            kx = lerp(76, STAND_X, ease_out(phase(f, sec(T_BACK), sec(T_RETURN))))
            fr = (f // 3) % 4
            wears_hat = True
        elif t < T_PLACE:
            wears_hat = True
            fr = 0
        else:
            fr = 4 if t > T_PLACE + 0.5 else 0
        ky = KID_Y - (1 if fr == 4 and t > T_PLACE + 0.5 and (f // 5) % 2 else 0)
        blit(img, GIRL.img(fr, flip=flip), kx, ky)
        if wears_hat:
            blit(img, TOP_HAT.img(), kx + 1, ky - 3)

        sp.step_draw(img)

        if t >= 15.0:
            w = text_width(CAPTION, "tiny")
            x = 70 - w
            reveal = int(lerp(0, w + 1, ease_in_out(phase(f, sec(15.0), sec(15.6)))))
            fade = 1 - phase(f, sec(16.5), sec(17.0))
            draw_text(img, CAPTION, x, 0, None, font="tiny", gradient=((255, 244, 170), (255, 170, 50)),
                      shadow=(120, 20, 30), reveal=reveal, alpha=fade)
            if reveal < w:
                sparkle(img, x + reveal, 2, f, 0.8)
        frames.append(img)
    return frames
