"""Original pixel-art sprites as ASCII grids (docs/DECISIONS.md D3, D5).

Each sprite: a palette {char: "#RRGGBB"} and one or more frames. '.' is transparent.
Sprites face RIGHT; use .img(i, flip=True) for left-facing.
"""

from __future__ import annotations

from functools import lru_cache
from PIL import Image, ImageOps

from canvas import hexc


class Sprite:
    def __init__(self, name: str, palette: dict[str, str], *frames: str):
        self.name = name
        self.palette = {k: hexc(v) for k, v in palette.items()}
        self._src = (dict(palette), frames)
        self.frames = [self._rows(f) for f in frames]
        w = {len(r) for f in self.frames for r in f}
        assert len(w) == 1, f"{name}: ragged rows {w}"
        self.w = w.pop()
        hs = {len(f) for f in self.frames}
        assert len(hs) == 1, f"{name}: frames differ in height {hs}"
        self.h = hs.pop()
        for f in self.frames:
            for r in f:
                for ch in r:
                    assert ch == "." or ch in self.palette, f"{name}: unknown color {ch!r}"
        self._imgs = [self._render(f) for f in self.frames]

    @staticmethod
    def _rows(s: str) -> list[str]:
        return [ln.strip() for ln in s.strip("\n").splitlines() if ln.strip()]

    def _render(self, rows: list[str]) -> Image.Image:
        img = Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))
        px = img.load()
        for y, r in enumerate(rows):
            for x, ch in enumerate(r):
                if ch != ".":
                    px[x, y] = self.palette[ch] + (255,)
        return img

    def recolor(self, name: str, **colors: str) -> "Sprite":
        """Same pixels, some palette entries swapped (e.g. scarf colors)."""
        palette, frames = self._src
        return Sprite(name, {**palette, **colors}, *frames)

    def img(self, i: int = 0, flip: bool = False) -> Image.Image:
        im = self._imgs[i % len(self._imgs)]
        return ImageOps.mirror(im) if flip else im

    def __len__(self) -> int:
        return len(self.frames)


# ---------------------------------------------------------------------------
# Snowy owl (front view, wings: up / mid / down / mid)
OWL = Sprite("owl", {
    "W": "#F4F4FF", "w": "#A9AECB", "Y": "#FFC21A", "k": "#E08A1E", "o": "#C99A4A", "e": "#1A1A1A",
}, """
W....WWW....W
WW..WYWYW..WW
.WWWWeWeWWWW.
..wWWWkWWWw..
....WwWwW....
....wWWWw....
.....o.o.....
""", """
.....WWW.....
....WYWYW....
WWWWWeWeWWWWW
.wWWWWkWWWWw.
....WwWwW....
....wWWWw....
.....o.o.....
""", """
.....WWW.....
....WYWYW....
....WeWeW....
...WWWkWWW...
.wWWWwWwWWWw.
WW..wWWWw..WW
W....o.o....W
""", """
.....WWW.....
....WYWYW....
WWWWWeWeWWWWW
.wWWWWkWWWWw.
....WwWwW....
....wWWWw....
.....o.o.....
""")

# Sealed letter
LETTER = Sprite("letter", {"c": "#EFE3BE", "d": "#B9A574", "R": "#D21F2B"}, """
ccccc
cdcdc
ccRcc
ccccc
""")

# Boy wizard: round glasses, scarf, robe. Frames: stand, step A, stand, step B, wand up
# G = glasses frame, e = green eyes (dark pixels are unlit LEDs, which read as holes/extra eyes)
_WIZ = {
    "h": "#5A3A22", "S": "#F6C79C", "g": "#202020", "G": "#B4BCCC", "e": "#2FA84F", "R": "#C8102E", "Y": "#F2B515",
    "M": "#4B4A78", "m": "#33325A", "b": "#6B3E1C", "w": "#9A6A3A", "*": "#FFF6B0",
}
WIZARD = Sprite("wizard", _WIZ, """
..hhhh...
.hhhhhh..
.hSSSSS..
.GeGGeG..
.SSSSSS..
..SSSS...
.RYRYRY..
.MMMMMM..
MMMMMMMS.
mMMMMMM..
.MMMMMM..
.mMMMMm..
..b..b...
..bb.bb..
""", """
..hhhh...
.hhhhhh..
.hSSSSS..
.GeGGeG..
.SSSSSS..
..SSSS...
.RYRYRY..
.MMMMMM..
MMMMMMMS.
mMMMMMM..
.MMMMMM..
.mMMMMm..
.b....b..
bb....bb.
""", """
..hhhh...
.hhhhhh..
.hSSSSS..
.GeGGeG..
.SSSSSS..
..SSSS...
.RYRYRY..
.MMMMMM..
MMMMMMMS.
mMMMMMM..
.MMMMMM..
.mMMMMm..
..b..b...
..bb.bb..
""", """
..hhhh...
.hhhhhh..
.hSSSSS..
.GeGGeG..
.SSSSSS..
..SSSS...
.RYRYRY..
.MMMMMM..
MMMMMMMS.
mMMMMMM..
.MMMMMM..
.mMMMMm..
...bb....
...bbb...
""", """
..hhhh..*
.hhhhhh.w
.hSSSSS.w
.GeGGeGS.
.SSSSSSM.
..SSSSM..
.RYRYRY..
.MMMMMM..
MMMMMMM..
mMMMMMM..
.MMMMMM..
.mMMMMm..
..b..b...
..bb.bb..
""")

# Wizard riding a broom (side view, robe flapping: 2 frames)
BROOM_RIDER = Sprite("broom_rider", {
    **_WIZ, "B": "#8A5A2B", "s": "#D9B25C", "t": "#A9822F",
}, """
.....hhh.....
....hhhhh....
....hSSSS....
....GeGeG....
.....SSS.....
....RYRYRSS..
...MMMMMM....
..mMMMMMM....
s.MMMMMbb....
ssBBBBBBBBBBB
st..m.m......
""", """
.....hhh.....
....hhhhh....
....hSSSS....
....GeGeG....
.....SSS.....
....RYRYRSS..
..MMMMMMM....
.mMMMMMMM....
s..MMMMbb....
ssBBBBBBBBBBB
tsm..........
""")

# Winged golden pumpkin pie ("the golden pie"), wings up/down
GOLDEN_PIE = Sprite("golden_pie", {
    "W": "#F0F4FF", "w": "#B8C2E0", "Y": "#FFD84A", "y": "#E39A1C", "c": "#FFF3B0",
}, """
W.....W
WW.c.WW
.wYYYw.
..yyy..
""", """
.......
...c...
wwYYYww
WWyyyWW
""")

# Turkey (side view, facing right). Frames: stand, step A, stand, step B
_TURKEY = {
    "1": "#C8102E", "2": "#F07B1A", "3": "#F5C242", "B": "#7A4521", "b": "#5A3015",
    "H": "#C9B79C", "r": "#E0202E", "O": "#F2A11B", "e": "#101010", "L": "#E39A1C",
}
TURKEY = Sprite("turkey", _TURKEY, """
.1.2.3......
1.2.3.1.....
.2.3.1.HH...
2.3BB.2HeO..
.3BBBB.Hr...
.BBBBBBBr...
..BbBBBB....
...BBBB.....
...L..L.....
..LL.LL.....
""", """
.1.2.3......
1.2.3.1.....
.2.3.1.HH...
2.3BB.2HeO..
.3BBBB.Hr...
.BBBBBBBr...
..BbBBBB....
...BBBB.....
..L....L....
.LL....LL...
""", """
.1.2.3......
1.2.3.1.....
.2.3.1.HH...
2.3BB.2HeO..
.3BBBB.Hr...
.BBBBBBBr...
..BbBBBB....
...BBBB.....
...L..L.....
..LL.LL.....
""", """
.1.2.3......
1.2.3.1.....
.2.3.1.HH...
2.3BB.2HeO..
.3BBBB.Hr...
.BBBBBBBr...
..BbBBBB....
...BBBB.....
....LL......
....LLL.....
""")

# Roast turkey on a platter
ROAST = Sprite("roast", {
    "G": "#C9741F", "g": "#9A4E12", "h": "#F6E2C0", "W": "#F4F4F4", "P": "#B8BCC8", "p": "#7E8494",
}, """
........h.
..GGGG.Gh.
.GGGGGGGG.
GGGGGGGGGG
GGGGGGGGgG
.gGGGGGgg.
PPPPPPPPPP
.pppppppp.
""")

# Raw (uncooked) turkey for the dragon scene: same shape, pale
RAW_TURKEY = Sprite("raw_turkey", {
    "G": "#F2C9B0", "g": "#D9A58A", "h": "#FFF0E6",
}, """
........h.
..GGGG.Gh.
.GGGGGGGG.
GGGGGGGGGG
GGGGGGGGgG
.gGGGGGgg.
""")

# Talking pointed hat. Frames: mouth closed, mouth open
HAT = Sprite("hat", {
    "B": "#9A6532", "b": "#63401C", "d": "#2A1606", "p": "#D49A5A",
}, """
......Bbb.
.....BB..b
....BBb...
...BBBbb..
...BdBdb..
..BBBBBbb.
..BBdddBb.
bbBBBBBBbb
""", """
......Bbb.
.....BB..b
....BBb...
...BBBbb..
...BdBdb..
..BBdddbb.
..BdpppdB.
bbBBdddBbb
""")

# Floating candle, flame frames
CANDLE = Sprite("candle", {"Y": "#FFE45C", "O": "#FF8A1E", "W": "#F3EEDD", "w": "#BDB59C"}, """
.Y.
.O.
.W.
.W.
.w.
""", """
Y..
.O.
.W.
.W.
.w.
""", """
.Y.
YO.
.W.
.W.
.w.
""", """
..Y
.O.
.W.
.W.
.w.
""")

# Steam locomotive (wheels: 2 frames)
LOCO = Sprite("loco", {
    "R": "#C8102E", "r": "#8A0A1F", "K": "#6A6A78", "Y": "#F2B515", "W": "#CFD6E6", "G": "#FFE07A",
    "g": "#5A6070",
}, """
..KK............
..KK.......RRRR.
.KKKK......RGGR.
RRRRRRRRRRRRRRR.
RYYYYYYYYYYRWWR.
RRRRRRRRRRRRRRRK
rrrrrrrrrrrrrrrK
.KgK..KgK..KgK..
..K....K....K...
""", """
..KK............
..KK.......RRRR.
.KKKK......RGGR.
RRRRRRRRRRRRRRR.
RYYYYYYYYYYRWWR.
RRRRRRRRRRRRRRRK
rrrrrrrrrrrrrrrK
.gKg..gKg..gKg..
.K.K..K.K..K.K..
""")

# Flat car (cargo drawn on top separately)
CAR = Sprite("car", {"B": "#7A4521", "b": "#4F2A10", "K": "#2A2A33", "g": "#5A6070"}, """
BBBBBBBBBB
bbbbbbbbbb
.KgK..KgK.
..K....K..
""", """
BBBBBBBBBB
bbbbbbbbbb
.gKg..gKg.
.K.K..K.K.
""")

GRAVY_BOAT = Sprite("gravy_boat", {"W": "#F4F4F4", "w": "#B8BCC8", "G": "#8A4B1A"}, """
.GGGG...
WWWWWWW.
.WWWWWWW
..wwww..
""")

PUMPKIN = Sprite("pumpkin", {"O": "#F07B1A", "o": "#B5530C", "G": "#3E8E2E"}, """
...G...
.OoOoO.
OOoOoOO
OOoOoOO
.OoOoO.
""")

# Cauldron (bubbling liquid color is drawn separately)
CAULDRON = Sprite("cauldron", {"K": "#5C5C70", "k": "#3A3A48", "g": "#9A9AB4"}, """
gKKKKKKKKKKg
.KKKKKKKKKK.
.KgKKKKKKKK.
.KKKKKKKKKK.
..KKKKKKKK..
..kk....kk..
""")

# Young witch in school robes: bushy brown hair, house scarf, wand. Frames: idle, wand flick (toss)
# Same chibi proportions and robe colors as WIZARD so the two read as classmates.
WITCH = Sprite("witch", {
    "h": "#7A4A26", "H": "#A8703C", "S": "#F6C79C", "e": "#202020", "R": "#C8102E", "Y": "#F2B515",
    "M": "#4B4A78", "m": "#33325A", "w": "#9A6A3A", "*": "#FFF6B0",
}, """
..hhHh...
.hHhhhhh.
hhhSSSShh
hhSSSeSh.
hhSSSSSh.
hhhSSSShh
h.RYRYR.h
..MMMMMS.
.MMMMMMM.
.mMMMMMm.
.MMMMMMM.
mMMMMMMMm
""", """
..hhHh...
.hHhhhhh.
hhhSSSShh
hhSSSeSh.
hhSSSSSh.
hhhSSSShh
h.RYRYRSw
..MMMMM.*
.MMMMMMM.
.mMMMMMm.
.MMMMMMM.
mMMMMMMMm
""")

APPLE = Sprite("apple", {"R": "#E0202E", "r": "#9A1020", "G": "#3E8E2E"}, """
.G.
RRR
RRr
.r.
""")

# Winged serpent dragon (docs/DECISIONS.md D22). The long body is drawn procedurally in scenes/dragon_roast.py;
# these are the head (jaw closed / open) and the bat wing (up / mid / down / mid).
_DRAGON = {
    "G": "#34AE5C", "g": "#1F7A3E", "b": "#C9B458", "H": "#E8DCC0", "R": "#FF2A1A", "W": "#F4F0E0",
    "r": "#B0121E",
}
DRAGON_HEAD = Sprite("dragon_head", _DRAGON, """
H........
.HGGG....
.GGGRGG..
GGGGGGGGG
GGgggggg.
.Gbbbbb..
""", """
H........
.HGGG....
.GGGRGGGG
GGGGGWGWG
GGrrrrr..
GGbWbWbb.
""")
DRAGON_WING = Sprite("dragon_wing", {"B": "#2FA05A", "m": "#6E1E3A", "n": "#4A1428"}, """
........B
......BBm
....BBmmm
..BBmmmn.
BBmmmn...
.mmn.....
""", """
.........
.........
BBBBBBBBB
.mmmmmmn.
..mmmmn..
...mmn...
""", """
.........
.........
.........
BBBBBBB..
.mmmmmmB.
...nmmmmB
""", """
.........
.........
BBBBBBBBB
.mmmmmmn.
..mmmmn..
...mmn...
""")

# Spit + campfire logs
SPIT = Sprite("spit", {"K": "#5A6070", "B": "#6B3E1C", "b": "#4A2A10"}, """
K...........K
KKKKKKKKKKKKK
K...........K
K...........K
K...BBbbB...K
K..bBBBBbB..K
""")

# Small house-colored confetti chips are drawn procedurally; star sparkle sprite:
SPARK = Sprite("spark", {"W": "#FFFFFF", "Y": "#FFF2A0"}, """
.Y.
YWY
.Y.
""")

# House scarves: every student who appears wears a different house's colors (docs/DECISIONS.md D19).
# Scarf stripes use palette keys R (main) and Y (accent). Black is an unlit LED, so "black" is a lit dark grey.
SCARLET_GOLD = {"R": "#C8102E", "Y": "#F2B515"}
GREEN_SILVER = {"R": "#1E8C46", "Y": "#C4CAD6"}
BLUE_BRONZE = {"R": "#2D50D2", "Y": "#C07A38"}
YELLOW_BLACK = {"R": "#F2C21A", "Y": "#5A5A5A"}

BROOM_RIDER_SG = BROOM_RIDER.recolor("broom_rider_scarlet_gold", **SCARLET_GOLD)   # scene 3 Broom Chase
WITCH_BB = WITCH.recolor("witch_blue_bronze", **BLUE_BRONZE)                       # scene 4 Cauldron Bake-Off
WIZARD_YB = WIZARD.recolor("wizard_yellow_black", **YELLOW_BLACK)                  # scene 5 Great Hall Feast
WIZARD_GS = WIZARD.recolor("wizard_green_silver", **GREEN_SILVER)                  # scene 8 Pumpkin Patronus

# Patronus turkey: same silhouette as TURKEY, recolored at runtime (see canvas.tint)
ALL = [OWL, LETTER, WIZARD, WIZARD_YB, WIZARD_GS, BROOM_RIDER_SG, WITCH_BB, BROOM_RIDER, GOLDEN_PIE, TURKEY, ROAST, RAW_TURKEY, HAT, CANDLE, LOCO, CAR,
       GRAVY_BOAT, PUMPKIN, CAULDRON, WITCH, APPLE, DRAGON_HEAD, DRAGON_WING, SPIT, SPARK]

# Plain pumpkin pie (cauldron scene)
PIE = Sprite("pie", {"o": "#E8B062", "O": "#F07B1A", "b": "#A8702E", "c": "#FFF3D6"}, """
...c...
.ooooo.
oOOOOOo
.bbbbb.
""")

ALL.append(PIE)
