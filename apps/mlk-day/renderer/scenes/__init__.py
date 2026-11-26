"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import bells, clock_bg, count_bg, dove, hands, march, mountaintop, service

# Playlist order (docs/DECISIONS.md D3): the march at sunrise opens, then peace, unity, freedom and service; the
# closing scene is dawn on the mountaintop with the word DREAM. Cards alternate between scenes (clock, count).
PLAYLIST = [march, dove, hands, bells, service, mountaintop]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
