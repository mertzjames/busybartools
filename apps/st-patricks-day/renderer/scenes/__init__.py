"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import clock_bg, count_bg, day_bg, finale, jig, knot, parade, rainbow, river, shamrocks

# Playlist order (docs/DECISIONS.md D3). Cards alternate between scenes (clock, count).
PLAYLIST = [jig, rainbow, shamrocks, parade, river, knot, finale]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
DAY_BG = day_bg
