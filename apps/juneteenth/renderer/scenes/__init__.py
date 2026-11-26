"""Scene registry. Each scene module exposes:

NAME      file-safe id (also the .anim file name)
TITLE     human title
SECONDS   duration
KEYFRAMES [(seconds, caption), ...] for storyboards
render()  -> list[PIL.Image] (RGBA, 72x16, canvas.FPS)

The playlist opens solemn (dawn, the news) and becomes joyful (the flag, the cookout, red foods, music, fireworks),
the way the day is observed (docs/DECISIONS.md D3).
"""

from . import clock_bg, cookout, count_bg, dawn, day_bg, finale, flag, music, news, red_foods

PLAYLIST = [dawn, news, flag, cookout, red_foods, music, finale]
CLOCK_BG = clock_bg
COUNT_BG = count_bg
DAY_BG = day_bg
