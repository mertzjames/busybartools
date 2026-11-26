"""Scene 1: Owl Post. A snowy owl delivers a letter that bursts into HAPPY / THANKSGIVING."""

import math

from canvas import FPS, blit, ease_in_out, ease_out, lerp, new, phase, sec, vgradient
from font import draw_text, text_width
from fx import SPARKLE, Particles, Stars, moon, sparkle
from sprites import LETTER, OWL

NAME = "owl_post"
TITLE = "Owl Post"
SECONDS = 18
KEYFRAMES = [(2.0, "Owl flies in with a letter"), (5.4, "Drops the letter"), (8.5, "HAPPY..."),
             (12.0, "...THANKSGIVING"), (16.5, "Owl swoops back home")]

GOLD = ((255, 236, 150), (235, 140, 25))
SHADOW = (90, 38, 0)


def render():
    sky = vgradient((6, 4, 26), (26, 10, 44))
    stars = Stars(seed=1, n=22, period=FPS * 4)
    sp = Particles(seed=11)
    frames = []
    letter_y = None
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = sky.copy()
        stars.draw(img, f)
        if not 7.0 <= t < 14.8:
            moon(img, 66, 1)

        # Owl: fly in 0-4s, hover 4-5.4s, exit 5.4-8s; return right->left 15-18s
        wing = (f // 3) % 4
        bob = math.sin(t * 5) * 1.2
        if t < 8:
            if t < 4:
                ox = lerp(-14, 29, ease_out(phase(f, 0, sec(4))))
            elif t < 5.4:
                ox = 29
            else:
                ox = lerp(29, 76, phase(f, sec(5.4), sec(8)) ** 1.6)
            oy = 1 + bob
            blit(img, OWL.img(wing), ox, oy)
            if t < 5.4:
                blit(img, LETTER.img(), ox + 4, oy + 7)
                letter_x, letter_y, letter_v = ox + 4, oy + 7, 0.0
        if 5.4 <= t < 7.0 and letter_y is not None:
            # letter drops and settles at the bottom center
            letter_v += 0.12
            letter_y = min(11, letter_y + letter_v)
            blit(img, LETTER.img(), letter_x, letter_y)
            if letter_y >= 11 and f % 2 == 0:
                sp.emit(letter_x + 2, letter_y, 2, vx=(-0.6, 0.6), vy=(-0.8, -0.2), life=(8, 16), colors=SPARKLE)
        if 7.0 <= t < 7.3 and letter_y is not None:
            sp.emit(letter_x + 2, 12, 6, vx=(-1.5, 1.5), vy=(-1.2, 0.1), life=(10, 22), colors=SPARKLE)

        # Text: HAPPY 7.2-10.2s, THANKSGIVING 10.4-14.6s (wipe in, sparkle dust out)
        for word, t0, t1 in (("HAPPY", 7.2, 10.2), ("THANKSGIVING", 10.4, 14.6)):
            if t0 <= t < t1:
                w = text_width(word)
                x = (72 - w) // 2
                reveal = int(lerp(0, w + 1, ease_in_out(phase(f, sec(t0), sec(t0 + 0.8)))))
                fade = 1.0 - phase(f, sec(t1 - 0.5), sec(t1))
                draw_text(img, word, x, 4, None, gradient=GOLD, shadow=SHADOW, reveal=reveal, alpha=fade)
                if reveal < w:
                    sparkle(img, x + reveal, 4 + (f % 7), f)
                if f % 5 == 0:
                    sp.emit(x + (f * 7) % w, 4 + (f * 3) % 7, 1, vy=(-0.3, -0.1), life=(6, 12), colors=SPARKLE,
                            glow=True)
                if t > t1 - 0.5 and f % 1 == 0:
                    sp.emit(x + (f * 13) % w, 5 + (f * 5) % 5, 2, vx=(-0.3, 0.3), vy=(-0.6, -0.1),
                            life=(8, 14), colors=SPARKLE, glow=True)

        if t >= 15:
            ox = lerp(74, -16, phase(f, sec(15), sec(18)))
            blit(img, OWL.img(wing, flip=True), ox, 2 + bob)

        sp.step_draw(img)
        frames.append(img)
    return frames
