"""Scene: Freedom Bells. At first light, three bells hang still in a stone frame. One after another they begin to
swing and ring; rings of sound spread across the sky and a flock of birds lifts off. As the bells settle, the word
FREEDOM appears."""

import math

from busybar.canvas import FPS, H, W, add, blit, ease_in_out, lerp, phase, put, sec
from mfx import caption, sky, sun
from sprites import BELL, BIRD

NAME = "bells"
TITLE = "Freedom Bells"
SECONDS = 15
KEYFRAMES = [(1.0, "Three bells wait at first light"), (4.5, "One by one, they ring"),
             (7.5, "Birds lift off as the sound spreads"), (13.5, "FREEDOM")]

POSTS = (1, 10, 19, 28)
BEAM_Y = 1
BASE_Y = 13
STONE = (92, 86, 120)
STONE_LIGHT = (130, 122, 160)
BELL_X = (5.5, 14.5, 23.5)
SWING_HZ = 0.55
# half a swing apart, with alternating sign (angle()), so the bells always swing the same way and never touch
STARTS = tuple(1.6 + i / SWING_HZ / 2 for i in range(3))
SETTLE = (9.5, 12.0)
CAPTION_X = 30

# birds: (start time, start x, start y, vx, vy)
BIRDS = [(3.2, 12, 3, 0.9, -0.03), (3.6, 20, 5, 1.0, -0.05), (4.1, 6, 4, 0.85, -0.02), (4.5, 16, 6, 1.05, -0.06),
         (5.0, 24, 4, 0.9, -0.04)]


def frame_art(img, light: float) -> None:
    """The stone bell frame: posts, beam and base, its top edge lit by the dawn."""
    for x in range(POSTS[0], POSTS[-1] + 1):
        put(img, x, BEAM_Y, STONE_LIGHT)
        put(img, x, BEAM_Y + 1, STONE)
        put(img, x, BEAM_Y, (255, 190, 110), 0.4 * light)
    for px in POSTS:
        for y in range(BEAM_Y, BASE_Y):
            put(img, px, y, STONE)
    for x in range(0, POSTS[-1] + 2):
        for y in range(BASE_Y, H):
            put(img, x, y, STONE if y == BASE_Y else (60, 56, 84))


def angle(i: int, t: float) -> float:
    """Swing angle in degrees: starts at STARTS[i], rings, then settles."""
    if t < STARTS[i]:
        return 0.0
    grow = ease_in_out(min(1.0, (t - STARTS[i]) / 1.2))
    settle = 1 - ease_in_out(phase(int(t * FPS), sec(SETTLE[0]), sec(SETTLE[1])))
    sign = -1 if i % 2 else 1
    return sign * 24 * grow * settle * math.sin(2 * math.pi * SWING_HZ * (t - STARTS[i]))


def draw_bell(img, cx: int, top: int, deg: float) -> None:
    """The bell swung about its crown: each row shifts sideways in proportion to its depth (a shear reads more
    cleanly than a rotation at this size). The clapper lags a little behind."""
    src = BELL.img(0)
    px = src.load()
    s = math.sin(math.radians(deg))
    for y in range(src.height):
        depth = y / (src.height - 1)
        lag = 0.7 if y == src.height - 1 else 1.0
        dx = round(s * 6 * depth * lag)
        for x in range(src.width):
            c = px[x, y]
            if c[3]:
                put(img, cx - 3 + x + dx, top + y, c[:3])


def render():
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        p = ease_in_out(phase(f, 0, sec(SECONDS)))
        img = sky(0.45 + 0.55 * p, horizon=H - 1)
        sun(img, 52, lerp(H + 3, H - 2, p), 3.4, strength=0.6 + 0.4 * p)
        # rings of sound: one each time a bell reaches the end of its swing
        caption_a = ease_in_out(phase(f, sec(11.0), sec(13.0)))
        for i, bx in enumerate(BELL_X):
            if t < STARTS[i]:
                continue
            period = 1 / SWING_HZ / 2
            k = int((t - STARTS[i] - period / 2) // period)
            for j in range(max(0, k - 2), k + 1):
                t0 = STARTS[i] + period / 2 + j * period
                amp = abs(angle(i, t0)) / 24
                age = t - t0
                if age < 0 or amp < 0.15:
                    continue
                r = 3 + age * 16
                fade = (1 - age / 2.0) * amp * (1 - 0.8 * caption_a)
                if fade <= 0:
                    continue
                for a in range(0, 360, 4):
                    x = bx + r * math.cos(math.radians(a))
                    y = 6 + r * 0.55 * math.sin(math.radians(a))
                    add(img, x, y, (255, 200, 110), 0.22 * fade)
        frame_art(img, p)
        for i, bx in enumerate(BELL_X):
            draw_bell(img, round(bx), BEAM_Y + 2, angle(i, t))
        for t0, x0, y0, vx, vy in BIRDS:
            age = (t - t0) * FPS
            if age < 0:
                continue
            x, y = x0 + vx * age, y0 + vy * age + 1.5 * math.sin(age * 0.2)
            if -5 < x < W and y > -3:
                blit(img, BIRD.img(int(age // 4) % 2), x, y)
        caption(img, "FREEDOM", 2, caption_a, font="big", x=CAPTION_X, back=False)
        frames.append(img)
    return frames
