"""The four students: 2 wizards and 2 witches, each with their own look and house (docs/DECISIONS.md D19, D28).

| Student       | Scenes                         | House          | Look                                                  |
|---------------|--------------------------------|----------------|-------------------------------------------------------|
| SCARLET       | Broom Chase, The Feast Appears | scarlet & gold | wizard: messy dark hair, round glasses (D18)          |
| BLUE          | Cauldron, The Feast Appears    | blue & bronze  | witch: big curly chestnut hair, blue headband, short  |
| YELLOW        | Great Hall, The Feast Appears  | yellow & black | wizard: deep brown skin, stocky, striped bobble hat   |
| GREEN         | Patronus, The Feast Appears    | green & silver | witch: long honey-blonde braid with a green bow, tall |

Every student sprite has the same frame layout (see the constants below), so scenes can swap students freely.
Frames are built from one standing grid plus small overlay grids: in an overlay, '_' keeps the pixel underneath,
'.' clears it, and any other character paints over it. Sprites face right; the faces are drawn front-on.

Faces only use lit colors: black is an unlit LED and reads as a hole (D18).
"""

from __future__ import annotations

from dataclasses import dataclass

from busybar.sprite import Sprite

# Frame layout shared by every student sprite
STAND, STEP_A, STAND_2, STEP_B, WAND, CHEER = range(6)
WALK = (STAND, STEP_A, STAND_2, STEP_B)
FLICK = 6  # BLUE only: sideways wand flick used by the cauldron scene

# House scarves (D19). R = main stripe, Y = accent. "Black" is a lit dark grey: true black is an unlit LED.
SCARLET_GOLD = {"R": "#C8102E", "Y": "#F2B515"}
BLUE_BRONZE = {"R": "#2D50D2", "Y": "#C07A38"}
YELLOW_BLACK = {"R": "#F2C21A", "Y": "#5A5A5A"}
GREEN_SILVER = {"R": "#1E8C46", "Y": "#C4CAD6"}

# School robes, shoes and wand are shared, so the four read as classmates.
_SCHOOL = {"M": "#4B4A78", "m": "#33325A", "b": "#6B3E1C", "w": "#9A6A3A", "*": "#FFF6B0", "o": "#E8606E"}


def _over(base: str, *patches: str) -> str:
    """Overlay patch grids onto a base grid (top-aligned; a patch may have fewer rows than the base)."""
    rows = [list(r.strip()) for r in base.strip("\n").splitlines() if r.strip()]
    for patch in patches:
        for y, line in enumerate(r.strip() for r in patch.strip("\n").splitlines() if r.strip()):
            for x, ch in enumerate(line):
                if ch != "_":
                    rows[y][x] = ch
    return "\n".join("".join(r) for r in rows)


def _feet(base: str, *rows: str) -> str:
    """Replace the last len(rows) rows of a grid (walk-cycle legs)."""
    lines = [r.strip() for r in base.strip("\n").splitlines() if r.strip()]
    return "\n".join(lines[: len(lines) - len(rows)] + list(rows))


@dataclass(frozen=True)
class Student:
    name: str
    sprite: Sprite                 # frames: STAND, STEP_A, STAND_2, STEP_B, WAND, CHEER (+ FLICK for BLUE)
    tip: tuple[int, int]           # wand tip (sprite-relative) in the WAND and CHEER frames
    house: tuple[tuple[int, int, int], tuple[int, int, int]]  # scarf colors, for house-colored effects


def _student(name: str, palette: dict, house: dict, stand: str, step_a: tuple, step_b: tuple, wand: str,
             cheer: str, tip: tuple[int, int], *extra: str) -> Student:
    frames = [stand, _feet(stand, *step_a), stand, _feet(stand, *step_b), _over(stand, wand),
              _over(stand, wand, cheer), *extra]
    spr = Sprite(name, {**_SCHOOL, **house, **palette}, *frames)
    return Student(name, spr, tip, (spr.palette["R"], spr.palette["Y"]))


# --- SCARLET: wizard, scarlet & gold. Messy dark hair, round glasses (silver frames G around green eyes e, D18).
_SCARLET_STAND = """
.h.hh.h..
.hhhhhhh.
.hShhSS..
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
"""
SCARLET = _student(
    "student_scarlet", {"h": "#5A3A22", "S": "#F6C79C", "G": "#B4BCCC", "e": "#2FA84F"}, SCARLET_GOLD,
    _SCARLET_STAND, (".b....b..", "bb....bb."), ("...bb....", "...bbb..."),
    # wand up: tip at column 8, row 0 (the sparkle positions in the scenes rely on it)
    """
________*
________w
________w
_______S.
_______M.
______M__
_________
_________
_______._
""",
    # cheer: other arm up too, mouth open
    """
_________
S________
M________
M________
M__oo____
M________
M________
M________
""",
    (8, 0))

# Broom rider version of SCARLET (Broom Chase), same hair, glasses and scarf. Robe flaps over 2 frames.
SCARLET_BROOM = Sprite("student_scarlet_broom", {
    **_SCHOOL, **SCARLET_GOLD, "h": "#5A3A22", "S": "#F6C79C", "G": "#B4BCCC", "e": "#2FA84F",
    "B": "#8A5A2B", "s": "#D9B25C", "t": "#A9822F",
}, """
....h.hh.....
....hhhhhh...
....hShSS....
....GeGeG....
.....SSS.....
....RYRYRSS..
...MMMMMM....
..mMMMMMM....
s.MMMMMbb....
ssBBBBBBBBBBB
st..m.m......
""", """
....h.hh.....
....hhhhhh...
....hShSS....
....GeGeG....
.....SSS.....
....RYRYRSS..
..MMMMMMM....
.mMMMMMMM....
s..MMMMbb....
ssBBBBBBBBBBB
tsm..........
""")

# --- BLUE: witch, blue & bronze. Big curly chestnut hair (D17) with a blue headband (house color R), warm tan
# skin, lit brown eyes; the shortest of the four.
_BLUE_STAND = """
.hHh.hHh..
hhRRRRRRh.
HhSSSSSShH
hhSeSSeShh
hHSSSSSSHh
hhhSSSShhh
.H.RYRY.H.
..MMMMMM..
.MMMMMMMS.
.mMMMMMm..
.MMMMMMM..
..b...b...
"""
BLUE = _student(
    "student_blue", {"h": "#6E3E1E", "H": "#A0622C", "S": "#EEBC90", "e": "#4A2414"}, BLUE_BRONZE,
    _BLUE_STAND, (".b.....b..",), ("...bb.....",),
    """
_________*
_________w
_________w
________S_
________M_
_______M__
__________
__________
________._
""",
    """
__________
S_________
M_________
M_________
M___oo____
M_________
""",
    (9, 0),
    # FLICK: wand flicked out sideways, tip at (9, 6), where the cauldron ingredients launch from
    _over(_BLUE_STAND, """
__________
__________
__________
__________
__________
__________
_________*
________Sw
________M_
"""))

# --- YELLOW: wizard, yellow & black. Deep brown skin, stocky build, striped bobble hat in house colors.
_YELLOW_STAND = """
....PP....
...RRRR...
..YYYYYY..
..RRRRRR..
..hSSSSh..
..SeSSeS..
..SSSSSS..
...SSSS...
.RYRYRYRY.
MMMMMMMMM.
MMMMMMMMMS
mMMMMMMMM.
.MMMMMMMM.
.mMMMMMMm.
..bb..bb..
"""
YELLOW = _student(
    "student_yellow", {"h": "#4A3024", "S": "#B07A50", "e": "#40261A", "P": "#FFF0A0"}, YELLOW_BLACK,
    _YELLOW_STAND, (".bb....bb.",), ("...bbb....",),
    """
_________*
_________w
_________w
________S_
________M_
________M_
________M_
________M_
__________
__________
_________.
""",
    """
__________
__________
S_________
M_________
M_________
M__oo_____
M_________
M_________
M_________
""",
    (9, 0))

# --- GREEN: witch, green & silver. Fair rosy skin, blue eyes, slim and tall, a long honey-blonde braid over her
# right shoulder (viewer's left) tied with a green bow.
_GREEN_STAND = """
...hhh...
..hhhhh..
.hhSSShh.
.hSeSeSh.
.hSSSSSh.
.h.SSS...
.hRYRYR..
.hMMMMM..
AAMMMMMS.
.hmMMMm..
..MMMMM..
..MMMMM..
..mMMMm..
..b...b..
"""
GREEN = _student(
    "student_green", {"h": "#E2B84C", "S": "#FAD2BC", "e": "#3E8AE6", "A": "#2ECC64"}, GREEN_SILVER,
    _GREEN_STAND, (".b.....b.",), ("...bb....",),
    """
________*
________w
________w
_______S_
_______M_
______M__
_________
_________
_______._
""",
    """
_________
S________
M________
M________
M__o_____
M________
M________
""",
    (8, 0))

CAST = (SCARLET, BLUE, YELLOW, GREEN)
CAST_SPRITES = [s.sprite for s in CAST] + [SCARLET_BROOM]
