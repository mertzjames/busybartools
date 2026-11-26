"""Dec 21: North Pole. Under a shimmering aurora, the letters on a candy-striped signpost light up: NORTH POLE."""

import math

from busybar.canvas import FPS, add, phase, put, rect, sec
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles, Stars, sparkle

from common import SNOW, SNOW_SHADE, Snow, aurora, glow, sky

NAME = "day21"
TITLE = "North Pole"
SECONDS = 8
KEYFRAMES = [(0.8, "A signpost under the aurora"), (2.6, "Its letters light up"),
             (5.0, "NORTH POLE"), (7.2, "The workshop is busy")]

WORD = "NORTH POLE"
BOARD_X, BOARD_Y = 17, 4
BOARD_W = text_width(WORD, "tiny") + 4   # 43


def render():
    bg = sky(((2, 6, 26), (14, 22, 56)))
    stars = Stars(seed=210, n=18, ymax=8, period=FPS * 4, dim=0.1, bright=0.8)
    snow = Snow(seed=21, n=22, speed=(0.12, 0.3), ymax=14)
    sp = Particles(seed=210)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        stars.draw(img, f)
        aurora(img, f, y0=1.5, amp=1.4, a=0.55, colors=((50, 230, 150), (170, 90, 255)))
        # workshop on the right: roof, lit windows, chimney smoke
        rect(img, 63, 8, 9, 6, (110, 50, 40))
        for x in range(62, 72):
            put(img, x, 7, SNOW)
            put(img, x, 8, (200, 40, 50))
        for wx in (65, 69):
            put(img, wx, 10, (255, 200, 90), 0.8 + 0.2 * math.sin(f * 0.7 + wx))
            put(img, wx, 11, (255, 200, 90), 0.8 + 0.2 * math.sin(f * 0.7 + wx))
        for k in range(4):
            age = (t * 2 + k * 0.9) % 3.6
            put(img, 66 + math.sin(age * 2) * 0.8, 6 - age * 1.6, (200, 200, 220), 0.5 * (1 - age / 3.6))
        rect(img, 66, 5, 2, 2, (110, 50, 40))
        # snowy ground
        for x in range(72):
            put(img, x, 14, SNOW)
            put(img, x, 15, SNOW_SHADE)
        # candy-striped pole with a gold ball
        for y in range(2, 14):
            put(img, 14, y, (230, 30, 46) if (y + f // 6) % 4 < 2 else (250, 250, 250))
            put(img, 15, y, (180, 20, 36) if (y + f // 6) % 4 < 2 else (200, 200, 210))
        put(img, 14, 1, (255, 214, 92))
        put(img, 15, 1, (255, 214, 92))
        glow(img, 14.5, 1, 2.5, (255, 220, 120), 0.4)
        # the sign: a cream board with an arrow tip
        rect(img, BOARD_X, BOARD_Y, BOARD_W, 7, (246, 236, 206))
        for y in range(BOARD_Y, BOARD_Y + 7):
            d = abs(y - (BOARD_Y + 3))
            for x in range(BOARD_W + BOARD_X, BOARD_W + BOARD_X + 3 - d):
                put(img, x, y, (246, 236, 206))
        for x in range(BOARD_X, BOARD_X + BOARD_W):
            put(img, x, BOARD_Y + 6, (190, 170, 130))
        put(img, BOARD_X + BOARD_W + 2, BOARD_Y + 3, (190, 170, 130))
        # snow cap on the board
        for x in range(BOARD_X, BOARD_X + BOARD_W, 1):
            if (x * 7) % 5:
                put(img, x, BOARD_Y - 1, SNOW, 0.9)
        # letters light up left to right
        tw = text_width(WORD, "tiny")
        reveal = int((tw + 1) * phase(f, sec(1.4), sec(4.0)))
        tx = BOARD_X + 2
        draw_text(img, WORD, tx, BOARD_Y + 1, (120, 120, 140), font="tiny")  # unlit letters
        if reveal > 0:
            draw_text(img, WORD, tx, BOARD_Y + 1, (220, 26, 40), font="tiny", reveal=reveal)
            if reveal <= tw:
                sparkle(img, tx + reveal, BOARD_Y + 2 + (f % 3), f)
        if t > 4.2 and f % 3 == 0:
            sp.emit(tx + (f * 11) % tw, BOARD_Y + 1, 1, vy=(-0.4, -0.1), life=(6, 12), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        snow.draw(img, f, alpha=0.8)
        if t > 4.0:
            add(img, 14, 1, (255, 255, 255), 0.4 + 0.4 * math.sin(f * 0.6))
        frames.append(img)
    return frames
