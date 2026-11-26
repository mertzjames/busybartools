"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import bouquet, breakfast, card, finale, garden, hug, tea

PLAYLIST = [bouquet, breakfast, garden, card, hug, tea, finale]
from . import clock_bg, count_bg  # noqa: E402

CLOCK_BG = clock_bg
COUNT_BG = count_bg
