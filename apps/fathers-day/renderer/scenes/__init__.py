"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)

The order follows one summer day, dawn to night (docs/DECISIONS.md D3).
"""

from . import bike, catch, finale, fishing, gift, grill, hammock

PLAYLIST = [fishing, catch, bike, grill, gift, hammock, finale]
from . import clock_bg, count_bg  # noqa: E402

CLOCK_BG = clock_bg
COUNT_BG = count_bg
