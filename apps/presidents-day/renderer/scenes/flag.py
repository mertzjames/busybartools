"""Scene: the flag is raised on a bright winter morning and waves in the breeze (docs/DECISIONS.md D3).

Thirteen stripes (one row each, red at the top and bottom) and a blue canton with the stars as dots. Clouds drift
behind; a gust at 9 s makes the flag snap out wider.
"""

import math

from busybar.canvas import H, W, ease_in_out, phase, put, sec

import pfx

NAME = "flag"
TITLE = "Old Glory"
SECONDS = 14
KEYFRAMES = [(0.5, "A flagpole on a winter morning"), (2.5, "The flag goes up"), (5.0, "At the top of the pole"),
             (9.5, "A gust snaps it out"), (13.0, "Waving in the breeze")]

POLE_X = 15
FLAG_W = 40
CANTON_W = 16
TOP = 1


def clouds(img, f):
    """Soft clouds drifting right to left, behind the flag (seamless over the scene)."""
    for i, (x0, y, w, speed) in enumerate(((10, 3, 9, 0.10), (44, 1, 12, 0.07), (70, 5, 8, 0.12), (100, 2, 10, 0.09))):
        x = (x0 - f * speed) % 110 - 20
        for dx in range(w):
            k = math.sin(math.pi * (dx + 0.5) / w)
            put(img, x + dx, y, (200, 214, 240), 0.35 * k)
            put(img, x + dx, y + 1, (180, 196, 232), 0.55 * k)
            if 1 < dx < w - 2:
                put(img, x + dx, y - 1, (210, 222, 246), 0.3 * k)


def render():
    base = pfx.sky([(0, (70, 126, 214)), (10, (120, 166, 230)), (14, (176, 204, 240))])
    frames = []
    t = 0.0
    for f in range(sec(SECONDS)):
        img = base.copy()
        clouds(img, f)
        pfx.glow(img, 64.5, 3.5, 8, (255, 240, 190), 0.6)  # the low winter sun
        for dx in (0, 1):
            for dy in (0, 1):
                put(img, 64 + dx, 3 + dy, (255, 250, 226))
        # distant slate hills with snow along their crests
        for x in range(W):
            top = 13 - (1 if 24 < x < 44 or x > 58 else 0) - (1 if 30 < x < 38 else 0)
            for y in range(top, H):
                put(img, x, y, (70, 92, 128) if y > top else (214, 224, 244))
        pfx.pole(img, POLE_X, 0, 15)
        put(img, POLE_X - 1, 15, (130, 112, 80))
        put(img, POLE_X + 1, 15, (130, 112, 80))
        rise = ease_in_out(phase(f, sec(0.8), sec(4.5)))
        y0 = round(H + 1 - (H + 1 - TOP) * rise)
        gust = math.sin(math.pi * phase(f, sec(8.5), sec(11.5)))
        amp = 1.1 + 0.5 * gust
        t += 1 / (30 - 10 * gust)
        unfurl = 0.6 + 0.4 * ease_in_out(phase(f, sec(0.8), sec(5.0)))
        pfx.draw_flag(img, POLE_X + 1, y0, FLAG_W, t, cw=CANTON_W, amp=amp, unfurl=unfurl)
        frames.append(img)
    return frames
