"""Scene: the gift. A wrapped present with a DAD tag sits on the table and gives an eager shake. The ribbon unties,
the lid pops off, and out springs a necktie like a jack-in-the-box, in the wildest pattern imaginable. Confetti flies,
TA-DA!, and the tie keeps changing its mind: stripes, polka dots, checks, zigzags."""

import math

from busybar import font
from busybar.canvas import H, W, add, mix, phase, put, sec
from busybar.party import Confetti

import ffx

NAME = "gift"
TITLE = "The Wild Tie"
SECONDS = 14
KEYFRAMES = [(1.0, "A present for Dad"), (2.0, "It shakes!"), (3.4, "The ribbon unties"), (4.6, "The lid pops"),
             (5.6, "A tie springs out"), (7.4, "TA-DA!"), (9.6, "Polka dots?"), (11.2, "Checks?"),
             (13.0, "Rainbow zigzags")]

BOX_X0, BOX_X1 = 40, 55  # the box front, columns
BOX_TOP = 10  # rows 10-14; the table is row 15
TIE_CX = 47
PAPER = (54, 92, 214)
PAPER_DOT = (255, 214, 80)
RIBBON = (236, 44, 70)
RIBBON_HI = (255, 120, 140)

# the tie: (row offset, half-width) from the knot down to the point (the point stays inside the box)
TIE_ROWS = [(0, 1), (1, 1), (2, 1), (3, 1), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3), (10, 2), (11, 1), (12, 0)]
WILD = [(255, 120, 30), (40, 220, 230), (240, 60, 200), (150, 240, 60), (255, 230, 60)]


def tie_color(u: int, v: int, mode: int, f: int):
    """Color of tie cell (u across, v down) in one of four wild patterns (some drift with the frame)."""
    if mode == 0:  # diagonal stripes that scroll
        return WILD[((u + v + f // 3) // 1) % len(WILD)]
    if mode == 1:  # polka dots on purple
        return (255, 236, 80) if (u + 2 * v) % 3 == 0 else (130, 60, 220)
    if mode == 2:  # red and white checks
        return (240, 50, 60) if (u + v) % 2 == 0 else (250, 246, 236)
    # rainbow zigzag rows
    return WILD[(v + abs(((u + f // 4) % 4) - 2)) % len(WILD)]


def draw_tie(img, top: float, mode: int, f: int, sway: float = 0.0) -> None:
    for dv, half in TIE_ROWS:
        y = ffx.rnd(top) + dv
        shift = ffx.rnd(sway * (dv / 10))  # sway the point more than the knot (a per-row shear)
        for u in range(-half, half + 1):
            c = tie_color(u + 3, dv, mode, f)
            if dv < 2:
                c = mix(c, (255, 255, 255), 0.15)  # the knot catches a little light
            put(img, TIE_CX + u + shift, y, c)
    y = ffx.rnd(top)
    for sgn in (-1, 1):  # white collar points either side of the knot, so it reads as a necktie
        put(img, TIE_CX + 2 * sgn, y, (250, 250, 250))
        put(img, TIE_CX + 2 * sgn, y + 1, (226, 226, 232))
        put(img, TIE_CX + 3 * sgn, y + 1, (250, 250, 250))


def box_front(img) -> None:
    for y in range(BOX_TOP, 15):
        for x in range(BOX_X0, BOX_X1 + 1):
            c = PAPER
            if (x + 2 * y) % 5 == 0 and y % 2 == 0:
                c = PAPER_DOT
            put(img, x, y, c)
    for x in range(BOX_X0, BOX_X1 + 1):  # a darker band at the top edge (the inside rim)
        put(img, x, BOX_TOP, mix(PAPER, (20, 30, 80), 0.4))


def ribbon(img, dy: int = 0, gone: float = 0.0) -> None:
    """The ribbon cross on the box front; `gone` (0..1) pulls it up and away."""
    if gone >= 1:
        return
    lift = ffx.rnd(gone * 8)
    for y in range(BOX_TOP - 2 + dy, 15 + dy - lift):
        put(img, TIE_CX, y, RIBBON)
        put(img, TIE_CX + 1, y, RIBBON_HI if y % 2 else RIBBON)
    if gone == 0:
        for x in range(BOX_X0, BOX_X1 + 1):
            put(img, x, 12 + dy, RIBBON)


def lid(img, x0: float, y0: float, tilt: float = 0.0, bow: bool = True) -> None:
    """The lid (18 x 2) with its bow; `tilt` raises the right end by up to that many rows (per-column shear)."""
    for i in range(BOX_X1 - BOX_X0 + 3):
        dy = ffx.rnd(-tilt * i / (BOX_X1 - BOX_X0 + 2))
        x = ffx.rnd(x0) + i
        for r in (0, 1):
            c = mix(PAPER, (255, 255, 255), 0.12) if r == 0 else PAPER
            if i in (8, 9):
                c = RIBBON
            put(img, x, ffx.rnd(y0) + r + dy, c)
    if bow:
        bx = ffx.rnd(x0) + 8
        by = ffx.rnd(y0) - ffx.rnd(tilt * 0.45)
        for dx, dy in ((-2, -1), (-1, -1), (-2, -2), (2, -1), (3, -1), (3, -2), (0, -1), (1, -1)):
            put(img, bx + dx, by + dy, RIBBON if dx not in (0, 1) else RIBBON_HI)


def tag(img) -> None:
    """A white tag hanging off the box's left edge on a string, reading DAD (tiny font)."""
    for y in range(10, 16):
        for x in range(28, 39):
            put(img, x, y, (248, 246, 236) if (x, y) not in ((28, 10), (28, 15)) else (190, 186, 176))
    put(img, 39, 10, (220, 220, 210))  # the string to the box
    font.draw_text(img, "DAD", 29, 11, (220, 50, 64), font="tiny")


def base_frame():
    img = ffx.sky([(0, (20, 60, 78)), (9, (28, 80, 96)), (14, (36, 92, 104))])
    for x in range(0, W, 6):  # faint wallpaper stripes
        for y in range(0, 15):
            add(img, x, y, (20, 40, 40), 0.5)
    for x in range(W):  # the table edge
        put(img, x, 15, ffx.WOOD_HI if x % 5 else ffx.WOOD)
    # a warm lamp glow on the left wall (steady)
    ffx.glow(img, 6, 3, 9, (255, 180, 90), 0.25)
    return img


def render():
    base = base_frame()
    confetti = Confetti(seed=7, t0=sec(5.2), x=TIE_CX + 0.5, y=6, n=34, vx=(-1.6, 1.6), vy=(-1.8, -0.6),
                        fall=(0.05, 0.1), colors=WILD + [(255, 255, 255)])
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        s = f / 15

        shake = 0
        for t0 in (1.6, 2.4):
            if t0 <= s < t0 + 0.4:
                shake = 1 if (f // 2) % 2 else -1

        # the tie (drawn first, so the box front hides its lower part as it rises)
        if s >= 5.0:
            rise = phase(f, sec(5.0), sec(5.6))
            e = 1 - (1 - rise) ** 3
            over = math.sin(min(1.0, max(0.0, (s - 5.6) / 0.8)) * math.pi) * 1.5 if s >= 5.6 else 0
            top = BOX_TOP + 1 - (BOX_TOP + 1) * e - over
            sway = 0.0
            if s >= 6.2:
                sway = 2.2 * math.sin((s - 6.2) * 4.0) * max(0.25, 1 - (s - 6.2) / 4)
            mode = 0
            if s >= 9.0:
                mode = 1
            if s >= 10.6:
                mode = 2
            if s >= 12.2:
                mode = 3
            draw_tie(img, top, mode, f, sway)
            if s >= 9.0 and any(t0 <= s < t0 + 0.4 for t0 in (9.0, 10.6, 12.2)):  # a pop of light on each change
                k = 1 - min((s - t0) / 0.4 for t0 in (9.0, 10.6, 12.2) if t0 <= s)
                for dx, dy in ((-3, 1), (3, 1), (-3, 5), (3, 5)):
                    add(img, TIE_CX + dx, top + dy, (255, 255, 255), 0.8 * k)

        # the box, the ribbon and the lid
        if shake:  # the whole box (front and ribbon) jiggles a pixel left and right
            tmp = img.copy()
            box_front(tmp)
            ribbon(tmp)
            region = tmp.crop((BOX_X0 - 1, BOX_TOP - 2, BOX_X1 + 2, 15))
            img.paste(region, (BOX_X0 - 1 + shake, BOX_TOP - 2))
        else:
            box_front(img)
            ribbon(img, 0, phase(f, sec(3.0), sec(3.8)))
        if s < 4.4:
            lid(img, BOX_X0 - 1 + shake, BOX_TOP - 2, bow=s < 3.0)
        else:
            fly = phase(f, sec(4.4), sec(5.4))
            lx = BOX_X0 - 1 + 13 * fly
            ly = BOX_TOP - 2 - 7 * math.sin(math.pi * min(1.0, fly * 1.1)) + (5 * fly if fly > 0.6 else 0)
            if fly >= 1:
                ly = BOX_TOP + 3  # it lands, leaning on the box's right side
            lid(img, lx, ly, tilt=3 * fly, bow=False)
        if 3.0 <= s < 4.0:  # the bow loops spring apart
            k = phase(f, sec(3.0), sec(4.0))
            for sgn in (-1, 1):
                put(img, TIE_CX + 0.5 + sgn * (2 + 4 * k), BOX_TOP - 4 - 3 * k + 6 * k * k, RIBBON, 1 - k)
        tag(img)

        if s >= 5.2:
            confetti.draw(img, f, floor=14)
        if s >= 6.6:  # TA-DA!
            reveal = int(phase(f, sec(6.6), sec(7.2)) * 40)
            font.draw_text(img, "TA-DA!", 1, 2, None, font="big", gradient=((255, 246, 222), (255, 156, 64)),
                           shadow=(12, 20, 58), reveal=reveal)
        frames.append(img)
    return frames
