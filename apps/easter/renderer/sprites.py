"""Text-grid sprites for Easter: the bunny, a chick, a butterfly, the chocolate bunny. Sprites face right; use
img(i, flip=True) for left.

Every small feature is a lit color (AGENTS.md: black is an unlit LED): the bunny's eye is a lit plum, the chick's
a lit brown, so neither reads as a hole (docs/DECISIONS.md D5).
"""

from busybar.sprite import Sprite

# An original cartoon bunny: caramel cream with a white tail and muzzle, pink inner ears and nose.
BUNNY_PAL = {
    "B": "#DEB88C",  # body
    "b": "#AE8460",  # shade (far legs, under the haunch)
    "W": "#FFF8F0",  # tail, muzzle, belly
    "P": "#FF8CAF",  # inner ear
    "e": "#40247A",  # eye: a lit deep violet
    "n": "#FF6E96",  # nose
}

# 13x13. 0 sitting, 1 crouched (about to hop), 2 mid-hop (stretched, ears back), 3 sitting, head down (sniffing)
BUNNY = Sprite("bunny", BUNNY_PAL, """
.......BB.BB.
.......BP.BP.
.......BP.BP.
.......BP.BB.
......BBBBBB.
......BBBBeBB
......BBBBBWn
...BBBBbBBWW.
.BBBBBBBbBB..
WBBBbbbBBBB..
WWBbBBBbBBB..
.WBbBBBbBWB..
..bBBBBBbbW..
""", """
.............
........BB.BB
........BP.BP
........BP.BB
......BBBBBB.
......BBBBeBB
......BBBBBWn
...BBBBbBBWW.
.BBBBBBBbBB..
WBBBbbbBBBB..
WWBbBBBbBBB..
.bBbBBBbBWB..
bbbBBBBBbbW..
""", """
.............
.............
.BBPPB.......
...BBPPBB....
.....BBBBBB..
....BBBBBBeB.
..BBBBBbBBBWn
.BBBbbbBBBWW.
WBBbBBBbBBB..
WWBbBBBbBWB..
.bbB....bBW..
.bb......bW..
.............
""", """
.......BB.BB.
.......BP.BP.
.......BP.BP.
.......BP.BB.
.............
......BBBBBB.
......BBBBBeB
...BBBBbBBBBW
.BBBBBBBbBBWn
WBBBbbbBBBB..
WWBbBBBbBBB..
.WBbBBBbBWB..
..bBBBBBbbW..
""")

# A fluffy chick, 8x7: 0 standing, 1 beak open (cheep), 2 wings up (flap)
CHICK_PAL = {"Y": "#FFDC3C", "y": "#E6A01E", "o": "#FF7A10", "e": "#50280A", "L": "#FFF5A0"}
CHICK = Sprite("chick", CHICK_PAL, """
..YYYY..
.YLYYeY.
.YYYYYoo
YYYYYYY.
YyyYYYY.
.YYYYY..
..o..o..
""", """
..YYYY.o
.YLYYeYo
.YYYYY..
YYYYYYYo
YyyYYYY.
.YYYYY..
..o..o..
""", """
..YYYY..
yYLYYeY.
yyYYYYoo
.yYYYYY.
.YYYYYY.
.YYYYY..
..o..o..
""")

# A butterfly seen from above, 5x4: wings open, half, closed (a flap cycle 0, 1, 2, 1)
BUTTERFLY = Sprite("butterfly", {"A": "#FF96D2", "a": "#FFDCF0", "b": "#6E3C5A"}, """
AA.AA
AabaA
.AbA.
.A.A.
""", """
.A.A.
.AbA.
.AbA.
.....
""", """
..b..
..b..
..b..
.....
""")

# The chocolate bunny for the basket: a lit milk-chocolate brown with a highlight and a gold foil bow
CHOC_PAL = {"C": "#9C5A32", "c": "#C88050", "D": "#74401E", "G": "#FFC832", "e": "#FFE6C8"}
CHOC_BUNNY = Sprite("choc_bunny", CHOC_PAL, """
.C.C.
.CcC.
.CcC.
.CCC.
CCeCc
CCCCc
GGGGG
CCCCc
CCCCc
DDDDD
""")

ALL = [BUNNY, CHICK, BUTTERFLY, CHOC_BUNNY]
