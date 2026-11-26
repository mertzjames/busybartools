"""Scene: The Tomb of the Unknown Soldier. A plain white marble tomb on a plaza. A sentinel in a dark-blue dress
uniform walks the mat before it: 21 steps across, a pause, a turn to face the tomb, a pause, a turn, a pause, and the
walk back. Around him the weather changes, clear day, rain, snow and then night, and he keeps walking through it:
the tomb is always guarded (docs/DECISIONS.md D13).

Tone rules (D2, D3): no inscription on the tomb, no face (he is seen from the side and from behind), and no rifle,
although the real sentinels carry one (no weapons, D3). No caption.
"""

from __future__ import annotations

import math
import random

from busybar.canvas import FPS, H, W, ease_in_out, mix, put, sec
from mdfx import glow, quant, sky

NAME = "tomb"
TITLE = "The Tomb of the Unknown Soldier"
SECONDS = 16
KEYFRAMES = [(2.0, "A clear day: 21 steps across the mat"), (6.0, "Rain"), (8.0, "Facing the tomb, in the snow"),
             (11.0, "The walk back"), (14.5, "Night: always guarded")]

# --- the sentinel's walk ----------------------------------------------------------------------------------------

STEP_S = 0.3  # seconds per step (the real cadence is slower; the scene compresses it)
STEPS = 21
X_LEFT, X_RIGHT = 10, 52  # the sentinel's left column at each end of the mat (2 px per step)
WALK1 = (0.0, STEPS * STEP_S)  # 21 steps to the right: 0.0-6.3 s
TURN1 = 7.0  # after a pause, he turns to face the tomb
TURN2 = 9.2  # after a pause, he turns to face back down the mat
WALK2 = (9.9, 9.9 + 20 * STEP_S)  # and walks back (the scene ends just before the 21st step)

PAL = {"C": (44, 56, 136), "V": (78, 78, 92), "h": (120, 86, 62), "S": (222, 174, 136), "B": (56, 76, 166),
       "G": (246, 246, 240), "L": (86, 116, 192), "Y": (226, 188, 96), "K": (96, 96, 110)}
SIDE = [  # facing right: cap and visor, face, coat with a white glove, light-blue trousers with a gold stripe, shoes
    [".CC..", "CCCCV", ".hSS.", ".BBB.", ".BBB.", ".BGB.", ".BBB.", ".LYL.", ".L.L.", "L...L", "K...K"],
    [".CC..", "CCCCV", ".hSS.", ".BBB.", ".BBB.", ".BGB.", ".BBB.", ".LYL.", ".LYL.", ".LL..", ".KK.."],
]
BACK = [".CCC.", "CCCCC", ".hhh.", "BBBBB", "BBBBB", "GBBBG", ".BBB.", ".LLL.", ".L.L.", ".L.L.", ".K.K."]
FIG_Y = 5  # top row of the figure: his shoes are on row 15


def sentinel(img, t: float, lift: float = 0.0) -> None:
    """Draw the sentinel at time t; `lift` brightens him under the night floodlights."""
    if t < WALK1[1]:
        p = (t - WALK1[0]) / (WALK1[1] - WALK1[0])
        x, rows, flip = X_LEFT + (X_RIGHT - X_LEFT) * p, SIDE[int(t / STEP_S) % 2], False
    elif t < TURN1:
        x, rows, flip = X_RIGHT, SIDE[1], False
    elif t < TURN2:
        x, rows, flip = X_RIGHT - 0.5, BACK, False
    elif t < WALK2[0]:
        x, rows, flip = X_RIGHT, SIDE[1], True
    else:
        p = min(1.0, (t - WALK2[0]) / (WALK2[1] - WALK2[0]))
        x = X_RIGHT - (X_RIGHT - X_LEFT) * 20 / 21 * p
        rows, flip = SIDE[int((t - WALK2[0]) / STEP_S) % 2], True
    x0 = int(math.floor(x + 0.5))
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row[::-1] if flip else row):
            if ch != ".":
                put(img, x0 + dx, FIG_Y + dy, mix(PAL[ch], (255, 255, 255), lift))


# --- weather ----------------------------------------------------------------------------------------------------

CLEAR, RAIN, SNOW, NIGHT = range(4)
# (start of the change, end of the change) into each next weather
CHANGES = [(3.4, 4.4), (7.4, 8.4), (11.4, 12.4)]

SKIES = [
    [(0, (56, 104, 184)), (7, (104, 152, 214)), (12, (178, 204, 232))],  # a clear day
    [(0, (58, 64, 78)), (7, (92, 98, 112)), (12, (124, 128, 138))],  # rain
    [(0, (96, 104, 124)), (7, (128, 134, 150)), (12, (150, 156, 170))],  # snow, grey enough for a white tomb
    [(0, (4, 6, 20)), (7, (12, 18, 44)), (12, (26, 32, 62))],  # night
]
PLAZA = [(198, 194, 184), (124, 126, 132), (222, 226, 234), (64, 64, 78)]
MARBLE = [(240, 238, 230), (210, 212, 214), (232, 234, 238), (226, 222, 210)]


def weights(t: float) -> list[float]:
    """How much of each weather shows at time t (quantized, so slow changes keep the .anim small)."""
    w = [1.0, 0.0, 0.0, 0.0]
    for i, (a, b) in enumerate(CHANGES):
        if t >= a:
            k = quant(ease_in_out((t - a) / (b - a)), 20)
            w = [0.0] * 4
            w[i], w[i + 1] = 1 - k, k
    return w


def blend(colors, w):
    out = [0.0, 0.0, 0.0]
    for c, k in zip(colors, w):
        for j in range(3):
            out[j] += c[j] * k
    return tuple(int(v) for v in out)


TOMB_X0, TOMB_X1 = 28, 45  # the body of the tomb
TOMB_TOP = 5


def scene_base(w):
    stops = [(row, blend([s[i][1] for s in SKIES], w)) for i, row in enumerate((0, 7, 12))]
    img = sky(stops)
    plaza = blend(PLAZA, w)
    marble = blend(MARBLE, w)
    for x in range(W):
        for y in range(13, H):
            put(img, x, y, mix(plaza, (0, 0, 0), 0.08 * (y - 13)))
    for x in range(6, 66):  # the mat the sentinel walks
        put(img, x, 15, mix(plaza, (40, 40, 48), 0.55))
    # the tomb: a cornice, a plain body with faint corner pilasters, a two-step plinth; no inscription
    for x in range(TOMB_X0 - 1, TOMB_X1 + 2):
        put(img, x, TOMB_TOP, mix(marble, (255, 255, 255), 0.3))
    for y in range(TOMB_TOP + 1, 12):
        for x in range(TOMB_X0, TOMB_X1 + 1):
            c = marble
            if x in (TOMB_X0 + 1, TOMB_X1 - 1) or y == TOMB_TOP + 1:
                c = mix(marble, (120, 124, 140), 0.22)  # pilasters and a frieze line, in faint relief
            put(img, x, y, c)
    for x in range(TOMB_X0 - 2, TOMB_X1 + 3):
        put(img, x, 12, mix(marble, (110, 112, 126), 0.25))
    for x in range(TOMB_X0 - 3, TOMB_X1 + 4):
        put(img, x, 13, mix(marble, (110, 112, 126), 0.4))
    return img


RNG = random.Random(41)
RAIN_DROPS = [(RNG.uniform(0, W + 8), RNG.uniform(0, H), RNG.uniform(26, 34)) for _ in range(30)]
FLAKES = [(RNG.uniform(0, W), RNG.uniform(0, H), RNG.uniform(2.5, 4.0), RNG.uniform(0, 6.3)) for _ in range(40)]
STARS = [(RNG.randrange(W), RNG.randrange(9), RNG.choice((0.4, 0.6, 0.85))) for _ in range(22)]


def rain(img, t: float, a: float) -> None:
    for x0, y0, v in RAIN_DROPS:  # slanting streaks, three pixels long
        y = (y0 + v * t) % (H + 3) - 2
        x = (x0 - 0.3 * v * t) % (W + 8) - 4
        for k in range(3):
            put(img, int(x - 0.5 * k), int(y + k), (206, 218, 236), a * (0.55 + 0.2 * k))


def snow(img, t: float, a: float) -> None:
    for x0, y0, v, ph in FLAKES:
        y = (y0 + v * t) % (H + 1)
        x = (x0 + 1.2 * math.sin(t * 1.3 + ph)) % W
        put(img, int(x), int(y), (246, 248, 252), a * 0.9)


def frame(f: int):
    t = f / FPS
    w = weights(t)
    img = scene_base(w)
    if w[SNOW] > 0:  # the snow settles on the cornice and the plaza while it falls
        lay = w[SNOW] * min(1.0, max(0.0, (t - 8.0) / 2.5))
        for x in range(TOMB_X0 - 1, TOMB_X1 + 2):
            put(img, x, TOMB_TOP - 1, (246, 248, 252), 0.8 * lay)
    if w[NIGHT] > 0:
        for x, y, a in STARS:
            put(img, x, y, (210, 214, 236), a * w[NIGHT])
        glow(img, 36, 13, 40, (255, 210, 150), 0.45 * w[NIGHT], squash=2.2)  # floodlights on the plaza and mist
    sentinel(img, t, 0.18 * w[NIGHT])
    if w[RAIN] > 0:
        rain(img, t, w[RAIN])
    if w[SNOW] > 0:
        snow(img, t, w[SNOW])
    return img


def render():
    return [frame(f) for f in range(sec(SECONDS))]
