"""Scene: The Unity Cup (kikombe cha umoja). Four family members stand in a warm room. The elder raises the cup and
pours a libation (tambiko) for the ancestors, then the cup passes from hand to hand and each one raises it. To
close, everyone raises a fist and pulls down together: HARAMBEE! ("let us all pull together")."""

from __future__ import annotations

import math

from busybar.canvas import FPS, add, ease_in_out, lerp, put, sec, vgradient
from busybar.font import draw_text, text_width
from busybar.fx import SPARKLE, Particles
from kfx import (GOLD, GOLD_DK, GOLD_HI, GREEN, RED, ROOM_BOTTOM, ROOM_TOP, SKIN, Kinara, dim_rect, mkeka,
                 person, room_glow)

NAME = "unity_cup"
TITLE = "The Unity Cup"
SECONDS = 16
KEYFRAMES = [(1.0, "The family gathers"), (3.4, "The elder raises the unity cup"), (4.8, "A libation for the ancestors"),
             (7.6, "The cup passes hand to hand"), (11.0, "Each one drinks"), (12.4, "Harambee: all pull together"), (14.8, "HARAMBEE!")]

FEET = 13
# x (left column), skin, cloth, accent, head, headwear color
FAMILY = [
    (2, SKIN[1], (120, 40, 110), GOLD, "hair", (206, 206, 214)),  # the elder: silver hair
    (12, SKIN[3], (30, 120, 60), GOLD, "wrap", (220, 50, 50)),
    (22, SKIN[0], (180, 50, 40), (40, 160, 80), "kufi", (40, 150, 70)),
    (32, SKIN[2], (210, 150, 40), (180, 40, 40), "wrap", (40, 140, 70)),
]
T_RAISE, T_POUR, T_POUR_END = 2.2, 4.0, 5.6
T_PASS0, T_PASS_STEP = 6.0, 1.9  # three passes
T_HARAMBEE = 12.0
LIT = (3, 0, 4, 1, 5, 2, 6)
T_CAPTION = T_HARAMBEE + 2.2  # after the three pulls, which stay visible


def mini_cup(img, x: float, y: float, tilt: int = 0, a: float = 1.0) -> None:
    """A 3x3 gold cup with its bowl's top-left at (x, y). tilt: 1 tips it to the right (pouring)."""
    x, y = round(x), round(y)
    if tilt:
        put(img, x, y + 1, GOLD_HI, a)
        put(img, x + 1, y, GOLD, a)
        put(img, x + 1, y + 1, GOLD, a)
        put(img, x + 2, y + 1, GOLD_DK, a)
        put(img, x, y + 2, GOLD_DK, a)
        return
    put(img, x, y, GOLD_HI, a)
    put(img, x + 1, y, GOLD, a)
    put(img, x + 2, y, GOLD_DK, a)
    put(img, x + 1, y + 1, GOLD, a)
    put(img, x, y + 2, GOLD_DK, a)
    put(img, x + 1, y + 2, GOLD, a)
    put(img, x + 2, y + 2, GOLD_DK, a)


def render():
    bg = vgradient(ROOM_TOP, ROOM_BOTTOM)
    # a soft wall light behind the family, so the figures stand out from the room
    for x in range(42):
        for y in range(14):
            add(bg, x, y, (60, 34, 18), 0.45 * max(0.0, 1 - abs(y - 7) / 9) * max(0.0, 1 - abs(x - 20) / 26))
    mkeka(bg, 14)
    kin = Kinara(56, 13)  # the kinara, all seven candles lit, beside the family
    sp = Particles(seed=33)
    frames = []
    for f in range(sec(SECONDS)):
        t = f / FPS
        img = bg.copy()
        room_glow(img, kin, LIT, f, 0.8)
        kin.draw(img, f, lit=LIT)
        holder = 0
        cup_pos = None
        arms = [(0.02, 0.02)] * 4
        drink = [0.0] * 4
        if t < T_PASS0:
            # the elder lifts the cup high, tips it to pour, then brings it down
            if t < T_RAISE:
                lift = 0.0
            elif t < T_POUR:
                lift = ease_in_out((t - T_RAISE) / (T_POUR - T_RAISE))
            elif t < T_POUR_END:
                lift = 1.0
            else:
                lift = 1 - ease_in_out((t - T_POUR_END) / (T_PASS0 - T_POUR_END))
            arms[0] = (0.02, lerp(0.15, 0.45, lift))
        else:
            k = min(2, int((t - T_PASS0) / T_PASS_STEP))
            u = (t - T_PASS0 - k * T_PASS_STEP) / T_PASS_STEP
            if t >= T_HARAMBEE:
                holder, u = 3, 1.0
                k = 2
            if u < 0.45:  # hand over: the giver reaches right, the receiver reaches left
                holder = k
                arms[k] = (0.02, 0.22)
                arms[k + 1] = (0.22, 0.02)
            else:
                holder = k + 1
                v = (u - 0.45) / 0.55
                drink[holder] = math.sin(math.pi * min(1.0, v * 1.3)) if v < 0.77 else 0.0
                arms[holder] = (0.02, lerp(0.15, 0.4, drink[holder]))
            lift = 0.0
        # HARAMBEE: everyone raises the right fist and pulls it down, three times
        pulls = 0.0
        if t >= T_HARAMBEE:
            beat = (t - T_HARAMBEE) / 0.8
            pulls = 0.5 + 0.5 * math.cos(2 * math.pi * beat) if beat < 3 else 1.0
            arms = [(0.02, lerp(0.08, 0.5, pulls)) for _ in range(4)]
        hands = []
        for i, (x, skin, cloth, accent, head, hw) in enumerate(FAMILY):
            bob = 1 if (t >= T_HARAMBEE and pulls < 0.3) else 0
            hands.append(person(img, x, FEET + bob, skin, cloth, accent, head=head, wrap=hw, arms=arms[i]))
        # the cup: in the holder's right hand (or between two hands while it passes)
        if t >= T_HARAMBEE:
            cup_pos = None
        elif t < T_PASS0:
            hx, hy = hands[0]["r"]
            cup_pos = (hx - 1, hy - 3, 1 if T_POUR <= t < T_POUR_END else 0)
        else:
            k = min(2, int((t - T_PASS0) / T_PASS_STEP))
            u = (t - T_PASS0 - k * T_PASS_STEP) / T_PASS_STEP
            if u < 0.45:
                a, b = hands[k]["r"], hands[k + 1]["l"]
                w = ease_in_out(u / 0.45)
                cup_pos = (lerp(a[0], b[0], w) - 1, lerp(a[1], b[1], w) - 3 - 2 * math.sin(math.pi * w), 0)
            else:
                hx, hy = hands[holder]["r"]
                cup_pos = (hx - 1, hy - 3, 0)
        if cup_pos:
            mini_cup(img, *cup_pos)
            if cup_pos[2]:  # the libation: drops fall to the floor
                for d in range(3):
                    ph = (f * 0.5 + d * 4) % 12
                    put(img, cup_pos[0] + 3, cup_pos[1] + 2 + ph, (180, 60, 80), 0.9 - ph / 15)
        if T_CAPTION - 0.1 <= t < T_CAPTION + 0.1:
            sp.emit(20, 4, 16, vx=(-1.6, 1.6), vy=(-1.2, 0.2), life=(6, 14), colors=SPARKLE, glow=True)
        sp.step_draw(img)
        if t >= T_CAPTION:
            a = min(1.0, (t - T_CAPTION) / 0.4)
            dim_rect(img, 0, 0, 71, 9, 0.6 * a)
            word = "HARAMBEE!"
            draw_text(img, word, (72 - text_width(word)) // 2, 1, None, gradient=((255, 236, 150), (240, 160, 40)),
                      shadow=(120, 20, 20), alpha=a)
            for x in range(10, 62, 4):  # a kente-colored rule under the word
                put(img, x, 9, (RED, GOLD, GREEN)[(x // 4) % 3], 0.8 * a)
        frames.append(img)
    return frames
