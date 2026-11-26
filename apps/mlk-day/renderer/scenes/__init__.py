"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import clock_bg, count_bg, dove, hands, march, service

# Playlist order (docs/DECISIONS.md D3): night into dawn into a day of service. Cards alternate between scenes.
PLAYLIST = [march, dove, hands, service]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
