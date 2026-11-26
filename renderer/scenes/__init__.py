"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import (broom_chase, cauldron, clock_bg, dragon_roast, gravy_express, great_hall, owl_post, patronus,
               sorting)

# Playlist order (docs/DECISIONS.md D6). A clock card follows each scene.
PLAYLIST = [owl_post, gravy_express, broom_chase, cauldron, great_hall, sorting, dragon_roast, patronus]
CLOCK_BG = clock_bg
