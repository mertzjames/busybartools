"""Live-text look for the app: the app-local "huge" digit font and the layout of every live screen.

The app draws all text that depends on the time (countdowns, the clock, the year) as xpmbitmaps from these fonts
and colors. build.py tone-maps the colors and exports them to app/shared/generated/show.ts and the mockup; the app
lays the text out with app/shared/screens.ts, and tests/live_parity.py checks it against busybar.font.draw_text.
"""

from __future__ import annotations

from busybar.font import register_font

# 10x15 digits with 3 px strokes for the final ten seconds and the new year (docs/DECISIONS.md D9).
HUGE = """
[0]
..######..
.########.
####..####
###....###
###....###
###....###
###....###
###....###
###....###
###....###
###....###
###....###
####..####
.########.
..######..
[1]
....###...
...####...
..#####...
.######...
....###...
....###...
....###...
....###...
....###...
....###...
....###...
....###...
....###...
.#########
.#########
[2]
..######..
.########.
####..####
###....###
.......###
......####
.....####.
....####..
...####...
..####....
.####.....
####......
###.......
##########
##########
[3]
..######..
.########.
####..####
###....###
.......###
......####
...######.
...######.
......####
.......###
.......###
###....###
####..####
.########.
..######..
[4]
......###.
.....####.
....#####.
...######.
..###.###.
.###..###.
###...###.
###...###.
##########
##########
......###.
......###.
......###.
......###.
......###.
[5]
##########
##########
###.......
###.......
###.......
########..
#########.
......####
.......###
.......###
.......###
###....###
####..####
.########.
..######..
[6]
..######..
.########.
####..####
###.......
###.......
###.......
########..
#########.
####..####
###....###
###....###
###....###
####..####
.########.
..######..
[7]
##########
##########
.......###
......####
......###.
.....####.
.....###..
....####..
....###...
...####...
...###....
...###....
...###....
...###....
...###....
[8]
..######..
.########.
####..####
###....###
###....###
####..####
.########.
.########.
####..####
###....###
###....###
###....###
####..####
.########.
..######..
[9]
..######..
.########.
####..####
###....###
###....###
###....###
####..####
.#########
..########
.......###
.......###
.......###
####..####
.########.
..######..
"""

register_font("huge", HUGE, 15, gap=2)

FONTS_USED = ["big", "tiny", "clock", "huge"]

GOLD = {"top": [255, 240, 170], "bottom": [236, 160, 30], "shadow": [104, 46, 0]}
SILVER = {"top": [255, 255, 255], "bottom": [168, 188, 226], "shadow": [40, 46, 96]}
PINK = {"top": [255, 196, 246], "bottom": [255, 46, 176], "shadow": [86, 0, 64]}
CYAN = {"top": [210, 255, 255], "bottom": [20, 196, 255], "shadow": [0, 52, 100]}


def spec(font: str, y: int, colors: dict) -> dict:
    return {"font": font, "y": y, **{k: list(v) for k, v in colors.items()}}


# Odometer windows (the odometer scene draws the frame around them; the app draws the digits).
ODO_WIN_W, ODO_WIN_H, ODO_WIN_Y = 9, 14, 1
ODO_WINDOWS = [15, 26, 37, 48]

# Untoned layout; build.py tone-maps every color before exporting it.
LAYOUT = {
    "card": {"main": spec("clock", 2, GOLD), "label": spec("tiny", 3, SILVER), "label_dy": 6, "gap": 3},
    "final": {"count": spec("clock", 1, GOLD), "bar": {"y": 15, "h": 1, "on": [255, 60, 184], "off": [56, 26, 72]}},
    # final10 picks specs[remaining % 4]: 10 pink, 9 silver, 8 gold, 7 cyan, ... and the 0 is gold
    "final10": {"specs": [spec("huge", 0, GOLD), spec("huge", 0, SILVER), spec("huge", 0, PINK), spec("huge", 0, CYAN)]},
    "celebrate": {"greeting": spec("tiny", 1, GOLD), "year": spec("big", 8, PINK), "huge": spec("huge", 0, GOLD)},
    "odometer": {"spec": spec("clock", 2, GOLD), "windows": ODO_WINDOWS, "win_y": ODO_WIN_Y, "win_w": ODO_WIN_W,
                 "win_h": ODO_WIN_H},
}
