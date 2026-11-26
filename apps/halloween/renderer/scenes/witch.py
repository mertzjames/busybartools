"""Scene: The Witch's Flight. Under a big full moon, a witch on her broom swoops in from the left, trailing green,
purple and gold sparkles. She crosses in front of the moon as a silhouette with a lit green face, dips low over the
rooftops, then circles back from the right, higher and smaller, and flies off past the moon."""

import math

from busybar.canvas import FPS, H, W, add, blit, put, sec
from hfx import NIGHT_MID, NIGHT_TOP, frame_t, full_moon, gradient, in_moon, stars
from sprites import WITCH, WITCH_FAR

NAME = "witch"
TITLE = "The Witch's Flight"
SECONDS = 14
KEYFRAMES = [(1.4, "A witch swoops in"), (3.4, "A trail of sparkles"), (4.8, "Across the moon"),
             (7.0, "Off to the right"), (10.2, "Back the other way, far off"), (12.8, "Off into the night")]

MOON = (50.0, 7.0, 6.6)
PASS1 = (0.4, 7.2)  # left to right
PASS2 = (8.2, 13.6)  # right to left, higher and smaller (every other column, like distance)
SPARKS = ((150, 255, 70), (190, 110, 255), (255, 220, 90), (255, 255, 255))


def pos1(t: float):
    u = (t - PASS1[0]) / (PASS1[1] - PASS1[0])
    if not 0 <= u <= 1:
        return None
    x = -20 + u * (W + 24)
    y = 0.5 + 2.5 * math.sin(math.pi * u) + 0.6 * math.sin(t * 3.0)
    return x, y


def pos2(t: float):
    u = (t - PASS2[0]) / (PASS2[1] - PASS2[0])
    if not 0 <= u <= 1:
        return None
    x = W + 2 - u * (W + 14)
    y = 4.5 - 2.5 * math.sin(math.pi * u) + 0.5 * math.sin(t * 4.0)
    return x, y


def render():
    bg = gradient([(0, NIGHT_TOP), (9, NIGHT_MID), (15, (72, 24, 86))])
    full_moon(bg, *MOON, halo=0.8)
    # rooftops along the bottom: lit violet shapes with a few warm windows
    roofs = [15] * W
    x = 0
    shapes = [(7, 13), (5, 14), (8, 12), (6, 13), (9, 12), (5, 14), (7, 13), (8, 12), (6, 14), (11, 13)]
    for w, top in shapes:
        for xx in range(x, min(W, x + w)):
            peak = top - min(xx - x, x + w - 1 - xx) // 2 if w >= 7 else top
            roofs[xx] = peak
        x += w
    for xx in range(W):
        for y in range(roofs[xx], H):
            put(bg, xx, y, (58, 32, 80))
        put(bg, xx, roofs[xx], (110, 80, 140))
    for wx in (3, 14, 22, 33, 45, 58, 66):
        put(bg, wx, 15, (255, 200, 90), 0.85)
    frames = []
    trail: list[tuple[float, float, int, int]] = []  # (x, y, birth frame, color index)
    for f in range(sec(SECONDS)):
        t = frame_t(f)
        img = bg.copy()
        stars(img, 31, 20, f, ymax=11, avoid=lambda x, y: in_moon(x, y, *MOON))
        p1, p2 = pos1(t), pos2(t)
        if p1 and f % 2 == 0:
            trail.append((p1[0] + 1, p1[1] + 9.5, f, (f // 2) % 4))
        if p2 and f % 3 == 0:
            trail.append((p2[0] + 8, p2[1] + 4.5, f, (f // 3) % 4))
        alive = []
        for x, y, b, ci in trail:
            age = f - b
            if age < 20:
                k = 1 - age / 20
                add(img, x - age * 0.15, y + age * 0.12, SPARKS[ci], k)
                alive.append((x, y, b, ci))
        trail = alive
        if p2:
            blit(img, WITCH_FAR.img(0, flip=True), p2[0], p2[1])
        if p1:
            blit(img, WITCH.img((f // 3) % 2), p1[0], p1[1])
        frames.append(img)
    return frames
