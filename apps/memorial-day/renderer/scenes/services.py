"""Scene: The Armed Services. The six U.S. armed services one after another, in order of precedence: Army, Marine
Corps, Navy, Air Force, Space Force and Coast Guard. Each is a small vignette of its domain with its name across the
top in the big font, and each slides in from the right as the last slides away (docs/DECISIONS.md D12).

Tone rules (D2, D3): the services are shown only by their domain, a plain vehicle silhouette, generic uniform colors
and the name in text. No emblems, seals, insignia, logos, medals or markings; no faces; no weapons or combat.

The file is self-contained (only the shared kit), so other apps can copy it.
"""

from __future__ import annotations

import math
import random

from PIL import Image

from busybar.canvas import FPS, H, W, ease_in_out, mix, put, sec
from busybar.font import draw_text, text_width

NAME = "services"
TITLE = "The Armed Services"
SLOT = 2.8  # seconds per service
SLIDE = 0.6  # seconds of each slide between services, centered on the boundary
SECONDS = 17
CAP_Y = 0  # caption row: the art keeps to rows 8-15 below it
# The names on screen, in order of precedence. The widest, MARINE CORPS, is 67 px (68 with its shadow).
CAPTIONS = ["ARMY", "MARINE CORPS", "NAVY", "AIR FORCE", "SPACE FORCE", "COAST GUARD"]

CAPTION_GRAD = ((246, 242, 232), (206, 212, 230))
CAPTION_SHADOW = (20, 22, 52)


# --- helpers ----------------------------------------------------------------------------------------------------

def gradient(stops) -> Image.Image:
    """A 72x16 vertical gradient through `stops` [(row, color), ...]."""
    img = Image.new("RGBA", (W, H))
    px = img.load()
    for y in range(H):
        c = stops[-1][1]
        if y <= stops[0][0]:
            c = stops[0][1]
        else:
            for (y0, c0), (y1, c1) in zip(stops, stops[1:]):
                if y0 <= y <= y1:
                    c = mix(c0, c1, (y - y0) / max(1, y1 - y0))
                    break
        for x in range(W):
            px[x, y] = tuple(c) + (255,)
    return img


def dim_rect(img, x0: int, y0: int, x1: int, y1: int, k: float, feather: int = 2) -> None:
    """Darken a box (inclusive) behind a caption, fading out over `feather` px around it."""
    px = img.load()
    for y in range(max(0, y0 - feather), min(H, y1 + feather + 1)):
        for x in range(max(0, x0 - feather), min(W, x1 + feather + 1)):
            d = max(x0 - x, 0, x - x1, y0 - y, 0, y - y1)
            f = k if d == 0 else k * (1 - d / (feather + 1))
            r, g, b, a = px[x, y]
            px[x, y] = (int(r * (1 - f)), int(g * (1 - f)), int(b * (1 - f)), a)


def caption(img, text: str, back: float = 0.45) -> None:
    """The service's name across the top in the big font, over a softly darkened box."""
    w = text_width(text, "big")
    x = (W - w) // 2
    if back:
        dim_rect(img, x - 1, CAP_Y, x + w + 1, CAP_Y + 7, back, feather=2)
    draw_text(img, text, x, CAP_Y, None, font="big", gradient=CAPTION_GRAD, shadow=CAPTION_SHADOW)


def sprite(img, rows, x: int, y: int, pal, flip: bool = False) -> None:
    """Draw a character-grid sprite (top-left at x, y); '.' is transparent."""
    for dy, row in enumerate(rows):
        for dx, ch in enumerate(row[::-1] if flip else row):
            if ch != ".":
                put(img, x + dx, y + dy, pal[ch])


def fx(x: float) -> int:
    """Round half up, like JS Math.round."""
    return int(math.floor(x + 0.5))


# --- ARMY: a column of soldiers marching along a road -----------------------------------------------------------

ARMY_SKY = gradient([(0, (50, 74, 134)), (5, (112, 132, 178)), (9, (196, 208, 226)), (14, (228, 216, 192))])
SOLDIER_PAL = {"H": (88, 100, 56), "S": (226, 178, 138), "U": (112, 124, 70), "P": (96, 106, 62),
               "B": (92, 70, 50)}
SOLDIER = [  # facing right; two strides, everyone in step
    [".HH.", "HHHH", ".HS.", ".UU.", ".UUU", ".UUS", ".PP.", "P..P"],
    [".HH.", "HHHH", ".HS.", ".UU.", ".UU.", "SUU.", ".PP.", ".PP."],
]


def army_base() -> Image.Image:
    img = ARMY_SKY.copy()
    for x in range(W):
        put(img, x, 15, (150, 128, 92))  # the road, dark enough that the boots read on it
    return img


ARMY_BASE = army_base()


def army(lt: float) -> Image.Image:
    img = ARMY_BASE.copy()
    step = int(math.floor((lt + 2) / 0.35))  # in step: every soldier changes stride together
    lead = 46 + 4.0 * lt
    caption(img, CAPTIONS[0], back=0.3)  # first, so its dimmed box never darkens the figures below it
    for k in range(5):
        sprite(img, SOLDIER[step % 2], fx(lead - 8 * k), 8, SOLDIER_PAL)
    return img


# --- MARINES: three figures in dress blues, at attention, then saluting -------------------------------------------

MARINE_SKY = gradient([(0, (52, 70, 130)), (5, (120, 116, 150)), (8, (230, 196, 150)), (15, (240, 214, 170))])
MARINE_PAL = {"W": (246, 244, 238), "S": (222, 172, 132), "C": (36, 48, 124), "Y": (240, 200, 96),
              "L": (84, 112, 180), "R": (214, 56, 56)}
MARINE = [  # front view, at attention; the face is plain skin
    ".WWW.", ".SSS.", "CCCCC", "CCYCC", "SCYCS", ".WWW.", ".L.L.", "RL.LR",
]
MARINE_SALUTE = [  # the right hand raised to the cap brim
    "SWWW.", "CSSS.", "CCCCC", ".CYCC", ".CYCS", ".WWW.", ".L.L.", "RL.LR",
]


def marines_base() -> Image.Image:
    img = MARINE_SKY.copy()
    for x in range(W):  # a plain sandstone wall behind them: the white caps and the dark coats both read on it
        for y in range(7, 14):
            put(img, x, y, (172, 142, 104) if (y - 7) % 3 or (x + (y // 3) * 4) % 8 else (150, 122, 88))
        put(img, x, 14, (214, 200, 172))
        put(img, x, 15, (192, 178, 150))
    return img


MARINES_BASE = marines_base()


def marines(lt: float) -> Image.Image:
    img = MARINES_BASE.copy()
    salute = 1.0 <= lt < 2.5
    caption(img, CAPTIONS[1], back=0.3)
    for cx in (21, 33, 45):
        sprite(img, MARINE_SALUTE if salute else MARINE, cx, 8, MARINE_PAL)
    return img


# --- NAVY: a grey ship under way at sea ------------------------------------------------------------------------

NAVY_SKY = gradient([(0, (48, 74, 132)), (5, (110, 122, 164)), (8, (232, 200, 160)), (12, (246, 222, 182))])
SHIP_PAL = {"M": (84, 90, 106), "T": (132, 140, 156), "S": (96, 104, 120), "H": (74, 80, 96),
            "D": (58, 62, 78)}
SHIP = [  # bow to the right: a raked bow, a bridge and a mast; no guns or numbers
    "...............M............",
    "..............MMM...........",
    ".............SSSSS..........",
    "...........SSSSSSSS..SS.....",
    "TTTTTTTTTTTTTTTTTTTTTTTTTTTT",
    ".HHHHHHHHHHHHHHHHHHHHHHHHHH.",
    "..DDDDDDDDDDDDDDDDDDDDDDDD..",
]
SEA_GLINTS = [(random.Random(3 + i).randrange(W), 13 + (i % 3)) for i in range(16)]


def navy_base() -> Image.Image:
    img = NAVY_SKY.copy()
    for y in range(13, H):
        for x in range(W):
            put(img, x, y, mix((44, 82, 136), (26, 52, 98), (y - 13) / 2))
    return img


NAVY_BASE = navy_base()


def navy(lt: float) -> Image.Image:
    img = NAVY_BASE.copy()
    for x0, y in SEA_GLINTS:  # glints drift slowly past
        put(img, (x0 - int(lt * 3)) % W, y, (130, 166, 208), 0.7)
    x = fx(18 + 3.0 * lt)
    sprite(img, SHIP, x, 6, SHIP_PAL)
    for k in range(7):  # the wake behind the stern and a bow wave
        put(img, x - 1 - k, 13 + (k % 2), (226, 236, 244), 0.9 - k * 0.12)
    put(img, x + 27, 12, (236, 242, 248))
    put(img, x + 28, 13, (200, 216, 232), 0.6)
    caption(img, CAPTIONS[2], back=0.3)
    return img


# --- AIR FORCE: jets in formation trailing white smoke ------------------------------------------------------------

AIR_SKY = gradient([(0, (20, 38, 104)), (8, (40, 72, 150)), (15, (70, 110, 182))])
JET = [".LL....", "..LLL..", "LLLLLLH", "..LLL..", ".LL...."]  # seen from below, nose right; no markings
JET_PAL = {"L": (206, 212, 226), "H": (250, 252, 255)}
FORMATION = [(0, 9), (-11, 11), (-22, 13)]  # an echelon: the lead and two wingmen (centre rows)


def air_force(lt: float) -> Image.Image:
    img = AIR_SKY.copy()
    caption(img, CAPTIONS[3], back=0.2)
    lead = 30 + 9.0 * lt
    for dx, y in FORMATION:
        x = fx(lead + dx)
        for k in range(1, 48):  # a fading smoke trail back toward the left edge
            put(img, x - k, y, (232, 236, 246), max(0.0, 0.5 - k * 0.012))
    for dx, y in FORMATION:
        sprite(img, JET, fx(lead + dx), y - 2, JET_PAL)
    return img


# --- SPACE FORCE: a satellite over the curve of the Earth ---------------------------------------------------------

def space_base() -> Image.Image:
    img = gradient([(0, (4, 6, 20)), (15, (12, 18, 46))])
    rng = random.Random(11)
    for _ in range(26):
        put(img, rng.randrange(W), rng.randrange(12), (200, 206, 230), rng.choice((0.4, 0.6, 0.9)))
    return img


SPACE_BASE = space_base()
EARTH = (36.0, 70.0, 57.0)  # centre x, centre y, radius: the top of the curve at row 13


def space_force(lt: float) -> Image.Image:
    img = SPACE_BASE.copy()
    cx, cy, r = EARTH
    spin = int(lt * 2)  # the land drifts slowly
    for y in range(9, H):
        for x in range(W):
            d = math.hypot(x - cx, y - cy)
            if d < r:
                u = x + spin
                land = math.sin(u * 0.21) + 0.8 * math.sin(u * 0.47 + y) > 0.9
                cloud = math.sin(u * 0.33 + y * 1.7) > 0.93
                c = (236, 240, 248) if cloud else (70, 128, 70) if land else (40, 92, 176)
                put(img, x, y, c)
            elif d < r + 1.2:
                put(img, x, y, (110, 176, 240), 0.9)  # the atmosphere's thin bright rim
            elif d < r + 2.4:
                put(img, x, y, (60, 110, 200), 0.35)
    x = fx(22 + 5.0 * lt)
    for y in (9, 10):
        for dx in (-5, -4, -3, 4, 5, 6):  # solar panels either side of the body
            put(img, x + dx, y, (84, 128, 222) if (dx + y) % 2 else (64, 104, 196))
        put(img, x - 2, y, (150, 150, 160))
        put(img, x + 3, y, (150, 150, 160))
        for dx in (-1, 0, 1, 2):
            put(img, x + dx, y, (230, 190, 96) if y == 9 else (198, 158, 74))
    put(img, x + 1, 8, (180, 180, 190))  # an antenna
    if int(lt * 2) % 2 == 0:
        put(img, x + 1, 7, (250, 236, 200), 0.8)  # a small blinking light
    caption(img, CAPTIONS[4], back=0.0)
    return img


# --- COAST GUARD: a rescue helicopter hovering over the waves ----------------------------------------------------

GUARD_SKY = gradient([(0, (70, 80, 100)), (7, (132, 140, 152)), (12, (176, 180, 182))])
HELO = [  # facing right; plain orange, no markings
    "..........OOO..",
    "OOOOOOOOOOOOOGG",
    ".O.......OOOOOO",
    ".........K...K.",
    "........KKKKKK.",
]
HELO_PAL = {"O": (234, 106, 44), "G": (190, 222, 240), "K": (110, 110, 120)}


def coast_guard(lt: float) -> Image.Image:
    img = GUARD_SKY.copy()
    f = int(math.floor(lt * FPS))
    for y in range(13, H):  # the sea, with white caps rolling past
        for x in range(W):
            put(img, x, y, mix((44, 92, 106), (26, 60, 74), (y - 13) / 2))
    roll = int(math.floor(lt * 5))
    for x in range(W):
        for y in range(13, H):
            if (x + roll + 5 * y) % 11 == 0:
                put(img, x, y, (214, 228, 232), 0.85)
    hx = fx(28 + 1.0 * lt)
    hy = 8 + (1 if (f // 12) % 2 else 0)  # a gentle hover
    sprite(img, HELO, hx, hy, HELO_PAL)
    span = 7 if f % 2 == 0 else 6  # the rotor blurs
    for dx in range(-span, span + 1):
        put(img, hx + 11 + dx, hy - 1, (214, 218, 224), 0.85)
    put(img, hx, hy + 1 - (f % 2) * 2, (214, 218, 224), 0.8)  # tail rotor
    for yy in range(hy + 5, 13):  # the hoist line down to a life raft
        put(img, hx + 10, yy, (236, 236, 228), 0.9)
    for dx in (-1, 0, 1):
        put(img, hx + 10 + dx, 13, (244, 132, 52))
    caption(img, CAPTIONS[5], back=0.3)
    return img


VIGNETTES = [army, marines, navy, air_force, space_force, coast_guard]
KEYFRAMES = [(1.4 + i * SLOT, name) for i, name in
             enumerate(["The Army marches", "The Marine Corps", "The Navy at sea", "The Air Force in formation",
                        "The Space Force in orbit", "The Coast Guard to the rescue"])]


def frame(t: float) -> Image.Image:
    """The frame at time t: one vignette, or two during the slide between them."""
    i = min(len(VIGNETTES) - 1, int(t / SLOT))
    for b in range(1, len(VIGNETTES)):
        edge = b * SLOT
        if abs(t - edge) < SLIDE / 2:
            p = ease_in_out((t - edge + SLIDE / 2) / SLIDE)
            s = fx(W * p)
            a = VIGNETTES[b - 1](t - (b - 1) * SLOT)
            nxt = VIGNETTES[b](t - b * SLOT)
            img = Image.new("RGBA", (W, H))
            img.paste(a.crop((s, 0, W, H)), (0, 0))
            img.paste(nxt.crop((0, 0, s, H)), (W - s, 0))
            return img
    return VIGNETTES[i](t - i * SLOT)


def render():
    return [frame(f / FPS) for f in range(sec(SECONDS))]
