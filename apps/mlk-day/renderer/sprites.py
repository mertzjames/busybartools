"""Text-grid sprites for MLK Day: the dove, a bell, small birds. Sprites face right; use img(i, flip=True) for left.
People are drawn procedurally in mfx.Person, so their skin tones and clothes can vary freely."""

from busybar.sprite import Sprite

DOVE_PAL = {"W": "#F6F6FF", "S": "#AAB4D6", "O": "#FFAA5A", "G": "#6EC050", "o": "#FF965A"}

# frames 0-2: wings up, level, down (flap cycle 0,1,2,1); frame 3: perched with folded wings
DOVE = Sprite("dove", DOVE_PAL, """
..WW......
...WW.....
....WW.WW.
.SWWWWWWWO
SS..WWW..G
..........
..........
""", """
..........
..........
.WWWWW.WW.
.SWWWWWWWO
SS..WWW..G
..........
..........
""", """
..........
..........
.......WW.
.SWWWWWWWO
SS..WWW..G
....WW....
.....W....
""", """
..........
..........
.......WW.
...WWWWWWO
..SSWWW..G
....o.o...
..........
""")

# a small bird (for the bells scene): two flap frames
BIRD = Sprite("bird", {"B": "#C8D2F0"}, """
B...B
.B.B.
..B..
""", """
.....
BBBBB
..B..
""")

# a bell (crown loop, rounded shoulder, flared lip, lit clapper); swung by shearing its rows in code
BELL = Sprite("bell", {"Y": "#FFC850", "y": "#C88A32", "L": "#FFE6A0", "c": "#FFF0C8"}, """
...y...
..YYY..
.YLYYy.
.YLYYy.
.YLYYy.
YLYYYYy
yyyyyyy
...c...
""")

ALL = [DOVE, BIRD, BELL]
