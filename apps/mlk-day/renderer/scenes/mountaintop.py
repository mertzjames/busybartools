"""Scene: Dawn on the Mountaintop (the closing scene). Under the last stars, layered mountain ridges wait in the
dark. The sun rises behind the highest peak, its light runs down the ridges, and the word DREAM appears in the
morning sky."""

import math

from busybar.canvas import FPS, H, W, add, ease_in_out, lerp, mix, phase, put, sec
from busybar.fx import Stars
from mfx import caption, sky, sun

NAME = "mountaintop"
TITLE = "Dawn on the Mountaintop"
SECONDS = 16
KEYFRAMES = [(1.0, "Mountains under the last stars"), (6.0, "First light behind the peak"),
             (10.0, "The sun rises; light runs down the ridges"), (14.5, "DREAM")]

PEAK_X = 20
SUN_X = 20


def ridge(x: float, seed: float, base: float, amp: float) -> float:
    """A smooth, deterministic ridge line (row of the top edge) at column x."""
    return base - amp * (0.55 * math.sin(x * 0.11 + seed) + 0.3 * math.sin(x * 0.27 + seed * 2.1)
                         + 0.15 * math.sin(x * 0.61 + seed * 3.7))


def near_top(x: int) -> float:
    """The nearest ridge with the main peak at PEAK_X (row 5)."""
    d = abs(x - PEAK_X)
    return min(H, 5 + d * 0.62 + 0.8 * math.sin(x * 0.9)) if d < 16 else ridge(x, 2.0, 12.5, 1.5)


LAYERS = [  # (top-edge function, dark color, lit-rim color strength)
    (lambda x: ridge(x, 0.4, 10.5, 2.0), (58, 54, 108), 0.35),
    (lambda x: ridge(x, 1.3, 12.5, 1.8), (38, 36, 84), 0.5),
    (near_top, (22, 24, 58), 0.9),
]


def render():
    stars = Stars(seed=29, n=26, ymax=8, period=FPS * 4, color=(220, 226, 255), dim=0.1, bright=0.75)
    frames = []
    for f in range(sec(SECONDS)):
        p = ease_in_out(phase(f, sec(1.0), sec(12.0)))
        img = sky(0.1 + 0.9 * p, horizon=10)
        stars.draw(img, f, alpha=1 - phase(f, sec(2), sec(9)))
        sy = lerp(9.0, 1.5, ease_in_out(phase(f, sec(4.0), sec(12.5))))
        # soft rays fanning up from the sun once it clears the peak
        rays = ease_in_out(phase(f, sec(8.5), sec(12.0)))
        if rays > 0:
            for y in range(H):
                for x in range(W):
                    ang = math.atan2(sy - y, x - SUN_X)
                    k = 0.5 + 0.5 * math.cos(11 * ang + f * 0.02)
                    d = math.hypot(x - SUN_X, y - sy)
                    add(img, x, y, (255, 180, 90), 0.09 * rays * k ** 6 * max(0.0, 1 - d / 46))
        sun(img, SUN_X, sy, 3.0, strength=0.5 + 0.5 * p)
        light = ease_in_out(phase(f, sec(6.0), sec(13.0)))
        for li, (top_fn, color, rim) in enumerate(LAYERS):
            for x in range(W):
                top = top_fn(x)
                t0 = int(math.floor(top + 0.5))
                for y in range(max(0, t0), H):
                    put(img, x, y, color)
                # the dawn light runs down the ridges, nearest the sun first
                reach = light * 1.2 - abs(x - SUN_X) / 36
                if reach > 0 and 0 <= t0 < H:
                    put(img, x, t0, mix(color, (255, 184, 100), min(1.0, reach) * rim))
                    if li == 2 and t0 + 1 < H:
                        put(img, x, t0 + 1, mix(color, (200, 120, 90), min(1.0, reach) * 0.4))
        a = ease_in_out(phase(f, sec(11.5), sec(13.8))) * (1 - phase(f, sec(15.5), sec(16)))
        caption(img, "DREAM", 1, a, font="big", x=38, back=False)
        frames.append(img)
    return frames
