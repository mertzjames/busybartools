"""Countdown card backdrop: a seamless 4 s loop: a deep violet ground framed by two big decorated eggs, one at
each end, with a glint that slides across each in turn (docs/DECISIONS.md D7). The middle stays dark, so the
countdown reads clearly; the eggs sit outside the widest text (SPRING IS, 47 px)."""

from busybar.canvas import add, sec, vgradient

import efx

NAME = "count_bg"
TITLE = "Countdown backdrop"
SECONDS = 4
LOOP = sec(SECONDS)
KEYFRAMES = [(0.0, "Countdown backdrop")]

EGGS = [(1, 3, efx.PINK, "zigzag"), (64, 3, efx.BLUE, "stripes")]


def render():
    bg = vgradient((22, 10, 44), (40, 18, 62))
    for x, y, c, pat in EGGS:
        efx.egg(bg, x, y, 7, 10, c, pat)
    frames = []
    for f in range(LOOP):
        img = bg.copy()
        # a glint sweeping down-right across one egg, then the other
        for k, (x, y, c, pat) in enumerate(EGGS):
            u = (f - k * LOOP // 2) % LOOP / (LOOP / 2)
            if u < 1:
                d = -3 + u * 16
                for dy in range(10):
                    for dx in range(7):
                        s = dx + dy * 0.6 - d
                        if 0 <= s < 1.2 and (dx, dy) in MASK:
                            add(img, x + dx, y + dy, (255, 255, 255), 0.35)
        frames.append(img)
    return frames


MASK = set(efx.egg_mask(7, 10))
