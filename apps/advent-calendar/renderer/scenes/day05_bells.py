"""Dec 5: Jingle Bells. Two golden bells under a red bow swing together and ring out with sparkles."""

import math

from busybar.canvas import FPS, add, blit, phase, put, sec
from busybar.fx import SPARKLE, Particles
from busybar.sprite import Sprite
from PIL import Image

from common import sky

NAME = "day05"
TITLE = "Jingle Bells"
SECONDS = 8
KEYFRAMES = [(0.5, "Two bells under a bow"), (2.2, "They start to swing"), (3.6, "Ding!"),
             (6.4, "Ringing out")]

BELL = Sprite("bell", {"Y": "#FFD24A", "y": "#C8901E", "W": "#FFF6C8", "o": "#8A5A10"}, """
...yy...
..YYYy..
.YWYYYy.
.YWYYYy.
.YYYYYy.
YYYYYYYy
yyyyyyyy
...oo...
""")
BOW = Sprite("bow", {"R": "#E8283A", "r": "#9A1222", "G": "#2E9E4E", "g": "#1C6A32"}, """
gG.RRR.RRR.Gg
gGGRrRRRrRGGg
.GgRRRrRRRgG.
....rR.Rr....
...rR...Rr...
""")


def swing_blit(img, sprite, px, py, ang):
    im = sprite.img()
    big = Image.new("RGBA", (im.width * 3, im.height * 3), (0, 0, 0, 0))
    big.paste(im, (im.width, im.height))
    rot = big.rotate(ang, resample=Image.NEAREST, center=(im.width * 1.5, im.height))
    blit(img, rot, px - im.width * 1.5, py - im.height)


def render():
    bg = sky(((40, 8, 20), (80, 14, 34)))
    sp = Particles(seed=55)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # wallpaper dots
        for y in range(1, 16, 4):
            for x in range((y // 4) % 2 * 4, 72, 8):
                put(img, x, y, (120, 30, 50))
        amp = 26 * phase(f, sec(1.6), sec(2.8))
        a = amp * math.sin((t - 1.6) * 5.2) if t > 1.6 else 0
        # strings from the bow down to the bells
        for k in range(4):
            put(img, 33 - k, 5 + k, (230, 40, 56))
            put(img, 39 + k, 5 + k, (230, 40, 56))
        swing_blit(img, BELL, 30, 8, a)
        swing_blit(img, BELL, 42, 8, -a)
        blit(img, BOW.img(), 30, 2)
        # ring when they meet in the middle (a crosses zero going inward)
        ring = math.sin((t - 1.6) * 5.2) > 0.9 and t > 2.8
        if ring:
            for side in (-1, 1):
                for r in (9, 11):
                    for dy in (-1, 0, 1):
                        add(img, 36 + side * r, 11 + dy, (255, 240, 170), 0.6 if r == 9 else 0.35)
            if f % 2 == 0:
                sp.emit(36, 13, 3, vx=(-1.4, 1.4), vy=(-0.9, 0.2), life=(8, 16), colors=SPARKLE, glow=True)
        # slow golden snow
        for i in range(10):
            x = (i * 29 + f * 0.0) % 72
            y = (i * 5 + f * 0.2 + i) % 16
            if 22 < x < 50:
                continue
            put(img, x, y, (255, 220, 120), 0.35)
        sp.step_draw(img)
        frames.append(img)
    return frames
