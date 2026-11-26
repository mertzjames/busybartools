"""Scene: the finale. Red, white, blue and gold fireworks burst over a night skyline of monuments, then a swag of
patriotic bunting drops in along the top, the greeting appears and confetti falls (docs/DECISIONS.md D3)."""

import math

from busybar.canvas import H, W, ease_out, phase, put, sec
from busybar.font import draw_text, text_width
from busybar.party import Confetti, Firework

import pfx

NAME = "finale"
TITLE = "Fireworks Finale"
SECONDS = 14
KEYFRAMES = [(1.4, "Fireworks over the monuments"), (4.0, "Red, white and blue"), (7.2, "A gold willow"),
             (9.4, "The bunting drops in"), (12.5, "HAPPY PRESIDENTS' DAY")]

FW_RED = (255, 56, 66)
FW_WHITE = (255, 255, 255)
FW_BLUE = (90, 130, 255)
FW_GOLD = (255, 200, 70)
CONFETTI = (FW_RED, FW_WHITE, FW_BLUE, FW_GOLD)

BUNTING0 = sec(8.6)
CAPTION0 = sec(9.6)
SUB0 = sec(10.6)


def skyline(img) -> None:
    """Silhouettes of the monuments, in a lit navy-grey (black would be unlit)."""
    c = (40, 44, 84)
    for x in range(W):
        top = 14 - (1 if (x * 5) % 7 < 3 else 0)
        for y in range(top, H):
            put(img, x, y, c)
    for y in range(4, H):  # the obelisk
        put(img, 50, y, c)
        put(img, 51, y, c)
    put(img, 50, 3, c)
    for x in range(10, 23):  # the domed hall
        for y in range(12, H):
            put(img, x, y, c)
    for y, (a, b) in zip(range(8, 12), ((15, 17), (14, 18), (13, 19), (13, 19))):
        for x in range(a, b + 1):
            put(img, x, y, c)
    put(img, 16, 7, c)


def bunting(img, drop: float) -> None:
    """Three swags of blue, white and red across the top, with gold rosettes where they hang. drop 0..1."""
    oy = -5 + 5 * ease_out(drop)
    for x in range(W):
        u = (x % 24) / 24
        depth = 1 + 2.2 * math.sin(math.pi * u) ** 0.8  # rows of cloth below the top edge, deepest mid-swag
        top = math.floor(oy + 0.5)
        n = math.floor(depth + 0.5)
        for i in range(n + 1):
            k = min(2, int(3 * i / (n + 1)))
            put(img, x, top + i, ((54, 84, 200), pfx.WHITE, pfx.RED)[k])
    for x in (0, 24, 48, 71):
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, 1), (0, -1)):
            put(img, x + dx, math.floor(oy + 0.5) + 1 + dy, pfx.GOLD if (dx, dy) != (0, 0) else pfx.GOLD_LIGHT)


def render():
    base = pfx.sky([(0, (6, 8, 34)), (15, (20, 20, 62))])
    skyline(base)
    shows = [
        Firework(1, sec(1.0), 22, 5, (FW_RED,), "peony", n=26),
        Firework(2, sec(1.8), 50, 4, (FW_WHITE,), "ring"),
        Firework(3, sec(2.8), 36, 6, (FW_BLUE, FW_WHITE), "peony", n=30),
        Firework(4, sec(3.8), 12, 4, (FW_RED, FW_WHITE), "palm"),
        Firework(5, sec(4.4), 60, 6, (FW_BLUE,), "peony", n=24),
        Firework(6, sec(5.4), 30, 4, (FW_WHITE, FW_RED), "ring"),
        Firework(7, sec(6.6), 46, 5, None, "willow"),
        Firework(8, sec(7.4), 18, 6, (FW_BLUE, FW_RED), "peony", n=28),
        Firework(9, sec(8.0), 58, 4, (FW_RED,), "ring"),
        # after the greeting: small bursts at the sides only
        Firework(10, sec(10.8), 6, 7, (FW_GOLD,), "peony", n=16, speed=0.6),
        Firework(11, sec(11.8), 66, 7, (FW_BLUE, FW_WHITE), "peony", n=16, speed=0.6),
        Firework(12, sec(12.8), 5, 8, (FW_RED,), "peony", n=16, speed=0.6),
    ]
    confetti = Confetti(21, CAPTION0, 36, 2, n=46, vx=(-2.2, 2.2), vy=(-0.8, 0.4), colors=CONFETTI, spread=30,
                        stagger=12)
    head, sub = "HAPPY", "PRESIDENTS' DAY"
    hx = (W - text_width(head, "big")) // 2
    sx = (W - text_width(sub, "tiny")) // 2
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        cap = phase(f, CAPTION0, CAPTION0 + sec(0.8))
        for fw in shows:
            fw.draw(img, f, 1.0)
        confetti.draw(img, f, 1.0, floor=None)
        if cap > 0:  # darken behind the words so the bursts never cross them
            pfx.dim_rect(img, hx - 1, 4, hx + text_width(head, "big"), 11, 0.75 * cap, feather=2)
            pfx.dim_rect(img, sx - 1, 11, sx + text_width(sub, "tiny"), 15, 0.75 * cap, feather=1)
        if f >= BUNTING0:
            bunting(img, phase(f, BUNTING0, BUNTING0 + sec(0.7)))
        if cap > 0:
            draw_text(img, head, hx, 4, None, font="big", gradient=(pfx.GOLD_LIGHT, pfx.GOLD), shadow=(16, 22, 70),
                      alpha=cap)
        subk = phase(f, SUB0, SUB0 + sec(0.8))
        if subk > 0:
            draw_text(img, sub, sx, 11, None, font="tiny", gradient=((255, 236, 236), (255, 130, 136)),
                      shadow=(16, 22, 70), alpha=subk)
        frames.append(img)
    return frames
