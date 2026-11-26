"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)

DAYS[i] is the vignette for December i+1; DAYS[24] is the Christmas Day finale (docs/DECISIONS.md D2).
"""

import importlib

DAY_MODULES = [
    "day01_first_snow", "day02_mittens", "day03_cocoa", "day04_candy_cane", "day05_bells", "day06_ornaments",
    "day07_candles", "day08_penguin", "day09_gingerbread", "day10_cookies", "day11_polar_bear", "day12_wreath",
    "day13_stockings", "day14_snowman", "day15_toy_soldier", "day16_sledding", "day17_carolers",
    "day18_nutcracker", "day19_presents", "day20_reindeer", "day21_north_pole", "day22_tree", "day23_sleigh",
    "day24_star", "day25_finale",
]

DAYS = [importlib.import_module(f"{__name__}.{m}") for m in DAY_MODULES]

from . import card_bg, door, winter  # noqa: E402

DOOR = door
WINTER = winter
CARD = card_bg
ALL = DAYS + [DOOR, WINTER, CARD]
