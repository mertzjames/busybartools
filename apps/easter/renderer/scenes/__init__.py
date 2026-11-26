"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)
"""

from . import basket, bunny_garden, clock_bg, count_bg, day_bg, egg_hunt, flowers, hatching, painting, sunrise

PLAYLIST = [bunny_garden, egg_hunt, hatching, painting, flowers, basket, sunrise]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
DAY_BG = day_bg
