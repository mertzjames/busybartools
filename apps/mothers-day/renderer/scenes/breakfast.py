"""Breakfast in bed: a child carries a tray into a sunny bedroom (pancakes with butter and syrup, a glass of orange
juice and a tulip in a little vase) and slides it onto Mom's lap. She lifts her arms in delight and hearts float up
(docs/DECISIONS.md D3)."""

import math

from busybar.canvas import add, ease_in_out, ease_out, lerp, mix, phase, put, sec

import mfx

NAME = "breakfast"
TITLE = "Breakfast in Bed"
SECONDS = 15
N = sec(SECONDS)
KEYFRAMES = [(0.5, "A sunny morning"), (3.5, "Here comes breakfast"), (7.5, "Onto Mom's lap"),
             (9.6, "Delight!"), (12.5, "Pancakes, juice and a flower")]

WALK0, WALK1 = sec(0.6), sec(6.4)
PUSH0, PUSH1 = sec(6.6), sec(8.4)
JOY0 = sec(9.0)
TRAY_ROW = 10
CHILD_START, CHILD_STOP, CHILD_END = -16, 33, 37
TRAY_FINAL = 46  # left end of the tray on Mom's lap

MOM_X = 60
MOM_SKIN = mfx.SKIN[1]
CHILD_SKIN = mfx.SKIN[3]
WALL_TOP, WALL_BOTTOM = (62, 34, 50), (48, 26, 42)


def room():
    img = mfx.sky([(0, WALL_TOP), (14, WALL_BOTTOM)])
    # the window, top left: morning sky, the sun, a cream frame and a cross bar
    for y in range(1, 9):
        for x in range(3, 16):
            frame = y in (1, 8) or x in (3, 15) or x == 9 or y == 4
            c = mfx.CREAM if frame else mix(mfx.SKY_HI, mfx.SKY, (y - 2) / 5)
            put(img, x, y, c)
    for dx, dy in ((0, 0), (1, 0), (0, 1), (1, 1)):
        put(img, 12 + dx, 2 + dy, mfx.YELLOW_HI)
    # a soft sunbeam falling down to the right (steady)
    for y in range(9, 16):
        for x in range(3 + (y - 9), 18 + (y - 9) * 2):
            add(img, x, y, (60, 44, 20), 0.35 * (1 - (y - 9) / 9))
    # floor
    for x in range(72):
        put(img, x, 15, mfx.WOOD if (x // 6) % 2 else mfx.WOOD_HI)
    # the bed: headboard on the right, pillow, mattress with a pink quilt, legs
    for y in range(4, 16):
        for x in range(67, 71):
            put(img, x, y, mfx.WOOD_HI if y == 4 or x == 67 else mfx.WOOD)
    # a big pillow propped against the headboard, behind Mom (a lit backdrop, so her head and arms read)
    for y in range(2, 11):
        for x in range(55, 67):
            corner = (x in (55, 66)) and (y in (2, 10))
            c = (236, 208, 214) if (x + y) % 5 else (226, 170, 196)
            put(img, x, y, mix(c, WALL_TOP, 0.6) if corner else c)
    return img


def bed_front(img):
    """The quilt and the bed's foot, drawn over Mom's waist."""
    for y in range(11, 14):
        for x in range(42, 67):
            check = ((x // 3) + (y - 11)) % 2 == 0
            put(img, x, y, mfx.PINK if check else mfx.PINK_HI)
    for x in range(42, 67):
        put(img, x, 11, mfx.WHITE if x > 56 else mix(mfx.PINK_HI, mfx.WHITE, 0.4))  # turned-down sheet
    for x in (43, 65):
        put(img, x, 14, mfx.WOOD_DK)
    for x in range(42, 67):
        put(img, x, 14, mfx.WOOD) if x in (42, 43, 64, 65) else None


def tray(img, x0: int, f: int, steam: bool = True):
    """The tray (11 px) at row TRAY_ROW with pancakes, juice and a tulip in a vase."""
    for x in range(x0, x0 + 11):
        put(img, x, TRAY_ROW, mfx.SILVER if x not in (x0, x0 + 10) else mix(mfx.SILVER, (0, 0, 0), 0.25))
    # pancakes: three golden layers, a butter pat and a syrup drip
    gold, gold_hi = (226, 150, 54), (250, 196, 96)
    for k, y in enumerate((9, 8, 7)):
        for x in range(x0 + 1, x0 + 5):
            put(img, x, y, gold_hi if k % 2 else gold)
    put(img, x0 + 2, 6, mfx.YELLOW_HI)
    put(img, x0 + 3, 6, (190, 96, 30))
    put(img, x0 + 4, 7, (170, 80, 26))
    # juice: a glass with a pale rim
    put(img, x0 + 6, 7, (200, 230, 255))
    put(img, x0 + 7, 7, (200, 230, 255))
    for y in (8, 9):
        put(img, x0 + 6, y, mfx.ORANGE)
        put(img, x0 + 7, y, (255, 184, 60))
    # a little blue vase with a pink tulip
    put(img, x0 + 9, 9, (90, 150, 255))
    put(img, x0 + 9, 8, (130, 180, 255))
    put(img, x0 + 9, 7, mfx.GREEN)
    put(img, x0 + 10, 7, mfx.GREEN_HI)
    mfx.tulip(img, x0 + 9, 4, mfx.PINK)
    if steam:  # two wisps over the pancakes, curling as they rise (a few lit pixels each)
        for i, sx in enumerate((x0 + 2, x0 + 4)):
            for k in range(3):
                age = (f / 9 + k / 3 + i * 0.5) % 1.0
                y = 5 - age * 5
                x = sx + 0.8 * math.sin(2 * math.pi * (age * 1.5 + i * 0.3))
                put(img, x, y, (236, 226, 236), 0.75 * (1 - age))


def child(img, x: int, f: int, walking: bool, arms_out: bool):
    """The child, side view, facing right: hair, head, shirt, an arm reaching forward, legs that step."""
    hair = mfx.HAIR_AUBURN
    shirt, pants = mfx.YELLOW, (90, 120, 220)
    for dx in (-1, 0, 1):
        put(img, x + dx, 6, hair)
    put(img, x - 1, 7, hair)
    put(img, x - 2, 7, hair)  # ponytail
    put(img, x - 2, 8, hair)
    put(img, x - 1, 8, hair)
    put(img, x, 7, CHILD_SKIN)
    put(img, x + 1, 7, CHILD_SKIN)
    put(img, x, 8, CHILD_SKIN)
    put(img, x + 1, 8, CHILD_SKIN)
    for y in (9, 10, 11):
        for dx in (-1, 0, 1):
            put(img, x + dx, y, shirt)
    if arms_out:
        put(img, x + 2, 10, CHILD_SKIN)
        put(img, x + 3, 10, CHILD_SKIN)
    else:
        put(img, x + 1, 11, mix(shirt, (0, 0, 0), 0.15))
        put(img, x + 1, 12, CHILD_SKIN)
    step = (f // 4) % 2 if walking else 0
    for y in (12, 13):
        put(img, x - 1, y, pants)
        put(img, x + 1, y, pants)
    put(img, x, 12, pants)
    if step:
        put(img, x - 2, 14, mfx.ROSE_DK)
        put(img, x + 2, 14, mfx.ROSE_DK)
    else:
        put(img, x - 1, 14, mfx.ROSE_DK)
        put(img, x + 1, 14, mfx.ROSE_DK)


def render():
    base = room()
    frames = []
    for f in range(N):
        img = base.copy()
        # Mom, sitting up in bed
        if f < JOY0:
            arms = (0.0, 0.0)
        else:
            k = ease_out(phase(f, JOY0, JOY0 + sec(0.6)))
            arms = (0.42 * k, 0.42 * k) if f < JOY0 + sec(2.4) else (0.08, 0.08)
        mfx.person(img, MOM_X, 14, MOM_SKIN, mfx.LAVENDER_DK, mfx.LAVENDER_DK, mfx.HAIR_DARK, style="puff", arms=arms,
                   seated=True)
        bed_front(img)
        # the child and the tray
        if f < WALK1:
            cx = int(round(lerp(CHILD_START, CHILD_STOP, phase(f, WALK0, WALK1))))
            tx = cx + 4
            walking, arms_out = WALK0 <= f, True
        elif f < PUSH1:
            p = ease_in_out(phase(f, PUSH0, PUSH1))
            tx = int(round(lerp(CHILD_STOP + 4, TRAY_FINAL, p)))
            cx = tx - 4  # the child walks the tray all the way to Mom
            walking, arms_out = 0 < p < 1, True
        else:  # lets go, then steps back to watch
            tx = TRAY_FINAL
            back = phase(f, PUSH1 + sec(0.4), PUSH1 + sec(1.0))
            cx = int(round(lerp(TRAY_FINAL - 4, CHILD_END, back)))
            walking, arms_out = 0 < back < 1, f < PUSH1 + sec(0.4)
        tray(img, tx, f)
        child(img, cx, f, walking, arms_out)
        # hearts after the delight
        for i, (hx, t0) in enumerate(((44, JOY0 + sec(0.3)), (31, JOY0 + sec(1.4)), (49, JOY0 + sec(2.6)),
                                      (37, JOY0 + sec(3.6)))):
            if f >= t0:
                q = phase(f, t0, t0 + sec(2.4))
                if q < 1:
                    mfx.heart(img, hx + math.sin(q * 6) * 0.8, 4 - 7 * q, 5 if i % 2 == 0 else 3,
                              mfx.ROSE if i % 2 else mfx.PINK, alpha=min(1.0, 3 * (1 - q)))
        frames.append(img)
    return frames
