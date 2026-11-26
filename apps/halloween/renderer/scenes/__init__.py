"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import bats, cat, clock_bg, count_bg, ghost, haunted, lanterns, skeletons, trick, witch

# Playlist order (docs/DECISIONS.md D3). Cards alternate between scenes (clock, count).
PLAYLIST = [lanterns, haunted, trick, bats, ghost, cat, witch, skeletons]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
