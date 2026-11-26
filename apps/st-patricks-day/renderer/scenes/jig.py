"""Scene: The Leprechaun's Jig. On a green hilltop at sunrise, a leprechaun (green coat, buckled hat, ginger beard)
taps his foot, then dances a jig: hops and kicks to the music, notes floating by. He leaps for a heel click, lands,
and tips his hat as gold sparkles rise around him."""

import math

from busybar.canvas import FPS, H, W, add, ease_in_out, mix, phase, put, sec, vgradient
from busybar.party import hash01
from pfx import GOLD_HI, SHAMROCK, SHAMROCK_DK, SHAMROCK_HI, glow, leprechaun, note, shamrock, sparkle4

NAME = "jig"
TITLE = "The Leprechaun's Jig"
SECONDS = 14
KEYFRAMES = [(0.8, "A leprechaun on the hilltop at sunrise"), (3.0, "The music starts: a hop and a kick"),
             (6.2, "Kicking up his heels"), (9.6, "A leap and a heel click"), (11.6, "He tips his hat"),
             (13.2, "Gold sparkles rise")]

BEAT = 6  # frames per jig step (0.4 s)
JIG = (sec(1.6), sec(9.0))
LEAP = (sec(9.0), sec(10.6))
TIP = sec(10.8)
HOME_X = 30
GROUND = 14  # top row of the hill under his feet


def background():
    """Sunrise sky over far blue-green hills and a near green hilltop, the sun low on the left. Static, so it costs
    nothing per frame. The far hills stay a dim teal so the leprechaun's green coat stands out against them."""
    img = vgradient((22, 44, 124), (196, 130, 110))
    glow(img, 9, 11, 10, (255, 180, 80), 0.55)
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            if dx * dx + dy * dy <= 5:
                put(img, 9 + dx, 10 + dy, (255, 226, 140) if dx * dx + dy * dy < 3 else (255, 196, 96))
    for x in range(W):
        far = 11.0 + 1.3 * math.sin(x * 0.11 + 1.2) + 0.6 * math.sin(x * 0.27)
        near = 14.0 + 0.8 * (1 - math.cos((x - HOME_X - 5) * 0.07))
        for y in range(H):
            if y >= near:
                put(img, x, y, mix((44, 160, 60), (26, 116, 44), (y - near) / 2))
            elif y >= far:
                put(img, x, y, mix((22, 66, 70), (18, 54, 58), (y - far) / 4))
    # a few shamrocks dotted in the near grass
    for x, y in ((5, 14), (17, 15), (53, 15), (64, 14), (70, 15)):
        shamrock(img, x, y, 0, SHAMROCK_HI, (190, 255, 160), SHAMROCK_DK)
    return img


def pose(f: int):
    """(x, lift, legs, arms, hat_lift) for frame f."""
    if f < JIG[0]:  # waiting: tapping a foot on the beat
        tap = (f // 5) % 2 and f > sec(0.6)
        return HOME_X, 0, "kick_r" if tap else "stand", "hips", 0
    if f < JIG[1]:
        k = (f - JIG[0]) // BEAT
        sub = (f - JIG[0]) % BEAT
        moves = (("kick_r", "up_l"), ("stand", "hips"), ("kick_l", "up_r"), ("stand", "hips"),
                 ("kick_r", "out"), ("kick_l", "out"), ("kick_r", "out"), ("stand", "hips"))
        legs, arms = moves[k % len(moves)]
        lift = 1 if legs != "stand" and sub < 4 else 0
        # travel: a few steps right, then back left, then home
        drift = int(round(5 * math.sin(2 * math.pi * (f - JIG[0]) / (JIG[1] - JIG[0]))))
        return HOME_X + drift, lift, legs, arms, 0
    if f < LEAP[1]:
        p = phase(f, *LEAP)
        if p < 0.15:
            return HOME_X, 0, "tuck", "hips", 0  # crouch
        if p < 0.85:
            u = (p - 0.15) / 0.7
            lift = int(round(2 * math.sin(math.pi * u)))
            return HOME_X, lift, "click" if 0.3 < u < 0.7 else "tuck", "up", 0
        return HOME_X, 0, "tuck", "out", 0
    lift_hat = 0
    if f >= TIP:
        p = phase(f, TIP, TIP + sec(0.5))
        back = phase(f, sec(12.6), sec(13.1))
        lift_hat = int(round(2 * ease_in_out(p) * (1 - ease_in_out(back))))
    return HOME_X, 0, "stand", "out_up" if lift_hat else "hips", lift_hat


def render():
    bg = background()
    frames = []
    for f in range(sec(SECONDS)):
        img = bg.copy()
        x, lift, legs, arms, hat = pose(f)
        blink = (f % 52) in (40, 41) and f < JIG[0] + 30
        # notes drift across from the right while the music plays
        if JIG[0] - 10 <= f < LEAP[1] + 10:
            for i in range(6):
                start = JIG[0] - 10 + i * 22
                age = f - start
                if 0 <= age < 60:
                    nx = W - 2 - age * 0.55 - (i % 2) * 6
                    ny = 3 + 2.0 * math.sin(age * 0.25 + i) + (i % 3)
                    a = min(1.0, age / 6) * min(1.0, (60 - age) / 10)
                    if abs(nx - (x + 5)) > 7:
                        note(img, nx, ny, (255, 236, 160), 0.8 * a, kind=i % 2)
        # shadow on the grass, smaller when he is in the air
        for dx in range(2 - lift, 9 + lift):
            put(img, x + dx, GROUND + 1, (14, 70, 28), 0.5 if lift else 0.7)
        leprechaun(img, x, GROUND + 1 - 13 - lift, legs, arms, hat_lift=hat, blink=blink)
        # landing puffs after the leap
        if LEAP[1] - 2 <= f < LEAP[1] + 6:
            age = f - (LEAP[1] - 2)
            for s in (-1, 1):
                add(img, x + 5 + s * (5 + age // 2), GROUND + 1, (180, 220, 160), 0.5 * (1 - age / 8))
        # gold sparkles and tiny shamrocks rise after the hat tip
        if f >= TIP:
            for i in range(24):
                t0 = TIP + i * 2
                age = f - t0
                if age < 0:
                    continue
                sx = x + 5 + (hash01(7, i) - 0.5) * 34
                sy = 14 - age * (0.18 + 0.1 * hash01(8, i))
                if sy < -2:
                    continue
                k = 0.5 + 0.5 * math.sin(age * 0.6 + i)
                if i % 4 == 0:
                    shamrock(img, sx, sy, 0, SHAMROCK, SHAMROCK_HI, SHAMROCK_DK, alpha=0.9)
                else:
                    sparkle4(img, sx, sy, k, GOLD_HI)
        frames.append(img)
    return frames
