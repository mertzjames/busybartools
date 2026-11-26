"""Countdown, greeting and phrase backdrop: a seamless 4 s loop. Cobwebs hang in both top corners and a small
jack-o'-lantern glows in each bottom corner, over a violet night with a few faint stars (docs/DECISIONS.md D7).
The corner art stays in columns 0-7 and 64-71, so every text line fits the 56 px between (scenes.text.TEXT_GAP)."""

from busybar.canvas import H, sec
from hfx import NIGHT_MID, NIGHT_TOP, cobweb, gradient, pumpkin, pumpkin_glow, stars

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

LANTERNS = ((0, 10, "classic"), (65, 10, "happy"))  # (x, y, face) of 7x6 jack-o'-lanterns
LW, LH = 7, 6


def render():
    bg = gradient([(0, NIGHT_TOP), (8, NIGHT_MID), (15, (46, 12, 62))])
    cobweb(bg, "tl", 7)
    cobweb(bg, "tr", 7)
    for x, y, _ in LANTERNS:
        pumpkin_glow(bg, x, y, LW, LH, 0.8)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars(img, 11, 12, f, ymax=H, period=LOOP, a=0.3, avoid=lambda x, y: x < 8 or x > 63)
        for i, (x, y, face) in enumerate(LANTERNS):
            pumpkin(img, x, y, LW, LH, face, lit=1.0, f=f, seed=i, small=True)
        frames.append(img)
    return frames
