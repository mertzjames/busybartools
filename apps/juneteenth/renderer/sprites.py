"""Original pixel-art sprites for Juneteenth (text grids, busybar.sprite.Sprite). Sprites face right; use
img(i, flip=True) to face left. Small dark features use lit colors (black is an unlit LED)."""

from busybar.sprite import Sprite

# A bay horse: standing, then two gallop frames (legs stretched, legs gathered). 14 x 8.
HORSE = Sprite("horse", {"H": "#7A4028", "h": "#9A5634", "D": "#4E2E22", "k": "#6A5A50"}, """
..........hh..
.........DHHh.
........DHHHHH
.DhhhhhhhHH...
D.HHHHHHHHH...
D.HHHHHHHH....
..H.D...D.H...
..k.k...k.k...
""", """
..........hh..
.........DHHh.
........DHHHHH
.DhhhhhhhHH...
D.HHHHHHHHH...
D.HHHHHHHH....
.H.D.....D.H..
k...k.....k.k.
""", """
..........hh..
.........DHHh.
........DHHHHH
.DhhhhhhhHH...
D.HHHHHHHHH...
D.HHHHHHHH....
...HD...DH....
....kk.kk.....
""")

# A two-masted sailing ship (square sails), bow to the right. 17 x 10. Sails catch the dawn light.
SHIP = Sprite("ship", {"S": "#E6D2B0", "s": "#BCA88C", "m": "#8A6A4A", "H": "#5E3C2C", "h": "#43302A",
                       "b": "#8A6A4A", "f": "#D23040"}, """
.....mf.....mf...
....SSs....SSs...
....SSs....SSs...
...SSSSs..SSSSs..
...SSSSs..SSSSs..
.....m......m....
.....m......m...b
.HHHHHHHHHHHHHHb.
..HHHHHHHHHHHHH..
...hhhhhhhhhhh...
""")

# A lighthouse with a red-banded white tower and a gold lamp room. 5 x 12.
LIGHTHOUSE = Sprite("lighthouse", {"r": "#B02A30", "L": "#FFD66A", "g": "#6A6A78", "W": "#E8E4DC", "R": "#C8303A",
                                   "w": "#BEB8AE", "d": "#7A6650"}, """
..r..
.rrr.
.LLL.
ggggg
.WWw.
.RRR.
.WWw.
.WWw.
.RRR.
.WWw.
WWWWw
WWdWw
""")
