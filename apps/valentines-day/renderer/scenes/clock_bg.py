"""Clock card backdrop: a seamless 6 s loop of a deep plum night with small hearts rising slowly, dimmed in the
middle where the time and date are drawn, and a few gold twinkles at the edges (docs/DECISIONS.md D7)."""

from busybar.canvas import W, sec
from vfx import BERRY, CRIMSON, PLUM, RED, ROSE, Drift, gradient, twinkle

NAME = "clock_bg"
TITLE = "Clock backdrop"
SECONDS = 6
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Clock backdrop")]

TWINKLES = [(3, 2, 0.0), (68, 4, 0.35), (5, 12, 0.6), (66, 13, 0.15), (1, 7, 0.8), (70, 9, 0.5)]


def text_mask(x: float, y: float) -> float:
    """Hearts fade out behind the text (columns 8..63)."""
    if 6 <= x <= 63:
        return 0.4
    return 1.0


def render():
    bg = gradient([(0, (20, 2, 20)), (8, PLUM), (15, BERRY)])
    drift = Drift(seed=14, n=16, period=LOOP, sizes=(3, 3, 5, 5, 7), colors=(ROSE, RED, CRIMSON, ROSE),
                  alpha=(0.45, 0.8))
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        drift.draw(img, f, mask=text_mask)
        for x, y, ph in TWINKLES:
            twinkle(img, x, y, f, a=0.8, period=LOOP // 2, ph=ph)
        frames.append(img)
    return frames
