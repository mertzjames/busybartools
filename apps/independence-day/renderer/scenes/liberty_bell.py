"""Scene: the Liberty Bell rings (docs/DECISIONS.md D3, D8). An original pixel-art bronze bell, its famous crack
running up from the lip, hangs from a wooden yoke on a summer morning. It begins to swing; each time the clapper
strikes, rings of sound spread out. Then LIBERTY appears beside it in gold."""

import math

from PIL import Image

from busybar.canvas import W, add, blit, ease_in_out, phase, put, sec
from busybar.font import draw_text, text_width
from busybar.sprite import Sprite

import jfx

NAME = "liberty_bell"
TITLE = "The Liberty Bell"
SECONDS = 14
KEYFRAMES = [(0.8, "The bell, crack and all"), (3.2, "It begins to swing"), (5.2, "The clapper strikes"),
             (7.4, "Rings of sound"), (10.0, "LIBERTY"), (13.2, "Still ringing")]

# bronze, lit: H highlight, B body, D shade, L the raised bands, C the crack (a darker, lit brown in a stepped line,
# which reads as a crack on LEDs where a 1-px zigzag disappears)
BELL_PAL = {"H": "#F0C080", "B": "#C88A48", "D": "#A86C38", "L": "#E8B070", "C": "#4A1E0C", "K": "#6E4A2A"}
BELL = Sprite("bell", BELL_PAL, """
......KKK......
....HBBBBBD....
...HBBBBBBBD...
...HLLLLLLLD...
...HBBBBBBBD...
...HBBBCBBBD...
...HBBBCBBBD...
...HBBBBCBBD...
...HBBBBCBBD...
..HBBBBBBCBBD..
..HLLLLLLCLLD..
.HBBBBBBBBCBBD.
LLLLLLLLLLCLLLL
""")
BELL_X, BELL_Y = 9, 1  # top-left of the bell sprite; it swings about its crown (BELL_X + 7, BELL_Y)
CAPTION = "LIBERTY"
CAP0 = sec(8.6)


def swing_angle(f):
    """Swing (pixels of shear per row): builds up from 2 s, full from 4.5 s, eases down after 10 s."""
    t = f / 15
    amp = 0.32 * ease_in_out(phase(f, sec(2.0), sec(4.5))) * (1 - 0.6 * ease_in_out(phase(f, sec(10.0), sec(14.0))))
    return amp * math.sin(2 * math.pi * (t - 2.0) / 1.6)


def sheared(sprite: Image.Image, a: float) -> Image.Image:
    """Swing a hanging sprite by shifting each row a whole number of pixels (rotation mangles pixel art)."""
    w, h = sprite.size
    pad = 5
    out = Image.new("RGBA", (w + 2 * pad, h), (0, 0, 0, 0))
    for y in range(h):
        dx = math.floor(a * y + 0.5)
        out.alpha_composite(sprite.crop((0, y, w, y + 1)), (pad + dx, y))
    return out


def tower(img):
    """A generic red-brick hall with a white steeple at the far right, softened by the haze."""
    c, trim = (150, 84, 70), (226, 222, 210)
    for x in range(54, W):
        for y in range(9, 14):
            put(img, x, y, c)
        if x % 3 == 0:
            for y in (10, 12):
                put(img, x, y, (230, 214, 170))
    for x in range(60, 66):
        for y in range(4, 9):
            put(img, x, y, c)
    for x in range(61, 65):
        put(img, x, 3, trim)
    for x in range(62, 64):
        put(img, x, 2, trim)
        put(img, x, 1, trim)
    put(img, 62, 0, trim)
    put(img, 62, 5, (255, 240, 200))
    put(img, 63, 5, (255, 240, 200))


def ring_waves(img, f, strikes):
    """Arcs of sound spreading out from the bell after each strike."""
    cx, cy = BELL_X + 7, BELL_Y + 8
    for s0 in strikes:
        age = f - s0
        if not 0 <= age < 22:
            continue
        r = 9 + age * 1.3
        k = 1.0 * (1 - age / 22) ** 0.7
        for side in (-1, 1):
            for dy in range(-4, 5):
                d2 = r * r - (dy * 1.6) ** 2
                if d2 <= 0:
                    continue
                x = cx + side * math.sqrt(d2)
                add(img, x, cy + dy, (255, 200, 80), k * (1 - abs(dy) / 6))
                add(img, x - side, cy + dy, (255, 170, 60), 0.4 * k * (1 - abs(dy) / 6))


def render():
    base = jfx.sky([(0, (30, 70, 180)), (9, (60, 110, 206)), (13, (110, 150, 220))])
    tower(base)
    for x in range(W):  # a lawn and a brick path
        put(base, x, 14, (70, 150, 70))
        put(base, x, 15, (160, 96, 70) if x % 4 else (130, 76, 56))
    # the yoke's frame: two posts and the beam (lit wood)
    for y in range(1, 14):
        put(base, BELL_X - 2, y, (128, 84, 48))
        put(base, BELL_X + 16, y, (128, 84, 48))
    for x in range(BELL_X - 3, BELL_X + 18):
        put(base, x, 0, (176, 122, 70))
        put(base, x, 1, (136, 90, 52))
    # find the strikes: the frames where the swing turns at either end (after it has built up)
    angles = [swing_angle(f) for f in range(sec(SECONDS) + 1)]
    strikes = [f for f in range(1, sec(SECONDS)) if abs(angles[f]) > 0.12 and
               abs(angles[f]) >= abs(angles[f - 1]) and abs(angles[f]) > abs(angles[f + 1])]
    cap_x = 30 + (W - 30 - text_width(CAPTION)) // 2
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        a = angles[f]
        cap = phase(f, CAP0, CAP0 + sec(1.0))
        if cap > 0:  # haze over the hall behind the caption
            for y in range(3, 13):
                for x in range(cap_x - 2, cap_x + text_width(CAPTION) + 2):
                    put(img, x, y, (30, 60, 150), 0.7 * cap)
        ring_waves(img, f, strikes)
        bell = sheared(BELL.img(0), a)
        blit(img, bell, BELL_X - 5, BELL_Y)
        # the clapper hangs below the lip, lagging the swing
        lag = swing_angle(f - 3)
        put(img, BELL_X + 7 + math.floor(lag * 14 + 0.5), BELL_Y + 13, (200, 180, 160))
        if cap > 0:
            draw_text(img, CAPTION, cap_x, 4, None, font="big", gradient=(jfx.GOLD_LIGHT, (230, 150, 40)),
                      shadow=(90, 40, 30), alpha=cap)
        frames.append(img)
    return frames
