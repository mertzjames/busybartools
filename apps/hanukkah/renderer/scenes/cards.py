"""Card backdrops: seamless 4 s loops that the app draws live text over (docs/DECISIONS.md D8).

clock_bg  the clock card (time, then date): a starry blue night with a faint silver shimmer at the edges.
count_bg  the countdown / greeting card: the same night with a lit candle standing at either end.

The middle stays calm because the text goes there. LAYOUT holds every live-text style; build.py tone-maps its
colors and exports it to the app and the mockup.
"""

from __future__ import annotations

from types import SimpleNamespace

from busybar.canvas import put, sec, vgradient
from busybar.fx import Stars
from busybar.party import glitter
from hfx import BLUE_HI, SILVER, WHITE, flame

SECONDS = 4
LOOP = sec(SECONDS)  # 60 frames

NAVY = (10, 16, 60)
LAYOUT = {
    # clock card: silver-white time with a blue shadow, then a gold date
    "time": {"font": "clock", "y": 2, "top": [255, 255, 255], "bottom": [176, 204, 255], "shadow": [24, 50, 160]},
    "date": {"font": "big", "y": 4, "top": [255, 232, 150], "bottom": [236, 168, 48], "shadow": list(NAVY)},
    # count card: a big headline over a tiny line
    "head": {"font": "big", "y": 1, "top": [255, 255, 255], "bottom": [150, 196, 255], "shadow": [24, 50, 160]},
    "sub": {"font": "tiny", "y": 10, "top": [255, 232, 150], "bottom": [236, 168, 48], "shadow": list(NAVY)},
    "time_ms": 4500,
    "date_ms": 3500,
    "count_ms": 4500,  # each page of the count card
}


def night(f: int, stars: Stars, img) -> None:
    stars.draw(img, f)
    for side in ((0, 0, 6, 16), (66, 0, 72, 16)):
        glitter(img, 11 + side[0], f, n=3, period=LOOP, area=side, colors=(SILVER, BLUE_HI), strength=0.55)


def render_clock():
    bg = vgradient((4, 8, 32), (12, 22, 66))
    stars = Stars(seed=17, n=22, period=LOOP, color=(200, 214, 255), dim=0.05, bright=0.45)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        night(f, stars, img)
        frames.append(img)
    return frames


def render_count():
    bg = vgradient((4, 8, 32), (12, 22, 66))
    stars = Stars(seed=19, n=18, period=LOOP, color=(200, 214, 255), dim=0.05, bright=0.4)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        stars.draw(img, f)
        for x, seed in ((2, 5), (68, 9)):  # a candle at each end
            for y in range(9, 16):
                put(img, x, y, WHITE)
                put(img, x + 1, y, (150, 176, 230))
            put(img, x + (seed % 2), 8, (130, 116, 104))
            flame(img, x, 7, f, seed)
        frames.append(img)
    return frames


CLOCK_BG = SimpleNamespace(NAME="clock_bg", TITLE="Clock backdrop", SECONDS=SECONDS,
                           KEYFRAMES=[(0.0, "Clock backdrop")], render=render_clock)
COUNT_BG = SimpleNamespace(NAME="count_bg", TITLE="Count backdrop", SECONDS=SECONDS,
                           KEYFRAMES=[(0.0, "Count backdrop")], render=render_count)
