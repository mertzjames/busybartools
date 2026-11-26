"""Scene: The Finale. Night falls over the green hills and fireworks burst in green, white and orange (the colors of
the Irish flag), with gold willows drifting down. HAPPY, then ST. PATRICK'S, shine in the middle of the show, and a
last volley fills the sky."""

import math

from busybar.canvas import W, ease_out, mix, phase, put, sec, vgradient
from busybar.fx import Stars
from busybar.party import GOLD, GOLD_LIGHT, Firework
from pfx import ORANGE, SHAMROCK_HI, WHITE, caption

NAME = "finale"
TITLE = "The Finale"
SECONDS = 16
KEYFRAMES = [(1.2, "Night over the green hills"), (3.2, "Green, white and orange fireworks"),
             (6.0, "Gold willows drift down"), (8.4, "HAPPY"), (11.2, "ST. PATRICK'S"), (14.6, "The last volley")]

GREEN_FW = (60, 230, 90)
TRI = (GREEN_FW, (235, 240, 255), ORANGE)
HAPPY = (sec(7.2), sec(9.8))
NAME_T = (sec(9.8), sec(13.0))

# (burst time s, x, y, colors, kind)
SHOW = [
    (1.4, 14, 5, (GREEN_FW,), "peony"), (2.2, 40, 4, (WHITE,), "ring"), (2.9, 60, 6, (ORANGE,), "peony"),
    (3.6, 26, 3, TRI, "peony"), (4.3, 52, 4, (GOLD,), "willow"), (5.0, 10, 6, (GREEN_FW, WHITE), "palm"),
    (5.6, 36, 5, (ORANGE, GOLD_LIGHT), "ring"), (6.2, 64, 3, (GREEN_FW,), "peony"), (6.8, 22, 4, (GOLD,), "willow"),
    # during the words: small bursts at the edges only
    (8.0, 6, 4, (GREEN_FW,), "ring"), (8.9, 66, 5, (ORANGE,), "ring"), (10.4, 5, 5, (WHITE,), "ring"),
    (11.4, 67, 4, (GREEN_FW,), "ring"), (12.4, 6, 3, (ORANGE,), "ring"),
    # the last volley
    (13.2, 18, 5, TRI, "peony"), (13.5, 54, 4, TRI, "peony"), (13.8, 36, 3, (GOLD,), "willow"),
    (14.1, 8, 6, (GREEN_FW,), "palm"), (14.3, 64, 6, (ORANGE,), "palm"), (14.6, 28, 5, (WHITE,), "ring"),
    (14.8, 46, 5, (GREEN_FW,), "ring"),
]


def background():
    img = vgradient((4, 6, 26), (14, 20, 46))
    for x in range(W):
        top = 13.0 + 1.1 * math.sin(x * 0.13 + 0.7) + 0.5 * math.sin(x * 0.37)
        for y in range(int(top), 16):
            put(img, x, y, mix((22, 84, 40), (12, 52, 26), (y - top) / 3))
    return img


def render():
    bg = background()
    stars = Stars(seed=4, n=16, ymax=10, period=sec(4), color=(200, 210, 255), dim=0.1, bright=0.5)
    works = []
    for i, (t, x, y, colors, kind) in enumerate(SHOW):
        small = 8.0 <= t < 13.0
        works.append(Firework(100 + i, sec(t), x, y, colors=colors, kind=kind, n=18 if small else 30,
                              speed=0.6 if small else 1.0))
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        stars.draw(img, f)
        for w in works:
            w.draw(img, f)
        if HAPPY[0] <= f < HAPPY[1]:
            a = ease_out(phase(f, HAPPY[0], HAPPY[0] + sec(0.6))) * (1 - phase(f, HAPPY[1] - sec(0.4), HAPPY[1]))
            caption(img, "HAPPY", 4, a, back=0.7)
        if NAME_T[0] <= f < NAME_T[1]:
            a = ease_out(phase(f, NAME_T[0], NAME_T[0] + sec(0.6))) * (1 - phase(f, NAME_T[1] - sec(0.4), NAME_T[1]))
            caption(img, "ST. PATRICK'S", 4, a, back=0.7, grad=((200, 255, 180), SHAMROCK_HI))
        frames.append(img)
    return frames
