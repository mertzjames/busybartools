"""A handmade card: a crayon-decorated card lies on a wooden table among crayons. It slides over and opens like a
book to show a big red heart on one page and MOM in crayon letters on the other, and the heart beats
(docs/DECISIONS.md D3)."""

import math

from PIL import Image

from busybar.canvas import H, W, ease_in_out, mix, phase, put, sec
from busybar.font import draw_text
from busybar.party import glitter

import mfx

NAME = "card"
TITLE = "A Handmade Card"
SECONDS = 12
N = sec(SECONDS)
KEYFRAMES = [(0.8, "A card made with crayons"), (2.6, "It slides over"), (3.6, "It opens..."),
             (5.6, "A heart, and MOM"), (9.5, "Made with love")]

PW, PH = 20, 14  # one page
TOP = 1
SLIDE0, SLIDE1 = sec(1.6), sec(2.8)
OPEN0, OPEN1 = sec(3.0), sec(4.6)
SPINE = 36
PAPER = (222, 180, 196)
PAPER_DK = (188, 140, 162)
CRAYONS = [((10, 3), mfx.ROSE, 1), ((4, 8), (60, 150, 255), -1), ((12, 12), mfx.GREEN, 1), ((61, 4), mfx.YELLOW, -1),
           ((66, 10), mfx.LAVENDER, 1), ((57, 13), mfx.ORANGE, 1)]


def page(art: str) -> Image.Image:
    img = Image.new("RGBA", (PW, PH), PAPER + (255,))
    if art == "front":
        for x in range(PW):  # a lavender squiggle border along the top and bottom
            put(img, x, 1 + (x // 2) % 2, mfx.LAVENDER_DK)
            put(img, x, PH - 2 - (x // 2) % 2, mfx.LAVENDER_DK)
        for y in range(7, 12):
            put(img, 9, y, mfx.GREEN_DK)
        put(img, 10, 9, mfx.GREEN)
        put(img, 11, 8, mfx.GREEN)
        mfx.big_daisy(img, 9, 6, mfx.PINK_DK, mfx.ORANGE)
        mfx.heart(img, 15, 4, 3, mfx.ROSE)
        mfx.heart(img, 4, 8, 3, mfx.ROSE)
    elif art == "left":  # the inside of the cover: a big heart and a few crayon stars
        mfx.heart(img, 10, 3, 9, mfx.ROSE, mfx.ROSE_HI)
        for x, y in ((3, 2), (16, 11), (3, 11), (17, 2)):
            put(img, x, y, mfx.ORANGE)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                put(img, x + dx, y + dy, mfx.YELLOW_DK, 0.8)
    elif art == "right":  # MOM in three crayon colors
        x = 2
        for ch, c in zip("MOM", (mfx.ROSE, (40, 110, 230), (140, 60, 230))):
            x = draw_text(img, ch, x, 4, c) + 1
        for xx in range(2, 18):  # a wavy underline
            put(img, xx, 12 - (xx // 2) % 2, mfx.GREEN_DK)
    else:  # the back of the cover: plain paper
        pass
    for y in range(PH):  # a soft darker edge
        put(img, 0, y, PAPER_DK)
        put(img, PW - 1, y, PAPER_DK)
    for x in range(PW):
        put(img, x, 0, PAPER_DK)
        put(img, x, PH - 1, PAPER_DK)
    return img


def squashed(dst, src: Image.Image, x0: int, w: int, mirror: bool = False, shade: float = 0.0) -> None:
    """Draw `src` squeezed to `w` columns starting at x0 (column sampling keeps pixels crisp)."""
    if w <= 0:
        return
    s = src.load()
    for i in range(w):
        u = min(PW - 1, int(i * PW / w))
        if mirror:
            u = PW - 1 - u
        for v in range(PH):
            c = s[u, v][:3]
            put(dst, x0 + i, TOP + v, mix(c, (0, 0, 0), shade))


def table():
    img = Image.new("RGBA", (W, H))
    for y in range(H):
        for x in range(W):
            plank = (y // 4) % 2
            grain = (x * 7 + y * 13) % 11 == 0
            c = (96, 54, 34) if plank else (108, 62, 38)
            put(img, x, y, mix(c, (70, 38, 24), 0.6) if grain or y % 4 == 3 else c)
    for (x, y), c, d in CRAYONS:
        for k in range(5):
            put(img, x + k * d, y, c if k < 4 else mix(c, mfx.WHITE, 0.4))
        put(img, x - d, y, mix(c, (0, 0, 0), 0.3))
    return img


def render():
    base = table()
    front, left, right = page("front"), page("left"), page("right")
    frames = []
    for f in range(N):
        img = base.copy()
        if f < OPEN0:
            x0 = 26 + int(round(10 * ease_in_out(phase(f, SLIDE0, SLIDE1))))
            squashed(img, front, x0, PW)
        else:
            p = ease_in_out(phase(f, OPEN0, OPEN1))
            squashed(img, right, SPINE, PW)
            c = math.cos(math.pi * p)
            w = int(round(PW * abs(c)))
            if c > 0:  # the cover lifts: the front squeezes toward the spine
                squashed(img, front, SPINE, w, shade=0.35 * p)
            else:  # and lands on the left as the inside page
                squashed(img, left, SPINE - w, w, shade=0.35 * (1 - p))
            for y in range(TOP, TOP + PH):  # the fold
                put(img, SPINE, y, PAPER_DK)
        if f >= OPEN1:  # the heart beats, and glitter twinkles over the card
            beat = ((f - OPEN1) % sec(1.2)) < 3
            if beat:
                mfx.heart(img, SPINE - 10, TOP + 2, 9, mfx.ROSE, mfx.ROSE_HI, halo=mfx.ROSE_HI)
            k = min(1.0, (f - OPEN1) / sec(1))
            glitter(img, seed=3, f=f, n=10, period=sec(2), colors=(mfx.YELLOW_HI, mfx.WHITE),
                    area=(14, 0, 58, 16), strength=0.6 * k)
        frames.append(img)
    return frames
