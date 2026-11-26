"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import city_fireworks, cookout, eagle_flag, finale, liberty_bell, parade, sparklers

PLAYLIST = [parade, liberty_bell, cookout, eagle_flag, sparklers, city_fireworks, finale]
from . import clock_bg, count_bg  # noqa: E402

CLOCK_BG = clock_bg
COUNT_BG = count_bg
