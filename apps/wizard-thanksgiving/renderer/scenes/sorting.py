"""Scene 4 (playlist #6): Sorting the Turkey. The talking hat thinks... GOBBLEDOR!"""

import math

from busybar.canvas import FPS, blit, ease_in_out, ease_out, lerp, phase, put, rect, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import HOUSE, SPARKLE, Particles, Stars
from sprites import HAT, TURKEY

NAME = "sorting"
TITLE = "Sorting the Turkey"
SECONDS = 17
KEYFRAMES = [(2.5, "A turkey waddles in"), (6.0, "The talking hat drops on"), (9.0, "Hmm... difficult..."),
             (12.5, "GOBBLEDOR!"), (16.0, "Off to the feast")]

TX, TY = 28, 6          # turkey resting position
HAT_LAND = (TX + 3, TY - 4)   # brim sits on the turkey's head


def render():
    bg = vgradient((10, 6, 26), (30, 14, 34))
    stars = Stars(seed=7, n=12, ymax=6, period=FPS * 4, dim=0.08, bright=0.5)
    confetti = Particles(seed=71)
    sp = Particles(seed=72)
    frames = []
    word = "GOBBLEDOR!"
    ww = text_width(word)
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        for x in range(72):
            put(img, x, 15, (40, 34, 46))

        # turkey: waddle in 0-4s, look around 4-5s, shuffle feet while sorted, waddle off 14.8s+
        flip = False
        if t < 4.0:
            tx = lerp(-12, TX, phase(f, 0, sec(4.0)))
            tf = (f // 3) % 4
        elif t < 14.8:
            tx, tf = TX, 0
            if 4.2 <= t < 4.7:
                flip = True
            if 7.5 <= t < 11.0:
                tf = (f // 4) % 4  # nervous shuffle
        else:
            tx = lerp(TX, 76, phase(f, sec(14.8), sec(17.0)))
            tf = (f // 3) % 4
        bob = -1 if tf in (1, 3) else 0
        blit(img, TURKEY.img(tf, flip=flip), tx, TY + bob)

        # hat: floats down 5.0-6.6s (wobbling), sits 6.6s+, rides off with the turkey
        if t >= 5.0:
            if t < 6.6:
                k = ease_out(phase(f, sec(5.0), sec(6.6)))
                hx = HAT_LAND[0] + math.sin(t * 6) * 2 * (1 - k)
                hy = lerp(-9, HAT_LAND[1], k)
            else:
                hx, hy = tx + 3, HAT_LAND[1] + bob
                if 7.5 <= t < 11.0:
                    hx += 1 if (f // 5) % 2 else 0  # thinking wiggle
                if 6.6 <= t < 6.8:
                    hy += 1  # squash on landing
            mouth = 1 if ((7.5 <= t < 11.0 and (f // 4) % 2) or 11.0 <= t < 13.6) else 0
            blit(img, HAT.img(mouth), hx, hy)

        if 7.6 <= t < 11.0:
            dots = int((t - 7.6) * 2.5) % 4
            draw_text(img, "HMM" + "." * dots, 46, 3, (230, 220, 200), font="tiny")

        # GOBBLEDOR! 11.0-14.6s: dim the stage, text bursts in, confetti rains
        if 11.0 <= t < 14.6:
            k = ease_out(phase(f, sec(11.0), sec(11.4)))
            fade = 1 - phase(f, sec(14.2), sec(14.6))
            rect(img, 0, 0, 72, 16, (6, 2, 14), 0.7 * k * fade)
            x = (72 - ww) // 2
            y = int(round(lerp(-8, 4, k)))
            cycle = (f // 4) % 2
            grad = ((255, 236, 150), (235, 140, 25)) if cycle == 0 else ((255, 90, 90), (200, 16, 46))
            draw_text(img, word, x, y, None, gradient=grad, shadow=(60, 10, 10), alpha=fade)
            if t < 13.8:
                confetti.emit(f * 5 % 72, -1, 2, vx=(-0.2, 0.2), vy=(0.25, 0.5), life=(20, 40), colors=HOUSE)
            if 11.0 <= t < 11.15:
                sp.emit(36, 7, 20, vx=(-2.5, 2.5), vy=(-1.5, 1.5), life=(8, 16), colors=SPARKLE, glow=True)
        confetti.step_draw(img)
        sp.step_draw(img)
        frames.append(img)
    return frames
