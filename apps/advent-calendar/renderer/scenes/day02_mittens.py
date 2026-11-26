"""Dec 2: Mittens. A pair of knitted mittens on a yarn string swing on the line while snow drifts past."""

import math

from busybar.canvas import FPS, blit, phase, put, sec
from busybar.sprite import Sprite
from PIL import Image

from common import Snow, sky

NAME = "day02"
TITLE = "Mittens"
SECONDS = 8
KEYFRAMES = [(0.5, "Mittens hang on the line"), (3.0, "A breeze sets them swinging"),
             (5.6, "A gust!"), (7.5, "Back to a gentle sway")]

MITTEN = Sprite("mitten", {
    "R": "#D8202E", "r": "#9A1222", "W": "#F4F4FF", "w": "#B8C4E0", "Y": "#FFD24A",
}, """
..WWWWW.
..WwWwW.
..RRRRR.
..RRRRR.
..RRRRR.
..YYYYY.
.RRRRRR.
RRRRRRRR
RR.RRRRR
.R.RRRRR
...RRRrr
....rr..
""")
MITTEN_G = MITTEN.recolor("mitten_green", R="#2E9E4E", r="#1C6A32", Y="#FFFFFF")

YARN = (255, 214, 92)


def hang(img, sprite, px, py, angle_deg, flip=False):
    """Blit a sprite hanging from its top-center pivot (px, py), rotated by angle."""
    im = sprite.img(flip=flip)
    big = Image.new("RGBA", (im.width * 3, im.height * 3), (0, 0, 0, 0))
    big.paste(im, (im.width, im.height))
    # rotate around the top-center of the original sprite
    rot = big.rotate(angle_deg, resample=Image.NEAREST, center=(im.width * 1.5, im.height))
    blit(img, rot, px - im.width * 1.5, py - im.height)


def render():
    bg = sky(((18, 14, 52), (62, 40, 90)))
    snow = Snow(seed=22, n=30, speed=(0.15, 0.35))
    snow_fast = Snow(seed=23, n=20, speed=(0.3, 0.5), wind=4.0)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        gust = phase(f, sec(5.0), sec(5.6)) * (1 - phase(f, sec(6.2), sec(7.4)))
        (snow_fast if gust > 0.2 else snow).draw(img, f)
        # sagging line between two posts
        amp = 6 + 10 * phase(f, sec(1.5), sec(3.0)) - 4 * phase(f, sec(6.8), sec(8))
        for x in range(72):
            y = 1 + 2.0 * (1 - ((x - 36) / 36) ** 2)
            put(img, x, y, YARN, 0.85)
        for i, (sprite, x) in enumerate(((MITTEN, 24), (MITTEN_G, 47))):
            y = 1 + 2.0 * (1 - ((x - 36) / 36) ** 2)
            ang = amp * math.sin(t * 2.4 + i * 1.3) + gust * 32
            hang(img, sprite, x, y + 1, -ang, flip=i == 1)
            # clothes peg
            put(img, x, y - 1, (190, 140, 80))
            put(img, x, y, (230, 180, 110))
        frames.append(img)
    return frames
