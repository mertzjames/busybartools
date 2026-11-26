"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import cherry_tree, eagle, finale, flag, log_cabin, monuments, quill

PLAYLIST = [flag, cherry_tree, eagle, quill, monuments, log_cabin, finale]
from . import clock_bg, count_bg  # noqa: E402

CLOCK_BG = clock_bg
COUNT_BG = count_bg
