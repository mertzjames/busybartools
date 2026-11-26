"""Scene: Carolers in the Snow. Three carolers stop under a street lamp and sing; a dog wanders up and howls
along, off key. Then everyone sings together: FA LA LA!"""

import math
import random

from busybar.canvas import FPS, add, blit, ease_in_out, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from sprites import CAROLER_BONNET, CAROLER_HAT, CAROLER_MUFFS, DOG, NOTE, NOTE2
from xfx import Snow, house, snow_ground

NAME = "carolers"
TITLE = "Carolers in the Snow"
SECONDS = 16
KEYFRAMES = [(2.4, "Carolers stroll in under the lamp"), (6.6, "They open their books and sing"),
             (9.6, "A dog wanders up..."), (11.3, "...and howls along, off key"), (14.4, "FA LA LA!")]

GROUND = 13
CAROLERS = [(CAROLER_HAT, 26, 0.0), (CAROLER_BONNET, 19, 0.5), (CAROLER_MUFFS, 12, 1.0)]  # sprite, stop x, delay
CY = GROUND - CAROLER_HAT.h + 1
DOG_X = 37
DOG_Y = GROUND - DOG.h + 1
LAMP_X = 5
CAPTION = "FA LA LA!"
NOTE_RED = NOTE.recolor("note_red", N="#FF7A6A")


def lamp(img):
    for y in range(3, GROUND + 1):
        put(img, LAMP_X, y, (110, 110, 130))
    rect(img, LAMP_X - 1, 2, 3, 1, (80, 80, 100))
    put(img, LAMP_X - 1, 3, (255, 220, 130))
    put(img, LAMP_X + 1, 3, (255, 220, 130))
    put(img, LAMP_X, 1, (80, 80, 100))
    # a small warm halo round the lamp, and a pool of light on the snow
    for y in range(0, 7):
        for x in range(LAMP_X - 3, LAMP_X + 4):
            d = math.hypot(x - LAMP_X, y - 3)
            if 0 < d <= 3:
                add(img, x, y, (255, 180, 60), 0.4 * (1 - d / 3.2))
    for y in range(GROUND + 1, 16):
        for x in range(LAMP_X - 6, LAMP_X + 7):
            add(img, x, y, (255, 170, 50), 0.28 * max(0.0, 1 - abs(x - LAMP_X) / 6.5))


def render():
    bg = vgradient((5, 8, 28), (18, 22, 48))
    snow_ground(bg, GROUND + 1, seed=3)
    house(bg, 56, 12, GROUND + 1, 4, (120, 50, 40), (70, 30, 40), chimney=64)
    put(bg, 58, GROUND - 1, (255, 196, 90))
    put(bg, 58, GROUND - 2, (255, 196, 90))
    lamp(bg)
    snow = Snow(seed=31, n=34, period=FPS * 5, laps=(1, 2), bright=(0.3, 0.85))
    rng = random.Random(33)
    notes = []  # [x, y, vx, vy, sprite, age, life, wobble]
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        snow.draw(img, f, drift=t * 0.6)

        singing = (4.6 <= t < 10.2) or t >= 12.0
        dog_howl = 10.6 <= t < 12.2 or t >= 12.0
        # --- carolers ---
        for k, (spr, stop, delay) in enumerate(CAROLERS):
            t0 = delay
            p = phase(f, sec(t0), sec(t0 + 3.6))
            x = lerp(-8 - k * 2, stop, ease_out(p))
            if p < 1:
                fr = (f // 3 + k) % 2
                bob = 0
            elif singing:
                beat = int((t * 2.5) + k * 0.5) % 2
                fr = 3 if beat else 2
                bob = -1 if (beat and k == 1) else 0
            else:
                fr, bob = 2, 0
            blit(img, spr.img(fr), x, CY + bob)
            if singing and p >= 1 and f % 18 == k * 6:
                spr_n = NOTE if (f // 18 + k) % 2 else NOTE2
                notes.append([x + 4, CY - 1, rng.uniform(0.15, 0.35), rng.uniform(-0.35, -0.22), spr_n, 0,
                              rng.randint(22, 34), rng.uniform(0, 6)])

        # --- the dog ---
        if t >= 8.6:
            p = phase(f, sec(8.6), sec(10.4))
            dx = lerp(74, DOG_X, ease_out(p))
            if p < 1:
                fr = (f // 3) % 2
                img_d = DOG.img(fr, flip=True)
            else:
                fr = 3 if (dog_howl and int(t * 2) % 2 == 0) else 2
                img_d = DOG.img(fr, flip=True)
            blit(img, img_d, dx, DOG_Y)
            if p >= 1 and dog_howl and f % 10 == 0 and t < 12.0:
                notes.append([dx + 1, DOG_Y - 3, rng.uniform(-0.25, 0.0), rng.uniform(-0.4, -0.25), NOTE_RED, 0,
                              rng.randint(14, 20), rng.uniform(0, 6) + 100])

        # --- notes drift up, wobbling; the dog's wobble wildly ---
        alive = []
        for n in notes:
            x, y, vx, vy, spr_n, age, life, wob = n
            wild = 2.2 if wob >= 100 else 0.8
            a = 1.0 - (age / life) ** 2
            blit(img, spr_n.img(), x + wild * math.sin(age * 0.4 + wob), y, alpha=a)
            n[0] += vx
            n[1] += vy
            n[5] += 1
            if n[5] < life:
                alive.append(n)
        notes = alive

        if t >= 12.2:
            w = text_width(CAPTION, "tiny")
            x = 56 - w // 2
            reveal = int(lerp(0, w + 1, ease_in_out(phase(f, sec(12.2), sec(12.9)))))
            fade = 1 - phase(f, sec(15.5), sec(16.0))
            draw_text(img, CAPTION, x, 0, None, font="tiny", gradient=((255, 244, 170), (255, 170, 50)),
                      shadow=(120, 20, 30), reveal=reveal, alpha=fade)
        frames.append(img)
    return frames
