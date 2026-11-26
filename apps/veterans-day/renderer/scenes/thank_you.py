"""Scene: a thank-you. An older veteran in a plain cap rests on a bench in front of a warmly lit café window, and a
flag flies from the wall beside it. A child walks up and holds out a handmade card; the veteran takes it, opens it
to a red heart, and the two wave. THANK YOU appears in small letters (docs/DECISIONS.md D3, D10)."""

import math

from busybar.canvas import W, ease_out, mix, new, phase, put, sec

from scenes.text import SCENE_CAPTIONS
from scenes.main_street import mini_flag
from vfx import HAIR_BROWN, HAIR_SILVER, RED, SKIN, U_DARK, WHITE, caption, draw_flag, fill, glow, person

NAME = "thank_you"
TITLE = "A Thank You"
SECONDS = 14
KEYFRAMES = [(1.0, "A veteran on a bench"), (3.5, "A child walks up"), (6.0, "A handmade card"),
             (8.6, "Opened: a red heart"), (12.5, "THANK YOU")]

WALL = (78, 84, 112)
WALL_LO = (64, 68, 94)
WINDOW = (255, 214, 140)
FRAME = (196, 176, 140)
WOOD = (56, 128, 84)  # a painted park-bench green: wood brown merged with skin tones
WOOD_HI = (80, 156, 104)
PAVE = (120, 116, 112)
CARD = (238, 236, 228)
CARD_BLUE = (70, 100, 200)

VET_X = 19
CHILD_STOP = 29
WALK = (sec(1.6), sec(4.6))
OFFER = sec(5.0)
TAKE = sec(6.6)
OPEN = sec(7.8)
WAVE = sec(9.8)
TEXT = sec(11.0)


def backdrop():
    img = new(WALL)
    for y in range(12, 14):
        for x in range(W):
            put(img, x, y, WALL_LO)
    fill(img, 4, 1, 26, 11, FRAME)  # the café window, warmly lit
    fill(img, 5, 2, 25, 10, WINDOW)
    glow(img, 15, 6, 14, (255, 200, 120), 0.25)
    for x in range(5, 26):  # a striped awning lip along the top of the window
        put(img, x, 1, RED if (x // 2) % 2 else WHITE)
    fill(img, 56, 3, 64, 9, FRAME)  # a second, smaller window down the street
    fill(img, 57, 4, 63, 8, mix(WINDOW, WALL, 0.35))
    for x in range(38, 43):  # a bracket on the wall for the flag
        put(img, x, 7 + (42 - x) // 2, (200, 180, 140))
    for x in range(W):
        put(img, x, 14, PAVE)
        put(img, x, 15, mix(PAVE, (0, 0, 0), 0.3))
    # the bench: a backrest behind the veteran, a seat plank, two legs
    for x in range(12, 27):
        put(img, x, 9, WOOD_HI)
    return img


def bench_front(img) -> None:
    for x in range(12, 27):
        put(img, x, 12, WOOD)
    for y in (13, 14):
        put(img, 13, y, WOOD)
        put(img, 25, y, WOOD)


def card(img, x: int, y: int, opened: bool) -> None:
    """A handmade card: folded, a white front with a blue band; opened, two white pages with a red heart."""
    if not opened:
        for dx in range(2):
            for dy in range(3):
                put(img, x + dx, y + dy, CARD_BLUE if dy == 0 else CARD)
        return
    for dx in range(-1, 3):
        for dy in range(3):
            put(img, x + dx, y + dy, CARD)
    put(img, x, y + 1, RED)
    put(img, x + 1, y + 1, RED)
    put(img, x, y, RED)
    put(img, x + 1, y, (230, 70, 80))


def render():
    n = sec(SECONDS)
    bg = backdrop()
    frames = []
    for f in range(n):
        img = bg.copy()
        draw_flag(img, 43, 7, 9, 5, f / 26, amp=0.8, wavelength=10, color=mini_flag, shade_levels=2)
        # the child walks in from the right
        p = ease_out(phase(f, *WALK))
        cx = int(74 - (74 - CHILD_STOP) * p + 0.5)
        walking = 0 < phase(f, *WALK) < 1
        step = (f // 4) % 2 if walking else 0
        reach = 0.25 if OFFER <= f < TAKE + sec(0.4) else 0.0
        waving = f >= WAVE
        wave = 0.42 + 0.06 * math.sin(2 * math.pi * (f - WAVE) / 12)
        vet_arm = 0.24 if TAKE - sec(0.4) <= f else 0.0
        if f >= OPEN:
            vet_arm = 0.30
        # the veteran: silver hair, a navy cap, a plain maroon jacket
        vh = person(img, VET_X, 15, SKIN[0], (156, 64, 76), U_DARK, HAIR_SILVER, hat="ball", hat_c=(56, 80, 170),
                    hat_c2=(84, 108, 196), arms=(0.0, vet_arm))
        bench_front(img)
        # the child: a light-blue sweater
        ch = person(img, cx, 15, SKIN[3], (120, 196, 236), (70, 80, 140), HAIR_BROWN, style="puff", child=True,
                    arms=(reach if not waving else 0.0, wave if waving else 0.0), legs=step)
        if f < TAKE:  # the card in the child's hand, held out from OFFER
            hx, hy = ch["l"]
            card(img, hx - (2 if f >= OFFER else 1), hy - 1, False)
        else:  # then in the veteran's, opened from OPEN
            hx, hy = vh["r"]
            card(img, hx + 1, hy - 2, f >= OPEN)
        if f >= TEXT:
            for text, font, x, y in SCENE_CAPTIONS[NAME]:
                caption(img, text, y, ease_out(phase(f, TEXT, TEXT + sec(1.2))), font=font, x=x, back=0.5)
        frames.append(img)
    return frames
