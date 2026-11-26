"""Props shared by the final-week scenes (Dec 22-25): the Christmas tree, the star, the sleigh team and gifts.

Reusing them makes the last days read as one story: the tree is decorated (22), the sleigh flies (23), the star goes
on top (24), and on Christmas Day everything comes together (25).
"""

from __future__ import annotations

import math

from busybar.canvas import add, put
from busybar.sprite import Sprite

from common import LIGHTS, PINE, PINE_DARK

TINSEL = (255, 214, 92)
ORNAMENT_COLORS = ((230, 40, 60), (60, 130, 255), (255, 200, 40), (240, 240, 255), (200, 80, 230))


def tree_mask(cx: int, top: int, base: int):
    """{(x, y): edge?} pixels of a tiered tree from row `top` to `base` (the trunk sits below base)."""
    pts = {}
    h = base - top + 1
    for y in range(top, base + 1):
        k = (y - top) / max(1, h - 1)
        tier = ((y - top) % 4) / 3
        half = int(round(0.6 + k * h * 0.44 + tier * 1.2))
        for x in range(cx - half, cx + half + 1):
            pts[(x, y)] = abs(x - cx) == half
    return pts


def light_points(cx: int, top: int, base: int):
    """Bulb positions along a garland that zig-zags down the tree, bottom first."""
    pts = []
    h = base - top + 1
    for y in range(base - 1, top, -2):
        k = (y - top) / max(1, h - 1)
        half = k * h * 0.44
        row = (base - 1 - y) // 2
        xs = [cx - half * 0.8 + i * (half * 1.6) / 3 for i in range(4)]
        if row % 2:
            xs.reverse()
        for x in xs:
            pts.append((round(x), y))
    return pts


def ornament_points(cx: int, top: int, base: int):
    pts = []
    h = base - top + 1
    for i, y in enumerate(range(base - 2, top + 2, -3)):
        k = (y - top) / max(1, h - 1)
        half = k * h * 0.44
        for j, f in enumerate((-0.5, 0.0, 0.55) if i % 2 else (-0.25, 0.3)):
            pts.append((round(cx + f * half * 1.6), y, ORNAMENT_COLORS[(i * 3 + j) % len(ORNAMENT_COLORS)]))
    return pts


def draw_tree(img, cx: int, top: int, base: int, f: int, lights: float = 0.0, ornaments: float = 0.0,
              tinsel: float = 0.0, twinkle: bool = False) -> None:
    """The Christmas tree. lights/ornaments/tinsel in 0..1 reveal that fraction of each decoration."""
    for (x, y), edge in tree_mask(cx, top, base).items():
        c = PINE if (edge or (x + y) % 3 == 0) else PINE_DARK
        put(img, x, y, c)
    for y in (base + 1, base + 2):
        put(img, cx, y, (120, 70, 30))
        put(img, cx - 1, y, (96, 56, 24))
    if tinsel > 0:
        h = base - top
        n = int(h * 2 * tinsel)
        for i in range(n):
            s = i / (h * 2)
            y = top + 3 + s * (h - 3)
            k = (y - top) / max(1, h)
            half = k * h * 0.44
            x = cx + half * math.sin(s * math.pi * 5)
            put(img, x, y, TINSEL, 0.85)
    if ornaments > 0:
        pts = ornament_points(cx, top, base)
        for x, y, c in pts[:int(round(len(pts) * ornaments))]:
            put(img, x, y, c)
    if lights > 0:
        pts = light_points(cx, top, base)
        for i, (x, y) in enumerate(pts[:int(round(len(pts) * lights))]):
            c = LIGHTS[i % len(LIGHTS)]
            a = 1.0
            if twinkle:
                a = 0.45 + 0.55 * (0.5 + 0.5 * math.sin(f * 0.5 + i * 2.3))
            put(img, x, y, c, a)
            if twinkle and a > 0.9:
                add(img, x, y, (255, 255, 255), 0.3)


STAR = Sprite("star", {"Y": "#FFE45C", "y": "#FFB020", "W": "#FFFFF0"}, """
..Y..
YYWYY
.yYy.
.y.y.
""")


def draw_star_glow(img, cx: float, cy: float, f: int, strength: float = 1.0) -> None:
    """Twinkling rays around the star."""
    for ang in range(0, 360, 45):
        r = 3 + (1 if (f // 3 + ang // 45) % 2 else 0)
        a = math.radians(ang + f * 2)
        add(img, cx + r * math.cos(a), cy + r * math.sin(a), (255, 230, 140), 0.5 * strength)


_REIN = {"B": "#8A4E28", "b": "#D8A878", "y": "#E8E0D0", "e": "#FFFFFF", "n": "#7A4A2A", "w": "#FFFFFF"}
SMALL_REINDEER = Sprite("small_reindeer", _REIN, """
.....y.y
......y.
.....BBB
.BBBBBBn
wBbbbbB.
B.....B.
""", """
.....y.y
......y.
.....BBB
.BBBBBBn
wBbbbbB.
.B...B..
""")
SLEIGH = Sprite("sleigh", {
    "W": "#FFFFFF", "R": "#E0202E", "r": "#9A1222", "S": "#F6C79C", "Y": "#FFD24A", "G": "#2E9E4E",
    "P": "#8A4AD0",
}, """
....RW.....
...RRR.....
...SSS.....
..WWWW.GP..
R.RRRRGGPP.
RYYYYYYYYYR
RRRRRRRRRRr
.Y.....Y.YY
YYYYYYYYYY.
""")


def draw_sleigh_team(img, x: float, y: float, f: int, reindeer: int = 2) -> None:
    """Sleigh at (x, y) facing right, pulled by `reindeer` small reindeer in front."""
    from busybar.canvas import blit
    # reins first, so the reindeer are drawn over them
    for k in range(4 + (reindeer - 1) * 10 + 3):
        put(img, x + 10 + k, y + 5, (200, 150, 60), 0.6)
    blit(img, SLEIGH.img(), x, y)
    for i in range(reindeer):
        rx = x + 13 + i * 10
        ry = y + 1 + (1 if (f // 3 + i) % 2 else 0)
        blit(img, SMALL_REINDEER.img((f // 3 + i) % 2), rx, ry)


def gift(img, x: int, y: int, w: int, h: int, body, ribbon) -> None:
    for yy in range(h):
        for xx in range(w):
            c = body
            if xx == 0 or yy == h - 1:
                c = tuple(int(v * 0.72) for v in body)
            if xx == w // 2 or yy == h // 2:
                c = ribbon
            put(img, x + xx, y + yy, c)
    cx = x + w // 2
    for dx, dy in ((-1, -1), (1, -1), (0, -1)):
        put(img, cx + dx, y + dy, ribbon)
