"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import (broom_chase, cauldron, clock_bg, dragon_roast, feast, gravy_express, great_hall, owl_post, patronus,
               sorting)

# Playlist order (docs/DECISIONS.md D6, D29). A clock card follows each scene. The feast is the finale: the four
# students from scenes 3, 4, 5 and 8 meet at one table before the loop starts again.
PLAYLIST = [owl_post, gravy_express, broom_chase, cauldron, great_hall, sorting, dragon_roast, patronus, feast]
CLOCK_BG = clock_bg
