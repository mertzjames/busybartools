"""Scene: a parade of trades. Under a swag of bunting, six workers march in along Main Street: a nurse, a teacher, a
farmer, a builder, a mechanic and a chef, in generic work clothes and a range of skin tones. They halt, each raises
the tool of their trade in turn, then all wave as streamers fall (docs/DECISIONS.md D3, D5)."""

from __future__ import annotations

from busybar.canvas import H, W, ease_out, phase, put, sec
from busybar.party import Confetti

import lfx

NAME = "parade"
TITLE = "Parade of Trades"
SECONDS = 14
KEYFRAMES = [(1.5, "The parade marches in"), (4.2, "Six trades on Main Street"), (6.6, "The nurse and the teacher"),
             (8.4, "Pitchfork, hammer, wrench, spatula"), (11.8, "Everyone waves")]

FEET = H - 1
WALK0, WALK1 = 0, sec(5.6)
RAISE0 = sec(6.0)  # each worker raises their tool in turn, leader first
RAISE_STEP = sec(0.55)
RAISE_LEN = sec(1.6)
WAVE0 = sec(10.0)

# (trade, final x, kwargs for lfx.person, prop)
CHECK = (226, 70, 70)
COVERALL = (112, 146, 200)
WORKERS = [
    ("nurse", 64, dict(skin=lfx.SKIN[2], shirt=lfx.TEAL, legs_c=lfx.TEAL, hair=lfx.HAIR_DARK, hat="nurse"),
     "clipboard"),
    ("teacher", 53, dict(skin=lfx.SKIN[0], shirt=lfx.PURPLE, legs_c=(120, 128, 156), hair=lfx.HAIR_GREY, hat="bun"),
     "apple"),
    ("farmer", 42, dict(skin=lfx.SKIN[4], shirt=CHECK, legs_c=lfx.DENIM, hat="straw", hat_c=lfx.RED, apron=lfx.DENIM),
     "pitchfork"),
    ("builder", 31, dict(skin=lfx.SKIN[1], shirt=lfx.WHITE, legs_c=lfx.DENIM, hat="hard", hat_c=lfx.SAFETY,
                         vest=lfx.ORANGE), "hammer"),
    ("mechanic", 20, dict(skin=lfx.SKIN[3], shirt=COVERALL, legs_c=COVERALL, hair=lfx.HAIR_AUBURN, hat="cap",
                          hat_c=lfx.RED), "wrench"),
    ("chef", 9, dict(skin=lfx.SKIN[1], shirt=lfx.WHITE, legs_c=(150, 150, 166), hat="toque"), "spatula"),
]


def backdrop():
    img = lfx.sky([(0, (90, 160, 240)), (6, (170, 214, 252))])
    for x in range(W):  # a park's tree line, rounded tops
        top = 7 - (1 if (x * 7) % 11 < 5 else 0) - (1 if (x * 3) % 13 == 0 else 0)
        for y in range(top, 13):
            c = lfx.GREEN if y < top + 1 else (66, 130, 66)
            put(img, x, y, c)
    for x in range(W):
        put(img, x, 13, (200, 196, 186))  # the curb
        put(img, x, 14, (128, 128, 140))
        put(img, x, 15, (112, 112, 126))
    for x in range(2, W, 8):  # a dashed lane line
        put(img, x, 15, (240, 220, 120))
        put(img, x + 1, 15, (240, 220, 120))
    for x in range(W):  # a shallow bunting swag along the top
        u = (x % 18) / 18
        n = 1 if 0.2 < u < 0.8 else 0
        put(img, x, 0, (54, 84, 200))
        if n:
            put(img, x, 1, lfx.RED)
    for x in range(0, W, 18):
        put(img, x, 1, lfx.GOLD)
    return img


def prop(img, kind: str, hand, other) -> None:
    hx, hy = hand
    S, WD = lfx.STEEL_HI, lfx.WOOD_HI
    if kind == "clipboard":
        lfx.grid(img, hx, hy - 1, ["wb", "bb"], {"w": lfx.WHITE, "b": lfx.WOOD_HI})
    elif kind == "apple":
        put(img, hx, hy, lfx.RED_HI)
        put(img, hx + 1, hy, lfx.RED)
        put(img, hx + 1, hy - 1, lfx.GREEN_HI)
        ox, oy = other  # a book in the other hand
        put(img, ox, oy, (60, 120, 255))
        put(img, ox - 1, oy, (60, 120, 255))
        put(img, ox - 1, oy - 1, lfx.WHITE)
    elif kind == "pitchfork":
        for y in range(hy - 4, hy + 2):
            put(img, hx, y, WD)
        for dx in (-1, 0, 1):
            put(img, hx + dx, hy - 5, S)
        put(img, hx - 1, hy - 6, S)
        put(img, hx + 1, hy - 6, S)
    elif kind == "hammer":
        put(img, hx, hy - 1, WD)
        put(img, hx, hy - 2, WD)
        for dx in (-1, 0, 1):
            put(img, hx + dx, hy - 3, S)
    elif kind == "wrench":
        put(img, hx, hy - 1, S)
        put(img, hx, hy - 2, S)
        put(img, hx - 1, hy - 3, S)
        put(img, hx + 1, hy - 3, S)
    elif kind == "spatula":
        put(img, hx, hy - 1, WD)
        put(img, hx, hy - 2, S)
        for dx in (0, 1):
            put(img, hx + dx, hy - 3, S)
            put(img, hx + dx, hy - 4, S)


def render():
    base = backdrop()
    confetti = Confetti(5, WAVE0, 36, -2, n=40, vx=(-2.4, 2.4), vy=(-0.2, 0.6), fall=(0.05, 0.11), spread=34,
                        stagger=20)
    frames = []
    for f in range(sec(SECONDS)):
        img = base.copy()
        walk = ease_out(phase(f, WALK0, WALK1))
        moving = f < WALK1 - 2
        off = round(-80 * (1 - walk))
        for i, (trade, x, kw, kind) in enumerate(WORKERS):
            r0 = RAISE0 + i * RAISE_STEP
            raised = r0 <= f < r0 + RAISE_LEN
            arm_r = 0.08
            arm_l = 0.04
            if raised:
                arm_r = 0.42
            if f >= WAVE0:
                k = ((f - WAVE0) // 5 + i) % 2
                arm_l = 0.38 if k else 0.3
                arm_r = 0.3 if k else 0.42
            step = (1 if ((f // 4) + i) % 2 else -1) if moving else 0
            hands = lfx.person(img, x + off, FEET, arms=(arm_l, arm_r), step=step, **kw)
            prop(img, kind, hands["r"], hands["l"])
        confetti.draw(img, f)
        frames.append(img)
    return frames
