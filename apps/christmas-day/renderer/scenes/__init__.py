"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import carolers, clock_bg, finale, presents, sleigh_ride, snowman, stockings, toy_train, tree_trim

# Playlist order (docs/DECISIONS.md D2): Christmas Eve into Christmas Day. A clock card follows each scene.
PLAYLIST = [tree_trim, carolers, sleigh_ride, stockings, presents, toy_train, snowman, finale]
CLOCK_BG = clock_bg
