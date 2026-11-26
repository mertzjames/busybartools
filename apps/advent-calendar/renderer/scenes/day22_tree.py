"""Dec 22: The Tree. A bare tree gets its lights, its ornaments and its tinsel, then everything twinkles."""

from busybar.canvas import FPS, phase, put, sec, vgradient
from busybar.fx import Particles

from props import draw_tree

NAME = "day22"
TITLE = "The Tree"
SECONDS = 8
KEYFRAMES = [(0.5, "A bare Christmas tree"), (2.2, "The lights go on"), (4.0, "Then the ornaments"),
             (5.4, "Tinsel"), (7.2, "Everything twinkles")]

CX, TOP, BASE = 36, 1, 13


def render():
    bg = vgradient((24, 12, 30), (46, 22, 34))
    # window frames either side and floorboards
    for x in range(72):
        put(bg, x, 15, (110, 66, 34))
    for wx in (6, 58):
        for y in range(2, 11):
            for x in range(wx, wx + 9):
                put(bg, x, y, (14, 22, 60))
        for x in range(wx, wx + 9):
            put(bg, x, 2, (170, 120, 70))
            put(bg, x, 10, (170, 120, 70))
            put(bg, x, 6, (170, 120, 70))
        for y in range(2, 11):
            put(bg, wx, y, (170, 120, 70))
            put(bg, wx + 8, y, (170, 120, 70))
            put(bg, wx + 4, y, (170, 120, 70))
    flakes = Particles(seed=22)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        # snow outside the windows
        for i in range(10):
            wx = (6, 58)[i % 2]
            x = wx + 1 + (i * 3) % 7
            y = 3 + ((i * 5 + f * 0.25) % 7)
            put(img, x, y, (230, 236, 255), 0.7)
        lights = phase(f, sec(1.0), sec(3.2))
        orn = phase(f, sec(3.4), sec(4.6))
        tins = phase(f, sec(4.8), sec(5.8))
        draw_tree(img, CX, TOP, BASE, f, lights=lights, ornaments=orn, tinsel=tins, twinkle=t > 6.0)
        flakes.step_draw(img)
        frames.append(img)
    return frames
