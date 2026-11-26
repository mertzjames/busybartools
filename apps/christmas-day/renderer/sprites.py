"""Original pixel-art sprites for Christmas Day, as text grids (docs/DECISIONS.md D3).

Each sprite has a palette {char: "#RRGGBB"} and one or more frames; '.' is transparent. Sprites face RIGHT; use
.img(i, flip=True) for left-facing. Small features (eyes, noses, buttons) use lit colors, never near-black,
because black is an unlit LED and reads as a hole (D6). The Sprite class is the shared kit's busybar.sprite.
"""

from __future__ import annotations

from busybar.sprite import Sprite

SKIN = "#F2C29A"
EYE = "#7A4A3A"  # a lit brown: dark enough to read as an eye, bright enough not to be a hole

# ---------------------------------------------------------------------------
# Children. Frames: 0 stand, 1 step A, 2 stand, 3 step B, 4 arms up (cheer / startled), 5 push (arms forward)
_KID_BODY = {
    "stand": """
.CCCC..
.CCCCM.
.CCCC..
..b.b..
.bb.bb.
""",
    "stepA": """
.CCCC..
.CCCCM.
.CCCC..
.b...b.
bb...bb
""",
    "stepB": """
.CCCC..
.CCCCM.
.CCCC..
...b...
..bbb..
""",
    "cheer": """
.CCCC..
.CCCC..
.CCCC..
..b.b..
.bb.bb.
""",
    "push": """
.CCCCCM
.CCCC.M
.CCCC..
.b..b..
bb..bb.
""",
}

_BOY_HEAD = """
...W...
..RRR..
.RRRRR.
.hSSeS.
.hSSSS.
"""
_BOY_HEAD_CHEER = """
...W...
..RRR..
MRRRRRM
ChSSeSC
ChSSSSC
"""
_GIRL_HEAD = """
...W...
..GGG..
.GGGGG.
yySSeS.
yySSSS.
"""
_GIRL_HEAD_CHEER = """
...W...
..GGG..
MGGGGGM
CySSeSC
CySSSSC
"""


def _kid(name: str, palette: dict[str, str], head: str, head_cheer: str) -> Sprite:
    b = _KID_BODY
    return Sprite(name, palette, head + b["stand"], head + b["stepA"], head + b["stand"], head + b["stepB"],
                  head_cheer + b["cheer"], head + b["push"])


# Boy: red beanie, green coat, brown hair. Girl: green beanie, red coat, blonde hair.
BOY = _kid("boy", {"W": "#F4F4FF", "R": "#D8202A", "h": "#8A5530", "S": SKIN, "e": EYE, "C": "#2E9A48",
                   "M": "#F4F4FF", "b": "#5A6FA8"}, _BOY_HEAD, _BOY_HEAD_CHEER)
GIRL = _kid("girl", {"W": "#F4F4FF", "G": "#2E9A48", "y": "#F2CF4A", "S": SKIN, "e": EYE, "C": "#D8202A",
                     "M": "#F4F4FF", "b": "#8A5AA8"}, _GIRL_HEAD, _GIRL_HEAD_CHEER)

# ---------------------------------------------------------------------------
# Elf: pointed hat with a bell, pointy ear. Frames: stand, step, stand, step B, arms up, throw (arm high)
_ELF = {"G": "#2EB04E", "Y": "#FFD84A", "S": SKIN, "e": EYE, "R": "#D8202A", "W": "#F4F4FF", "g": "#1E8A3A"}
_ELF_HEAD = """
Y......
.GG....
..GGG..
.SSSeS.
..SSS..
"""
ELF = Sprite("elf", _ELF, _ELF_HEAD + """
.RRRRS.
.RYRR..
..WW...
.gg.gg.
""", _ELF_HEAD + """
.RRRRS.
.RYRR..
.W..W..
gg..gg.
""", _ELF_HEAD + """
.RRRRS.
.RYRR..
..WW...
.gg.gg.
""", _ELF_HEAD + """
.RRRRS.
.RYRR..
...W...
..ggg..
""", """
Y......
.GG....
S.GGG.S
RSSSeSR
.RSSSR.
..RRR..
.RYRR..
..WW...
.gg.gg.
""", """
Y.....S
.GG...R
..GGGR.
.SSSeS.
..SSS..
.RRRR..
.RYRR..
..WW...
.gg.gg.
""")

# ---------------------------------------------------------------------------
# Santa in his sleigh (side view, facing right). Frames: wave arm down / up
_SLEIGH = {"W": "#F4F4FF", "R": "#D8202A", "r": "#A0141E", "S": SKIN, "e": "#5A8AD0", "Y": "#FFC83A",
           "y": "#C8902A", "B": "#7A4A2A", "s": "#C8C8D8"}
SLEIGH = Sprite("sleigh", _SLEIGH, """
W.RRR...........
.RRRRR..........
.WWWWW..........
.SSSeS..........
WWWWWWW.........
RWWWWWRR.......Y
YRRRRRRRRRRRRRY.
.YrrrrrrrrrrrY..
..y...y...y.....
yyyyyyyyyyyyyy..
""", """
W.RRR....W......
.RRRRR...R......
.WWWWW..R.......
.SSSeS.R........
WWWWWWW.........
RWWWWWRR.......Y
YRRRRRRRRRRRRRY.
.YrrrrrrrrrrrY..
..y...y...y.....
yyyyyyyyyyyyyy..
""")

# Reindeer (flying gallop, 4 frames). Lead deer wears a gold bell collar (recolor 'c').
_DEER = {"A": "#E8D2A0", "B": "#A0643A", "b": "#D8B07A", "w": "#F4F4FF", "c": "#A0643A", "n": "#5A3020",
         "e": "#2A1A10", "h": "#6A4022"}
_DEER_HEAD = """
.......A.A.
........AA.
........BBB
.......cBBn
"""
REINDEER = Sprite("reindeer", _DEER, _DEER_HEAD + """
wBBBBBBBc..
.BbbbbBB...
B.....B....
B......B...
""", _DEER_HEAD + """
wBBBBBBBc..
.BbbbbBB...
.B....B....
B......B...
""", _DEER_HEAD + """
wBBBBBBBc..
.BbbbbBB...
..B..B.....
..h..h.....
""", _DEER_HEAD + """
wBBBBBBBc..
.BbbbbBB...
.B...B.....
..B...B....
""")
LEAD_DEER = REINDEER.recolor("lead_deer", c="#FFD84A")

# ---------------------------------------------------------------------------
# Cat (orange tabby). Frames: walk A, walk B, sit (facing right, tail up), crouch, leap, bat (paw up)
_CAT = {"O": "#F09A3A", "S": "#F09A3A", "o": "#C0641E", "g": "#7AE05A", "p": "#FF8AA0", "W": "#FFE8D0"}
CAT = Sprite("cat", _CAT, """
O.....O.O.
O.....OOO.
.O....OgOp
.OOoOoOOO.
..OoOoOO..
..O.O.O.O.
""", """
O.....O.O.
O.....OOO.
.O....OgOp
.OOoOoOOO.
..OoOoOO..
.O..OO..O.
""", """
....O.O...
O...OOO...
O...OgOp..
.O..OOO...
.O.OoOO...
..OOoOWO..
""", """
..........
..........
......O.O.
OO....OOO.
..OOoOOgOp
..OoOoOOO.
""", """
.......O.O
OO.....OOO
..O....OgO
...OOoOOOp
..OoOoOO..
.O.....O..
""", """
.....SO.O.
....SOOOO.
O....OgOp.
O...OOOO..
.O.OoOO...
..OOoOWO..
""")

# ---------------------------------------------------------------------------
# Puppy (cream with brown ears). Frames: peek (head only), run A, run B, sit, lick (tongue)
_PUP = {"T": "#F2D8A8", "B": "#A0643A", "n": "#C04A3A", "e": "#6A4A9A", "t": "#FF6A8A"}
PUPPY = Sprite("puppy", _PUP, """
.........
.....B.B.
.....TTTB
.....TeTn
.....TTT.
.........
""", """
.....B.B.
.....TTTB
T....TeTn
TTTTTTTT.
.TTTTTT..
.T.T..TT.
""", """
.....B.B.
.....TTTB
T....TeTn
TTTTTTTT.
.TTTTTT..
T..TT...T
""", """
.....B.B.
.....TTTB
.....TeTn
.....TTT.
T...TTTT.
.TTTTT.T.
""", """
.....B.B.
.....TTTB
.....TeTn
.....TTTt
T...TTTT.
.TTTTT.T.
""")

# Jack-in-the-box head (jester hat, round face, red smile). The spring is drawn procedurally.
JACK = Sprite("jack", {"R": "#E0303A", "Y": "#FFD84A", "S": "#FFE0C8", "e": "#3A7AE0", "m": "#E0303A",
                       "c": "#FF8A9A"}, """
Y.....Y
RR...YY
.RRYYY.
.SSSSS.
.SeSeS.
.cSSSc.
..SmS..
""")

# ---------------------------------------------------------------------------
# Toy train: engine (facing right) and a car carrying gifts
TRAIN_ENGINE = Sprite("engine", {"R": "#D8202A", "r": "#A0141E", "G": "#2E9A48", "g": "#1E7A34",
                                 "Y": "#FFD84A", "y": "#FFF0A0", "D": "#8A8AA0", "W": "#C8C8D8", "w": "#7A7A90"},
                      """
.......DD..
RRRR...DD..
RyyR.......
RRRRGGGGGG.
RRRRGGGGGGy
rrrrrrrrrrY
.WW..WW.WW.
""", """
.......DD..
RRRR...DD..
RyyR.......
RRRRGGGGGG.
RRRRGGGGGGy
rrrrrrrrrrY
.ww..ww.ww.
""")
TRAIN_CAR = Sprite("car", {"B": "#3A6AD0", "b": "#2A4AA0", "W": "#C8C8D8", "w": "#7A7A90", "R": "#E0303A",
                           "Y": "#FFD84A", "G": "#2EB04E"}, """
.RYGG..
BBBBBBB
bbbbbbb
.WW.WW.
""", """
.RYGG..
BBBBBBB
bbbbbbb
.ww.ww.
""")

# ---------------------------------------------------------------------------
# Carolers. Frames: walk A, walk B, sing closed, sing open (mouth 'o')
_CAROL_LEGS = {"walkA": """
.k..k.
k....k
""", "walkB": """
..kk..
..kk..
""", "stand": """
.k..k.
.k..k.
"""}


def _caroler(name: str, palette: dict[str, str], head: str, body: str) -> Sprite:
    closed = head.replace("o", "S")
    legs = _CAROL_LEGS
    return Sprite(name, palette, closed + body + legs["walkA"], closed + body + legs["walkB"],
                  closed + body + legs["stand"], head + body + legs["stand"])


_CAROL_BOOK = "#F4F0E0"
CAROLER_HAT = _caroler("caroler_hat", {"K": "#5A4A9A", "k": "#3A3A5A", "R": "#D8202A", "S": SKIN, "e": EYE,
                                       "o": "#C83A3A", "C": "#3A6AD0", "B": _CAROL_BOOK, "r": "#A0141E"},
                       """
.KKK..
.KKK..
KRRRK.
.SSeS.
.SSoS.
""", """
.RRR..
CCCBB.
CCCBB.
.CCC..
.CCC..
""")
CAROLER_BONNET = _caroler("caroler_bonnet", {"P": "#E04A8A", "W": "#F4F4FF", "y": "#F2CF4A", "S": SKIN, "e": EYE,
                                             "o": "#C83A3A", "C": "#2E9A48", "B": _CAROL_BOOK, "k": "#3A3A5A"},
                          """
.PPP..
PPPPP.
PySeS.
PySoS.
.yy...
""", """
.WWW..
CCCBB.
CCCBB.
CCCCC.
CCCCC.
""")
CAROLER_MUFFS = _caroler("caroler_muffs", {"R": "#D8202A", "h": "#8A5530", "S": SKIN, "e": EYE, "o": "#C83A3A",
                                           "C": "#C83A3A", "G": "#2EB04E", "B": _CAROL_BOOK, "k": "#3A3A5A",
                                           "W": "#F4F4FF"}, """
.hhh..
RhhhR.
RSSeR.
.SSoS.
..SS..
""", """
.GGG..
CCCBB.
CCCBB.
.CCC..
.CCC..
""")

# Dog (brown, floppy ears). Frames: walk A, walk B, sit, howl (head up, mouth open)
_DOG = {"B": "#B07A4A", "b": "#7A4A2A", "n": "#4A2A1A", "e": "#FFE08A", "W": "#F4E8D8", "o": "#E05A6A"}
DOG = Sprite("dog", _DOG, """
.......BB..
B.....BeBBn
.B....bBBB.
.BBBBBBBB..
..BBBBBB...
..B.B..B.B.
""", """
.......BB..
B.....BeBBn
.B....bBBB.
.BBBBBBBB..
..BBBBBB...
.B..BB...B.
""", """
......BB...
.....BeBBn.
.....bBBB..
B...BBBB...
.B.BBBBB...
..BBBWBW...
""", """
......B.on.
.....BeBB..
.....bBB...
B...BBBB...
.B.BBBBB...
..BBBWBW...
""")

# ---------------------------------------------------------------------------
# Small props
HEART = Sprite("heart", {"R": "#FF4A6A", "r": "#FF9AB0"}, """
.R.R.
RrRRR
.RRR.
..R..
""")
NOTE = Sprite("note", {"N": "#FFE08A"}, """
.NN
.N.
NN.
NN.
""")
NOTE2 = Sprite("note2", {"N": "#BFE8FF"}, """
.NNN
.N.N
NN.N
N.NN
""")
STAR = Sprite("star", {"Y": "#FFE04A", "W": "#FFFBE0"}, """
..Y..
YYWYY
.YYY.
.Y.Y.
""")
TOP_HAT = Sprite("top_hat", {"K": "#5A4A9A", "R": "#D8202A"}, """
.KKK.
.KKK.
.RRR.
KKKKK
""")
CARROT = Sprite("carrot", {"O": "#FF8A2A"}, "OO")
GIFT_SMALL = Sprite("gift_small", {"R": "#E0303A", "Y": "#FFD84A"}, """
.Y.
RYR
RYR
""")
LADDER = Sprite("ladder", {"L": "#B07A4A"}, """
L..L
LLLL
L..L
L..L
LLLL
L..L
L..L
LLLL
L..L
L..L
LLLL
L..L
""")

# Stockings: hanging (toe points left) and fallen flat (cuff on the right). Recolor 'C' / 'S' per stocking.
STOCKING = Sprite("stocking", {"W": "#F4F4FF", "C": "#D8202A", "S": "#F4F4FF"}, """
.WWWW
.WWWW
..CCC
..CSC
..CCC
CCCCC
CCCC.
""")
STOCKING_FLAT = Sprite("stocking_flat", {"W": "#F4F4FF", "C": "#D8202A", "S": "#F4F4FF"}, """
.CCCCCWW
CCCSCCWW
CCCCCCWW
CC....WW
""")
CAT_HEAD = Sprite("cat_head", {"O": "#F09A3A", "g": "#7AE05A", "p": "#FF8AA0"}, """
O.O.
OOO.
OgOp
.OO.
""")
CANDY_CANE = Sprite("candy_cane", {"R": "#E0303A", "W": "#F4F4FF"}, """
.RW
W.R
..W
..R
""")

ALL = [BOY, GIRL, ELF, SLEIGH, REINDEER, LEAD_DEER, CAT, PUPPY, JACK, TRAIN_ENGINE, TRAIN_CAR, CAROLER_HAT,
       CAROLER_BONNET, CAROLER_MUFFS, DOG, HEART, NOTE, NOTE2, STAR, TOP_HAT, CARROT, GIFT_SMALL, LADDER,
       STOCKING, STOCKING_FLAT, CAT_HEAD, CANDY_CANE]
