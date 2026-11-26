"""Scene: The March at Dawn. A long line of people of every age and skin tone walks together toward the rising sun:
families holding hands, a child on a parent's shoulders, an elder with a cane. The sky slowly turns from night to
gold, and the word TOGETHER appears."""

from PIL import Image

from busybar.canvas import FPS, H, W, blit, put, ease_in_out, lerp, phase, sec
from busybar.fx import Stars
from mfx import mix_light, BOTTOMS, HAIR, SKIN, TOPS, Person, caption, ground, join_hands, rim_light, sky, sun

NAME = "march"
TITLE = "The March at Dawn"
SECONDS = 16
KEYFRAMES = [(0.5, "Before dawn, the marchers set out"), (5.0, "Families walk hand in hand"),
             (9.0, "The sun rises ahead of them"), (14.0, "TOGETHER")]

FEET = 14
HORIZON = 9
SUN_X = 60
STEP_FRAMES = 4  # one pixel forward every 4 frames: an unhurried walk


def P(kind, s, h, t, b, child=None):
    return Person(kind, SKIN[s], HAIR[h], TOPS[t], BOTTOMS[b], child)


# (person, gap to the next person behind, holds hands with the person behind)
LINE = [
    (P("adult", 3, 0, 0, 0), 6, False),
    (P("adult", 0, 4, 1, 2), 6, True),
    (P("child", 1, 3, 3, 0), 5, True),
    (P("adult", 2, 1, 2, 1), 7, False),
    (P("elder", 5, 2, 4, 2), 7, False),
    (P("carrier", 4, 5, 6, 0, child=(SKIN[4], HAIR[5], TOPS[3])), 7, False),
    (P("teen", 1, 0, 5, 3), 6, True),
    (P("teen", 3, 5, 7, 0), 7, False),
    (P("adult", 5, 0, 3, 1), 6, True),
    (P("child", 5, 0, 1, 2), 5, True),
    (P("adult", 0, 2, 4, 0), 7, False),
    (P("adult", 2, 3, 6, 3), 6, False),
    (P("child", 0, 4, 2, 1), 5, True),
    (P("adult", 4, 1, 0, 2), 7, False),
    (P("elder", 1, 2, 7, 1), 7, False),
    (P("adult", 3, 5, 5, 0), 6, True),
    (P("adult", 1, 0, 1, 3), 6, False),
    (P("teen", 4, 0, 2, 2), 7, False),
]
LEAD_X0 = 40  # where the front of the line is at the start


def land(img, p: float, sy: float) -> None:
    """Dark fields below the horizon, a faint road under the marchers, and the sun's warmth on the land."""
    for y in range(HORIZON + 1, H):
        for x in range(W):
            c = (20, 18, 42) if y < FEET + 1 else (44, 34, 56)
            put(img, x, y, c)
            d = abs(x - SUN_X) / 30 + (y - HORIZON) / 9
            if sy < HORIZON + 3:
                put(img, x, y, (150, 84, 70), 0.45 * p * max(0.0, 1 - d))
    for x in range(W):  # the horizon line catches the light
        put(img, x, HORIZON + 1, mix_light(p, x), 0.6)


def render():
    stars = Stars(seed=11, n=22, ymax=9, period=FPS * 4, color=(220, 226, 255), dim=0.1, bright=0.7)
    frames = []
    # offsets of each person from the front of the line
    offs, x = [], 0
    for _, gap, _ in LINE:
        offs.append(x)
        x -= gap
    for f in range(sec(SECONDS)):
        t = f / FPS
        p = ease_in_out(phase(f, 0, sec(13.5)))
        img = sky(p * 0.95 + 0.05, horizon=HORIZON)
        stars.draw(img, f, alpha=1 - phase(f, sec(3), sec(10)))
        # the sun rises over the far horizon, ahead of the marchers
        sy = lerp(HORIZON + 4.5, 3.5, ease_in_out(phase(f, sec(2), sec(14.5))))
        sun(img, SUN_X, sy, 3.2, strength=min(1.0, 0.4 + p))
        land(img, p, sy)

        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lead = LEAD_X0 + f // STEP_FRAMES
        stride_on = (f // STEP_FRAMES) % 2
        hands = []
        for i, (person, _, holds) in enumerate(LINE):
            px = lead + offs[i]
            stride = bool((stride_on + i) % 2)
            behind_holds = holds and i + 1 < len(LINE)
            person.draw(layer, px, FEET, stride, swing=1, front_hand=not (i > 0 and LINE[i - 1][2]))
            if behind_holds:
                back = LINE[i + 1][0]
                bx = lead + offs[i + 1]
                hands.append((back.hand(bx, FEET), person.back_hand(px, FEET), back.skin, person.skin))
        for a, b, ca, cb in hands:
            join_hands(layer, a, b, ca, cb)
        rim_light(layer, (255, 170, 70), 0.06 + 0.16 * p)
        blit(img, layer, 0, 0)

        # TOGETHER, slowly, high in the sky on the left
        caption(img, "TOGETHER", 0, ease_in_out(phase(f, sec(11.0), sec(13.0))) * (1 - phase(f, sec(15.4), sec(16))),
                font="tiny", x=2, back=False)
        frames.append(img)
        _ = t
    return frames
