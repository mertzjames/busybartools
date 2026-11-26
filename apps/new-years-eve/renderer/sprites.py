"""Original pixel-art sprites for New Year's Eve, as text grids ('.' = transparent). Sprites face right.

Small features use lit colors (black is an unlit LED): guests have no dark eyes, and the bottle is a lit green.
"""

from __future__ import annotations

from busybar.sprite import Sprite

# Party guest, 7x11: pompom p, party hat H/h (stripe), skin s, shirt C, sleeves/arms c, legs l.
# Frames: 0 arms down, 1 arms up, 2 step left, 3 step right, 4 horn pose (hand at mouth)
GUEST = Sprite("guest", {
    "p": "#FFF4C8", "H": "#FF2EAA", "h": "#FFD040", "s": "#FFC9A0", "C": "#2AD8FF", "c": "#1AA0D0", "l": "#8C9CFF",
}, """
...p...
...H...
..HhH..
..HHH..
..sss..
..sss..
.cCCCc.
.cCCCc.
s.CCC.s
..l.l..
..l.l..
""", """
s..p..s
c..H..c
c.HhH.c
.cHHHc.
..sss..
..sss..
..CCC..
..CCC..
..CCC..
..l.l..
..l.l..
""", """
...p...
...H...
..HhH..
..HHH..
..sss..
..sss..
.cCCCc.
s.CCC.s
..CCC..
.l..l..
l...l..
""", """
...p...
...H...
..HhH..
..HHH..
..sss..
..sss..
.cCCCc.
s.CCC.s
..CCC..
..l..l.
..l...l
""", """
...p...
...H...
..HhH..
..HHH..
..sss..
..ssss.
.cCCcs.
.cCCC..
..CCC..
..l.l..
..l.l..
""")

GUEST_COLORS = [
    dict(H="#FF2EAA", h="#FFD040", C="#2AD8FF", c="#1AA0D0", l="#8C9CFF"),   # pink hat, cyan top
    dict(H="#FFC21A", h="#FFFFFF", C="#FF4FB8", c="#C8308C", l="#9A7CFF"),   # gold hat, pink top
    dict(H="#46E06A", h="#FFE070", C="#FFB43A", c="#D0801A", l="#7FA8FF"),   # green hat, orange top
    dict(H="#3AB4FF", h="#FF7AD0", C="#C8D2EC", c="#9AA6C8", l="#B08CFF"),   # blue hat, silver top
]
GUESTS = [GUEST.recolor(f"guest{i}", **c) for i, c in enumerate(GUEST_COLORS)]

# Champagne bottle, 5x12: gold foil F/f, lit green glass G/g (highlight), cream label L, gold label band b
BOTTLE = Sprite("bottle", {
    "F": "#FFC83A", "f": "#C88A18", "G": "#1E8A4C", "g": "#5AD08A", "L": "#FFF0C8", "b": "#E0A020",
}, """
.FfF.
.FfF.
.GgG.
.GgG.
GGgGG
GgGGG
GLLLG
GLbLG
GLLLG
GgGGG
GgGGG
GGGGG
""")

CORK = Sprite("cork", {"K": "#E8B070", "k": "#B07840"}, """
KK
kk
""", """
Kk
Kk
""")

ALL = [GUEST, *GUESTS, BOTTLE, CORK]
