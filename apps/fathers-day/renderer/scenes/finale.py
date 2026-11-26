"""Scene: the finale. Summer-night fireworks over a dark treeline; HAPPY / FATHER'S DAY wipes in between the bursts,
then a gold trophy rises beside #1 DAD (an app-local '#' glyph, registered in scenes/text.py) with confetti and a
glint across the cup."""

import math

from busybar import font
from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.fx import Stars
from busybar.party import Confetti, Firework

import ffx

from . import text as _text  # noqa: F401  (registers the big font's app-local "#" glyph)

NAME = "finale"
TITLE = "Fireworks for Dad"
SECONDS = 14
KEYFRAMES = [(1.2, "Summer-night fireworks"), (3.0, "HAPPY"), (5.4, "FATHER'S DAY"), (8.6, "A trophy rises"),
             (10.0, "#1 DAD"), (12.4, "Confetti and a glint")]

WARM = ((255, 246, 222), (255, 156, 64))
GOLDEN = ((255, 248, 200), (255, 178, 40))
SHADOW = (12, 20, 58)

TROPHY = [
    ".GGGGGGGGG.",
    "HLGGGGGGGGH",
    "H.LGGGGGG.H",
    "H.LGGGGGG.H",
    ".HLGGGGGGH.",
    "...LGGGG...",
    "....LGG....",
    ".....G.....",
    ".....G.....",
    "...BBBBB...",
    "..BBBBBBB..",
]
TROPHY_PAL = {"G": (255, 192, 50), "L": (255, 238, 150), "H": (214, 146, 30), "B": (150, 92, 56)}
TROPHY_X = 7
CUP_ROWS = range(0, 7)

# fireworks: summer colors (sky blue, lime, sunset orange, gold, pink, white); bursts kept off the text where possible
BLUE, LIME, ORANGE, GOLD, PINK, WHITE = (60, 190, 255), (150, 255, 80), (255, 140, 40), (255, 200, 60), \
    (255, 80, 170), (240, 240, 255)


def fireworks():
    spec = [  # (t0 s, x, y, colors, kind)
        (0.5, 14, 5, (BLUE, WHITE), "peony"), (1.1, 54, 4, (ORANGE, GOLD), "ring"), (1.9, 34, 6, (LIME,), "peony"),
        (3.0, 64, 4, (PINK, WHITE), "peony"), (4.2, 7, 3, (GOLD,), "willow"), (5.6, 62, 5, (BLUE, LIME), "ring"),
        (6.8, 36, 5, (ORANGE, PINK), "palm"), (7.6, 20, 4, (WHITE, BLUE), "peony"),
        (9.0, 64, 3, (GOLD,), "willow"), (10.4, 62, 6, (PINK, ORANGE), "peony"), (11.8, 66, 4, (LIME, BLUE), "ring"),
        (13.0, 60, 3, (GOLD, WHITE), "peony"),
    ]
    return [Firework(seed=100 + i, t0=sec(t0), x=x, y=y, colors=c, kind=k, n=26, life=22)
            for i, (t0, x, y, c, k) in enumerate(spec)]


def base_frame():
    img = ffx.sky([(0, (6, 8, 30)), (10, (14, 20, 58)), (15, (24, 30, 72))])
    for x in range(W):  # a dark treeline along the bottom (a lit deep green, never black)
        top = 13 - (1 if math.sin(x * 0.5) + math.sin(x * 0.19 + 1) > 0.7 else 0) - (1 if x % 11 == 3 else 0)
        for y in range(top, H):
            put(img, x, y, (16, 46, 34) if (x + y) % 3 else (20, 56, 40))
    return img


def trophy(img, top: int, glint: float | None) -> None:
    for dy, row in enumerate(TROPHY):
        for dx, ch in enumerate(row):
            if ch != ".":
                put(img, TROPHY_X + dx, top + dy, TROPHY_PAL[ch])
    if glint is not None:  # a diagonal shine sweeping across the cup
        gx = TROPHY_X - 2 + glint * 15
        for dy in CUP_ROWS:
            x = ffx.rnd(gx - dy * 0.5)
            if 0 <= x - TROPHY_X < 11 and TROPHY[dy][x - TROPHY_X] in "GL":
                put(img, x, top + dy, (255, 255, 240))


def render():
    base = base_frame()
    stars = Stars(seed=41, n=20, ymax=11, period=sec(7), color=(220, 224, 255), dim=0.08, bright=0.6)
    works = fireworks()
    confetti = Confetti(seed=12, t0=sec(9.6), x=36, y=-2, n=40, vx=(-1.8, 1.8), vy=(0.0, 0.3), fall=(0.05, 0.1),
                        colors=(BLUE, LIME, ORANGE, GOLD, PINK, WHITE), spread=26, stagger=sec(2))
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        s = f / 15
        stars.draw(img, f)
        for w in works:
            w.draw(img, f)

        # HAPPY / FATHER'S DAY, wiped in, then out
        if 2.2 <= s < 7.4:
            out = phase(f, sec(7.0), sec(7.4))
            ffx.dim_rect(img, 18, 0, 53, 7, 0.55 * (1 - out), feather=2)
            ffx.dim_rect(img, 3, 8, 68, 15, 0.55 * (1 - out), feather=1)
            a = 1 - out
            r1 = int(phase(f, sec(2.2), sec(2.8)) * 40)
            r2 = int(phase(f, sec(3.8), sec(4.8)) * 80)
            for text, y, reveal in (("HAPPY", 0, r1), ("FATHER'S DAY", 8, r2)):
                font.draw_text(img, text, (W - font.text_width(text)) // 2, y, None, gradient=WARM, shadow=SHADOW,
                               alpha=a, reveal=reveal)

        # the trophy rises; #1 DAD wipes in beside it; a glint crosses the cup
        if s >= 7.8:
            rise = phase(f, sec(7.8), sec(8.8))
            top = ffx.rnd(16 - 13 * (1 - (1 - rise) ** 3))
            g = None
            for t0 in (10.6, 12.8):
                if t0 <= s < t0 + 0.6:
                    g = (s - t0) / 0.6
            trophy(img, top, g)
            if rise >= 1:  # a soft glow under the cup, steady
                for dx in range(-1, 12):
                    add(img, TROPHY_X + dx, 14, (255, 190, 60), 0.15)
        if s >= 9.2:
            text = "#1 DAD"
            x0 = 24
            ffx.dim_rect(img, x0, 4, x0 + font.text_width(text), 11, 0.5, feather=2)
            font.draw_text(img, text, x0, 4, None, gradient=GOLDEN, shadow=SHADOW,
                           reveal=int(phase(f, sec(9.2), sec(9.9)) * 40))
        if s >= 9.6:
            confetti.draw(img, f, floor=15)
        frames.append(img)
    return frames
