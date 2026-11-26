"""Original pixel-art sprites for Halloween (docs/DECISIONS.md D5). Sprites face right; flip for left.

Black is an unlit LED, so "black" things (the bat, the cat, the witch's dress) are lit deep violet-greys with a
lighter rim, and every eye is a lit color.
"""

from busybar.sprite import Sprite

# Bat, 7x4, three flap frames: wings up, level, down. Lit violet-grey with a lighter body.
BAT = Sprite("bat", {"V": "#5A4680", "B": "#7A64A8", "E": "#FF5A3C"}, """
V.....V
VV.B.VV
.VBBBV.
...B...
""", """
.......
VVBBBVV
V.EBE.V
...B...
""", """
.......
..BBB..
.VEBEV.
VV.B.VV
""", """
.......
VVBBBVV
V.EBE.V
...B...
""")


# The haunted house, 26x16: a tower with a spire on the left, a steep central gable with an attic window, a lower
# roof to the right and a chimney. W wall, R roof, L moonlit roof edge (the moon is on the left), E moonlit wall
# edge, C chimney, T eaves; digits are windows and D the door (both drawn per frame). Built in code so the gable's
# slopes stay exact.
def _house_grid() -> list[str]:
    g = [["."] * 26 for _ in range(16)]

    def put_(x, y, ch):
        if 0 <= x < 26 and 0 <= y < 16:
            g[y][x] = ch

    # tower: spire rows 0-4, wall rows 5-15, x 1-5
    put_(3, 0, "E")
    put_(3, 1, "E")
    for x in (2, 3, 4):
        put_(x, 2, "LRR"[x - 2])
        put_(x, 3, "LRR"[x - 2])
    for x in range(1, 6):
        put_(x, 4, "L" if x == 1 else "R")
        for y in range(5, 16):
            put_(x, y, "E" if x == 1 else "W")
    # right-hand roof (rows 6-9) and its moonlit top edge, then the main wall (rows 10-15)
    for x in range(17, 26):
        put_(x, 6, "L")
        for y in range(7, 10):
            put_(x, y, "R")
    for x in range(6, 26):
        for y in range(10, 16):
            put_(x, y, "E" if x == 6 else "W")
        put_(x, 10, "T")
    # the gable: apex at (14, 1), 45-degree slopes two pixels thick, wall inside
    for y in range(1, 10):
        d = y - 1
        for x in range(14 - d, 14 + d + 1):
            edge_l, edge_r = x <= 14 - d + 1, x >= 14 + d - 1
            put_(x, y, "L" if x == 14 - d else ("R" if edge_l or edge_r else "W"))
    for x, y in ((22, 3), (23, 3), (22, 4), (23, 4), (22, 5), (23, 5)):
        put_(x, y, "C")
    for ch, cells in {"1": [(3, 6), (4, 6), (3, 7), (4, 7)], "5": [(3, 11), (4, 11), (3, 12), (4, 12)],
                      "3": [(x, y) for x in (13, 14, 15) for y in (5, 6, 7)],
                      "2": [(x, y) for x in (8, 9, 10) for y in (11, 12)],
                      "4": [(x, y) for x in (19, 20, 21) for y in (11, 12)],
                      "6": [(x, y) for x in (8, 9) for y in (14, 15)],
                      "7": [(x, y) for x in (21, 22) for y in (14, 15)],
                      "D": [(x, y) for x in (14, 15, 16) for y in (12, 13, 14, 15)]}.items():
        for x, y in cells:
            put_(x, y, ch)
    return ["".join(r) for r in g]


HOUSE_GRID = "\n".join(_house_grid())
HOUSE_X = 31
HOUSE_WINDOWS: dict[str, list[tuple[int, int]]] = {}
for _y, _r in enumerate(HOUSE_GRID.splitlines()):
    for _x, _ch in enumerate(_r):
        if _ch.isdigit() or _ch == "D":
            HOUSE_WINDOWS.setdefault(_ch, []).append((_x, _y))
HOUSE = Sprite("house", {"W": "#56467A", "R": "#2E2248", "L": "#7C6AA8", "E": "#7C6AA8", "C": "#4A3C64",
                         "T": "#3A2C56", "D": "#6E3C32", **{str(i): "#1E0C1E" for i in range(1, 8)}}, HOUSE_GRID)


# Trick-or-treaters, facing right, two walk frames each (feet swap), each with a candy bucket or bag in front.
# Generic costumes: a sheet ghost, a little witch, a pumpkin suit and a caped hero. Eyes are lit dark violet on
# light skin and sheets; the hats are lit violet so they read against the night.
GHOST_KID = Sprite("ghost_kid", {"W": "#EEF2FF", "w": "#B4BEDC", "E": "#3C1E5A", "h": "#C8C8C8", "O": "#FF780A",
                                 "o": "#FFD25A", "S": "#8C6450"}, """
..WWW...
.WWWWW..
.WWEWE..
.WWWWW..
WWWWWWw.
WWWWWWwh
WWWWWwOO
WWWWWwoO
W.WW.Ww.
.S...S..
""", """
..WWW...
.WWWWW..
.WWEWE..
.WWWWW..
WWWWWWw.
WWWWWWwh
WWWWWwOO
WWWWWwoO
WW.WW.w.
..S.S...
""")

WITCH_KID = Sprite("witch_kid", {"H": "#7A4AB4", "G": "#8CFF3C", "S": "#F0BE96", "E": "#3C1E3C", "P": "#9A46D2",
                                 "p": "#6A2EA0", "h": "#C8C8C8", "O": "#FF780A", "o": "#FFD25A", "L": "#FF8C1E",
                                 "l": "#F0F0F0"}, """
...H....
..HHH...
..GGG...
HHHHHHH.
..SSSE..
..SSSS..
.PPPPPh.
PPPPpOO.
PPPPpoO.
.L..L...
""", """
...H....
..HHH...
..GGG...
HHHHHHH.
..SSSE..
..SSSS..
.PPPPPh.
PPPPpOO.
PPPPpoO.
..LL....
""")

PUMPKIN_KID = Sprite("pumpkin_kid", {"G": "#5AB428", "g": "#3C8C1E", "S": "#B07048", "E": "#2A1020",
                                     "O": "#FF7A0A", "o": "#C85000", "B": "#F0F0F0", "b": "#C0C0D0",
                                     "L": "#3C8C1E"}, """
...G....
..GGg...
..SSSE..
..SSSS..
.OOOOo..
OOoOOoB.
OOoOOBBB
OOoOObBB
.OOOo...
..L.L...
""", """
...G....
..GGg...
..SSSE..
..SSSS..
.OOOOo..
OOoOOoB.
OOoOOBBB
OOoOObBB
.OOOo...
.L...L..
""")

HERO_KID = Sprite("hero_kid", {"H": "#8C5A32", "S": "#E6AA78", "M": "#28A0FF", "E": "#F0F0FF", "C": "#E6283C",
                               "c": "#A0142A", "B": "#2864DC", "Y": "#FFD23C", "h": "#C8C8C8", "O": "#B45AFF",
                               "o": "#FFD25A", "R": "#E6283C"}, """
...HHH...
..HHHHH..
..MMEME..
..SSSS...
.cBBBB...
CcBYBBh..
CcBBBBOO.
CC.BB.oO.
C..B.B...
...R.R...
""", """
...HHH...
..HHHHH..
..MMEME..
..SSSS...
.cBBBB...
CcBYBBh..
CcBBBBOO.
CC.BB.oO.
C...BB...
....RR...
""")


# A big bat, 15x7, three flap frames, for flying close past the moon.
BIG_BAT = Sprite("big_bat", {"V": "#5A4680", "v": "#46366A", "B": "#7A64A8", "E": "#FFDC3C", "F": "#F0F0F0"}, """
V.............V
VV....B.B....VV
VVV..BBBBB..VVV
.VVVVBEBEBVVVV.
..VVVBBBBBVVV..
...V.vBFBv.V...
.......B.......
""", """
...............
...............
.....BB.BB.....
VVVVVBEBEBVVVVV
VVVVVBBBBBVVVVV
V.V..vBFBv..V.V
.......B.......
""", """
...............
...............
.....BB.BB.....
....VBEBEBV....
..VVVBBBBBVVV..
.VVV.vBFBv.VVV.
VV.....B.....VV
""")

# The witch on her broom, 16x11, facing right: a tall violet hat with a green band, a green face with a long nose
# and a lit violet eye, orange hair, a violet dress (lit, since black is an unlit LED) and a wooden broom with
# straw bristles. Two frames: the hair and hem flutter.
WITCH = Sprite("witch", {"H": "#8A52C8", "h": "#6A3AA6", "G": "#8CFF3C", "F": "#7CE050", "N": "#5CC038",
                         "E": "#2C1448", "R": "#FF6E1E", "D": "#7040A8", "d": "#54308A", "A": "#7CE050",
                         "B": "#A8683C", "S": "#F0C850", "s": "#C8963C", "L": "#FF8C1E"}, """
......H.........
......HH........
......HHH.......
......GGG.......
....hHHHHHh.....
......FFEFN.....
.....RFFFF......
.....RDDDAA.....
ss..RDDDDDA.....
SSSBBBBBBBBBBBB.
ss...DdLL.......
""", """
......H.........
......HH........
......HHH.......
......GGG.......
....hHHHHHh.....
......FFEFN.....
....RRFFFF......
....RRDDDAA.....
ss.RRDDDDDA.....
SSSBBBBBBBBBBBB.
ss..DDdLL.......
""")
# The witch far away (for her second pass), 9x6.
WITCH_FAR = Sprite("witch_far", {"H": "#8A52C8", "F": "#7CE050", "R": "#FF6E1E", "D": "#7040A8", "B": "#A8683C",
                                 "S": "#F0C850"}, """
....H....
...HHH...
..HHHHH..
...RFF...
SSBBBBBBB
...DD....
""")


# A friendly ghost, 11x11, two frames (the hem ripples). Lit violet eyes, pink cheeks, a small smile.
GHOST = Sprite("ghost", {"W": "#F0F6FF", "w": "#B4C4E6", "E": "#3A2470", "P": "#FF8CB4", "M": "#6E3C8C"}, """
...WWWWW...
..WWWWWWW..
.WWWWWWWWW.
.WWEWWWEWW.
.WWEWWWEWW.
.WPWWMWWPW.
WWWWWWWWWWw
.WWWWWWWWw.
.WWWWWWWWw.
.WWWWWWWww.
..W.WW.W.w.
""", """
...WWWWW...
..WWWWWWW..
.WWWWWWWWW.
.WWEWWWEWW.
.WWEWWWEWW.
.WPWWMWWPW.
WWWWWWWWWWw
.WWWWWWWWw.
.WWWWWWWWw.
.WWWWWWWww.
.W.WW.WW.w.
""", """
...WWWWW...
..WWWWWWW..
.WWWWWWWWW.
.WWEWWWEWW.
.WWEWWWEWW.
.WPWWMWWPW.
.WWWWWWWWWw
WWWWWWWWWw.
.WWWWWWWWw.
.WWWWWWWww.
..W.WW.W.w.
""")
# The same ghost with a blink (eyes closed: a lit violet line one row lower).
GHOST_BLINK = Sprite("ghost_blink", {"W": "#F0F6FF", "w": "#B4C4E6", "E": "#3A2470", "P": "#FF8CB4",
                                     "M": "#6E3C8C"}, """
...WWWWW...
..WWWWWWW..
.WWWWWWWWW.
.WWWWWWWWW.
.WEEWWWEEW.
.WPWWMWWPW.
WWWWWWWWWWw
.WWWWWWWWw.
.WWWWWWWWw.
.WWWWWWWww.
..W.WW.W.w.
""")
# A small ghost, 7x7, two frames.
LITTLE_GHOST = Sprite("little_ghost", {"W": "#F0F6FF", "w": "#B4C4E6", "E": "#3A2470", "P": "#FF8CB4"}, """
..WWW..
.WWWWW.
.WEWEW.
.WPWPW.
WWWWWWw
.WWWWw.
.W.W.w.
""", """
..WWW..
.WWWWW.
.WEWEW.
.WPWPW.
WWWWWWw
.WWWWw.
W.W.W..
""")


# The black cat, 16x9, facing right. Black is an unlit LED, so the cat is a deep violet-grey (V) with a lavender rim
# light (R) along its top edges, lit yellow-green eyes (E) and a pink nose (P). Frames: two walk steps, the arched
# back with a puffed-up tail, sitting, and sitting with the eyes closed (a slow blink).
_CAT_PAL = {"T": "#3E3256", "V": "#3E3256", "v": "#2E2444", "R": "#9C86CC", "E": "#C8FF46", "P": "#FF8CB4", "W": "#F0F0F0"}
CAT = Sprite("cat", _CAT_PAL, """
................
T...........R..R
T...........RRRR
T...........VEVE
.T.RRRRRRRRRVVPV
.TVVVVVVVVVVVVV.
..VVVVVVVVVVVV..
..V.V.....V.V...
.V...V...V...V..
""", """
................
T...........R..R
T...........RRRR
T...........VEVE
.T.RRRRRRRRRVVPV
.TVVVVVVVVVVVVV.
..VVVVVVVVVVVV..
...VV......VV...
...VV......VV...
""", """
TRT....RRRR.....
RTR...RVVVVR.R.R
TRT..RVVVVVVRRRR
.T..RVVVVVVVVEVE
.T.RVVVVVVVVVVPV
.TRVVVVVVVVVVWV.
..V.V......V.V..
..V.V......V.V..
..V.V......V.V..
""", """
..........R..R..
..........RRRR..
..........VEVE..
.........VVVPV..
.......RRVVVV...
......RVVVVVV...
..T..RVVVVVVV...
..TTVVVVVVVVV...
...TTTVVVV.VV...
""", """
..........R..R..
..........RRRR..
..........VVVV..
.........VRRPR..
.......RRVVVV...
......RVVVVVV...
..T..RVVVVVVV...
..TTVVVVVVVVV...
...TTTVVVV.VV...
""")
