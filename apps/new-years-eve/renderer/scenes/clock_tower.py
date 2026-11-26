"""The Clock Tower: snow over a sleeping town; the view climbs a stone tower to its clock, where the minute hand
ticks toward twelve. TICK... TOCK... (a generic tower, no real landmark)."""

import math

from PIL import Image

from busybar.canvas import FPS, add, ease_in_out, phase, put, sec
from busybar.font import draw_text
from party import GOLD, GOLD_LIGHT, SILVER, Snowfall, dim, disc, glitter, line

NAME = "clock_tower"
TITLE = "The Clock Tower"
SECONDS = 14
KEYFRAMES = [(0.5, "Snow over the rooftops"), (2.6, "Up the old tower..."), (5.0, "...to the clock: 11:55"),
             (6.2, "TICK"), (7.8, "TOCK"), (12.6, "11:59. Almost!")]

TALL = 40              # the tall world the camera pans over
CX, FACE_Y, FACE_R = 36, 15, 7
VIEW_START, VIEW_END = TALL - 16, FACE_Y - 8
STONE = (70, 64, 92)
STONE_DARK = (52, 46, 72)
FACE = (30, 36, 84)
RIM = (230, 170, 50)
HAND = (255, 236, 160)
MINUTE = (255, 255, 255)
MARK = (150, 160, 200)
TICKS = [sec(5.6 + 1.6 * k) for k in range(4)]     # 11:55 -> 11:59, one minute per tick


def world() -> Image.Image:
    img = Image.new("RGBA", (72, TALL), (0, 0, 0, 255))
    for y in range(TALL):
        c = (int(6 + 14 * y / TALL), int(6 + 6 * y / TALL), int(26 + 22 * y / TALL))
        for x in range(72):
            put(img, x, y, c)
    # moon
    disc(img, 10, 11, 2.6, (255, 246, 210))
    disc(img, 11.2, 10.3, 2.2, (12, 9, 34))
    # rooftops of the town at the bottom
    for x0, w, h, c in ((0, 10, 6, (40, 34, 66)), (9, 8, 9, (34, 30, 60)), (48, 9, 8, (38, 32, 64)),
                        (56, 8, 5, (34, 30, 58)), (63, 9, 7, (40, 34, 66)), (18, 8, 4, (36, 30, 62))):
        for x in range(x0, x0 + w):
            peak = h + 2 - abs(x - (x0 + w / 2)) * 0.8
            for y in range(int(TALL - peak), TALL):
                put(img, x, y, c)
        put(img, x0 + w // 2, TALL - h + 1, (255, 200, 90))  # a lit window
        put(img, x0 + w // 2 + 2, TALL - h + 2, (255, 200, 90))
    # the tower
    for y in range(FACE_Y - 9, TALL):
        half = 8 if y >= FACE_Y - 8 else 6
        for x in range(CX - half, CX + half):
            brick = (y % 3 == 0) or ((x + (y // 3) * 3) % 6 == 0)
            put(img, x, y, STONE_DARK if brick else STONE)
        put(img, CX - half - 1, y, (90, 84, 120))  # lit edge
    for y in range(FACE_Y - 9, FACE_Y - 7):  # cornice
        for x in range(CX - 10, CX + 10):
            put(img, x, y, (120, 110, 150))
    for y in range(FACE_Y + 9, FACE_Y + 11):
        for x in range(CX - 10, CX + 10):
            put(img, x, y, (110, 100, 140))
    # roof (only seen at the very start of the pan? no: above the view; kept for completeness)
    for y in range(0, FACE_Y - 9):
        half = max(0, (y - (FACE_Y - 18)) * 1.0)
        for x in range(int(CX - half), int(CX + half)):
            put(img, x, y, (40, 120, 110))
    # lit arched windows down the tower
    for wy in (28, 34):
        for wx in (CX - 5, CX + 3):
            for dy in range(3):
                for dx in range(2):
                    put(img, wx + dx, wy + dy, (255, 196, 90) if dy else (255, 226, 140))
    return img


def face(img, oy: int, minute: float, glow: float) -> None:
    cy = FACE_Y - oy
    disc(img, CX, cy, FACE_R + 0.5, RIM)
    disc(img, CX, cy, FACE_R - 0.6, FACE)
    if glow > 0:
        for a in range(0, 360, 12):
            r = math.radians(a)
            add(img, CX + (FACE_R + 1) * math.cos(r), cy + (FACE_R + 1) * math.sin(r), GOLD_LIGHT, 0.5 * glow)
    for h in range(12):
        a = math.radians(h * 30 - 90)
        r = FACE_R - 1.6
        put(img, CX + r * math.cos(a), cy + r * math.sin(a), MARK if h % 3 else GOLD)
    # hands: hour just short of 12, minute creeping up
    ha = math.radians((11 + minute / 60) * 30 - 90)
    ma = math.radians(minute * 6 - 90)
    line(img, CX, cy, CX + 3.2 * math.cos(ha), cy + 3.2 * math.sin(ha), HAND)
    line(img, CX, cy, CX + 5.4 * math.cos(ma), cy + 5.4 * math.sin(ma), MINUTE)
    put(img, CX, cy, (255, 120, 60))


def render():
    base = world()
    snow = Snowfall(seed=51, n=22, period=FPS * 7, color=(225, 232, 255), alpha=(0.35, 0.85))
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        k = ease_in_out(phase(f, sec(1.2), sec(4.6)))
        oy = round(VIEW_START + (VIEW_END - VIEW_START) * k)
        img = base.crop((0, oy, 72, oy + 16))
        glitter(img, 52, f, n=8, period=FPS * 5, colors=(SILVER, (200, 210, 255)), strength=0.5, ymax=8,
                area=(0, 0, 26, 16))
        minute = 55.0
        for i, tk in enumerate(TICKS):
            if f >= tk:
                minute = 56.0 + i + (0.5 if f - tk < 2 else 0)  # tiny overshoot on each tick
                if f - tk >= 2:
                    minute = 56.0 + i
        glow = phase(f, sec(12.0), sec(12.6)) * (0.6 + 0.4 * math.sin(t * 9))
        face(img, oy, min(minute, 59.0), glow)
        snow.draw(img, f)
        # TICK / TOCK alternate with each tick, either side of the tower
        for i, tk in enumerate(TICKS):
            if tk <= f < tk + sec(1.2):
                a = 1 - phase(f, tk + sec(0.8), tk + sec(1.2))
                if i % 2 == 0:
                    draw_text(img, "TICK", 6, 6, GOLD_LIGHT, font="tiny", shadow=(70, 30, 0), alpha=a)
                else:
                    draw_text(img, "TOCK", 51, 6, GOLD_LIGHT, font="tiny", shadow=(70, 30, 0), alpha=a)
        if f >= sec(12.2):
            a = phase(f, sec(12.2), sec(12.6))
            draw_text(img, "ALMOST", 1, 11, dim(GOLD_LIGHT, 1.0), font="tiny", shadow=(70, 30, 0), alpha=a)
            draw_text(img, "TIME!", 52, 11, dim(GOLD_LIGHT, 1.0), font="tiny", shadow=(70, 30, 0), alpha=a)
        frames.append(img)
    return frames
