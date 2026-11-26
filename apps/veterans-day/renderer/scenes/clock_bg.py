"""Clock card backdrop: a seamless 4 s loop of a calm evening sky: a few faint stars along the top and a small flag
on a pole in each bottom corner, waving gently (docs/DECISIONS.md D8). The live time and date are drawn over the
middle, which stays dark and still."""

from busybar.canvas import sec, vgradient
from busybar.fx import Stars

from vfx import draw_flag, pole, tiny_flag_color

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
# Boxes (x0, y0, x1, y1, inclusive) holding edge art: live text must stay clear (tests/text_parity.py).
ART = [(0, 8, 6, 15), (65, 8, 71, 15)]  # the two corner flags on their poles (with the wave)
KEYFRAMES = [(0.0, "Clock backdrop")]


def render():
    bg = vgradient((8, 10, 34), (20, 18, 50))
    stars = Stars(seed=1111, n=9, ymax=2, period=LOOP, color=(210, 220, 255), dim=0.08, bright=0.5)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        # one breeze cycle per loop, so the loop is seamless; the right flag flies toward the edge too
        pole(img, 1, 8, 15, color=(150, 140, 120))
        draw_flag(img, 2, 9, 4, 3, f / LOOP, amp=0.6, wavelength=6, color=tiny_flag_color)
        pole(img, 70, 8, 15, color=(150, 140, 120))
        draw_flag(img, 69, 9, 4, 3, f / LOOP + 0.5, amp=0.6, wavelength=6, color=tiny_flag_color, direction=-1)
        frames.append(img)
    return frames
